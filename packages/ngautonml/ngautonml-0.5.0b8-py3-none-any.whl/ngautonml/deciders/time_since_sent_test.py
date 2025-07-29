'''Tests for time_since_send.py'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import time


from ..algorithms.impl.neighbor_metadata import NeighborMetadata
from ..algorithms.impl.toy_neighbor_state import ToyNeighborState
from ..config_components.distributed_config import DistributedConfig
from ..deciders.impl.decider import Decider
from ..neighbor_manager.node_id import NodeID

from .impl.decider_auto import DeciderCatalogAuto


def test_time_since_sent() -> None:
    '''Test the time_since_send decider with a geometric term.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'time_since_sent': {
                    'time_seconds': 1.0,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('time_since_sent')(
        config=distributed.decider.time_since_sent)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=my_state)

    neighbor_id = NodeID(-1)

    # We send the first time.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors={}) is True
    my_meta.sent_current_state()
    # We should not send immediately after sending...
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors={}) is False
    time.sleep(0.1)
    # ...or after a short interval.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors={}) is False
    time.sleep(1.0)
    # We should send after a full interval.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors={}) is True
    my_meta.sent_current_state()
    # See that the sequence repeats.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors={}) is False
    time.sleep(0.1)
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors={}) is False
    time.sleep(1.0)
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors={}) is True
