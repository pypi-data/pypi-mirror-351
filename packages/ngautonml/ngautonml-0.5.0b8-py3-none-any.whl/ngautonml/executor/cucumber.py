'''Handles for trained models.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pickle

from typing import Any, Dict, Optional

from ..algorithms.impl.algorithm import Algorithm
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..algorithms.impl.fittable_algorithm_instance import FittableAlgorithmInstance
from ..generator.designator import Designator, StepDesignator


class CucumberError(Exception):
    '''Base class for all errors thrown related to Cucumbers'''


class DeserializationError(CucumberError):
    '''Ran into issues while deserializing.'''


class Cucumber():
    '''Model-specific representation of a trained model.'''
    _serialized_model: Optional[bytes] = None
    _filename: StepDesignator
    _pipeline_designator: Designator
    _hyperparams: Dict[str, Any]
    _catalog_name: str

    @classmethod
    def deserialize(cls, pickled_cucumber: bytes) -> 'Cucumber':
        '''Convert a pickled Cucumber back into a Cucumber.'''
        return pickle.loads(pickled_cucumber)

    def __init__(self,
                 impl: AlgorithmInstance,
                 filename: StepDesignator,
                 pipeline_designator: Designator,
                 hyperparams: Dict[str, Any]):
        self._catalog_name = impl.catalog_name
        if isinstance(impl, FittableAlgorithmInstance):
            self._serialized_model = impl.serialize()
        self._filename = filename
        self._pipeline_designator = pipeline_designator
        self._hyperparams = hyperparams

    def serialize(self) -> bytes:
        '''Make an on-disk representation of the Cucumber.'''
        # TODO(Merritt/Piggy): Find more stable pickling protocol
        return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)

    def deserialize_model(self, alg: Algorithm) -> AlgorithmInstance:
        '''Make a new instance of the algorithm passed in.

        Deserialize the saved trained model, and apply the saved hyperparams, if any.
        '''
        if alg.name != self._catalog_name:
            raise DeserializationError(
                f'Catalog name of Algorithm used for deserialization ({alg.name}) '
                f'and saved catalog name in cucumber ({self._catalog_name}) '
                'do not match.')
        hyperparams = self._hyperparams
        retval = alg.instantiate(**hyperparams)
        if isinstance(retval, FittableAlgorithmInstance):
            assert self._serialized_model is not None, (
                'BUG: cucumber asked to deserialize fittable model'
                ' but has no bytes to deserialize.')
            retval = retval.deserialize(serialized_model=self._serialized_model)
        assert isinstance(retval, AlgorithmInstance), (
            f'BUG: {alg.name}.instantiate() returned a  {type(retval)}, not an AlgorithmInstance '
            f'got: {retval}')
        return retval

    @property
    def serialized_model(self) -> Optional[bytes]:
        '''Typically a pickled representation of the trained model.'''
        return self._serialized_model

    @property
    def filename(self) -> StepDesignator:
        '''Returns the filename property.'''
        return self._filename

    @property
    def catalog_name(self) -> str:
        '''Returns the catalog name of the algorithm associated with this cucumber.'''
        return self._catalog_name

    @property
    def pipeline_designator(self) -> Designator:
        '''Returns the pipeline designator'''
        return self._pipeline_designator

    @property
    def hyperparams(self) -> Dict[str, Any]:
        '''Hyperparameter state for this cucumber.'''
        if self._hyperparams is None:
            return {}
        return self._hyperparams


class JarOfCucumbers(Dict[StepDesignator, Cucumber]):
    '''Trained models indexed by the designators for their steps.'''

    def trained_model(self, step_designator: StepDesignator) -> Cucumber:
        '''The trained model for the step designator.'''
        return self[step_designator]

    def set(self, designator: StepDesignator, trained_model: Cucumber) -> None:
        '''Saves the trained model into the training dictionary.'''
        self[designator] = trained_model
