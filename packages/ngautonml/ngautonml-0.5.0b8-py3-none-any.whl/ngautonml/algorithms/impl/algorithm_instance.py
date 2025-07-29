'''Holds an instance of a model.'''
import abc
from typing import Any, Dict, Optional
from typing_extensions import Protocol

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...wrangler.dataset import Dataset

from .algorithm import Algorithm


class Error(Exception):
    '''Base error class for AlgorithmInstance.'''


class DatasetError(Error):
    '''Something is malformed about the dataset.'''


class AlgorithmInstance(metaclass=abc.ABCMeta):
    '''Holds an instance of an algorithm as made by the instantiator.'''
    _algorithm: Optional[Algorithm]
    _hyperparameters: Dict[str, Any]

    def __init__(self, parent: Algorithm, **kwargs):
        self._algorithm = parent
        self._hyperparameters = kwargs

    @property
    def algorithm(self) -> Algorithm:
        '''self._algorithm asserted to non-optional'''
        assert self._algorithm is not None, (
            'BUG: we should never access AlgorithmInstance.algorithm if it is not set.'
        )
        return self._algorithm

    def hyperparams(self, **kwargs) -> Dict[str, Any]:
        '''Return hyperparameters for this instance.'''
        retval = self._hyperparameters.copy()
        retval.update(kwargs)
        if self._algorithm is None:
            return retval
        return self._algorithm.hyperparams(**retval)

    @abc.abstractmethod
    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        '''Apply model to input dataset to create output.

        This may require that the model is fit (self.trained == True) before it is called.
        '''

    @property
    def catalog_name(self) -> str:
        '''The catalog name of our algorithm.'''
        assert self._algorithm is not None
        return self._algorithm.name

    def start(self) -> None:
        '''Start any threads that the algorithm needs.

        This is a no-op if the algorithm does not have threads.
        '''

    def stop(self) -> None:
        '''Stop all the threads.

        This is a no-op if the algorithm does not have threads.
        '''

    @property
    def locked(self) -> bool:
        '''Is this instance currently thread-locked?

        This can only return True for subclasses that spawn their own threads.
        '''
        return False

    @property
    def converged(self) -> bool:
        '''If this is a distributed model, has it converged?

        Always returns True for non-distributed models.
        '''
        return True


class Constructor(Protocol):
    '''Match the signature of a generic model constructor.'''
    def __call__(self, **kwargs: Any) -> Any:
        ...


def not_implemented(**kwargs):
    '''A constructor must be specified in a subclass'''
    raise NotImplementedError('Implementation must specify a model _constructor')
