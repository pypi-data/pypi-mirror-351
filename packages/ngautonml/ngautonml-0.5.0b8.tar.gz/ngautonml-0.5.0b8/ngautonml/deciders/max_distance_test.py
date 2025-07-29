'''Tests for distance.py'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


from typing import Mapping

from ..algorithms.impl.neighbor_metadata import NeighborMetadata
from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..algorithms.impl.toy_neighbor_state import ToyNeighborState
from ..config_components.distributed_config import DistributedConfig
from ..deciders.impl.decider import Decider
from ..neighbor_manager.node_id import NodeID

from .impl.decider_auto import DeciderCatalogAuto

# pylint: disable=duplicate-code


def test_sunny_day() -> None:
    '''Test the max_distance decider.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'max_distance': {
                    'num_neighbors': 1,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('max_distance')(
        config=distributed.decider.max_distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=my_state)
    near_id = NodeID(1)
    below_id = NodeID(2)
    distant_id = NodeID(3)
    neighbors = {
        near_id: NeighborMetadata(my_state=ToyNeighborState(center=0.1)),
        below_id: NeighborMetadata(my_state=ToyNeighborState(center=0.3)),
        distant_id: NeighborMetadata(my_state=ToyNeighborState(center=1.0)),
    }

    assert decider.decide(my_meta=my_meta, neighbor_id=near_id, neighbors=neighbors) is False
    assert decider.decide(my_meta=my_meta, neighbor_id=below_id, neighbors=neighbors) is False
    assert decider.decide(my_meta=my_meta, neighbor_id=distant_id, neighbors=neighbors) is True


def test_max_distance_no_state() -> None:
    '''Test the decider_stub in the DeciderCatalog class.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'max_distance': {
                    'num_neighbors': 1,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('max_distance')(
        config=distributed.decider.max_distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=my_state)
    near_id = NodeID(1)
    below_id = NodeID(2)
    distant_id = NodeID(3)
    neighbors = {
        near_id: NeighborMetadata(my_state=ToyNeighborState(center=0.1)),
        below_id: NeighborMetadata(my_state=None),
        distant_id: NeighborMetadata(my_state=None),
    }

    assert decider.decide(my_meta=my_meta, neighbor_id=near_id, neighbors=neighbors) is False
    assert decider.decide(my_meta=my_meta, neighbor_id=below_id, neighbors=neighbors) is True
    assert decider.decide(my_meta=my_meta, neighbor_id=distant_id, neighbors=neighbors) is True


def test_max_distance_no_neighbors() -> None:
    '''Test the decider_stub in the DeciderCatalog class.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'max_distance': {
                    'num_neighbors': 1,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('max_distance')(
        config=distributed.decider.max_distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=my_state)
    neighbor_id = NodeID(1)
    neighbors: Mapping[NodeID, NeighborMetadataInterface] = {}

    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
