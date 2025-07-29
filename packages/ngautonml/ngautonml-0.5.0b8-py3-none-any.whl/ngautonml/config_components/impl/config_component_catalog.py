'''Catalog for metrics that can be used to evaulate pipelines'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Type, Union

from ...catalog.memory_catalog import MemoryCatalog
from .config_component import ConfigComponent


class ConfigComponentCatalog(MemoryCatalog[Type[ConfigComponent]], metaclass=abc.ABCMeta):
    '''Base class for config component catalogs.'''

    def register(self, obj: Type[ConfigComponent], name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)


class ConfigComponentCatalogStub(ConfigComponentCatalog):
    '''stub'''
