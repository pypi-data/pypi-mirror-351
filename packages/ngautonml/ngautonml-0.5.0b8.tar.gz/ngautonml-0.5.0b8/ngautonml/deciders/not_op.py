'''Decider that requires its subdecider to decide False.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from copy import deepcopy
from typing import Mapping

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig, DeciderConfig
from ..neighbor_manager.node_id import NodeID

from .impl.decider_catalog import DeciderCatalog

from .boolean import BooleanDeciderConfig, BooleanDecider


class NotDeciderConfig(BooleanDeciderConfig):
    '''Configuration for NotDecider.'''

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        clause = deepcopy(self._clause)
        clause.pop(DeciderConfig.Keys.ENABLED, None)
        if len(clause) != 1:
            raise ValueError('NotDeciderConfig takes only one subclause.')

    def __str__(self) -> str:
        return f'not({",".join([str(c) for c in self._clause])})'


class NotDecider(BooleanDecider):
    '''Decider that decides True if its subdecider decides False.'''
    name = 'not'
    tags = {}
    _config: NotDeciderConfig

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        return not all(self._all_decisions(
            my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors))


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(NotDecider)
    DecidersConfig.register(name=NotDecider.name, config_type=NotDeciderConfig)
