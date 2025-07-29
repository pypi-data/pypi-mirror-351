'''Decider that uses the algorithm-specific distance metric to compare against our last state.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Mapping

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig
from ..neighbor_manager.node_id import NodeID

from .distance import DistanceDeciderConfig, DistanceDecider
from .impl.decider_catalog import DeciderCatalog


class SelfDistanceDeciderConfig(DistanceDeciderConfig):
    '''Configuration for SelfDistanceDecider.'''


class SelfDistanceDecider(DistanceDecider):
    '''Decider that uses the algorithm-specific distance metric against our last state.'''
    name = 'self_distance'
    tags = {}

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        if my_meta.current_state is None:
            return False
        if my_meta.last_state is None:
            return True
        threshold = self._threshold(my_meta)
        return (my_meta.current_state.distance(my_meta.last_state_sent)
                > threshold)  # type: ignore[union-attr]


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(SelfDistanceDecider)
    DecidersConfig.register(name=SelfDistanceDecider.name, config_type=SelfDistanceDeciderConfig)
