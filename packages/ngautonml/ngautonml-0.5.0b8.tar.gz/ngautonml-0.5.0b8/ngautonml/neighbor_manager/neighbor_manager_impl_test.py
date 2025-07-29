'''tests for ssnm.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..config_components.distributed_config import DistributedConfig
from ..communicators.stub_communicator import CommunicatorStub
from ..discoverers.static_discoverer import StaticDiscoverer

from .node_id import NodeID
from .neighbor_manager import NewNeighbor
from .neighbor_manager_impl import NeighborManagerImpl

# pylint: disable=missing-function-docstring, duplicate-code


def test_neighbor_startup():
    distributed_config = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [2, 4, 5],
                    '2': [1, 3, 5],
                    '3': [5, 2],
                    '4': [1],
                    '5': [1, 2, 3]
                }
            }
        }
    })
    my_id = NodeID(2)
    discoverer = StaticDiscoverer(
        config=distributed_config,
        communicator=CommunicatorStub(my_id=my_id))
    dut = NeighborManagerImpl(discoverer=discoverer)

    dut.start()

    # WARNING: By the rules for queue.Queue this test
    # could be flakey. We're not guaranteed to be able
    # to read all the queued NewNeighbor events.
    events = dut.poll_for_events()

    assert all(isinstance(e, NewNeighbor) for e in events)

    neighbors = set(e.neighbor for e in events)

    assert neighbors == {NodeID(1), NodeID(3), NodeID(5)}

    dut.stop()
