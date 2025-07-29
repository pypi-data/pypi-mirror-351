'''Tests for boolan.py and related files.'''
# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Mapping

import pytest

from ..algorithms.impl.neighbor_metadata import NeighborMetadata
from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..algorithms.impl.toy_neighbor_state import ToyNeighborState
from ..config_components.distributed_config import DistributedConfig
from ..deciders.impl.decider import Decider
from ..neighbor_manager.node_id import NodeID

from .impl.decider_auto import DeciderCatalogAuto


@pytest.mark.parametrize('op,lhs,rhs,result', [
    ('and', 'true', 'true', True),
    ('and', 'true', 'false', False),
    ('and', 'false', 'true', False),
    ('and', 'false', 'false', False),
    ('or', 'true', 'true', True),
    ('or', 'true', 'false', True),
    ('or', 'false', 'true', True),
    ('or', 'false', 'false', False),
    ('not', 'true', 'true', False),
    ('not', 'false', 'false', True),
])
def test_and_or(op: str, lhs: str, rhs: str, result: bool):
    '''Test the decider_stub in the DeciderCatalog class.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                op: {
                    lhs: {},
                    rhs: {}
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name(op)(config=getattr(distributed.decider, op))  # pylint: disable=no-member

    my_meta = NeighborMetadata(my_state=ToyNeighborState(center=0.0))
    neighbor_id = NodeID(1)
    neighbors = {
        neighbor_id: NeighborMetadata(my_state=ToyNeighborState(center=0.0))
    }

    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) == result


@pytest.mark.parametrize('threshold,result', [
    (0.1, False),
    (0.5, True),
])
def test_compound(threshold: float, result: bool):
    '''Test a compund Boolean decider.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'and': {
                    'true': {},
                    'or': {
                        'not': {
                            'distance': {
                                'threshold': threshold,
                            },
                        },
                        'false': {},
                    }
                }
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider: Decider = catalog.lookup_by_name('and')(config=getattr(distributed.decider, 'and'))  # pylint: disable=no-member

    my_meta = NeighborMetadata(my_state=ToyNeighborState(center=0.0))
    neighbor_id = NodeID(1)
    neighbors: Mapping[NodeID, NeighborMetadataInterface] = {
        neighbor_id: NeighborMetadata(my_state=ToyNeighborState(center=0.5))
    }

    assert decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors) is result
