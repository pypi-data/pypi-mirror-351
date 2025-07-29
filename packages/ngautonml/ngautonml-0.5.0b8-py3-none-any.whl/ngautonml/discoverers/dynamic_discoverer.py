'''Discoverer that uses dynamic configuration.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from queue import Queue
from typing import Dict, List

from .impl.discoverer import Discoverer
from .impl.discoverer_catalog import DiscovererCatalog


class DynamicDiscoverer(Discoverer):
    '''Discoverer that dynamically discovers neighbors.'''
    name = 'dynamic'
    tags: Dict[str, List[str]] = {}

    def start(self, queue: Queue):
        self._communicator.start(
            queue=queue
        )

    def laplacian(self) -> List[List[int]]:
        raise NotImplementedError('DynamicDiscoverer does not support laplacian')


def register(catalog: DiscovererCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(DynamicDiscoverer)
