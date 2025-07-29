'''Base class for classes that load pipelines.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Any, Dict, Optional

from ngautonml.algorithms.impl.algorithm import AlgorithmCatalog
from ngautonml.templates.impl.template import TemplateCatalog

from ...generator.bound_pipeline import BoundPipeline


class Error(BaseException):
    '''base class for all errors thrown by this module'''


class MissingArgumentsError(Error):
    '''The pipeline loader did not encounter a required argument.'''


class UnknownArgumentsError(Error):
    '''The pipeline loader encounter unknown arguments to load()'''


class PipelineLoader(metaclass=abc.ABCMeta):
    '''Base class for classes that load pipelines.

    '''
    name: str
    tags: Dict[str, Any]

    _algorithm_catalog: Optional[AlgorithmCatalog]
    _template_catalog: Optional[TemplateCatalog]

    def __init__(self,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 template_catalog: Optional[TemplateCatalog] = None,
                 **unused_kwargs):
        self._algorithm_catalog = algorithm_catalog
        self._template_catalog = template_catalog
        super().__init__()

    def load(self, *args, **kwargs) -> BoundPipeline:
        '''Load the pipeline.'''
        # This exists so we have a place to hang logging or other
        # monitoring.
        return self._load(*args, **kwargs)

    @abc.abstractmethod
    def _load(self, *args, **kwargs) -> BoundPipeline:
        '''Load the pipeline.'''


class PipelineLoaderStub(PipelineLoader):
    '''stub'''
    name = 'stub_pipeline_loader'
    tags: Dict[str, Any] = {}

    def _load(self, *args, **unused_kwargs) -> BoundPipeline:
        return BoundPipeline(name=args[0])
