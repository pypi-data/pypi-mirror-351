'''Catalog for aggregators

   These can be used to select pipelines based on multiple unreliable metrics.
'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Union

from ...catalog.memory_catalog import MemoryCatalog
from ...aggregators.impl.aggregator import Aggregator


class AggregatorCatalog(MemoryCatalog[Aggregator], metaclass=abc.ABCMeta):
    '''Base class for aggregator catalogs'''
    def register(self, obj: Aggregator, name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)


class AggregatorCatalogStub(AggregatorCatalog):
    '''stub'''
