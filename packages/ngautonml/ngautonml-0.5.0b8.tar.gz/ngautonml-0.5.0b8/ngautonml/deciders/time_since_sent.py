'''Decider that measures elapsed time since last send to any neighbor.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
import time
from typing import Mapping

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig, DeciderConfig
from ..neighbor_manager.node_id import NodeID  # type: ignore[import-untyped]

from .impl.decider import Decider
from .impl.decider_catalog import DeciderCatalog


class TimeSinceSentDeciderConfig(DeciderConfig):
    '''Configuration for TimeSinceSentDecider.'''

    def __init__(self, name: str, clause: dict) -> None:
        super().__init__(name=name, clause=clause)

    def __str__(self) -> str:
        return f'time_seconds: {self.time_seconds}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeSinceSentDeciderConfig):
            return False
        return self.time_seconds == other.time_seconds

    class Defaults(Enum):
        '''Default values for the clause.'''
        TIME_SECONDS = 1.0

    class Keys(AEnum):
        '''Keys for the clause.'''
        ENABLED = 'enabled'
        TIME_SECONDS = 'time_seconds'

    @property
    def time_seconds(self) -> float:
        '''Get the refractory period.

        This is how long we wait before returning True.
        '''
        return self._get_with_default(
            self.Keys.TIME_SECONDS, dflt=self.Defaults.TIME_SECONDS.value)


class TimeSinceSentDecider(Decider):
    '''Decider that triggers a refractory time past the last sent message.'''
    name = 'time_since_sent'
    tags = {}
    _config: TimeSinceSentDeciderConfig

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        assert my_meta.current_state is not None
        interval = time.monotonic() - my_meta.last_state_sent_time
        return interval > self._config.time_seconds


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(TimeSinceSentDecider)
    DecidersConfig.register(name=TimeSinceSentDecider.name, config_type=TimeSinceSentDeciderConfig)
