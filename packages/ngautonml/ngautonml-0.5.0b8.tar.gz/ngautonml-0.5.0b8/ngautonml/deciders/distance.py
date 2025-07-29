'''Decider that uses the algorithm-specific distance metric.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
import math
import time
from typing import Mapping, Optional

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DecidersConfig, DeciderConfig
from ..neighbor_manager.node_id import NodeID  # type: ignore[import-untyped]

from .impl.decider import Decider
from .impl.decider_catalog import DeciderCatalog


class DistanceDeciderConfig(DeciderConfig):
    '''Configuration for DistanceDecider.'''

    def __init__(self, name: str, clause: dict) -> None:
        super().__init__(name=name, clause=clause)

    def __str__(self) -> str:
        return f'threshold: {self.threshold}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DistanceDeciderConfig):
            return False
        return self.threshold == other.threshold

    class Defaults(Enum):
        '''Default values for the clause.'''
        DEFAULT_THRESHOLD = 0.5
        GEOMETRIC_TERM = 1.0
        LINEAR_TERM = 0.0
        MIN = 0.0

    class Keys(AEnum):
        '''Keys for the clause.'''
        ENABLED = 'enabled'
        THRESHOLD = 'threshold'
        GEOMETRIC_TERM = 'geometric_term'
        LINEAR_TERM = 'linear_term'
        MIN = 'min'
        INTERVAL_SECONDS = 'interval_seconds'

    @property
    def threshold(self) -> float:
        '''Get the threshold.

        This is the initial value for the threshold.
        '''
        return self._get_with_default(
            self.Keys.THRESHOLD, dflt=self.Defaults.DEFAULT_THRESHOLD.value)

    @property
    def geometric_term(self) -> float:
        '''Get the geometric term.'''
        return self._get_with_default(
            self.Keys.GEOMETRIC_TERM, dflt=self.Defaults.GEOMETRIC_TERM.value)

    @property
    def linear_term(self) -> float:
        '''Get the linear term.'''
        return self._get_with_default(
            self.Keys.LINEAR_TERM, dflt=self.Defaults.LINEAR_TERM.value)

    @property
    def min(self) -> float:
        '''Get the minimum value.'''
        return self._get_with_default(
            self.Keys.MIN, dflt=self.Defaults.MIN.value)

    @property
    def interval_seconds(self) -> Optional[float]:
        '''Get the interval in seconds.

        If this is None (the default), every time the decider is called,
        the threshold will advance one cycle. This is cycle time.

        If this is not None, we advance by wall time.

        Thresholds are calculated one decide call before they are applied,
        so the initial threshold is always used at least once.
        '''
        return self._get_with_default(
            self.Keys.INTERVAL_SECONDS, dflt=None)


class DistanceDecider(Decider):
    '''Decider that uses the algorithm-specific distance metric.'''
    name = 'distance'
    tags = {}
    _config: DistanceDeciderConfig

    def _threshold(self, my_meta: NeighborMetadataInterface) -> float:
        '''Get the threshold, calculating the next threshold for later.'''
        if self.name not in my_meta.scratch:
            my_meta.scratch[self.name] = {
                'threshold': self._config.threshold,
                'start_time': time.monotonic(),
                'cycle': 1,
            }
        retval = my_meta.scratch[self.name]['threshold']

        assert self._config is not None

        initial_threshold = self._config.threshold
        geom_term = self._config.geometric_term
        linear_term = self._config.linear_term
        min_val = self._config.min
        interval_seconds = self._config.interval_seconds

        threshold = my_meta.scratch[self.name]['threshold']
        if interval_seconds is not None:
            # Advance by wall time.
            elapsed = time.monotonic() - my_meta.scratch[self.name]['start_time']
            intervals = math.ceil(elapsed / interval_seconds)
        else:
            # Advance by cycle.
            intervals = my_meta.scratch[self.name]['cycle']
            my_meta.scratch[self.name]['cycle'] += 1
        threshold = initial_threshold * (geom_term ** intervals) + (intervals * linear_term)
        threshold = max(threshold, min_val)
        my_meta.scratch[self.name]['threshold'] = threshold
        return retval

    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
        assert my_meta.current_state is not None
        threshold = self._threshold(my_meta)
        if neighbors[neighbor_id].current_state is None:
            # We haven't heard from this neighbor yet. Let them know our state.
            return True
        return (my_meta.current_state.distance(neighbors[neighbor_id].current_state)
                > threshold)  # type: ignore[union-attr]


def register(catalog: DeciderCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(DistanceDecider)
    DecidersConfig.register(name=DistanceDecider.name, config_type=DistanceDeciderConfig)
