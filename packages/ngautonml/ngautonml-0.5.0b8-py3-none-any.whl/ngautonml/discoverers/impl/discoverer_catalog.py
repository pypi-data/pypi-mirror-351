'''Catalog for objects that control neighbor discovery in distributed algorithms.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Type, Union

from ...catalog.memory_catalog import MemoryCatalog

from .discoverer import Discoverer


class DiscovererCatalog(MemoryCatalog[Type[Discoverer]], metaclass=abc.ABCMeta):
    '''Base class for Discoverer catalogs'''

    def register(self, obj: Type[Discoverer], name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)


class DiscovererCatalogStub(DiscovererCatalog):
    '''stub'''
