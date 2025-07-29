'''Distributed Linear Regression'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# Linear and Logistic Regression have portions of identical code that should
# not be abstracted away.
# pylint: disable=duplicate-code

import pickle
from typing import Callable, Iterable, Optional, Tuple

import numpy as np


from ...catalog.catalog import upcast
from ...problem_def.task import DataType, TaskType
from ...wrangler.dataset import Dataset
from ...wrangler.logger import Logger

from ..impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..impl.distributed_algorithm_instance import NoDataError
from ..impl.linear_distributed_algorithm_instance import (
    LinearDistributedAlgorithmInstance, LinearNeighborState,
    norm2, inner_product)


logger = Logger(__file__).logger()


class AutonLinearRegressionNeighbor(LinearNeighborState):
    '''A neighbor in the distributed linear regression model.'''

    def encode(self) -> bytes:
        '''Encode message for distributed neighbors.'''
        #  minimal: communicate as little information as possible
        return pickle.dumps((self._v, self.columns))

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'AutonLinearRegressionNeighbor':
        '''Decode a message from a neighbor.'''
        got = pickle.loads(serialized_model)
        assert len(got) == 2, (
            f'BUG: expected to recv a tuple of length 2, instead found {got} of length {len(got)}.'
        )
        (v, cols) = got
        assert isinstance(v, np.ndarray), (
            f'BUG: expected v to be an np.ndarray, instead found {v} of type {type(v)}'
        )
        if cols is not None:
            cols = cls._cast_columns(columns=cols)
        return cls(v=v, columns=cols)


class AutonLinearRegressionInstance(LinearDistributedAlgorithmInstance):
    '''Binary logistic regression that supports distributed AI.

    As a distributed model, this instance can share information about its
    trained state with other instances and update its trained state using
    information shared by other instances.
    '''
    _neighbor_constructor = AutonLinearRegressionNeighbor

    # This is a type annotation for _my_state.
    _predict_state: Optional[AutonLinearRegressionNeighbor] = None

    @property  # type: ignore[override]
    def _my_state(self) -> Optional[AutonLinearRegressionNeighbor]:
        retval = LinearDistributedAlgorithmInstance._my_state.fget(self)  # type: ignore[attr-defined] # pylint: disable=assignment-from-no-return,line-too-long
        assert retval is None or isinstance(retval, AutonLinearRegressionNeighbor), (
            'BUG: expected _my_state to be None or an AutonLinearRegressionNeighbor.')
        return retval

    @_my_state.setter
    def _my_state(self, value: Optional[AutonLinearRegressionNeighbor]) -> None:
        assert value is None or isinstance(value, AutonLinearRegressionNeighbor), (
            'BUG: expected value to be None or an AutonLinearRegressionNeighbor.')
        LinearDistributedAlgorithmInstance._my_state.fset(self, value)  # type: ignore[attr-defined]

    @property
    def _yhat_is_proba(self) -> bool:
        return False

    @property
    def _neighbor_models_iter(self) -> Iterable[AutonLinearRegressionNeighbor]:
        for v in super()._neighbor_models_iter:
            assert isinstance(v, AutonLinearRegressionNeighbor), (
                'BUG: expected neighbor_models to contain AutonLinearRegressionNeighbor, '
                f'instead found {v} of type {type(v)}'
            )
            yield v

    def _standardize_y(self, y: np.ndarray) -> np.ndarray:
        '''Regularize the target values.'''
        return y

    def _yhat(self, x: np.ndarray) -> np.ndarray:
        assert self._predict_state is not None, (
            'BUG: self._predict_state should not be None when _yhat is called.'
            ' This should have been set in _fit'
        )
        return self._predict_state.v @ x.T

    def _decode(self, serialized_model: bytes) -> AutonLinearRegressionNeighbor:
        '''Decode a message from distributed neighbors.'''
        return AutonLinearRegressionNeighbor.decode(serialized_model)

    def _prepare_data(self, dataset: Optional[Dataset]) -> Tuple[np.ndarray, np.ndarray]:
        '''Extract covariates and target, accounting for the possibility that there's no data.'''
        np_tar: np.ndarray[Tuple[int, ...], np.dtype[np.float64]] = np.zeros(0)
        if dataset is None:
            if list(self._neighbor_models_iter):
                d = max(len(m.v) for m in self._neighbor_models_iter) - 1
                np_cov = np.zeros((0, d))
            else:
                # TODO(Piggy/Dan) Need to figure out how to deal with no neighbors and no data.
                raise NoDataError("No data and no neighbors.")
        else:
            try:
                np_tar = dataset.target_table.as_(np.ndarray)
            except KeyError:
                np_tar = np.array([0], dtype=np.float64)
            np_cov = dataset.covariates_table.as_(np.ndarray)

        # Add a column for the intercept.
        np_cov = np.hstack((np_cov, np.ones((np_cov.shape[0], 1))))  # type: ignore[assignment]

        _, d = np_cov.shape

        if self._my_state is None:
            self._my_state = AutonLinearRegressionNeighbor(
                v=np.zeros(d),
                columns=self._columns)

        return np_cov, np_tar

    def _objective_with_gradient(
            self, x: np.ndarray, y: np.ndarray, v_old: np.ndarray,
            l2: np.float64, _lambda: np.float64, omega: np.float64,
            k: int) -> Tuple[Callable[[np.ndarray], np.float64],
                             Callable[[np.ndarray], np.ndarray]]:
        '''Return the objective function and:190
          its gradient.'''

        if k > 0:
            def fun(v: np.ndarray) -> np.float64:
                data_loss = (
                    np.square(y - ((v @ x.T))).sum()
                )
                l2_regularization = l2 * norm2(v[:-1])
                # TODO(Merritt): Jack doesn't think dividing by k works here since
                #   neighbors will weight each other non-symmetrically.
                # Send information about neighbors' neighbors?
                neighbor_regularization = (
                    -2 * _lambda / k
                    * sum(inner_product(m.v, v) for m in self._neighbor_models_iter)
                )
                self_regularization = (
                    -2 * _lambda * (1 - omega) / omega * inner_product(v_old, v)
                )
                shared_regularization = (_lambda / omega) * norm2(v)
                return (data_loss
                        + l2_regularization
                        + neighbor_regularization
                        + self_regularization
                        + shared_regularization)

            def jac(v: np.ndarray) -> np.ndarray:
                data_loss_grad = (2 * (v @ x.T - y) * x.T).sum(1)
                # TODO(Merritt): maybe we can do this without allocating an extra array
                v_zero_intercept = v.copy()
                v_zero_intercept[-1] = 0
                l2_regularization_grad = 2 * l2 * v_zero_intercept
                neighbor_regularization_grad = -2 * _lambda / k * sum(
                    m.v for m in self._neighbor_models_iter)
                self_regularization_grad = -2 * _lambda * (1 - omega) / omega * v_old
                shared_regularization_grad = 2 * (_lambda / omega) * v
                return (data_loss_grad
                        + l2_regularization_grad
                        + neighbor_regularization_grad
                        + self_regularization_grad
                        + shared_regularization_grad)

        else:
            def fun(v: np.ndarray) -> np.float64:
                data_loss = np.square(y - (v @ x.T)).sum()
                l2_regularization = l2 * norm2(v[:-1])
                return data_loss + l2_regularization

            def jac(v: np.ndarray) -> np.ndarray:
                data_loss_grad = (2 * (v @ x.T - y) * x.T).sum(1)
                v_zero_intercept = v.copy()
                v_zero_intercept[-1] = 0
                l2_regularization_grad = 2 * l2 * v_zero_intercept
                return (data_loss_grad
                        + l2_regularization_grad)

        return fun, jac


class AutonLinearRegression(Algorithm):
    '''Class for Auton Lab's implementation of Linear Regression'''
    _name = "auton_linear_regression"
    _tags = {
        'tasks': [TaskType.REGRESSION.name],
        'data_types': [DataType.TABULAR.name],
        'source': ['auton_lab'],
        'distributed': ['true']
    }
    _instance_constructor = AutonLinearRegressionInstance
    _default_hyperparams = {
        'Lambda': 100.0,  # Neighbor regularization
        'L2': 1.0,  # The normal weight regularization
        'omega': 2.0 / 3.0,  # Self regularization with last iteration's local weights
        'tol': 0.000000001,
        'maxiter': None,
    }

    def instantiate(self, **hyperparams) -> 'AutonLinearRegressionInstance':
        return super().instantiate(**hyperparams)


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = AutonLinearRegression(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
