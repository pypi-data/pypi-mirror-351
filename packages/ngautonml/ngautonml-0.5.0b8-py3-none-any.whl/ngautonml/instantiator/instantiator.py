'''Compiles bound pipelines into executable pipelines'''
# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from pathlib import Path
from typing import Dict, Optional

from ..algorithms.impl.algorithm import AlgorithmCatalog
from ..executor.cucumber import JarOfCucumbers
from ..executor.executor_kind import ExecutorKind
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator, StepDesignator
from ..wrangler.saver import Saver
from .executable_pipeline import ExecutablePipeline, ExecutablePipelineStub


class InstantiatorError(Exception):
    '''An error occurred in use of the instantiator'''


class Instantiator(metaclass=abc.ABCMeta):
    '''Base class for pipeline instantiator kinds'''
    _kind: Optional[ExecutorKind] = None
    _saver: Optional[Saver] = None
    _algorithm_catalog: Optional[AlgorithmCatalog] = None

    def __init__(self,
                 saver: Optional[Saver] = None,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None):
        self._saver = saver
        self._algorithm_catalog = algorithm_catalog

    @abc.abstractmethod
    def instantiate(self, pipeline: BoundPipeline) -> ExecutablePipeline:
        '''Instantiate a single bound pipeline into a single kind of executable pipeline.

        Optionally instantiate the pipeline with the given trained models.
        '''

    def instantiate_all(self,
                        pipelines: Dict[Designator, BoundPipeline]
                        ) -> Dict[Designator, ExecutablePipeline]:
        '''Instantiate a dict of bound pipelines into a dict of executable pipelines.'''
        retval: Dict[Designator, ExecutablePipeline] = {}

        for des, pipe in pipelines.items():
            retval[des] = self.instantiate(pipeline=pipe)

        return retval

    @abc.abstractmethod
    def save(self, pipeline: BoundPipeline, model_paths: Dict[StepDesignator, Path]) -> Path:
        '''Save a bound pipeline to disk using self._saver.

        We use model_paths to set the hyperparams, and to supply
        pretrained models if they are needed.

        Returns the path to that bound pipeline's saved file.
        '''


class InstantiatorStub(Instantiator):
    '''stub'''
    _kind = ExecutorKind('stub_executor_kind')
    _cucumbers: Optional[JarOfCucumbers]

    def __init__(self, cucumbers: Optional[JarOfCucumbers] = None, **kwargs):
        super().__init__(**kwargs)
        self._cucumbers = cucumbers

    def instantiate(self, pipeline: BoundPipeline) -> ExecutablePipeline:
        retval = ExecutablePipelineStub(
            kind=self._kind,
            pipeline=pipeline,
            cucumbers=self._cucumbers)
        return retval

    def save(self, pipeline: BoundPipeline, model_paths: Dict[StepDesignator, Path]) -> Path:
        return Path('stub')
