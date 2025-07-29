'''A "simple" executable parallel step'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, Iterable, Optional

from typing_extensions import Protocol

from ...algorithms.impl.algorithm_instance import AlgorithmInstance
from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import Designator
from ...templates.impl.parallel_step import ParallelStep
from ...templates.impl.pipeline_step import PipelineStep
from ...wrangler.dataset import Dataset
from ..cucumber import JarOfCucumbers
from .simple_executable_step import InstantiationError, SimpleExecutableStep

# pylint: disable=missing-function-docstring


class PipelineConstructor(Protocol):
    '''Match the signature of SimpleExecutablePipeline().'''
    # Should be __call__(self, pipeline: BoundPipeline) -> SimpleExecutablePipeline
    # but that would cause circular imports.
    def __call__(self, pipeline: BoundPipeline) -> Any:
        ...


class SimpleParallelExecutableStep(SimpleExecutableStep):
    '''Executable step for a bound parallel step

    We want to build and store SimpleExecutablePipelines, but that would lead
    to a circulate import. We use an Any placehold for SimpleExecutablePipeline
    in the _pipelines property below. We still need to build
    SimpleExecutablePipelines, so we pass the constructor to __init__ where
    we need to use it. The constructor takes a named parameter called pipeline.
    See PipelineConstructor for the standard pythonic solution to defining a
    callable with named arguments.
    '''
    # This is really a Dict[str, SimpleExecutablePipeline], but that would lead
    # to a circular import.
    _pipelines: Dict[str, Any]
    _trained: bool = False

    def __init__(self, step: PipelineStep, pipeline_constructor: PipelineConstructor):
        '''Build a SimpleParallelStep.

        Args:
          step: PipelineStep,
          pipeline_constructor needs to be SimpleExecutablePipeline.
        '''
        super().__init__(bound_step=step, model=None)
        if not isinstance(step, ParallelStep):
            raise InstantiationError(
                'SimpleParallelStep requires a ParallelStep for name '
                f'{self.pipeline_designator_component}')
        self._bound_step = step
        self._pipelines = {}
        for key in step.subpipeline_keys:
            self._pipelines[key] = pipeline_constructor(pipeline=step.subpipeline(key))

    def _init_model(self, **unused_kwargs):
        '''PipelineStep has no model.'''
        self._model = None
        self._model_instance = None

    def set_trained(self):
        super().set_trained()
        for pipeline in self._pipelines.values():
            pipeline.set_trained()

    def fit(self, *args, **kwargs):
        '''Call fit for all the pipelines.'''
        for pipe in self._pipelines.values():
            pipe.fit(*args, **kwargs)
        self._trained = True

    def predict(self, *args, dataset: Optional[Dataset] = None, **kwargs) -> Dataset:
        '''Apply all models to the dataset.

        Returns:
          Dataset where the keys are the names given to the constructor
          and the values are the Datasets from the respective pipelines.
          You generally want to use Connect to pull out the pieces needed
          by the next step.
        '''
        assert dataset is not None
        result = dataset.output()
        for k, pipe in self._pipelines.items():
            executor_result = pipe.predict(*args, dataset=dataset, **kwargs)
            result[k] = executor_result.prediction
        return result

    def cucumberize_all(self, pipeline_designator: Designator) -> JarOfCucumbers:
        models = JarOfCucumbers()
        for pipe in self._pipelines.values():
            # pipe is a SimpleExecutablePipeline
            models.update(pipe.cucumberize_all(parent_designator=pipeline_designator))
        return models

    @property
    def trained(self) -> bool:
        return self._trained

    @property
    def all_instances(self) -> Iterable[AlgorithmInstance]:
        '''Iterate through all algorithm instances.'''
        for pipe in self._pipelines.values():
            for instance in pipe.all_instances:
                assert isinstance(instance, AlgorithmInstance)
                yield instance
