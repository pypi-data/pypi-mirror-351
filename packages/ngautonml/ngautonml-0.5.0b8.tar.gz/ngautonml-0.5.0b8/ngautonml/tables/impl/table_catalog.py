'''Catalog for objects to hold taables.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Type, Union

from ...catalog.memory_catalog import MemoryCatalog

from .table import Table


class TableCatalog(MemoryCatalog[Type[Table]], metaclass=abc.ABCMeta):
    '''Base class for Table catalogs'''

    def register(self, obj: Type[Table], name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)


class TableCatalogStub(TableCatalog):
    '''stub'''
