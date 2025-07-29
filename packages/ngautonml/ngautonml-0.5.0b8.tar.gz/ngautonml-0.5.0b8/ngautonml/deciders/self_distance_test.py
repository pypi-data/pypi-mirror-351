'''Tests for self_distance.py'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Mapping


from ..algorithms.impl.neighbor_metadata import NeighborMetadata, NeighborMetadataInterface
from ..algorithms.impl.toy_neighbor_state import ToyNeighborState
from ..config_components.distributed_config import DistributedConfig
from ..deciders.impl.decider import Decider
from ..neighbor_manager.node_id import NodeID

from .impl.decider_auto import DeciderCatalogAuto


def test_catalog() -> None:
    '''Test the decider_stub in the DeciderCatalog class.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'self_distance': {
                    'threshold': 0.2,  # Default is 0.5.
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('self_distance')(
        config=distributed.decider.self_distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata()
    near_state = ToyNeighborState(center=0.1)
    below_state = ToyNeighborState(center=0.3)
    distant_state = ToyNeighborState(center=1.0)

    neighbor_id_ignored = NodeID(-1)

    # No previous or current state should not send.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id_ignored, neighbors={}) is False

    # Previous state sent is None, but the current state is not; we should send.
    my_meta.current_state = my_state
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id_ignored, neighbors={}) is True
    my_meta.sent_current_state()

    # Previous state sent and current state are the same; we should not send.
    my_meta.current_state = my_state
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id_ignored, neighbors={}) is False

    # Previous state sent is center=0.0, current state is center=0.1, threshold=0.2;
    # we should not send.
    my_meta.current_state = near_state
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id_ignored, neighbors={}) is False

    # Previous state sent is center=0.0, current state is center=0.3, threshold=0.2;
    # we should send.
    my_meta.current_state = below_state
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id_ignored, neighbors={}) is True
    my_meta.sent_current_state()

    # Previous state sent is center=0.3, current state is center=1.0, threshold=0.2;
    # we should send.
    my_meta.current_state = distant_state
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id_ignored, neighbors={}) is True
    my_meta.sent_current_state()

    # Previous state sent and current state are the same; we should not send.
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id_ignored, neighbors={}) is False


def test_geometric_term() -> None:
    '''Test the distance decider with a geometric term.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'self_distance': {
                    'threshold': 8.0,
                    'geometric_term': 0.5,
                    'min': 0.1,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('self_distance')(
        config=distributed.decider.self_distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    initial_state = ToyNeighborState(center=0.3)
    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=initial_state)
    my_meta.sent_current_state()
    my_meta.current_state = my_state

    neighbor_id = NodeID(-1)
    neighbors: Mapping[NodeID, NeighborMetadataInterface] = {}

    assert 'self_distance' not in my_meta.scratch
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 4.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 2.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 1.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 0.5
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 0.25
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['self_distance']['threshold'] == 0.125
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['self_distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['self_distance']['threshold'] == 0.1


def test_linear_term() -> None:
    '''Test the distance decider with a geometric term.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'self_distance': {
                    'threshold': 4.0,
                    'linear_term': -1.0,
                    'min': 0.1,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('self_distance')(
        config=distributed.decider.self_distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    initial_state = ToyNeighborState(center=0.3)
    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=initial_state)
    my_meta.sent_current_state()
    my_meta.current_state = my_state

    neighbor_id = NodeID(-1)
    neighbors: Mapping[NodeID, NeighborMetadataInterface] = {}

    assert 'self_distance' not in my_meta.scratch
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 3.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 2.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 1.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['self_distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['self_distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
