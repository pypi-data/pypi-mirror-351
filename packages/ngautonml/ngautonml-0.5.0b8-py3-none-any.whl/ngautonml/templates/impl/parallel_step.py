'''A step consisting of parallel pipelines.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Optional

from ...algorithms.impl.algorithm import Algorithm, AlgorithmCatalog
from ...generator.designator import Designator
from .pipeline_step import PipelineStep, GeneratorInterface


class Error(Exception):
    '''Base error for ParallelStep'''


class GeneratorError(Error):
    '''Something has gone wrong during generate()'''


class ParallelStep(PipelineStep):
    '''A collection of parallel pipelines

    The output of each pipeline will be in a Dataset
    object keyed by the parameters given in the constructor.
    '''
    # This is really Dict[str, PipelineTemplate], but that's a
    # circular reference
    _subpipelines: Dict[str, Any]

    def __init__(self,
                 model: Optional[Algorithm] = None,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 generator: Optional[GeneratorInterface] = None,
                 **pipelines):
        super().__init__(model=model, algorithm_catalog=algorithm_catalog, generator=generator)
        self._subpipelines = pipelines

    @property
    def subpipeline_keys(self) -> List[str]:
        '''Get the keys for all the pipelines.'''
        return list(self._subpipelines.keys())

    @property
    def subpipelines(self) -> Dict[str, Any]:
        '''Get all the subpipelines.

        Really returns a Dict[str, PipelineTemplate], but that's a
            circular reference.
        '''
        return self._subpipelines

    def subpipeline(self, key: str) -> Any:
        '''Look up an individual pipeline by the key given in the constructor.

        Args:
          key: the Dataset key that will be used to hold the results of the given
          pipeline.

        Returns:
          The PipelineTemplate keyed by key.
        '''
        return self._subpipelines[key]

    def lift(self) -> 'PipelineStep':
        '''View a ParallelStep as just a PipelineStep.'''
        return self

    def generate(self,
                 future_steps: List['PipelineStep']
                 ) -> Dict[Designator, List['PipelineStep']]:
        '''Generate pipeline sketches (lists of bound steps) for this step and all subsequent steps.

        Subsequent query steps may expand into multiple 'pipeline sketches'. We do not currently
        support query steps within parallel pipelines.

        ParallelStep version.

        Our designator component looks like

            my_name(p1=a_step:another_step,p2=different_step)

        where p1 and p2 are the keys to the parallel constructor in asciibetical order.
        '''
        assert self._generator is not None, (
            'BUG: PipelineStep built without a generator, '
            f'name: {self.pipeline_designator_component}')
        new_subpipelines: Dict[str, Dict[Designator, Any]] = {
            key: self._generator.generate(pipeline)
            for key, pipeline in self._subpipelines.items()
        }

        # Calculating an n-way cross product is hard, so for
        # the moment, we do not try.
        # Real type is Dict[str, BoundPipeline].
        bound_subpipelines: Dict[str, Any] = {}
        long_designators: List[Designator] = []
        for key, candidate_pipelines in new_subpipelines.items():
            # If there is more than 1 candidate_pipeline, there must
            # have been a query in the subpipeline template, which is currently
            # unsupported.
            if len(candidate_pipelines) != 1:
                raise GeneratorError(
                    f'{key}: Subpipelines that multiply are not currently supported.'
                )
            # Extract the unique subpipeline.
            bound_subpipelines[key] = list(candidate_pipelines.values())[0]
            subkey = list(candidate_pipelines.keys())[0]
            long_designators.append(Designator(f'{key}={subkey}'))

        new_step = self.__class__(
            model=None,
            algorithm_catalog=self._algorithm_catalog,
            generator=self._generator,
            **bound_subpipelines).lift()

        if len(future_steps) == 0:
            return {Designator('_'): [new_step]}
        step0 = future_steps[0]
        sketches = step0.generate(future_steps[1:])
        return {
            Designator(f'{key}'): [new_step] + rest[:]
            for key, rest in sketches.items()
        }
