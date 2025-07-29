'''Tests for kafka_communicator.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring

# To start a kafka server to run these tests, run the following commands:
# $ docker pull apache/kafka:3.8.0
# $ KAFKA_AUTO_CREATE_TOPICS_ENABLE=TRUE docker run -p 9092:9092 apache/kafka:3.8.0

from copy import deepcopy
import datetime
import getpass
import os
from pathlib import Path
from queue import Queue
import time
from typing import Any, Dict, List, Optional, Set

import pytest

from kafka import KafkaProducer, KafkaConsumer  # type: ignore[import,attr-defined]

from ..config_components.distributed_config import DistributedConfig
from ..neighbor_manager.event import NewNeighbor, Recv
from ..neighbor_manager.node_id import NodeID

from .kafka_communicator import KafkaCommunicator
from .impl.communicator_auto import CommunicatorCatalogAuto

# pylint: disable=duplicate-code, redefined-outer-name
_ = CommunicatorCatalogAuto()


BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')

SHORT_QUEUE_TIMEOUT = 0.5
LONG_QUEUE_TIMEOUT = 30.0


def topic_name(topic: str) -> str:
    '''Generate a unique topic name for the given test.'''
    return f'{Path(__file__).stem}_{getpass.getuser()}_{topic}'


class Producer():
    '''A Kafka producer that sends messages to a topic.

    Only used by distributed algorithms.
    '''
    _producer: KafkaProducer

    def __init__(self):
        self._producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS.split(','),
            client_id='1')

    def __call__(
        self,
    ) -> KafkaProducer:
        return self._producer


@pytest.fixture(scope='session')
def kafka_producer() -> Producer:
    '''A fixture that returns a Kafka producer.'''
    return Producer()


RECV_TOPIC = topic_name('test_receive')


@pytest.mark.skip(reason='This test fails with QueueEmpty.')
def test_receive(kafka_producer) -> None:
    '''KafkaCommunicator listens on a topic and receives a message.'''
    known_neighbors: Set[NodeID] = set()
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'kafka',
            'kafka': {
                'bootstrap_servers': BOOTSTRAP_SERVERS.split(','),
                'topic': RECV_TOPIC
            }
        }
    })
    dut = KafkaCommunicator(
        my_id=NodeID(0),
        distributed=distributed,
        known_neighbors=known_neighbors
    )
    queue: Queue = Queue()
    dut.start(queue=queue, timeout=SHORT_QUEUE_TIMEOUT)
    kafka_producer().send(RECV_TOPIC, key=str(NodeID(1)).encode('utf-8'), value=b'Hello, world!')
    try:
        first_event = queue.get(block=True, timeout=LONG_QUEUE_TIMEOUT)
        assert isinstance(first_event, NewNeighbor)
        assert first_event.neighbor == NodeID(1)
        assert known_neighbors == {NodeID(1)}

        second_event = queue.get(block=True, timeout=SHORT_QUEUE_TIMEOUT)
        assert isinstance(second_event, Recv)
        assert second_event.neighbor == NodeID(1)
        assert second_event.payload == b'Hello, world!'
    finally:
        dut.stop()


SEND_TOPIC = topic_name('test_send')
SEND_GROUP_ID = 'test_send_group_id'


@pytest.mark.skip(reason='This test hangs waiting for message to listener.')
def test_send() -> None:
    '''KafkaCommunicator talks on node 1, node 0 listens on a topic'''
    known_neighbors: Set[NodeID] = set()
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'kafka',
            'kafka': {
                'bootstrap_servers': BOOTSTRAP_SERVERS.split(','),
                'topic': SEND_TOPIC
            }
        }
    })
    print("DEBUG: test_send creating dut")
    dut = KafkaCommunicator(
        my_id=NodeID(0),
        known_neighbors=known_neighbors,
        distributed=distributed
    )
    queue: Queue = Queue()
    print("DEBUG: test_send starting dut")
    dut.start(queue=queue)
    print("DEBUG: test_send dut started")

    listener = KafkaConsumer(
        SEND_TOPIC,
        group_id=SEND_GROUP_ID,
        bootstrap_servers=BOOTSTRAP_SERVERS.split(','),
        auto_offset_reset='latest',
        enable_auto_commit=False,
        request_timeout_ms=20000
    )
    print("DEBUG: test_send created listener")
    try:
        dut.send_all(payload=b'Hello World!')
        print("DEBUG: test_send waiting on message to listener")
        message = next(listener)
        print("DEBUG: test_send got message from listener")
        listener.commit()
        assert message.topic == SEND_TOPIC
        assert message.key == b'1'
        assert message.value == b'Hello World!'
    finally:
        dut.stop()
        listener.close()


EXCHANGE_TOPIC = topic_name('test_exchange')


@pytest.mark.skip(reason='This fails with out-of-sync messages.')
def test_exchange() -> None:
    '''2 KafkaCommunicator on different nodes talk and listen to each other.'''

    known_neighbors0: Set[NodeID] = set()
    known_neighbors1: Set[NodeID] = set()

    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'kafka',
            'kafka': {
                'bootstrap_servers': BOOTSTRAP_SERVERS.split(','),
                'topic': EXCHANGE_TOPIC,
            }
        }
    })

    dut0 = KafkaCommunicator(
        my_id=NodeID(0),
        known_neighbors=known_neighbors0,
        distributed=distributed
    )
    dut1 = KafkaCommunicator(
        my_id=NodeID(1),
        known_neighbors=known_neighbors1,
        distributed=distributed
    )

    queue0: Queue = Queue()
    queue1: Queue = Queue()

    dut0.start(queue=queue0)
    dut1.start(queue=queue1)

    try:
        payload0 = f'Hello, Node 1! {datetime.datetime.now()}'.encode()
        dut0.send_all(payload=payload0)
        first_event = queue1.get(block=True, timeout=LONG_QUEUE_TIMEOUT)
        assert isinstance(first_event, NewNeighbor)
        assert first_event.neighbor == NodeID(0)
        assert known_neighbors1 == {NodeID(0)}

        second_event = queue1.get(block=True, timeout=LONG_QUEUE_TIMEOUT)
        assert isinstance(second_event, Recv)
        assert second_event.neighbor == NodeID(0)
        assert second_event.payload == payload0

        payload1 = f'Nice to meet you, Node 0 :) {datetime.datetime.now()}'.encode()
        dut1.send_all(payload1)

        first_event = queue0.get(block=True, timeout=LONG_QUEUE_TIMEOUT)
        assert isinstance(first_event, NewNeighbor)
        assert first_event.neighbor == NodeID(1)
        assert known_neighbors0 == {NodeID(1)}

        second_event = queue0.get(block=True, timeout=LONG_QUEUE_TIMEOUT)
        assert isinstance(second_event, Recv)
        assert second_event.neighbor == NodeID(1)
        assert second_event.payload == payload1

    finally:
        dut0.stop()
        dut1.stop()


SENDALL_TOPIC = topic_name('test_sendall')


# This test passes with kafka-python 2.0.4 but fails for 2.1.5.
@pytest.mark.skip(reason='This test fails with _queue.Empty.')
def test_sendall() -> None:
    '''One node sends to a bunch of neighbors.'''

    known_neighbors: Dict[NodeID, Set[NodeID]] = {}
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'kafka',
            'kafka': {
                'bootstrap_servers': BOOTSTRAP_SERVERS.split(','),
                'topic': SENDALL_TOPIC,
            }
        }
    })

    dut: Dict[NodeID, KafkaCommunicator] = {}
    queues: Dict[NodeID, Queue] = {}
    for node_id in range(0, 5):
        node = NodeID(node_id)
        known_neighbors[node] = set()
        queues[node] = Queue()
        dut[node] = KafkaCommunicator(
            my_id=node,
            known_neighbors=known_neighbors[node],
            distributed=distributed)
        dut[node].start(queue=queues[node], timeout=SHORT_QUEUE_TIMEOUT)

    # For KafkaCommunicator, there is no need for neighbors to introduce themselves.
    try:
        # This is what we are testing.
        dut[NodeID(0)].send_all(payload=b'Hello, All Nodes!')

        # Confirm that the test worked.
        for node_id in range(1, 5):
            node = NodeID(node_id)

            first_event = queues[node].get(block=True, timeout=LONG_QUEUE_TIMEOUT)
            assert isinstance(first_event, NewNeighbor)
            assert first_event.neighbor == NodeID(0)
            assert known_neighbors[node] == {NodeID(0)}

            second_event = queues[node].get(block=True, timeout=LONG_QUEUE_TIMEOUT)
            assert isinstance(second_event, Recv)
            assert second_event.neighbor == NodeID(0)
            assert known_neighbors[node] == {NodeID(0)}
            assert second_event.payload == b'Hello, All Nodes!'

    finally:
        for node_id in range(0, 5):
            node = NodeID(node_id)
            dut[node].stop()


DYNAMIC_DISCOVERY_TOPIC = topic_name('test_dynamic_discovery')


@pytest.mark.skip(reason='This test fails with _queue.Empty.')
def test_dynamic_discovery() -> None:
    '''A bunch of neighbors send to one node who learns their identities.'''

    known_neighbors: Dict[NodeID, Set[NodeID]] = {}
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'kafka',
            'kafka': {
                'bootstrap_servers': BOOTSTRAP_SERVERS.split(','),
                'topic': DYNAMIC_DISCOVERY_TOPIC,
            }
        }
    })

    dut: Dict[NodeID, KafkaCommunicator] = {}
    queues: Dict[NodeID, Queue] = {}
    for node_id in range(0, 5):
        node = NodeID(node_id)
        known_neighbors[node] = set()
        queues[node] = Queue()
        dut[node] = KafkaCommunicator(
            my_id=node,
            known_neighbors=known_neighbors[node],
            distributed=distributed)
        dut[node].start(queue=queues[node], timeout=SHORT_QUEUE_TIMEOUT)

    # This is the test. Everybody introduces themselves.
    for node_id in range(1, 5):
        node = NodeID(node_id)
        dut[node].send_all(f'Hello, I am {node}.'.encode())

    # Confirm that the test worked.
    try:
        # Read a NewNeighbor and a Recv for each neighbor.
        # The pairs of requests are randomly interleaved due to threading,
        # so we don't bother checking what they are.
        # This is needed to make sure every message has been recieved before
        #   checking known_neighbors.
        # We receive a NewNeighbor and a Recv from each neighbor.
        for _ in range(1, 5):
            _ = queues[NodeID(0)].get()
            _ = queues[NodeID(0)].get()

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


KAFKA_TOPIC = topic_name('test_kafka')


@pytest.mark.skip(
    reason='This test deliberately fails in order to provide exploratory information.')
def test_kafka() -> None:
    '''Test Kafka.'''
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS.split(','),
        client_id='kafka_producer_client_id')

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        group_id='kafka_consumer_group_id',
        client_id='kafka_consumer_client_id',
        bootstrap_servers=BOOTSTRAP_SERVERS.split(','),
        auto_offset_reset='latest',
        enable_auto_commit=True)

    # send 2 messages with producer that log time that they were sent

    producer.send(KAFKA_TOPIC,
                  key=b'some key',
                  value=f'Message 1: {datetime.datetime.now()}'.encode('utf-8'))
    time.sleep(0.5)
    producer.send(KAFKA_TOPIC,
                  key=b'some key',
                  value=f'Message 2: {datetime.datetime.now()}'.encode('utf-8'))

    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print(f'{message.topic}:{message.partition}:{message.offset}: '
              f'key={str(message.key)} value={str(message.value)}')
    assert False


SEND_UNICAST_PREFIX = topic_name('test_send_unicast')
SEND_UNICAST_GROUP_ID = 'test_send_unicast_group_id'


@pytest.mark.skip(reason='This test hangs indefinitely waiting for messsages on 1.')
def test_send_unicast() -> None:
    '''KafkaCommunicator talks on node 0, nodes 1 and 2 listen on their topics.'''
    known_neighbors: Set[NodeID] = set()
    distributed = DistributedConfig(clause={
        'communicator': {
            'name': 'kafka',
            'strategy': 'unicast',
            'kafka': {
                'bootstrap_servers': BOOTSTRAP_SERVERS.split(','),
                'topic_prefix': SEND_UNICAST_PREFIX,
            }
        },
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '0': [1, 2],
                    '1': [0, 2],
                    '2': [0, 1],
                }
            }
        },
        'my_id': 0,
    })

    print(f"DEBUG: test_send_unicast create listner1 on {SEND_UNICAST_PREFIX}1")
    listener1 = KafkaConsumer(
        f'{SEND_UNICAST_PREFIX}1',
        group_id=SEND_UNICAST_GROUP_ID,
        bootstrap_servers=BOOTSTRAP_SERVERS.split(','),
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )

    print(f"DEBUG: test_send_unicast create listner2 on {SEND_UNICAST_PREFIX}2")
    listener2 = KafkaConsumer(
        f'{SEND_UNICAST_PREFIX}2',
        group_id=SEND_UNICAST_GROUP_ID,
        bootstrap_servers=BOOTSTRAP_SERVERS.split(','),
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )

    print("DEBUG: test_send_unicast creating dut")
    dut = KafkaCommunicator(
        my_id=NodeID(0),
        known_neighbors=known_neighbors,
        distributed=distributed
    )
    queue: Queue = Queue()
    print("DEBUG: test_send_unicast starting dut")
    dut.start(queue=queue)
    print("DEBUG: test_send_unicast sending message")
    try:
        dut.send(dest_ids=[NodeID(1), NodeID(2)], payload=b'Hello World!')

        print("DEBUG: test_send_unicast waiting for messages on 1")
        # TODO(piggy): Figure out why the second next(listenern) is hanging.
        message1 = next(listener1)
        listener1.commit()
        assert message1.topic == f'{SEND_UNICAST_PREFIX}1'
        assert message1.key == b'1'
        assert message1.value == b'Hello World!'

        print("DEBUG: test_send_unicast waiting for messages on 2")
        message2 = next(listener2)
        listener2.commit()
        assert message2.topic == f'{SEND_UNICAST_PREFIX}2'
        assert message2.key == b'1'
        assert message2.value == b'Hello World!'

    finally:
        dut.stop()
        listener1.close()
        listener2.close()


THREE_NODE_PREFIX = topic_name('test_3_node_unicast')


# This test passes with kafka-python 2.0.4 but fails for 2.1.5.
@pytest.mark.skip(reason='This test fails with out of sync messages.')
def test_3_node_unicast() -> None:
    '''3 KafkaCommunicators on different nodes talk to and listen to each other.'''

    distributed: Dict[str, Any] = {
        'communicator': {
            'name': 'kafka',
            'kafka': {
                'bootstrap_servers': BOOTSTRAP_SERVERS.split(','),
                'topic_prefix': THREE_NODE_PREFIX,
            },
            'strategy': 'unicast',
        },
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '0': [1, 2],
                    '1': [0, 2],
                    '2': [0, 1],
                }
            }
        },
        'my_id': None,
    }

    known_neighbors: List[Set[NodeID]] = [set(), set(), set()]
    duts: List[Optional[KafkaCommunicator]] = [None, None, None]
    configs: List[Dict[str, Any]] = [{}, {}, {}]
    queues: List[Queue] = [Queue(), Queue(), Queue()]

    for i in range(3):
        configs[i] = deepcopy(distributed)
        configs[i]['my_id'] = i
        duts[i] = KafkaCommunicator(
            my_id=NodeID(i),
            known_neighbors=known_neighbors[i],
            distributed=DistributedConfig(clause=configs[i])
        )

    for i in range(3):
        dut = duts[i]
        assert dut is not None
        dut.start(queue=queues[i])

    try:
        payload0 = f'Hello, Node 1! {datetime.datetime.now()}'.encode()
        dut = duts[0]
        assert dut is not None
        dut.send(dest_ids=[NodeID(1)], payload=payload0)
        first_event = queues[1].get(block=True, timeout=LONG_QUEUE_TIMEOUT)
        assert isinstance(first_event, NewNeighbor)
        assert first_event.neighbor == NodeID(0)
        assert known_neighbors[1] == {NodeID(0)}

        second_event = queues[1].get(block=True, timeout=LONG_QUEUE_TIMEOUT)
        assert isinstance(second_event, Recv)
        assert second_event.neighbor == NodeID(0)
        assert second_event.payload == payload0

        payload1 = f'Hello nodes 2 and 0 {datetime.datetime.now()}'.encode()
        dut = duts[1]
        assert dut is not None
        dut.send(dest_ids=[NodeID(0), NodeID(2)], payload=payload1)

        for i in [0, 2]:
            first_event = queues[i].get(block=True, timeout=LONG_QUEUE_TIMEOUT)
            assert isinstance(first_event, NewNeighbor)
            assert first_event.neighbor == NodeID(1)
            assert known_neighbors[i] == {NodeID(1)}

            second_event = queues[i].get(block=True, timeout=LONG_QUEUE_TIMEOUT)
            assert isinstance(second_event, Recv)
            assert second_event.neighbor == NodeID(1)
            assert second_event.payload == payload1

    finally:
        for i in range(3):
            if duts[i] is not None:
                dut = duts[i]
                assert dut is not None
                dut.stop()
