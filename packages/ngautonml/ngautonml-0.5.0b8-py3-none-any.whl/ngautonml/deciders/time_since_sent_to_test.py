'''Tests for time_since_sent_specific.py'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import time
from typing import Optional


from ..algorithms.impl.neighbor_metadata import NeighborMetadata
from ..algorithms.impl.distributed_algorithm_instance import NeighborState
from ..config_components.distributed_config import DistributedConfig
from ..deciders.impl.decider import Decider
from ..neighbor_manager.node_id import NodeID

from .impl.decider_auto import DeciderCatalogAuto

# pylint: disable=duplicate-code


class TestNeighborState(NeighborState):
    '''Test class for NeighborState.'''
    _center: float

    def __init__(self, center: float = 0.0) -> None:
        super().__init__()
        self._center = center

    @property
    def center(self) -> float:
        '''Get the center.'''
        return self._center

    def encode(self) -> bytes:
        '''Encode a message for distributed neighbors. '''
        return b'test neighbor state'

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'TestNeighborState':
        '''Decode a message from distributed neighbors.

        This should just redirect to the relevant NeighborState subclass.
        '''
        return cls(center=0.0)

    def state_differs(self,
                      distributed: DistributedConfig,
                      other: Optional[NeighborState]) -> bool:
        '''Decide if our state differs meaningfully from the last one we sent.

        :distributed: contains information from the problem definition, including fit_eps
        :last_state_sent: is an instance of type(self) or None.
        '''
        return True

    def distance(self, other: NeighborState) -> float:
        '''Return the distance between two states.'''
        assert isinstance(other, TestNeighborState)
        return abs(self.center - other.center)


def test_time_since_sent_to() -> None:
    '''Test the time_since_sent_to decider.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'time_since_sent_to': {
                    'time_seconds': 1.0,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('time_since_sent_to')(
        config=distributed.decider.time_since_sent_to)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = TestNeighborState()
    my_meta = NeighborMetadata(my_state=my_state)

    neighbor_id2 = NodeID(2)
    neighbor_id3 = NodeID(3)
    neighbors = {
        neighbor_id2: NeighborMetadata(my_state=TestNeighborState()),
        neighbor_id3: NeighborMetadata(my_state=TestNeighborState())
    }

    # We send the first time.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id2, neighbors=neighbors) is True
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id3, neighbors=neighbors) is True
    # Mark that we sent to both neighbors.
    neighbors[neighbor_id2].last_state_sent = my_meta.current_state
    neighbors[neighbor_id3].last_state_sent = my_meta.current_state
    # We should not send immediately after sending...
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id2, neighbors=neighbors) is False
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id3, neighbors=neighbors) is False
    time.sleep(0.1)
    # ...or after a short interval.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id2, neighbors=neighbors) is False
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id3, neighbors=neighbors) is False
    time.sleep(0.5)
    # Refresh node 3.
    neighbors[neighbor_id3].last_state_sent = my_meta.current_state
    time.sleep(0.5)
    # We should send to node 2 after a full interval, but not to node 3.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id2, neighbors=neighbors) is True
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id3, neighbors=neighbors) is False
    neighbors[neighbor_id2].last_state_sent = my_meta.current_state
    # The nodes are now out of sync.
    time.sleep(0.1)
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id2, neighbors=neighbors) is False
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id3, neighbors=neighbors) is False
    time.sleep(0.5)
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id2, neighbors=neighbors) is False
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id3, neighbors=neighbors) is True
    neighbors[neighbor_id3].last_state_sent = my_meta.current_state
    time.sleep(0.5)
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id2, neighbors=neighbors) is True
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id3, neighbors=neighbors) is False
