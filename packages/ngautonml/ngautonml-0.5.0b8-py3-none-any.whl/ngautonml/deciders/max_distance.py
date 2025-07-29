'''Decider that uses the algorithm-specific distance metric.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
import math
from typing import Mapping

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig, DeciderConfig
from ..neighbor_manager.node_id import NodeID  # type: ignore[import-untyped]

from .impl.decider import Decider
from .impl.decider_catalog import DeciderCatalog


class MaxDistanceDeciderConfig(DeciderConfig):
    '''Configuration for DistanceDecider.'''

    def __init__(self, name: str, clause: dict) -> None:
        super().__init__(name=name, clause=clause)

    def __str__(self) -> str:
        return f'num_neighbors: {self.num_neighbors}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MaxDistanceDeciderConfig):
            return False
        return self.num_neighbors == other.num_neighbors

    class Defaults(Enum):
        '''Default values for the clause.'''
        NUM_NEIGHBORS = 1

    class Keys(AEnum):
        '''Keys for the clause.'''
        ENABLED = 'enabled'
        NUM_NEIGHBORS = 'num_neighbors'

    @property
    def num_neighbors(self) -> int:
        '''Get the number of most distant neighbors we would send to.'''
        return self._get_with_default(
            self.Keys.NUM_NEIGHBORS, dflt=self.Defaults.NUM_NEIGHBORS.value)


class MaxDistanceDecider(Decider):
    '''Decider that uses the algorithm-specific distance metric.'''
    name = 'max_distance'
    tags = {}
    _config: MaxDistanceDeciderConfig

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        assert my_meta.current_state is not None
        distances = []
        for nid in neighbors:
            if neighbors[nid].current_state is None:
                # A neighbor with no state is infinitely far away.
                distances.append((nid, math.inf))
                continue
            distance = my_meta.current_state.distance(neighbors[nid].current_state)
            distances.append((nid, distance))

        distances.sort(key=lambda x: x[1], reverse=True)

        if not distances:
            return False

        max_distance = distances[0][1]

        possible_neighbors = [nid for nid, distance in distances if distance == max_distance]

        if len(possible_neighbors) < self._config.num_neighbors:
            possible_neighbors = [
                nid for nid, _ in distances[:self._config.num_neighbors]]

        return neighbor_id in possible_neighbors


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(MaxDistanceDecider)
    DecidersConfig.register(name=MaxDistanceDecider.name, config_type=MaxDistanceDeciderConfig)
