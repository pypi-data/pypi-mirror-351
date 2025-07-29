'''This is the executable pipeline for the "simple" executor.'''
from typing import Iterable, List, Optional

from ...algorithms.impl.algorithm_instance import AlgorithmInstance
from ...algorithms.impl.fittable_algorithm_instance import UntrainedError
from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import Designator
from ...instantiator.executable_pipeline import (ExecutablePipeline,
                                                 PipelineResult,
                                                 FitError)
from ...templates.impl.parallel_step import ParallelStep
from ...wrangler.dataset import Dataset, DatasetKeys
from ..cucumber import JarOfCucumbers
from ..executor_kind import ExecutorKind
from .simple_executable_step import SimpleExecutableStep
from .simple_parallel_executable_step import SimpleParallelExecutableStep

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


class SimpleExecutablePipeline(ExecutablePipeline):
    '''A pipeline for the 'simple' executor.'''
    _kind = ExecutorKind('simple')
    _steps: List[SimpleExecutableStep]

    def __init__(self,
                 pipeline: BoundPipeline):
        trained = False
        self._pipeline = pipeline
        self._steps = []
        for step in pipeline.steps:
            if isinstance(step, ParallelStep):
                executable_step: SimpleExecutableStep = (
                    SimpleParallelExecutableStep(step, SimpleExecutablePipeline))
            else:
                executable_step = SimpleExecutableStep(step)
                if executable_step.trained:
                    trained = True
            self._steps.append(executable_step)
        if trained:
            # Mainly, this catches the subpipelines of parallel steps
            # which are not otherwise marked as trained.
            self.set_trained()

    def set_trained(self):
        super().set_trained()
        for step in self._steps:
            step.set_trained()

    @property
    def locked(self) -> bool:
        '''Does this pipeline contain a model that is currently locked?'''
        return any(step.locked for step in self._steps)

    def converged(self) -> bool:
        '''Is every distributed model in this pipeline converged?

        Always returns True for pipelines with no distributed models.
        '''
        return all(step.converged() for step in self._steps)

    def set_fit_error(self, err: FitError) -> None:
        '''Set this pipeline as throwing an error at fit time'''
        self._fit_error = err

    def fit(self, dataset: Optional[Dataset]) -> JarOfCucumbers:
        '''Fit models to dataset.

        Args:
            dataset: The training dataset.

        Returns:
            A JarOfCucumbers
            (mapping from step designators to cucumbers for each step).
        '''
        # Pipelines set themselves as trained first, so that they are
        #   marked trained even if they throw an exception along the way
        self._trained = True

        # If there is a fit error recorded, remove it.
        self._fit_error = None

        # If dataset is None, just call fit(None) on all the steps.
        # This allows distributed pipelines to fit themselves with
        # neighbor data.
        result = None
        inp = dataset
        for step in self._steps:
            step.fit(dataset=inp)
            if inp is not None:
                result = step.predict(dataset=inp)
            inp = result
        if inp is not None:
            return self.cucumberize_all()
        return JarOfCucumbers()

    def predict(self, dataset: Optional[Dataset]) -> PipelineResult:
        '''Run prediction for a complete pipeline.'''
        if not self._trained:
            raise UntrainedError(f'pipeline "{self.name}" needs to be fit before it can predict')
        if dataset is None:
            inp = None
        else:
            inp = dataset.output()
        if self._fit_error is not None:
            if inp is None:
                inp = Dataset(metadata=None, **{DatasetKeys.ERROR.value: self._fit_error})
            else:
                inp[DatasetKeys.ERROR.value] = self._fit_error
        else:
            if inp is not None and dataset is not None:
                inp.update(dataset)
            else:
                inp = dataset
            for step in self._steps:
                result = step.predict(dataset=inp)
                inp = result
        return PipelineResult(executable_pipeline=self, prediction=inp)

    def cucumberize_all(self, parent_designator: Optional[Designator] = None) -> JarOfCucumbers:
        '''Cucumberize all steps that hold algorithms, and return the result.

        This has the same output as fit() but requires the pipeline to be fit already.

        The parent_designator argument is not None iff this pipeline is a subpipeline inside
            a parallel step.  It is there so that steps in subpipelines can be saved with
            their parent's designator.
        '''
        if not self._trained:
            raise UntrainedError(
                f'pipeline "{self.name}" needs to be fit before it can cucumberize_all')

        models = JarOfCucumbers()
        for step in self._steps:
            models.update(
                step.cucumberize_all(
                    parent_designator or self.designator))
        return models

    def start(self) -> None:
        '''Start the pipeline.'''
        for step in self._steps:
            step.start()

    def stop(self) -> None:
        '''Stop the pipeline.'''
        for step in self._steps:
            step.stop()

    @property
    def all_instances(self) -> Iterable[AlgorithmInstance]:
        '''Iterate through all algorithm instances.'''
        for step in self._steps:
            yield from step.all_instances
