'''Base class for distributed linear algorithms.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Callable, Iterable, List, Optional, Tuple, TypeVar, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize  # type: ignore[import]


from ...algorithms.impl.algorithm import Algorithm, HyperparamError
from ...config_components.distributed_config import DistributedConfig
from ...tables.impl.table import TableFactory
from ...wrangler.dataset import Dataset, RoleName
from ...wrangler.logger import Level, Logger

from .distributed_algorithm_instance import (
    DistributedAlgorithmInstance, NeighborState, NoDataError)


log = Logger(__file__, level=Level.INFO).logger()


# These functions assume x is 1 or 2 dimensional and v is 1-dimensional


def grad_norm2(a: np.ndarray) -> np.ndarray:
    '''Return the gradient of the squared norm of a.'''
    return 2.0 * a


def grad_inner_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:  # pylint: disable=unused-argument
    '''Return the gradient of the inner product of a and b.'''
    return a


def inner_product(a: np.ndarray, b: np.ndarray) -> Union[np.float64, np.ndarray]:
    '''Return the inner product of a and b.'''
    return a @ b


def norm2(a: np.ndarray) -> np.float64:
    '''Return the squared norm of a.'''
    return np.square(a).sum()  # np.linalg.norm(a) ** 2


NeighborStateSubclass = TypeVar('NeighborStateSubclass', bound='NeighborState')


class LinearNeighborState(NeighborState[NeighborStateSubclass]):
    '''Base class for Linear Neighbor States.'''
    _v: np.ndarray

    def __init__(self, v: np.ndarray, columns: Optional[List[Union[int, str]]] = None) -> None:
        super().__init__(columns=columns)
        self._v = v

    def __str__(self) -> str:
        '''Used for more readable logs when investigating convergence.'''
        return str(self._v)

    def __repr__(self) -> str:
        '''A more verbose representation of our state than __str__.'''
        return f'{self.__class__.__name__}(v = {self._v}, columns = {self.columns})'

    @property
    def v(self) -> np.ndarray:
        '''The internal state of the model.'''
        return self._v

    @v.setter
    def v(self, value: np.ndarray) -> None:
        '''The internal state of the model.'''
        self._v = value

    def _distance(self, other: 'LinearNeighborState') -> np.float64:
        '''Compute distance between two models.'''
        assert isinstance(other, type(self))
        a: np.float64 = norm2(other.v)
        b: np.float64 = norm2(self.v)
        ab = inner_product(self.v, other.v)
        assert isinstance(ab, np.float64), (
            f'BUG: expected np.float64, instead found {type(ab)}'
        )
        dist: np.float64 = a + b - 2 * ab
        return dist

    def distance(self, other: NeighborStateSubclass) -> float:
        assert isinstance(other, type(self))
        return float(self._distance(other))


class LinearDistributedAlgorithmInstance(DistributedAlgorithmInstance, metaclass=abc.ABCMeta):
    '''Base class for distributed linear algorithms.'''

    _l2: np.float64
    _tol: np.float64
    _maxiter: int

    def __init__(self,
                 parent: Algorithm,
                 distributed: DistributedConfig,
                 **kwargs):
        hyperparams = parent.hyperparams(**kwargs)
        if not isinstance(distributed, DistributedConfig):
            raise HyperparamError(
                'distributed must be a DistributedConfig, instead found '
                f'{distributed} of type {type(distributed)}')
        self._l2 = np.float64(hyperparams.pop('L2'))

        self._last_dataset = None
        super().__init__(parent, distributed=distributed, **hyperparams)

    @property
    def _neighbor_models_iter(self) -> Iterable[LinearNeighborState]:
        for v in super()._neighbor_models_iter:
            assert isinstance(v, LinearNeighborState), (
                'BUG: expected neighbor_models to contain AutonLinearRegressionNeighbor, '
                f'instead found {v} of type {type(v)}'
            )
            yield v

    @property
    @abc.abstractmethod
    def _yhat_is_proba(self) -> bool:
        '''Is yhat probabilites?'''

    @property
    def _yhat_is_multivalued(self) -> bool:
        '''True if yhat returns a vector of results, 1 per column of x.'''
        return False

    @abc.abstractmethod
    def _prepare_data(self, dataset: Optional[Dataset]) -> Tuple[np.ndarray, np.ndarray]:
        '''Prepare data for fitting or predicting.'''
        raise NotImplementedError

    def _standardize_y(self, y: np.ndarray) -> np.ndarray:
        '''Regularize the target values.'''
        log.error('%s._standardize_y should not be called.', type(self).__name__)
        return y

    def _objective_with_gradient(
        self, x: np.ndarray, y: np.ndarray, v_old: np.ndarray,
        l2: np.float64, _lambda: np.float64, omega: np.float64,
        k: int) -> Tuple[Callable[[np.ndarray], np.float64],
                         Callable[[np.ndarray], np.ndarray]]:
        '''Return the objective function and its gradient.'''
        _, _, _, _, _, _, _ = x, y, v_old, l2, _lambda, omega, k
        log.error(
            '%s._objective_with_gradient should not be called.', type(self).__name__)
        return (lambda _: np.float64(0.0), lambda _: np.zeros_like(v_old))

    @abc.abstractmethod
    def _yhat(self, x: np.ndarray) -> np.ndarray:
        '''Return the predicted values as an np.ndarray.'''
        raise NotImplementedError

    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Fit a model based on train data.
        '''

        try:
            np_cov, np_tar = self._prepare_data(dataset)
        except NoDataError:
            return  # There is nothing to do.

        log.log(5,  # log level verbose
                'Node %s (%x) is fitting %s; len(neighbor_models): %s,\n dataset: %r',
                self._my_id, id(self),
                type(self).__name__, len(list(self._neighbor_models_iter)), dataset)
        x = np_cov
        n, d = x.shape

        # If we have neither data nor neighbors, there's nothing to do.
        if dataset is None and not list(self._neighbor_models_iter):
            return

        omega = self._omega
        _lambda = self._lambda

        assert self._my_state is not None, (
            'BUG: self._my_state should not be None when _fit is called.'
        )
        assert isinstance(self._my_state, LinearNeighborState), (
            'BUG: expected self._my_state to be a LinearNeighborState, '
            f'instead found {self._my_state} of type {type(self._my_state)}'
        )
        y = self._standardize_y(np_tar)
        k = len(self._neighbor_metadata)

        if n == 0:
            # If you have no data take the mean of your neighbors.
            # If there are also no neighbors do nothing.
            if k != 0:
                self._my_state.v = np.mean([m.v for m in self._neighbor_models_iter], axis=0)
        else:
            if self._my_state.v.size != d:
                # no previous fit
                # v_old (v from last fit) to all zeros
                v_old = np.zeros(d)
                # set omega to 1 to disable self-regularization
                omega = np.float64(1.0)
            else:
                # previous fit exists
                v_old = self._my_state.v.copy()

            l2 = self._l2
            fun, jac = self._objective_with_gradient(
                x=x, y=y, v_old=v_old, l2=l2, _lambda=_lambda, omega=omega, k=k)
            x0 = self._my_state.v if self._my_state is not None else np.zeros(d)
            if self._maxiter is not None:
                soln = minimize(
                    fun, x0, method='BFGS', jac=jac,
                    tol=self._tol, options={'maxiter': self._maxiter})
            else:
                soln = minimize(
                    fun, x0, method='BFGS', jac=jac,
                    tol=self._tol)
            self._my_state.v = soln.x

    def _predict(self, dataset: Optional[Dataset], **kwargs) -> Optional[Dataset]:
        '''Apply model to input dataset to create output.

        This may require that the model is fit (self.trained == True) before it is called.
        '''
        assert self._predict_state is not None, (
            'BUG: self._predict_state should not be None when predict is called.'
        )
        assert isinstance(self._predict_state, LinearNeighborState), (
            'BUG: expected my_state to be a LinearNeighborState, '
            f'instead found {self._predict_state} of type {type(self._predict_state)}'
        )

        if dataset is None:
            return None

        x = self._prepare_data(dataset)[0]

        yhat = self._yhat(x)

        retval = dataset.output()
        # TODO(Piggy/Merritt): Convert to picard format.
        #   Preserve the column names as class names
        #   Other classification algorithms should follow the
        #   format of one column per class with probabilities
        #   for that class.
        if self._yhat_is_multivalued:
            pred_df = pd.DataFrame(yhat).transpose()
            assert self._columns is not None
            pred_df.columns = pd.Index(self._columns)
        else:
            target_col_name = dataset.metadata.roles[RoleName.TARGET][0].name
            if self._yhat_is_proba:
                retval.probabilities = TableFactory(pd.DataFrame(yhat))  # type: ignore[abstract] # pylint: disable=abstract-class-instantiated

                pred_df = pd.DataFrame({
                    target_col_name: np.argmax(yhat, axis=1)
                })
            else:
                pred_df = pd.DataFrame({
                    target_col_name: yhat
                })
        retval.predictions_table = TableFactory(pred_df)
        return retval

    @property
    def coef(self) -> np.ndarray:
        '''Weights for the model.'''
        assert self._predict_state is not None
        assert isinstance(self._predict_state, LinearNeighborState)
        return self._predict_state.v[:-1].copy()

    @property
    def intercept(self) -> np.float64:
        '''Intercept for the model.'''
        assert self._predict_state is not None
        assert isinstance(self._predict_state, LinearNeighborState)
        return self._predict_state.v[-1]

    @property
    def params(self) -> np.ndarray:
        '''All the params for the model.'''
        assert self._predict_state is not None
        assert isinstance(self._predict_state, LinearNeighborState)
        return self._predict_state.v
