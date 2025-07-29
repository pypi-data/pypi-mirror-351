'''Distributed Logistic Regression'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# Linear and Logistic Regression have portions of identical code that should
# not be abstracted away.
# pylint complains about various members of autograd.numpy being missing,
# but we see them when we check manually.
# pylint: disable=duplicate-code,no-member

import pickle
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

import autograd.numpy as np  # type: ignore[import]
from autograd import jacobian  # type: ignore[import]
from autograd.scipy.special import expit  # type: ignore[import]

from ...algorithms.impl.distributed_algorithm_instance import NoDataError  # type: ignore[import]
from ...catalog.catalog import upcast
from ...neighbor_manager.node_id import NodeID
from ...problem_def.task import DataType, TaskType
from ...wrangler.dataset import Dataset, RoleName, MetadataError
from ...wrangler.logger import Logger

from ..impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..impl.linear_distributed_algorithm_instance import (
    LinearDistributedAlgorithmInstance, LinearNeighborState,
    norm2, inner_product)


log = Logger(__file__).logger()


def _validate_xv(x: np.ndarray, v: np.ndarray) -> None:
    '''Validate the dimensions of x and v.

    x: np.ndarray with 2 or fewer dimensions
    y: np.ndarray with 1 dimension
    '''
    assert x.ndim <= 2, (
        f'BUG: exepcted x.ndim <=2, instead found {x.ndim}'
    )
    assert v.ndim == 1, (
        'BUG: expected 1 dimensional v; instead found {v.ndim}'
    )


def _grad_log_phi(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    '''Return the gradient of the log of phi(x, v).'''
    _validate_xv(x, v)
    eps = 1e-15
    phi = _phi(x, v)
    if isinstance(phi, np.ndarray):
        phi = phi[:, np.newaxis]
    return _grad_phi(x, v) / (phi + eps)


def _grad_log_1mphi(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    '''Return the gradient of the log of 1 - phi(x, v).'''
    _validate_xv(x, v)
    eps = 1e-15
    phi = _phi(x, v)
    if isinstance(phi, np.ndarray):
        phi = phi[:, np.newaxis]
    return -_grad_phi(x, v) / (1 - phi + eps)


def _grad_phi(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    '''Return the gradient of the logistic function of x and v.'''
    _validate_xv(x, v)
    xv = x @ v
    if x.ndim > 1:
        return (np.exp(-xv) / (1.0 + np.exp(-xv)) ** 2)[:, np.newaxis] * x
    return (np.exp(-xv) / (1.0 + np.exp(-xv)) ** 2) * x


def _log_phi(x: np.ndarray, v: np.ndarray) -> Union[np.float64, np.ndarray]:
    '''Return the log of phi(x, v).'''
    _validate_xv(x, v)
    eps = 1e-15
    return np.log(_phi(x, v) + eps)


def _log_1mphi(x: np.ndarray, v: np.ndarray) -> Union[np.float64, np.ndarray]:
    '''Return the log of 1 - phi(x, v).'''
    _validate_xv(x, v)
    eps = 1e-15
    return np.log(1 - _phi(x, v) + eps)


def _phi(x: np.ndarray, v: np.ndarray) -> Union[np.float64, np.ndarray]:
    '''Return the logistic function of x and v.'''
    _validate_xv(x, v)
    # Fixes overflow error (return 1.0 / (1.0 + np.exp(-x @ v)))
    return expit(x @ v)


class AutonLogisticRegressionNeighbor(LinearNeighborState):
    '''A neighbor in the distributed logistic regression model.'''
    _positive_class: int

    def __init__(self,
                 positive_class: int, v: np.ndarray, columns: Optional[List[Union[int, str]]]):
        super().__init__(v=v, columns=columns)
        assert isinstance(positive_class, int)  # mypy does not catch when this is violated
        self._positive_class = positive_class

    def encode(self) -> bytes:
        '''Encode message for distributed neighbors.'''
        #  minimal: communicate as little information as possible
        return pickle.dumps(
            (self._positive_class, self._v, self.columns))

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'AutonLogisticRegressionNeighbor':
        '''Decode a message from a neighbor.'''
        # minimal: communicate as little information as possible
        positive_class, v, cols = pickle.loads(serialized_model)
        assert isinstance(positive_class, int), (
            'BUG: expected positive_class to be an int, '
            f'instead found {positive_class} of type {type(positive_class)}'
        )
        assert isinstance(v, np.ndarray), (
            f'BUG: expected v to be an np.ndarray, instead found {v} of type {type(v)}'
        )
        if cols is not None:
            cols = cls._cast_columns(cols)
        return cls(positive_class=positive_class,
                   v=v,
                   columns=cols)

    @property
    def positive_class(self) -> int:
        '''The numeric identifier of the positive class in the classification problem.'''
        return self._positive_class

    @positive_class.setter
    def positive_class(self, value: int) -> None:
        '''The numeric identifier of the positive class in the classification problem.'''
        assert isinstance(value, int)  # mypy does not catch when this is violated.
        self._positive_class = value


class AutonLogisticRegressionInstance(LinearDistributedAlgorithmInstance):
    '''Binary logistic regression that supports distributed AI.

    As a distributed model, this instance can share information about its
    trained state with other instances and update its trained state using
    information shared by other instances.
    '''
    _neighbor_constructor = AutonLogisticRegressionNeighbor

    # This is a type annotation for _my_state.
    _predict_state: Optional[AutonLogisticRegressionNeighbor] = None

    # _my_state: Optional[AutonLogisticRegressionNeighbor] = None
    @property  # type: ignore[override]
    def _my_state(self) -> Optional[AutonLogisticRegressionNeighbor]:
        retval = LinearDistributedAlgorithmInstance._my_state.fget(self)  # type: ignore[attr-defined] # pylint: disable=assignment-from-no-return, line-too-long
        assert retval is None or isinstance(retval, AutonLogisticRegressionNeighbor), (
            'BUG: expected _my_state to be None or an AutonLogisticRegressionNeighbor.')
        return retval

    @_my_state.setter
    def _my_state(self, value: Optional[AutonLogisticRegressionNeighbor]) -> None:
        assert value is None or isinstance(value, AutonLogisticRegressionNeighbor), (
            'BUG: expected value to be None or an AutonLogisticRegressionNeighbor.')
        LinearDistributedAlgorithmInstance._my_state.fset(self, value)  # type: ignore[attr-defined]

    @property
    def _yhat_is_proba(self) -> bool:
        return True

    @property
    def _neighbor_models_iter(self) -> Iterable[AutonLogisticRegressionNeighbor]:
        for v in super()._neighbor_models_iter:
            assert isinstance(v, AutonLogisticRegressionNeighbor), (
                'BUG: expected neighbor_models to contain AutonLogisticRegressionNeighbor, '
                f'instead found {v} of type {type(v)}'
            )
            yield v

    def _standardize_y(self, y: np.ndarray) -> np.ndarray:
        '''Regularize the target values.'''
        positive_class = 1
        if self._my_state is not None and self._my_state.positive_class is not None:
            positive_class = self._my_state.positive_class
        return np.array(
            [1 if y_ == positive_class else 0 for y_ in y])

    def _yhat(self, x: np.ndarray) -> np.ndarray:
        assert self._predict_state is not None, (
            'BUG: self._predict_state should not be None when _yhat is called.'
            ' This should have been set in _fit'
        )
        yhat = np.empty((x.shape[0], 2))
        yhat[:, 1] = _phi(x, self._predict_state.v)
        yhat[:, 0] = 1.0 - yhat[:, 1]
        return yhat

    def _reconcile_class(self) -> None:
        '''Make sure models agree about which class is positive.'''
        assert self._my_state is not None, (
            'BUG: self._my_state should not be None when _reconcile_class is called.'
        )
        if all(m.positive_class == self._my_state.positive_class
               for m in self._neighbor_models_iter):
            return  # nothing to do

        old_positive_class = self._my_state.positive_class or 0
        self._my_state.positive_class = int(max(
            [old_positive_class]
            + [m.positive_class for m in self._neighbor_models_iter]
        ))
        # modify models in place
        for m in self._neighbor_models_iter:
            if m.positive_class != self._my_state.positive_class:
                m.v = -m.v
                m.positive_class = self._my_state.positive_class
        if self._my_state.positive_class != old_positive_class and self._my_state is not None:
            self._my_state.v = -self._my_state.v  # pylint: disable=invalid-unary-operand-type

    def _decode(self, serialized_model: bytes) -> AutonLogisticRegressionNeighbor:
        '''Decode a message from distributed neighbors.'''
        return AutonLogisticRegressionNeighbor.decode(serialized_model)

    def _prepare_data(self, dataset: Optional[Dataset]  # pylint: disable=too-many-branches
                      ) -> Tuple[np.ndarray, np.ndarray]:
        '''Extract covariates and target, accounting for the possibility that there's no data.'''
        if dataset is None:
            if list(self._neighbor_models_iter):
                positive_class = int(max(m.positive_class for m in self._neighbor_models_iter))
                d = max(len(m.v) for m in self._neighbor_models_iter) - 1
                np_cov = np.zeros((0, d))
            else:
                # TODO(Piggy/Dan) Need to figure out how to deal with no neighbors and no data.
                raise NoDataError("No data and no neighbors.")
            np_tar = np.zeros(0)
        else:
            try:
                np_tar = dataset.target_table.as_(np.ndarray)
            except KeyError:
                np_tar = np.array([0])
            np_cov = dataset.covariates_table.as_(np.ndarray)

            positive_class = int(max(np_tar))
            if RoleName.TARGET in dataset.metadata.pos_labels:
                try:
                    poslabel = dataset.metadata.pos_labels[RoleName.TARGET]
                    positive_class = int(poslabel)
                except TypeError as e:
                    raise MetadataError(
                        f'{self._algorithm.name if self._algorithm is not None else None} requires '
                        'integer classes, but '
                        'positive label in metadata cannot be converted to int. '
                        f'Found {poslabel} of type {type(poslabel)} instead.'
                    ) from e

        # Add a column for the intercept.
        np_cov = np.hstack((np_cov, np.ones((np_cov.shape[0], 1))))

        _, d = np_cov.shape

        if self._my_state is None:
            self._my_state = AutonLogisticRegressionNeighbor(
                positive_class=positive_class,
                v=np.zeros(d),
                columns=self._columns)

        self._reconcile_class()
        return np_cov, np_tar

    def _objective_with_gradient(
            self, x: np.ndarray, y: np.ndarray, v_old: np.ndarray,
            l2: np.float64, _lambda: np.float64, omega: np.float64,
            k: int) -> Tuple[Callable[[np.ndarray], np.float64],
                             Callable[[np.ndarray], np.ndarray]]:
        """
        Data loss:
            min_v L2_Loss(data,v)
            + L2_coeff*||v||^2
            + lambda*(1-omega)/omega*||v-v0||^2
            + sum_{j in N} lambda/|N|*||v-v_j||
        """

        if k > 0:
            def fun(v: np.ndarray) -> np.float64:
                data_loss = (
                    -(y * _log_phi(x, v)).sum()             # positive class
                    - ((1 - y) * _log_1mphi(x, v)).sum()    # negative class
                )
                l2_regularization = (l2) * norm2(v[:-1])

                # whether to use DJAM or fn space reg
                # if DJAM: need to know weights for all neighbors
                # need a plan to handle 2 cases:
                #   weight from neighbor that we recieved no message from
                #       (set to 0?)
                #   message from neighbor with no weight
                #       (ignore or throw error)

                if self._distributed.regularization_type == 'djam':
                    weights: Dict[NodeID, float] = self._distributed.neighbor_weights
                    distributed_regularization = 0.0
                    for nid, neighbor in self._neighbor_metadata.items():
                        assert isinstance(neighbor.current_state, LinearNeighborState)

                        w = weights[nid]
                        inprod = inner_product(
                            v - neighbor.current_state.v, v - neighbor.current_state.v)
                        distributed_regularization += w * inprod  # type: ignore

                    distributed_regularization = 0.5 * distributed_regularization

                else:
                    neighbor_regularization = (
                        -2.0 * (_lambda / k)
                        * sum(inner_product(m.v, v) for m in self._neighbor_models_iter)
                    )
                    self_regularization = (
                        -2.0 * (_lambda * (1 - omega) / omega) * inner_product(v_old, v)
                    )
                    shared_regularization = (_lambda / omega) * norm2(v)
                    distributed_regularization = (
                        neighbor_regularization + self_regularization + shared_regularization)
                return (data_loss
                        + l2_regularization
                        + distributed_regularization)

            jac = jacobian(fun)  # pylint: disable=no-value-for-parameter

            # def jac(v: np.ndarray) -> np.ndarray:
            #     #This isn't necessarily correct
            #     data_loss = (
            #         -(y[:, np.newaxis] * _grad_log_phi(x, v)).sum(0)
            #         - ((1 - y[:, np.newaxis]) * _grad_log_1mphi(x, v)).sum(0)
            #     )
            #     l2_regularization = (_lambda / omega + l2) * grad_norm2(v)
            #     neighbor_regularization = (
            #         - 2 * _lambda / k
            #         * sum(grad_inner_product(m.v, v) for m in self._neighbor_models_iter)
            #     )
            #     self_regularization = (
            #         - 2 * _lambda * (1 - omega) / omega * grad_inner_product(v_old, v)
            #     )
            #     return (data_loss
            #             + l2_regularization
            #             + neighbor_regularization
            #             + self_regularization)

        else:
            def fun(v: np.ndarray) -> np.float64:
                data_loss = -(y * _log_phi(x, v)).sum() - ((1 - y) * _log_1mphi(x, v)).sum()
                l2_regularization = l2 * norm2(v[:-1])
                return data_loss + l2_regularization

            jac = jacobian(fun)  # pylint: disable=no-value-for-parameter

            # def jac(v: np.ndarray) -> np.ndarray:
            #     print("DEBUG v", v)
            #     data_loss = (
            #         -(y[:, np.newaxis] * _grad_log_phi(x, v)).sum(0)
            #         - ((1 - y[:, np.newaxis]) * _grad_log_1mphi(x, v)).sum(0)
            #     )
            #     l2_regularization = np.array(list(l2 * grad_norm2(v[:-1])) + [0])
            #     return data_loss + l2_regularization

        return fun, jac


class AutonLogisticRegression(Algorithm):
    '''Class for Auton Lab's implementation of Logistic Regression'''
    _name = "auton_logistic_regression"
    _tags = {
        'tasks': [TaskType.BINARY_CLASSIFICATION.name],
        'data_types': [DataType.TABULAR.name],
        'source': ['auton_lab'],
        'distributed': ['true']
    }
    _instance_constructor = AutonLogisticRegressionInstance
    _default_hyperparams = {
        'Lambda': 100.0,
        'L2': 1.0,
        'omega': 2.0 / 3.0,
        'tol': 0.000000001,
        'maxiter': None,
    }

    def instantiate(self, **hyperparams) -> 'AutonLogisticRegressionInstance':
        return super().instantiate(**hyperparams)


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = AutonLogisticRegression(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
