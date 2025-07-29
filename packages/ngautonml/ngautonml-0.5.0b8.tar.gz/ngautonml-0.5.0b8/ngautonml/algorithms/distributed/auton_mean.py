'''Distributed Mean'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# Linear and Logistic Regression have portions of identical code that should
# not be abstracted away.
# pylint: disable=duplicate-code,no-member

import logging
import pickle
from typing import Iterable, Optional, Tuple

import numpy as np

from ...algorithms.impl.distributed_algorithm_instance import NoDataError
from ...catalog.catalog import upcast
from ...problem_def.task import DataType
from ...wrangler.dataset import Dataset
from ...wrangler.logger import Logger

from ..impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..impl.linear_distributed_algorithm_instance import (
    LinearDistributedAlgorithmInstance, LinearNeighborState)


logger = Logger(__file__, level=logging.DEBUG).logger()


class AutonMeanNeighbor(LinearNeighborState['AutonMeanNeighbor']):
    '''A neighbor in the distributed mean model.

    The elements of v are the mean of each column in the data.
    '''

    def encode(self) -> bytes:
        '''Encode message for distributed neighbors.'''
        return pickle.dumps((self._v, self._columns))

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'AutonMeanNeighbor':
        '''Decode a message from a neighbor.'''
        v, columns = pickle.loads(serialized_model)
        assert isinstance(v, np.ndarray), (
            f'BUG: expected v to be an np.ndarray, instead found {v} of type {type(v)}'
        )
        columns = cls._cast_columns(columns)
        return cls(v=v, columns=columns)


class AutonMeanInstance(LinearDistributedAlgorithmInstance):
    '''A distributed model that calculates the mean of each column in the data

    As a distributed model, this instance can share information about its
    trained state with other instances and update its trained state using
    information shared by other instances.
    '''
    _neighbor_constructor = AutonMeanNeighbor

    # This is a type annotation for _my_state.
    _predict_state: Optional[AutonMeanNeighbor] = None

    @property  # type: ignore[override]
    def _my_state(self) -> Optional[AutonMeanNeighbor]:
        retval = LinearDistributedAlgorithmInstance._my_state.fget(self)  # type: ignore[attr-defined] # pylint: disable=assignment-from-no-return, line-too-long
        assert retval is None or isinstance(retval, AutonMeanNeighbor), (
            'BUG: expected _my_state to be None or an AutonMeanNeighbor.')
        return retval

    @_my_state.setter
    def _my_state(self, value: Optional[AutonMeanNeighbor]) -> None:
        assert value is None or isinstance(value, AutonMeanNeighbor), (
            'BUG: expected value to be None or an AutonMeanNeighbor.')
        LinearDistributedAlgorithmInstance._my_state.fset(self, value)  # type: ignore[attr-defined]

    @property
    def _yhat_is_proba(self) -> bool:
        return False

    @property
    def _yhat_is_multivalued(self) -> bool:
        """True if yhat returns a vector of results, 1 per column of x."""
        return True

    @property
    def _neighbor_models_iter(self) -> Iterable[AutonMeanNeighbor]:
        for v in super()._neighbor_models_iter:
            assert isinstance(v, AutonMeanNeighbor), (
                'BUG: expected neighbor_models to contain AutonMeanNeighbor, '
                f'instead found {v} of type {type(v)}'
            )
            yield v

    def _yhat(self, x: np.ndarray) -> np.ndarray:
        assert self._predict_state is not None, (
            'BUG: self._predict_state should not be None when _yhat is called.'
            ' This should have been set in _fit'
        )
        return self._predict_state.v

    def _decode(self, serialized_model: bytes) -> AutonMeanNeighbor:
        '''Decode a message from distributed neighbors.'''
        return AutonMeanNeighbor.decode(serialized_model)

    def _prepare_data(self, dataset: Optional[Dataset]) -> Tuple[np.ndarray, np.ndarray]:
        '''Extract covariates and target, accounting for the possibility that there's no data.'''
        if dataset is None:
            if list(self._neighbor_models_iter):
                d = max(len(m.v) for m in self._neighbor_models_iter)
                np_cov = np.zeros((0, d)).astype(float)
            else:
                # TODO(Piggy/Dan) Need to figure out how to deal with no neighbors and no data.
                raise NoDataError("No data and no neighbors.")
            np_tar = np.zeros(0)
        else:
            dataset = dataset.sorted_columns()
            if dataset.dataframe_table is not None:
                np_cov = dataset.dataframe_table.as_(np.ndarray).astype(float)
            else:
                # This is for the case of predict with an empty dataset.
                np_cov = np.zeros((0, 0)).astype(float)
            np_tar = np.array([0])  # type: ignore[assignment]

        return np_cov, np_tar

    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Fit a model based on train data.

        This sets self.trained to True.
        '''
        if dataset is None:
            if list(self._neighbor_models_iter):
                if self._columns is None:
                    # TODO(piggy/Dan): Consider the case of neighbors with different columns.
                    self._columns = next(iter(self._neighbor_models_iter)).columns
            else:
                return  # We have neither data nor neighbors: there is nothing to do.

        try:
            np_cov, _ = self._prepare_data(dataset)
        except NoDataError:
            return  # There is nothing to do.

        logger.debug('Fitting %s; dataset: %r, len(neighbor_models): %s',
                     type(self).__name__, dataset, len(list(self._neighbor_models_iter)))
        x = np_cov
        n, _ = x.shape

        # number of non-nan observations per column
        per_col_n = np.count_nonzero(~np.isnan(x), axis=0)

        omega = self._omega
        _lambda = self._lambda

        if self._my_state is None:
            # v is the mean of every column.
            self._my_state = AutonMeanNeighbor(v=np.nanmean(x, axis=0), columns=self._columns)
        elif self._my_state.columns is None:
            self._my_state.columns = self._columns

        assert isinstance(self._my_state, AutonMeanNeighbor), (
            'BUG: expected self._my_state to be a AutonMeanNeighbor, '
            f'instead found {self._my_state} of type {type(self._my_state)}'
        )
        k = len(self._neighbor_metadata)

        neighbor_vs = [np.array(m.v, dtype=float) for m in self._neighbor_models_iter]

        if n == 0:
            # If you have no data take the mean of your neighbors.
            # If there are also no neighbors do nothing.
            if k != 0:
                self._my_state.v = np.nanmean(neighbor_vs, axis=0)
        else:
            x_sum = np.nansum(x, axis=0)

            # nansum outputs 0.0 if a col is all nans, but we want nan.
            x_sum[per_col_n == 0] = np.nan

            # get v_old (v from last fit) if it exists or set it to 0
            v_old = self._my_state.v.copy()

            prev_self_coef = (1 - omega) / omega

            old_nan_indicator = np.array(~np.isnan(v_old), dtype=int)

            neighbor_non_nan_counts = (~np.isnan(np.array(neighbor_vs))).sum(axis=0)

            vs_to_sum = np.array(
                [x_sum, prev_self_coef * v_old] + [_lambda * nv for nv in neighbor_vs])

            # 1darray - for each column of vs_to_sum, True if all values are nan
            all_nan_cols = np.count_nonzero(~np.isnan(vs_to_sum), axis=0) == 0

            self._my_state.v = np.nansum(vs_to_sum, axis=0) / (
                per_col_n + (prev_self_coef * old_nan_indicator)
                + (_lambda * neighbor_non_nan_counts))

            # nansum outputs 0.0 if a col is all nans, but we want nan.
            self._my_state.v[all_nan_cols] = np.nan
        logger.debug('%s fit complete; v: %r', type(self).__name__, self._my_state.v)


class AutonMean(Algorithm):
    '''Class for Auton Lab's implementation of distributed mean.'''
    _name = "auton_mean"
    _tags = {
        'preprocessor': ['true'],
        'data_types': [DataType.TABULAR.name],
        'source': ['auton_lab'],
        'distributed': ['true']
    }
    _instance_constructor = AutonMeanInstance
    _default_hyperparams = {
        'L2': 0.0,  # Not used by mean, but needed for linear algorithms
        'Lambda': 1.0,
        'omega': 2.0 / 3.0,
        'tol': 0.000000001,
        'maxiter': None,
    }

    def instantiate(self, **hyperparams) -> 'AutonMeanInstance':
        return super().instantiate(**self.hyperparams(**hyperparams))


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = AutonMean(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
