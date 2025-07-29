'''An algorithm for computing moments.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional

import numpy as np
import pandas as pd

from ..algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..algorithms.impl.fittable_algorithm_instance import FittableAlgorithmInstance
from ..catalog.catalog import upcast
from ..wrangler.dataset import Dataset


class MomentsInstance(FittableAlgorithmInstance):
    '''A model that computes the moments.'''

    _mu: np.ndarray
    _cov: np.ndarray

    def fit(self, dataset: Optional[Dataset]):
        '''Compute moments

        We call fit with the domain adaptation source dataset, and
        then predict with the domain adaptation target dataset.
        '''
        if dataset is None:
            return
        self._trained = True

        numeric = dataset.dataframe_table.as_(pd.DataFrame).select_dtypes(include=['number'])

        self._mu = np.mean(numeric, axis=0)
        self._cov = np.cov(numeric.T)

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        ''''We produce a dataset that only has a 'hyperparameters' field
        that contains the mean and covariance of the input dataset.
        '''
        return Dataset(hyperparams={
            'mean': self._mu,
            'covariance': self._cov,
        })


class Moments(Algorithm):
    '''A model that calculates the moments of a dataset.'''
    _name = 'moments'
    _instance_constructor = MomentsInstance
    _tags = {
        'source': ['auton_lab'],
        'preprocessor': ['true'],
    }


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = Moments(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
