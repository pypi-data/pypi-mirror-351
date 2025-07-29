'''Catalog for objects that load bound pipelines.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Union

from ...algorithms.impl.algorithm import AlgorithmCatalog
from ...catalog.memory_catalog import MemoryCatalog
from ...templates.impl.template import TemplateCatalog

from .pipeline_loader import PipelineLoader


class PipelineLoaderCatalog(MemoryCatalog[PipelineLoader], metaclass=abc.ABCMeta):
    '''Base class for PipelineLoader catalogs'''
    _algorithm_catalog: Optional[AlgorithmCatalog]
    _template_catalog: Optional[TemplateCatalog]

    def __init__(self,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 template_catalog: Optional[TemplateCatalog] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self._algorithm_catalog = algorithm_catalog
        self._template_catalog = template_catalog

    def register(self, obj: PipelineLoader, name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)


class PipelineLoaderCatalogStub(PipelineLoaderCatalog):
    '''stub for PipelineLoaderCatalog'''
