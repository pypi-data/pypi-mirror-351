'''Executes executable pipelines and returns results'''
import abc
from typing import Dict, Optional, Union

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .cucumber import JarOfCucumbers
from .executor_kind import ExecutorKind
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import (ExecutablePipeline, PipelineResult,
                                                FitError)
from ..wrangler.dataset import Dataset


class TrainedPipelineCollection(Dict[Designator, Union[FitError, JarOfCucumbers]]):
    '''The trained models for each pipeline indexed by pipeline name.'''

    def models(self, name: Designator) -> Union[FitError, JarOfCucumbers]:
        '''The models for a pipeline with the given name.'''
        return self[name]

    def set(self, name: Designator, models: Union[FitError, JarOfCucumbers]) -> None:
        '''Save a trained model at a step name.'''
        self[name] = models


class Executor(metaclass=abc.ABCMeta):
    '''Base class for pipeline executors'''
    _kind: ExecutorKind

    @property
    def kind(self) -> ExecutorKind:
        '''Documents the kind of ExecutablePipeline we need.'''
        return self._kind

    @abc.abstractmethod
    def fit(self,
            dataset: Optional[Dataset],
            pipelines: Dict[Designator, ExecutablePipeline]
            ) -> TrainedPipelineCollection:
        '''Train a list of pipelines on a dataset.'''

    @abc.abstractmethod
    def predict(self,
                dataset: Dataset,
                pipelines: Dict[Designator, ExecutablePipeline]
                ) -> Dict[Designator, PipelineResult]:
        '''Use a list of pipelines to predict from a dataset.'''


class ExecutorStub(Executor):
    '''stub'''
    _kind = ExecutorKind('stub_executor_kind')

    def fit(self,
            dataset: Optional[Dataset],
            pipelines: Dict[Designator, ExecutablePipeline]
            ) -> TrainedPipelineCollection:
        '''Train a list of pipelines on a dataset.'''
        return TrainedPipelineCollection()

    def predict(self,
                dataset: Dataset,
                pipelines: Dict[Designator, ExecutablePipeline]
                ) -> Dict[Designator, PipelineResult]:
        '''Use a list of pipelines to predict from a dataset.'''
        return {d: PipelineResult(executable_pipeline=p, prediction=dataset)
                for d, p in pipelines.items()}
