'''Tests for memory_communicator.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring
# pylint: disable=duplicate-code, redefined-outer-name


from queue import Queue
from typing import Dict, Set

from ..config_components.distributed_config import DistributedConfig
from ..neighbor_manager.event import NewNeighbor, Recv
from ..neighbor_manager.node_id import NodeID

from .impl.communicator_auto import CommunicatorCatalogAuto
from .memory_communicator import MemoryCommunicator

_ = CommunicatorCatalogAuto()


def test_exchange() -> None:
    '''2 MemoryCommunicator on different nodes talk and listen to each other.'''

    known_neighbors0: Set[NodeID] = set()
    known_neighbors1: Set[NodeID] = set()

    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'memory',
            'memory': {
                'domain': 'test_exchange',
            },
        }
    })

    dut0 = MemoryCommunicator(
        my_id=NodeID(0),
        known_neighbors=known_neighbors0,
        distributed=distributed
    )
    dut1 = MemoryCommunicator(
        my_id=NodeID(1),
        known_neighbors=known_neighbors1,
        distributed=distributed
    )

    queue0: Queue = Queue()
    queue1: Queue = Queue()

    dut0.start(queue=queue0)
    dut1.start(queue=queue1)

    try:
        dut0.send(dest_ids=[NodeID(1)], payload=b'Hello, Node 1!')
        first_event = queue1.get(block=True, timeout=0.5)
        assert isinstance(first_event, NewNeighbor)
        assert first_event.neighbor == NodeID(0)
        assert known_neighbors1 == {NodeID(0)}

        second_event = queue1.get(block=True, timeout=0.5)
        assert isinstance(second_event, Recv)
        assert second_event.neighbor == NodeID(0)
        assert second_event.payload == b'Hello, Node 1!'

        dut1.send(dest_ids=[NodeID(0)], payload=b'Nice to meet you, Node 0 :)')

        first_event = queue0.get(block=True, timeout=0.5)
        assert isinstance(first_event, NewNeighbor)
        assert first_event.neighbor == NodeID(1)
        assert known_neighbors0 == {NodeID(1)}

        second_event = queue0.get(block=True, timeout=0.5)
        assert isinstance(second_event, Recv)
        assert second_event.neighbor == NodeID(1)
        assert second_event.payload == b'Nice to meet you, Node 0 :)'

    finally:
        dut0.stop()
        dut1.stop()


def test_sendall() -> None:
    '''One node sends to a bunch of neighbors.'''

    known_neighbors: Dict[NodeID, Set[NodeID]] = {}
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'memory',
            'memory': {
                'domain': 'test_sendall',
            },
        }
    })

    dut: Dict[NodeID, MemoryCommunicator] = {}
    queue: Dict[NodeID, Queue] = {}
    for node_id in range(0, 5):
        node = NodeID(node_id)
        known_neighbors[node] = set()
        queue[node] = Queue()
        dut[node] = MemoryCommunicator(
            my_id=node,
            known_neighbors=known_neighbors[node],
            distributed=distributed)
        dut[node].start(queue=queue[node], timeout=0.5)

    for node_id in range(1, 5):
        node = NodeID(node_id)
        # We need to send an initial message to establish our neighborliness.
        dut[node].send([NodeID(0)], f'Hello, I am {node}.'.encode())

    try:
        # Read a NewNeighbor and a Recv for each neighbor.
        # The pairs of requests are randomly interleaved due to threading,
        # so we don't bother checking what they are.
        for _ in range(1, 5):
            _ = queue[NodeID(0)].get()
            _ = queue[NodeID(0)].get()

        # This is what we are testing.
        dut[NodeID(0)].send_all(payload=b'Hello, All Nodes!')

        # Confirm that the test worked.
        for node_id in range(1, 5):
            node = NodeID(node_id)

            first_event = queue[node].get(block=True, timeout=0.5)
            assert isinstance(first_event, NewNeighbor)
            assert first_event.neighbor == NodeID(0)
            assert known_neighbors[node] == {NodeID(0)}

            second_event = queue[node].get(block=True, timeout=0.5)
            assert isinstance(second_event, Recv)
            assert second_event.neighbor == NodeID(0)
            assert known_neighbors[node] == {NodeID(0)}
            assert second_event.payload == b'Hello, All Nodes!'

    finally:
        for node_id in range(0, 5):
            node = NodeID(node_id)
            dut[node].stop()


def test_dynamic_discovery() -> None:
    '''One node sends to a bunch of neighbors.'''

    known_neighbors: Dict[NodeID, Set[NodeID]] = {}
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'memory',
            'memory': {
                'domain': 'test_dynamic_discovery',
            },
        }
    })

    dut: Dict[NodeID, MemoryCommunicator] = {}
    queue: Dict[NodeID, Queue] = {}
    for node_id in range(0, 5):
        node = NodeID(node_id)
        known_neighbors[node] = set()
        queue[node] = Queue()
        dut[node] = MemoryCommunicator(
            my_id=node,
            known_neighbors=known_neighbors[node],
            distributed=distributed)
        dut[node].start(queue=queue[node], timeout=0.5)

    # This is the test. Everybody introduces themselves.
    for node_id in range(1, 5):
        node = NodeID(node_id)
        dut[node].send([NodeID(0)], f'Hello, I am {node}.'.encode())

    # Confirm that the test worked.
    try:
        # Read a NewNeighbor and a Recv for each neighbor.
        # The pairs of requests are randomly interleaved due to threading,
        # so we don't bother checking what they are.
        # This is needed to make sure every message has been recieved before
        #   checking known_neighbors.
        for _ in range(1, 5):
            _ = queue[NodeID(0)].get()
            _ = queue[NodeID(0)].get()

        assert known_neighbors[NodeID(0)] == {
            NodeID(1),
            NodeID(2),
            NodeID(3),
            NodeID(4),
        }

    finally:
        for node_id in range(0, 5):
            node = NodeID(node_id)
            dut[node].stop()
