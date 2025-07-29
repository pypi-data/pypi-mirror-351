'''Combines pipeline templates with hyperparameter bindings to generate bound pipelines'''
import abc
from typing import Dict, List

from ..algorithms.impl.algorithm import AlgorithmCatalog
from ..algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ..problem_def.problem_def import ProblemDefinition
from ..templates.impl.pipeline_step import PipelineStep
from ..templates.impl.pipeline_template import PipelineTemplate
from .bound_pipeline import BoundPipeline, BoundPipelineStub
from .designator import Designator

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


class Generator(metaclass=abc.ABCMeta):
    '''Base class for pipeline generators'''

    def __init__(
        self,
        algorithm_catalog: AlgorithmCatalog,
        problem_definition: ProblemDefinition,
    ):
        self._algorithm_catalog = algorithm_catalog
        self._problem_definition = problem_definition

    @abc.abstractmethod
    def generate(self, pipeline: PipelineTemplate) -> Dict[Designator, BoundPipeline]:
        '''Generate bound pipelines for one template.'''
        raise NotImplementedError

    def generate_all(self, templates: Dict[str, PipelineTemplate]
                     ) -> Dict[Designator, BoundPipeline]:
        '''Generate bound pipelines for a set of templates.'''
        retval: Dict[Designator, BoundPipeline] = {}
        for pipeline_template in templates.values():
            retval.update(self.generate(pipeline=pipeline_template))
        return retval


class GeneratorStub(Generator):
    '''stub'''
    _name: str

    def __init__(self, **kwargs):
        name = kwargs.get('name', 'default_stub_name')
        del kwargs['name']
        for arg, cls in [
            ('algorithm_catalog', AlgorithmCatalogAuto),
        ]:
            kwargs[arg] = kwargs.get(arg, cls())
        super().__init__(**kwargs)
        self._name = name

    def generate(self, pipeline: PipelineTemplate) -> Dict[Designator, BoundPipeline]:  # pylint: disable=unused-argument
        return {Designator(pipeline.name): BoundPipelineStub(self._name)}


class GeneratorImpl(Generator):
    '''The default implementation of Generator.'''

    def generate(self, pipeline: PipelineTemplate) -> Dict[Designator, BoundPipeline]:
        step0 = pipeline.steps[0]
        future_steps: Dict[Designator, List[PipelineStep]] = step0.generate(pipeline.steps[1:])
        pipelines = [BoundPipeline.build(template_name=pipeline.name, steps=steps)
                     for steps in future_steps.values()]
        return {
            bound.designator: bound for bound in pipelines
        }
