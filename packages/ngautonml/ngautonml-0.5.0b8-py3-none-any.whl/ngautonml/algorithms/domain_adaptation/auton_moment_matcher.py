'''Simple Domain Confusion'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from ...catalog.catalog import upcast
from ...tables.impl.table import TableFactory
from ...wrangler.dataset import Dataset, DatasetKeys
from ...wrangler.logger import Logger

from ..impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..impl.fittable_algorithm_instance import FittableAlgorithmInstance

logger = Logger(__file__).logger()


class AutonMomentMatcherInstance(FittableAlgorithmInstance):
    '''Instance of Simple Domain Confusion.

    This is a Domain Adaptation algorithm, that allows the use of a pretrained
    model adapted for a new datasaet.

    AutonSimpleDomainConfusion uses the mean and variance of a new dataset to
    adapt a model trained on a different dataset. The model is adapted by
    adjusting the the mean and variance of the new dataset to match the mean
    and variance of the original dataset.
    '''
    _A: np.ndarray
    _b: np.ndarray
    _hyperparam_overrides: Dict[str, Any]

    def __init__(self, parent: Algorithm, **hyperparams):
        self._hyperparam_overrides = {}

        mean = hyperparams.pop('mean', None)
        covariance = hyperparams.pop('covariance', None)
        if mean is not None:
            self._hyperparam_overrides['mean'] = mean
        if covariance is not None:
            self._hyperparam_overrides['covariance'] = covariance
        super().__init__(parent=parent, **hyperparams)

    def hyperparams(self, **hyperparams) -> Dict[str, Any]:
        '''Hyperparam override order:

        1. hyperparams from the Algorithm are overridden by
        2. hyperparams from __init__ are overridden by
        3. hyperparams from the dataset
        '''
        errors: List[str] = []
        overrides = self._hyperparam_overrides.copy()
        overrides.update(hyperparams)
        retval = self.algorithm.hyperparams(**overrides)
        if retval['mean'] is None:
            errors.append(
                f'mean is a required hyperparam for {self.algorithm.name}')
        if retval['covariance'] is None:
            errors.append(
                f'covariance is a required hyperparam for {self.algorithm.name}')
        if errors:
            raise ValueError('\n'.join(errors))
        return retval

    def fit(self, dataset: Optional[Dataset]) -> None:
        if dataset is None:
            return

        self._trained = True

        if DatasetKeys.HYPERPARAMS.value in dataset:
            hyperparams = self.hyperparams(**dataset[DatasetKeys.HYPERPARAMS.value])
        else:
            hyperparams = self.hyperparams()

        mu_source = hyperparams['mean']
        cov_source = hyperparams['covariance']

        numeric = dataset.dataframe_table.as_(pd.DataFrame).select_dtypes(include=['number'])

        mu_target = numeric.mean(axis=0)
        cov_target = np.cov(numeric.T)

        epsilon = 1e-9
        vals, vecs = np.linalg.eigh(cov_target)
        vals[vals < 0] = 0
        root_target = vecs @ np.diag(np.sqrt(vals))
        vals, vecs = np.linalg.eigh(cov_source)
        vals[vals < 0] = 0
        root_source = vecs @ np.diag(np.sqrt(vals))
        n, _ = root_target.T.shape
        # pylint: disable-next=invalid-name
        self._A = np.linalg.solve(root_target.T + epsilon * np.eye(n), root_source.T).T
        self._b = (mu_source - self._A @ mu_target).to_numpy()

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        old_df = dataset.dataframe_table.as_(pd.DataFrame)
        columns = old_df.columns
        numeric = old_df.select_dtypes(include=['number'])
        nonnumeric = old_df.select_dtypes(exclude=['number'])
        new_df = numeric @ self._A.T + self._b[np.newaxis, :]
        new_df = new_df.join(nonnumeric)
        new_df = new_df.rename(columns=dict(zip(new_df.columns, columns)))
        new_dataset = dataset.output()
        new_dataset.dataframe_table = TableFactory(new_df)
        return new_dataset


class AutonMomentMatcher(Algorithm):
    '''Class for Auton Lab's implementation of Simple Domain Confusion.'''
    _name = "auton_simple_domain_confusion"
    _tags = {
        'source': ['auton_lab'],
        'preprocessor': ['true'],
    }
    _instance_constructor = AutonMomentMatcherInstance
    _default_hyperparams = {
        'mean': None,
        'covariance': None,
    }

    def instantiate(self, **hyperparams) -> 'AutonMomentMatcherInstance':
        return super().instantiate(**hyperparams)


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = AutonMomentMatcher(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
