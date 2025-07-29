'''Tests for unix_domain_communicator.py.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring
# pylint: disable=duplicate-code, redefined-outer-name

import getpass
from pathlib import Path
from queue import Queue
import socket
from typing import Dict, Set


from ..config_components.distributed_config import DistributedConfig
from ..neighbor_manager.event import NewNeighbor, Recv
from ..neighbor_manager.node_id import NodeID

from .impl.communicator_auto import CommunicatorCatalogAuto
from .impl.ud_endpoint import UDEndpoint
from .unix_domain_communicator import UnixDomainCommunicator

_ = CommunicatorCatalogAuto()


def path_name(path: str) -> str:
    '''Generate a unique path name for the given test.'''
    return f'/tmp/{Path(__file__).stem}_{getpass.getuser()}_{path}'


RECV_UNIT_PATH_0 = path_name('recv_unit_0')
RECV_UNIT_PATH_1 = path_name('recv_unit_1')


def test_receive() -> None:
    '''UnixDomainCommunicator listens on node 0, node 1 talks on a socket'''
    known_neighbors: Set[NodeID] = set()
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'unix_domain',
            'unix_domain': {
                'nodes_and_endpoints': [
                    (0, RECV_UNIT_PATH_0),
                    (1, RECV_UNIT_PATH_1),
                ]
            }
        }
    })
    dut = UnixDomainCommunicator(
        my_id=NodeID(0),
        distributed=distributed,
        known_neighbors=known_neighbors
    )
    Path(RECV_UNIT_PATH_1).unlink(missing_ok=True)
    queue: Queue = Queue()
    dut.start(queue=queue)
    sock = socket.socket(socket.AF_UNIX, type=socket.SOCK_DGRAM)
    sock.bind(RECV_UNIT_PATH_1)
    sock.sendto(b'Hello, world!', RECV_UNIT_PATH_0)
    sock.close()
    try:
        first_event = queue.get(block=True, timeout=0.5)
        assert isinstance(first_event, NewNeighbor)
        assert first_event.neighbor == NodeID(1)
        assert known_neighbors == {NodeID(1)}

        second_event = queue.get(block=True, timeout=0.5)
        assert isinstance(second_event, Recv)
        assert second_event.neighbor == NodeID(1)
        assert second_event.payload == b'Hello, world!'
    finally:
        dut.stop()


SEND_UNIT_PATH_0 = path_name('send_unit_0')
SEND_UNIT_PATH_1 = path_name('send_unit_1')

SEND_UNIT_NODES_AND_ENDPOINTS = [
    (NodeID(0), UDEndpoint(SEND_UNIT_PATH_0)),
    (NodeID(1), UDEndpoint(SEND_UNIT_PATH_1))
]


def test_send() -> None:
    '''UnixDomainCommunicator talks on node 1, node 0 listens on a socket'''
    known_neighbors: Set[NodeID] = set()
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'unix_domain',
            'unix_domain': {
                'nodes_and_endpoints': [
                    (0, (SEND_UNIT_PATH_0)),
                    (1, (SEND_UNIT_PATH_1)),
                ]
            }
        }
    })

    dut = UnixDomainCommunicator(
        my_id=NodeID(1),
        known_neighbors=known_neighbors,
        distributed=distributed
    )
    queue: Queue = Queue()
    dut.start(queue=queue)

    Path(SEND_UNIT_PATH_0).unlink(missing_ok=True)
    listener = socket.socket(socket.AF_UNIX, type=socket.SOCK_DGRAM)
    listener.bind(SEND_UNIT_PATH_0)

    try:

        dut.send(dest_ids=[NodeID(0)], payload=b'Hello World!')

        payload, addr = listener.recvfrom(1024)
        assert payload == b'Hello World!'
        assert addr == SEND_UNIT_PATH_1
    finally:
        listener.close()
        dut.stop()


INTEGRATION_PATH_0 = path_name('integration_0')
INTEGRATION_PATH_1 = path_name('integration_1')

INTEGRATION_NODES_AND_ENDPOINTS = [
    (NodeID(0), UDEndpoint(INTEGRATION_PATH_0)),
    (NodeID(1), UDEndpoint(INTEGRATION_PATH_1))
]


def test_exchange() -> None:
    '''2 UnixDomainCommunicator on different nodes talk and listen to each other.'''

    known_neighbors0: Set[NodeID] = set()
    known_neighbors1: Set[NodeID] = set()

    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'unix_domain',
            'unix_domain': {
                'nodes_and_endpoints': [
                    (0, (INTEGRATION_PATH_0)),
                    (1, (INTEGRATION_PATH_1)),
                ]
            }
        }
    })

    dut0 = UnixDomainCommunicator(
        my_id=NodeID(0),
        known_neighbors=known_neighbors0,
        distributed=distributed
    )
    dut1 = UnixDomainCommunicator(
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


SENDALL_PATH_0 = path_name('sendall_0')
SENDALL_PATH_1 = path_name('sendall_1')
SENDALL_PATH_2 = path_name('sendall_2')
SENDALL_PATH_3 = path_name('sendall_3')
SENDALL_PATH_4 = path_name('sendall_4')


SENDALL_NODES_AND_ENDPOINTS = [
    (NodeID(0), UDEndpoint(SENDALL_PATH_0)),
    (NodeID(1), UDEndpoint(SENDALL_PATH_1)),
    (NodeID(2), UDEndpoint(SENDALL_PATH_2)),
    (NodeID(3), UDEndpoint(SENDALL_PATH_3)),
    (NodeID(4), UDEndpoint(SENDALL_PATH_4)),
]


def test_sendall() -> None:
    '''One node sends to a bunch of neighbors.'''

    known_neighbors: Dict[NodeID, Set[NodeID]] = {}
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'unix_domain',
            'unix_domain': {
                'nodes_and_endpoints': [
                    (0, SENDALL_PATH_0),
                    (1, SENDALL_PATH_1),
                    (2, SENDALL_PATH_2),
                    (3, SENDALL_PATH_3),
                    (4, SENDALL_PATH_4),
                ]
            }
        }
    })

    dut: Dict[NodeID, UnixDomainCommunicator] = {}
    queue: Dict[NodeID, Queue] = {}
    for node_id in range(0, 5):
        node = NodeID(node_id)
        known_neighbors[node] = set()
        queue[node] = Queue()
        dut[node] = UnixDomainCommunicator(
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


DYNAMIC_DISCOVERY_PATH_0 = path_name('dynamic_discovery_0')
DYNAMIC_DISCOVERY_PATH_1 = path_name('dynamic_discovery_1')
DYNAMIC_DISCOVERY_PATH_2 = path_name('dynamic_discovery_2')
DYNAMIC_DISCOVERY_PATH_3 = path_name('dynamic_discovery_3')
DYNAMIC_DISCOVERY_PATH_4 = path_name('dynamic_discovery_4')


DYNAMIC_DISCOVERY_NODES_AND_ENDPOINTS = [
    (NodeID(0), UDEndpoint(DYNAMIC_DISCOVERY_PATH_0)),
]

DYNAMIC_DISCOVERY_ENDPOINTS = [
    UDEndpoint(DYNAMIC_DISCOVERY_PATH_0),
    UDEndpoint(DYNAMIC_DISCOVERY_PATH_1),
    UDEndpoint(DYNAMIC_DISCOVERY_PATH_2),
    UDEndpoint(DYNAMIC_DISCOVERY_PATH_3),
    UDEndpoint(DYNAMIC_DISCOVERY_PATH_4),
]


def test_dynamic_discovery() -> None:
    '''One node sends to a bunch of neighbors.'''

    known_neighbors: Dict[NodeID, Set[NodeID]] = {}
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'unix_domain',
            'unix_domain': {
                'nodes_and_endpoints': [
                    (0, DYNAMIC_DISCOVERY_PATH_0),
                    (1, DYNAMIC_DISCOVERY_PATH_1),
                    (2, DYNAMIC_DISCOVERY_PATH_2),
                    (3, DYNAMIC_DISCOVERY_PATH_3),
                    (4, DYNAMIC_DISCOVERY_PATH_4),
                ]
            }
        }
    })

    dut: Dict[NodeID, UnixDomainCommunicator] = {}
    queue: Dict[NodeID, Queue] = {}
    for node_id in range(0, 5):
        node = NodeID(node_id)
        known_neighbors[node] = set()
        queue[node] = Queue()
        dut[node] = UnixDomainCommunicator(
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

        known_endpoints = {
            dut[NodeID(0)].lookup_endpoint(node_id).path
            for node_id in known_neighbors[NodeID(0)]
        }
        assert known_endpoints == {
            DYNAMIC_DISCOVERY_PATH_1,
            DYNAMIC_DISCOVERY_PATH_2,
            DYNAMIC_DISCOVERY_PATH_3,
            DYNAMIC_DISCOVERY_PATH_4,
        }

    finally:
        for node_id in range(0, 5):
            node = NodeID(node_id)
            dut[node].stop()
