'''Decider for tests that always decides to send.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Mapping
from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..neighbor_manager.node_id import NodeID
from ..config_components.distributed_config import DecidersConfig, DeciderConfig

from .impl.decider import Decider
from .impl.decider_catalog import DeciderCatalog


class DeciderStubConfig(DeciderConfig):
    '''Configuration for DeciderStub.'''


class DeciderStub(Decider):
    '''Stub Decider.'''
    name = 'stub_decider'
    tags = {}

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        return True


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(DeciderStub)
    DecidersConfig.register(name=DeciderStub.name, config_type=DeciderStubConfig)
