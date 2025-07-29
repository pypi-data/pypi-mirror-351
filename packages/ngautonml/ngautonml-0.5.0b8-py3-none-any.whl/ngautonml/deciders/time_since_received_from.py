'''Decider that measures elapsed time since last send to a specific neighbor.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import time
from typing import Mapping

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig
from ..neighbor_manager.node_id import NodeID  # type: ignore[import-untyped]

from .impl.decider import Decider
from .impl.decider_catalog import DeciderCatalog

from .time_since_sent import TimeSinceSentDeciderConfig


class TimeSinceReceivedFromDeciderConfig(TimeSinceSentDeciderConfig):
    '''Configuration for TimeSinceReceivedFromDecider.'''


class TimeSinceReceivedFromDecider(Decider):
    '''Decider that triggers a refractory time past the last sent message.'''
    name = 'time_since_received_from'
    tags = {}
    _config: TimeSinceReceivedFromDeciderConfig

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        assert my_meta.current_state is not None
        interval = time.monotonic() - neighbors[neighbor_id].last_state_update_time
        return interval > self._config.time_seconds


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(TimeSinceReceivedFromDecider)
    DecidersConfig.register(name=TimeSinceReceivedFromDecider.name,
                            config_type=TimeSinceReceivedFromDeciderConfig)
