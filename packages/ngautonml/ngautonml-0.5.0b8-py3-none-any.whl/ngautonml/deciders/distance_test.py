'''Tests for distance.py'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import time

from ..algorithms.impl.neighbor_metadata import NeighborMetadata
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
                'distance': {
                    'threshold': 0.2,  # Default is 0.5.
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('distance')(config=distributed.decider.distance)  # type: ignore[attr-defined] # pylint: disable=no-member

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
    assert decider.decide(my_meta=my_meta, neighbor_id=below_id, neighbors=neighbors) is True
    assert decider.decide(my_meta=my_meta, neighbor_id=distant_id, neighbors=neighbors) is True


def test_geometric_term() -> None:
    '''Test the distance decider with a geometric term.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'distance': {
                    'threshold': 8.0,
                    'geometric_term': 0.5,
                    'min': 0.1,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('distance')(config=distributed.decider.distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=my_state)

    neighbor_id = NodeID(1)
    neighbors = {
        neighbor_id: NeighborMetadata(my_state=ToyNeighborState(center=0.3)),
    }

    assert 'distance' not in my_meta.scratch
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 4.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 2.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 1.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 0.5
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 0.25
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['distance']['threshold'] == 0.125
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['distance']['threshold'] == 0.1


def test_linear_term() -> None:
    '''Test the distance decider with a geometric term.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'distance': {
                    'threshold': 4.0,
                    'linear_term': -1.0,
                    'min': 0.1,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('distance')(config=distributed.decider.distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=my_state)

    neighbor_id = NodeID(1)
    neighbors = {
        neighbor_id: NeighborMetadata(my_state=ToyNeighborState(center=0.3)),
    }

    assert 'distance' not in my_meta.scratch
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 3.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 2.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 1.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True


def test_interval_seconds() -> None:
    '''Test the distance decider with a geometric term.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'distance': {
                    'threshold': 4.0,
                    'linear_term': -1.0,
                    'min': 0.1,
                    'interval_seconds': 1.0,
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('distance')(config=distributed.decider.distance)  # type: ignore[attr-defined] # pylint: disable=no-member

    my_state = ToyNeighborState(center=0.0)
    my_meta = NeighborMetadata(my_state=my_state)

    neighbor_id = NodeID(1)
    neighbors = {
        neighbor_id: NeighborMetadata(my_state=ToyNeighborState(center=0.3)),
    }

    assert 'distance' not in my_meta.scratch
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 3.0
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 3.0
    time.sleep(3.0)
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is False
    assert my_meta.scratch['distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
    assert my_meta.scratch['distance']['threshold'] == 0.1
    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is True
