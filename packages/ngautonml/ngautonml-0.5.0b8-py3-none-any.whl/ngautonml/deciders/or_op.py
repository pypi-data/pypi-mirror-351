'''Decider that requires one of its subdeciders to decide True.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Mapping
from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig
from ..neighbor_manager.node_id import NodeID

from .impl.decider_catalog import DeciderCatalog

from .boolean import BooleanDeciderConfig, BooleanDecider


class OrDeciderConfig(BooleanDeciderConfig):
    '''Configuration for OrDecider.'''

    def __str__(self) -> str:
        return f'or({[str(c) for c in self._clause]}'


class OrDecider(BooleanDecider):
    '''Decider that decides True if any of its subdeciders decides True.'''
    name = 'or'
    tags = {}
    _config: OrDeciderConfig

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        return any(self._all_decisions(
            my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors))


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(OrDecider)
    DecidersConfig.register(name=OrDecider.name, config_type=OrDeciderConfig)
