'''Decider that unconditionally returns True.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from copy import deepcopy
from typing import Mapping

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig, DeciderConfig
from ..neighbor_manager.node_id import NodeID

from .impl.decider import Decider
from .impl.decider_catalog import DeciderCatalog


class TrueDeciderConfig(DeciderConfig):
    '''Configuration for TrueDecider.'''

    def __init__(self, name: str, clause: dict) -> None:
        subclause = deepcopy(clause)
        subclause.pop(TrueDeciderConfig.Keys.ENABLED, None)
        if subclause:
            raise ValueError('TrueDeciderConfig takes only an enabled key.')
        super().__init__(name=name, clause=clause)

    def __str__(self) -> str:
        return f'true({",".join([str(c) for c in self._clause])})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrueDeciderConfig):
            return False
        return True

    class Keys(AEnum):
        '''Keys for the clause.'''
        ENABLED = 'enabled'


class TrueDecider(Decider):
    '''Decider that decides True unconditionally.'''
    name = 'true'
    tags = {}

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        return True


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(TrueDecider)
    DecidersConfig.register(name=TrueDecider.name, config_type=TrueDeciderConfig)
