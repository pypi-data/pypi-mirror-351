'''Catalog for objects communicate with neighbors in distributed algorithms.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Type, Union

from ...catalog.memory_catalog import MemoryCatalog

from .decider import Decider


class DeciderCatalog(MemoryCatalog[Type[Decider]], metaclass=abc.ABCMeta):
    '''Base class for Decider catalogs'''

    def register(self, obj: Type[Decider], name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)


class DeciderCatalogStub(DeciderCatalog):
    '''stub'''
