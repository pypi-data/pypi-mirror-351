'''Discoverer that uses static configuration.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import logging
from queue import Queue
from typing import Dict, List

import numpy as np

from ..communicators.impl.communicator import Communicator
from ..config_components.distributed_config import DistributedConfig
from ..neighbor_manager.event import NewNeighbor
from ..neighbor_manager.node_id import NodeID
from .impl.discoverer import Discoverer
from .impl.discoverer_catalog import DiscovererCatalog

from ..wrangler.logger import Logger

log = Logger(__file__, level=logging.DEBUG).logger()


class StaticDiscoverer(Discoverer):
    '''Discoverer that uses static configuration.'''
    name = 'static'
    tags: Dict[str, List[str]] = {}

    def __init__(self, config: DistributedConfig,
                 communicator: Communicator):
        super().__init__(config=config, communicator=communicator)
        neighbors = self._config.get_static_adjacency(my_id=communicator.my_id)
        assert neighbors is not None, (
            'BUG: Attempt to define StaticDiscoverer with no static config.')
        self._neighbors = neighbors
        known = self._communicator.known_neighbors
        log.debug('StaticDiscoverer: known_neighbors=%s, adding=%s', known, neighbors)
        known.update(neighbors)

    def start(self, queue: Queue):
        for node in self._neighbors:
            queue.put(NewNeighbor(neighbor=NodeID(node)))
        self._communicator.start(
            queue=queue
        )

    def laplacian(self) -> List[List[int]]:
        '''Convert the row adjacency config to a Laplacian matrix.

        # https://en.wikipedia.org/wiki/Laplacian_matrix#:~:text=Definitions%20for%20simple%20graphs,-%5Bedit%5D
        '''
        row_adjacency = self._config.get_adjacency()
        assert row_adjacency is not None, (
            'BUG: Attempt to get Laplacian with no adjacency config.')

        max_id = max(k for k in row_adjacency.keys())
        degree = np.zeros((max_id, max_id), dtype=int)
        adjacency = np.zeros((max_id, max_id), dtype=int)
        for i in range(max_id):
            i_node = NodeID(i + 1)
            if i_node not in row_adjacency.keys():
                continue
            degree[i][i] = len(row_adjacency[i_node])
            for j in row_adjacency[i_node]:
                adjacency[i][j - 1] = 1

        return (degree - adjacency).tolist()


def register(catalog: DiscovererCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(StaticDiscoverer)
