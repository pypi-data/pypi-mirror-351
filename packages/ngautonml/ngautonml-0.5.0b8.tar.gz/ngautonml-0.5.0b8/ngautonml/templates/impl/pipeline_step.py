'''The PipelineStep object.

These are manipulable Steps in a PipelineTemplate.
'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import threading
from typing import Any, Dict, List, Optional

from typing_extensions import Protocol

from ...algorithms.impl.algorithm import (Algorithm, AlgorithmCatalog,
                                          AlgorithmCatalogStub)
from ...generator.designator import Designator, StepDesignator

# pylint: disable=protected-access


class GeneratorInterface(Protocol):
    '''Interface for a Generator

    We are avoiding circular imports.

    The type should be
      generate(self, pipeline: PipelineTemplate) -> Dict[Designator, BoundPipeline]
    '''
    def generate(self, pipeline: Any) -> Dict[Designator, Any]:
        '''Generates Dict[Designator, BoundPipeline] for a PipelineTemplate'''


class Error(Exception):
    '''Base error for PipelineStep'''


class AlreadyDefinedError(Error):
    '''Attempt to set a value that can only be set once.'''


class BadValueError(Error, ValueError):
    '''A parameter was passed that makes no sense.'''


# pylint: disable=too-many-instance-attributes
class PipelineStep:
    '''A single step in a pipeline template

    Default hyperparams from the model are overridden by the
    PipelineStep constructor (for use in templates). These in
    turn are overridden by values specified in the Problem Definition.

    If hyperparams are passed in using the 'overrides' argument, rather than kwargs,
        they will contribute to the filename of this step when it is saved.
    '''
    _model: Optional[Algorithm]
    _save_output: Optional[str]
    _hyperparams: Dict[str, Any]
    _overrides: Optional[Dict[str, Any]]
    _algorithm_catalog: AlgorithmCatalog
    _generator: Optional[GeneratorInterface]
    _queried: bool
    _name: Optional[str] = None
    _sn_lock = threading.Lock()
    _serial_number: int = 0
    _serialized_model: Optional[bytes] = None

    @classmethod
    def _assign_sn(cls):
        '''Assign a unique serial number to this step.

        This number is used to ensure each step has a unique filename.'''
        with cls._sn_lock:
            retval = cls._serial_number
            cls._serial_number += 1
        return retval

    @classmethod
    def reset_serial_number(cls):
        '''Set serial number back to 0 for testing.

        Do not use this outside of tests.
        '''
        with cls._sn_lock:
            cls._serial_number = 0

    def __init__(self,  # pylint: disable=duplicate-code, too-many-arguments
                 model: Optional[Algorithm] = None,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 generator: Optional[GeneratorInterface] = None,
                 name: Optional[str] = None,
                 serialized_model: Optional[bytes] = None,
                 overrides: Optional[Dict[str, Any]] = None,
                 **hyperparams):
        self._model = model
        self._overrides = overrides
        self._algorithm_catalog = algorithm_catalog or AlgorithmCatalogStub()
        self._generator = generator
        self._queried = False
        self._name = name or self._name
        self._serialized_model = serialized_model

        self._serial_number = self._assign_sn()

        assert isinstance(model, Algorithm) or model is None
        if model is not None:
            current_overrides = {}
            current_overrides.update(hyperparams)
            if overrides is not None:
                current_overrides.update(overrides)
            self._hyperparams = model.hyperparams(**current_overrides)
        elif len(hyperparams) != 0:
            raise BadValueError(f'hyperparameter overrides specified with no model: {hyperparams}')
        else:
            # Case: parallel or query step
            self._hyperparams = {}

    @property
    def locked(self) -> bool:
        '''Does this step have a model instance that is currently locked?

        For base PipelineStep, this always returns False as there is no model instance.
        '''
        return False

    def converged(self) -> bool:
        '''If this step has a distributed model, has it converged?

        Always returns True for steps with no models or a non-distributed model.
        '''
        return True

    def set_name(self, name: str) -> 'PipelineStep':
        '''Give this step a name.'''
        if self._name is not None:
            raise AlreadyDefinedError(
                f'can not set name to {name.lower()};'
                f' already set to {self._name}')
        self._name = name.lower()
        return self

    def mark_queried(self) -> 'PipelineStep':
        '''Mark this step as the result of a query step.'''
        self._queried = True
        return self

    @property
    def queried(self) -> bool:
        '''Was this step generated from a query step?'''
        return self._queried

    @property
    def pipeline_designator_component(self) -> str:
        '''Our pipeline_designator_component is generally the name of our model.'''
        if self._name is not None:
            return self._name
        if self._model is not None:
            return self._model.name
        return '_'

    @property
    def opt_name(self) -> Optional[str]:
        '''Give raw access to _name.'''
        return self._name

    @property
    def filename(self) -> Optional[StepDesignator]:
        '''Filename to use when saving this step as part of a trained pipeline.

        If this step does not have a name assigned by the generator or searcher,
            its model name and serial number are used.
        '''
        if self._model is None:
            # We don't save parallel steps or query steps
            return None

        overrides = {}
        if self._overrides is not None:
            overrides.update(self._overrides)
        bindings = sorted([
            f'{hyperparam}={str(value)}'
            for hyperparam, value in overrides.items()])

        suffix = f':{",".join(bindings)}' if len(bindings) > 0 else ''
        retval = f'@{self._model.name}_{self._serial_number}@{self._name or ""}{suffix}'

        return StepDesignator(retval.lower())

    @property
    def serial_number(self) -> int:
        '''Serial number used to ensure that this step's designator is unique'''
        return self._serial_number

    def has_model(self) -> bool:
        '''Does the step have an associated model?'''
        return self._model is not None

    @property
    def model_name(self) -> Optional[str]:
        '''If we have a model, what is its name?'''
        # TODO(Merritt): rename to algorithm_name
        if self._model is None:
            return None
        return self._model.name

    @property
    def model(self):
        '''Provide access to our associated model.'''
        assert self._model is not None, (
            f'BUG: attempt to get unbound model from step {self.pipeline_designator_component}'
        )
        return self._model

    @property
    def serialized_model(self) -> Optional[bytes]:
        '''Provide access to any serialized model state.

        This is used during instatiation to preload model state.
        '''
        return self._serialized_model

    @property
    def tags(self) -> Optional[Dict[str, List[str]]]:
        '''Return the tags from our model if we have one.'''
        if self._model is None:
            return None
        return self._model.tags

    def hyperparams(self, **overrides) -> Dict[str, Any]:
        '''Get the hyperparameters for this step.

        Arguments passed to this function override defaults for the template step.
        '''
        default_hyperparams = self._hyperparams.copy()
        default_hyperparams.update(**overrides)
        return default_hyperparams

    def generate(self,
                 future_steps: List['PipelineStep']
                 ) -> Dict[Designator, List['PipelineStep']]:
        '''Generate pipeline sketches (lists of bound steps) for this step and all subsequent steps.

        Each query step may expand into multiple 'pipeline sketches'
        '''
        if len(future_steps) == 0:
            return {Designator(): [self]}
        step0 = future_steps[0]
        sketches = step0.generate(future_steps[1:])
        return {
            Designator(key): [self] + rest[:]
            for key, rest in sketches.items()
        }

    def clone(self, **overrides) -> 'PipelineStep':
        '''Clone this step, providing hyperparameter overrides.

        'overrides' argument will contribute to step filename when it is saved.

        Pre-existing hyperparams on this step will be passed along to
        the child step but will not contribute to its filename.
        '''
        child_overrides = {}
        if self._overrides is not None:
            child_overrides.update(self._overrides)
        child_overrides.update(overrides)

        retval = self.__class__(
            name=self.opt_name,
            model=self._model,
            algorithm_catalog=self._algorithm_catalog,
            generator=self._generator,
            overrides=child_overrides,
            **self._hyperparams
        )
        if self.queried:
            retval = retval.mark_queried()
        return retval
