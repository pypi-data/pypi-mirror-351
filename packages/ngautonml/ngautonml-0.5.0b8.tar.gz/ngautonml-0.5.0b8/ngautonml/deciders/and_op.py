'''Decider that requires all of its subdeciders to decide True.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Mapping

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig
from ..neighbor_manager.node_id import NodeID

from .impl.decider_catalog import DeciderCatalog

from .boolean import BooleanDeciderConfig, BooleanDecider


class AndDeciderConfig(BooleanDeciderConfig):
    '''Configuration for AndDecider.'''

    def __str__(self) -> str:
        return f'and({",".join([str(c) for c in self._clause])})'


class AndDecider(BooleanDecider):
    '''Decider that decides True if all of its subdeciders decide True.'''
    name = 'and'
    tags = {}
    _config: AndDeciderConfig

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        return all(self._all_decisions(
            my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors))


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(AndDecider)
    DecidersConfig.register(name=AndDecider.name, config_type=AndDeciderConfig)
