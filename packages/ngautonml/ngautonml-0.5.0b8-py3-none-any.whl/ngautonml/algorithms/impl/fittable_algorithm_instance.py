'''Holds an instance of a fittable algorithm.'''
import abc
from copy import deepcopy
import pickle
from typing import Any, Optional
from typing_extensions import Protocol

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...wrangler.dataset import Dataset

from .algorithm_instance import AlgorithmInstance, Error


class UntrainedError(Error):
    '''Attempt to save the training of a model before it is trained.'''


class DeserializationError(Error):
    '''Attempt to deserialize a trained model failed'''


class FittableAlgorithmInstance(AlgorithmInstance, metaclass=abc.ABCMeta):
    '''Holds an instance of a fittable algorithm.'''
    _trained: bool = False

    @property
    def trained(self) -> bool:
        '''Is this algorithm trained?'''
        return self._trained

    def deserialize(self, serialized_model: bytes) -> 'FittableAlgorithmInstance':
        '''Restore a trained model.'''
        self._trained = True
        try:
            instance = pickle.loads(serialized_model)
        except pickle.UnpicklingError as err:
            raise DeserializationError(
                'Base AlgorithmInstance unexpectedly handed a serialized_model '
                'that is not a pickle. '
                'Is there a missing implementation of deserialize()?'
            ) from err
        if not isinstance(instance, FittableAlgorithmInstance):
            raise DeserializationError(
                f'Base AlgorithmInstance unexpectedly handed a {instance} '
                f'of type {type(instance)}, expected a subtype of AlgorithmInstance. '
                'Is there a missing implementation of deserialize()?')
        # The algorithm may contain catalogs which are not pickleable.
        instance._algorithm = self._algorithm   # pylint: disable=protected-access
        return instance

    def serialize(self) -> bytes:
        '''Return a serialized version of a trained model.

        By default, we save the whole AlgorithmInstance.'''
        if not self._trained:
            raise UntrainedError(f'attempt to serialize before fit for {self.catalog_name}')
        minime = deepcopy(self)
        # The algorithm may contain catalogs which are not pickleable.
        minime._algorithm = None  # pylint: disable=protected-access
        return pickle.dumps(minime)

    @abc.abstractmethod
    def fit(self, dataset: Optional[Dataset]) -> None:
        '''Fit a model based on train data.

        This should set self._trained to True
        '''

    @abc.abstractmethod
    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        '''Apply model to input dataset to create output.

        This may require that the model is fit (self.trained == True) before it is called.
        '''


class Constructor(Protocol):
    '''Match the signature of a generic model constructor.'''
    def __call__(self, **kwargs: Any) -> Any:
        ...


def not_implemented(**kwargs):
    '''A constructor must be specified in a subclass'''
    raise NotImplementedError('Implementation must specify a model _constructor')
