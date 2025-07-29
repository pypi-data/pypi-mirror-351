'''A bound pipeline is a DAG of models with bound hyperparameters'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, List, Optional

from ..generator.designator import Designator
from ..searcher.frozen_overrides import FrozenOverrides
from ..templates.impl.parallel_step import ParallelStep
from ..templates.impl.pipeline_step import PipelineStep
from ..templates.impl.pipeline_template import PipelineTemplate


class Error(Exception):
    '''Base error class for BoundPipeline.'''


class StepError(Error):
    '''A step violates BoundPipeline constraints.'''


class ValidationError(Error):
    '''The BoundPipeline object violates constraints.'''


class BoundPipeline(PipelineTemplate):
    '''A ``BoundPipeline`` is a ``PipelineTemplate`` with no query steps.

    ``BoundPipeline``\\ s are outputs of the ``Generator``,
    inputs and outputs of the ``Searcher``,
    and inputs to the ``Instantiator``.
    '''
    _frozen_overrides: Optional[FrozenOverrides] = None

    def __init__(self,
                 name: Optional[str] = None,
                 **kwargs):
        assert name is not None, (
            'BoundPipeline constructor requires a name or designator')
        super().__init__(name=name, **kwargs)
        self.validate()

    @property
    def family_designator(self) -> Designator:
        '''The name this bound pipeline shares when we ignore overrides.'''
        components = [self.name]
        components.extend(
            step.pipeline_designator_component
            for step in self.steps
            if step.queried
        )
        return Designator('@'.join(components).lower())

    @property
    def designator(self) -> Designator:
        '''The unique designator for this bound pipeline'''
        components = [self.name]

        for step in self.steps:
            has_overrides = (self._frozen_overrides is not None
                             and step.pipeline_designator_component in self._frozen_overrides)
            if not has_overrides:
                if not step.queried:
                    # Case: no overrides, not queried.
                    continue
                # Case: no overrides, queried.
                components.append(step.pipeline_designator_component)
                continue
            # Case: has overrides, may or may not be queried.
            assert self._frozen_overrides is not None
            step_overrides = self._frozen_overrides[step.pipeline_designator_component]
            overrides_strs = sorted(
                [f'{k}={v}' for k, v in step_overrides.items()])
            components.append(
                f'{step.pipeline_designator_component}:{",".join(overrides_strs)}')

        return Designator('@'.join(components).lower())

    @property
    def _query_names(self) -> List[str]:
        '''A list of names of all steps that are from a query.

        We currently don't support query steps inside parallel steps.
        '''
        return [step.pipeline_designator_component for step in self._steps if step.queried]

    @classmethod
    def build(cls,
              steps: List[PipelineStep],
              template_name: str,
              frozen_overrides: Optional[FrozenOverrides] = None,
              **kwargs):
        '''Build a BoundPipeline with precalculated steps.'''
        retval = cls(name=template_name, **kwargs)
        retval._steps = steps
        retval._frozen_overrides = frozen_overrides
        return retval

    def new(self, name: str) -> 'BoundPipeline':
        '''Create a new descendant BoundPipeline

        This is for building parallel threads.
        '''
        child = BoundPipeline(name=f'{name}')
        return child

    def validate(self) -> None:
        '''Raise an exception if not everything in the pipeline is bound.'''
        errors: List[Error] = []
        for step in self._steps:
            if not step.has_model():
                if isinstance(step, ParallelStep):
                    for key in step.subpipeline_keys:
                        try:
                            step.subpipeline(key).validate()
                        except Error as err:
                            errors.append(err)
                    continue
                errors.append(StepError(f'step {step.pipeline_designator_component} lacks a model'))
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.designator}'


class BoundPipelineStub(BoundPipeline):
    '''this is a stub'''
    _name = 'stub_pipeline'

    def __init__(self, name: str, tags: Optional[Any] = None, **kwargs):
        tags = tags or {}
        super().__init__(name=name, tags=tags, **kwargs)
