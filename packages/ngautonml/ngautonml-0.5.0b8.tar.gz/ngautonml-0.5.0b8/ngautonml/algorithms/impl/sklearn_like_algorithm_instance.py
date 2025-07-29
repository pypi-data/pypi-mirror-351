'''An instance of a fittable algorithm that follows sklearn conventions.'''
import pickle
from typing import Any, Optional

import pandas as pd

from ...wrangler.dataset import Dataset, TableFactory
from .algorithm import Algorithm
from .algorithm_instance import DatasetError
from .fittable_algorithm_instance import FittableAlgorithmInstance, UntrainedError


class SklearnLikeAlgorithmInstance(FittableAlgorithmInstance):
    '''An instance of a fittable algorithm that follows sklearn conventions.'''
    _impl: Any
    _constructor: type

    def __init__(self, parent: Algorithm, *args, **kwargs):
        super().__init__(parent, *args)
        self._impl = self._constructor(**self.algorithm.hyperparams(**kwargs))

    def deserialize(self, serialized_model: bytes) -> 'SklearnLikeAlgorithmInstance':
        '''Restore the serialized version of a model.'''
        self._impl = pickle.loads(serialized_model)
        self._trained = True
        return self

    def serialize(self) -> bytes:
        '''Return a serialized version of a trained model.'''
        if not self._trained:
            raise UntrainedError(f'attempt to save training before fit for {self.algorithm.name}')

        return pickle.dumps(self._impl, pickle.HIGHEST_PROTOCOL)

    def fit(self, dataset: Optional[Dataset]) -> None:
        '''Fit a model based on input dataset.'''
        if dataset is None:
            raise DatasetError(f'attempt to fit with no data for {self.algorithm.name}')
        try:
            self._impl.fit(dataset.covariates_table.as_(pd.DataFrame),
                           dataset.target_table.as_(pd.Series))
        except KeyError as err:
            raise DatasetError(f'fit dataset malformed {dataset!r}') from err
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if not self._trained:
            raise UntrainedError(f'attempt to predict before fit for {self.algorithm.name}')
        if dataset is None:
            return None
        try:
            result = self._impl.predict(dataset.covariates_table.as_(pd.DataFrame))
        except KeyError as err:
            raise DatasetError(f'predict dataset malformed {dataset!r}') from err
        retval = dataset.output()
        retval.predictions_table = TableFactory(result)
        return retval
