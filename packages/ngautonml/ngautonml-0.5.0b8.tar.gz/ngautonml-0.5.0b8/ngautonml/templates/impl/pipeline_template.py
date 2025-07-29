'''The PipelineTemplate object.

This holds the steps in an AutonML pipeline template, and any
supporting metadata.
'''
from typing import Any, Dict, List, Optional, Union, Iterable

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...algorithms.impl.algorithm import Algorithm, AlgorithmCatalog, AlgorithmCatalogStub
from ...catalog.catalog_element_mixin import CatalogElementMixin
from ...generator.designator import Designator
from .parallel_step import ParallelStep
from .pipeline_step import PipelineStep, GeneratorInterface
from .query_step import QueryStep


class Error(Exception):
    '''Base exception for PipelineTemplate objects.'''


class UndefinedError(Error):
    '''An undefined variable was referenced.'''


class PipelineTemplate(CatalogElementMixin):
    '''A template for a group of pipelines.

    The :doc:`/_autosummary/ngautonml.generator.generator.Generator`
    converts a template into several
    :doc:`/_autosummary/ngautonml.generator.bound_pipeline.BoundPipeline`\\ s.

    The ``Generator`` creates a new ``BoundPipeline`` for each combination of
    algorithms returned by all the query steps in the template.

    The ``Searcher`` creates new ``BoundPipeline``s out of those created
    by the ``Generator``, using hyperparameter search.

    Finally, the ``Instantiator`` turns all of these ``BoundPipelines``
    into ``ExecutablePipelines`` to be run by the ``Executor``.

    :name: the unique primary key for this template in the template catalog.

    :tags: secondary keys for this template in the template catalog.
        If specified, they override all the tags in the declaration of the class.

    '''
    _name: str = 'unnamed'
    _steps: List[PipelineStep]
    _algorithm_catalog: AlgorithmCatalog
    _generator: Optional[GeneratorInterface]

    def __init__(self,    # pylint: disable=too-many-arguments
                 name: Optional[str] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 generator: Optional[GeneratorInterface] = None):
        super().__init__(name=name, tags=tags)
        self._steps = []
        self._algorithm_catalog = algorithm_catalog or AlgorithmCatalogStub()
        self._generator = generator

    @property
    def steps(self) -> List[PipelineStep]:
        '''Returns the steps of this pipeline.'''
        return self._steps[:]

    def step(self,
             model: Optional[Algorithm] = None,
             serialized_model: Optional[bytes] = None,
             **overrides) -> PipelineStep:
        '''Add a step to the end of the template.'''
        step = PipelineStep(
            model=model,
            serialized_model=serialized_model,
            algorithm_catalog=self._algorithm_catalog,
            generator=self._generator,
            **overrides)
        self._steps.append(step)
        return step

    def new(self, name: str) -> 'PipelineTemplate':
        '''Create a new descendant PipelineTemplate

        This is for building parallel threads.
        '''
        child = PipelineTemplate(name=f'{name}',
                                 algorithm_catalog=self._algorithm_catalog,
                                 generator=self._generator)
        return child

    def parallel(self, **pipelines: 'PipelineTemplate') -> PipelineStep:
        '''Add a parallel step, which contains 2 or more subpipelines.

        Parallel steps allow pipelines to do different things with different parts of the data.
        For example, running preprocessors on the covariates but not the target column.

        * ``**pipelines``: A dictionary of ``{output_key: pipeline}``.
          The ``output_key`` for a subpipeline is where the parallel step stores
          the results in the Dataset,
          and can be any string, naming the subpipeline.
          The pipelines should be generated from ``PipelineTemplate().new()``.

        **Returns**: The new parallel step.
        '''
        retval = ParallelStep(model=None,
                              algorithm_catalog=self._algorithm_catalog,
                              generator=self._generator,
                              **pipelines)
        self._steps.append(retval)
        return retval

    def query(self, **tags: Union[str, Iterable[str]]) -> PipelineStep:
        '''Creates a query pipeline step and adds it to the template.

        A query step queries the ``AlgorithmCatalog`` by tag,
        and returns a set of ``Algorithms``.
        The ``Generator`` creates a new ``BoundPipeline``
        for each element of the cartesian product of
        all the query steps in the template.

        * ``**tags``: looks like ``tag_type = tag_value`` or
          ``tag_type = (tag_value1, tag_value2)``

        Queries for algorithms that match at least one specified tag value
        for all specified tag types.
        '''
        retval = QueryStep(algorithm_catalog=self._algorithm_catalog, **tags)
        self._steps.append(retval)
        return retval

    def generate(self) -> Dict[Designator, Any]:
        '''Generate all the bound pipelines for this pipeline template.'''
        return {}
