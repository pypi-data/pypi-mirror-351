'''Sends and recieves messages using Kafka.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
import logging
from queue import Queue, Full
from typing import Any, Callable, Dict, List, Optional, Set

from aenum import Enum as AEnum  # type: ignore[import-untyped]
from kafka import (  # type: ignore[import-untyped,attr-defined]
    KafkaProducer, KafkaConsumer, KafkaAdminClient, KafkaClient)
from kafka.admin import NewTopic  # type: ignore[import-untyped]
from kafka.errors import TopicAlreadyExistsError  # type: ignore[import-untyped]


from ..config_components.distributed_config import DistributedConfig, CommunicatorConfig
from ..config_components.impl.config_component import ConfigComponent
from ..neighbor_manager.event import NewNeighbor, Recv
from ..neighbor_manager.node_id import NodeID
from ..wrangler.constants import Defaults
from ..wrangler.exception_thread import ExceptionThread
from ..wrangler.logger import Logger

from .impl.communicator import Communicator
from .impl.communicator_catalog import CommunicatorCatalog

log = Logger(__file__, level=logging.DEBUG, to_stdout=True).logger()


class KafkaConfig(ConfigComponent):
    '''Specifies Kafka configuration in a distributed AI setting.'''
    name = 'kafka'
    tags: Dict[str, Any] = {}
    _my_id: NodeID

    def __init__(self,
                 clause: Dict[str, Any],
                 name: Optional[str] = None,
                 my_id: NodeID = NodeID(0)) -> None:
        if name is None:
            name = self.name
        super().__init__(name=self.name, clause=clause)
        self._my_id = my_id

    class Constants(Enum):
        '''Keys below the top level.'''
        BOOTSTRAP_SERVERS = 'bootstrap_servers'
        TOPIC = 'topic'
        TOPIC_PREFIX = 'topic_prefix'

    class Keys(AEnum):
        '''Valid keys for the top level.'''
        BOOTSTRAP_SERVERS = 'bootstrap_servers'
        TOPIC = 'topic'

    class Defaults(Enum):
        '''Default values'''
        TOPIC_PREFIX = 'node_'

    def required_keys(self) -> Set[str]:
        return {
            self.Keys.BOOTSTRAP_SERVERS.value,  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
            self.Keys.TOPIC.value,  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        }

    @property
    def bootstrap_servers(self) -> List[str]:
        '''List of Kafka servers to connect to.'''
        return self._get(self.Keys.BOOTSTRAP_SERVERS)

    @property
    def topic(self) -> str:
        '''Topic to publish and subscribe to.'''
        return self._get(self.Keys.TOPIC)

    def node_topic(self, node_id: Optional[NodeID] = None) -> str:
        '''Topic for unicast communication.'''
        if node_id is None:
            node_id = self._my_id
        prefix = self._get_with_default(self.Constants.TOPIC_PREFIX,
                                        dflt=self.Defaults.TOPIC_PREFIX.value)
        return f'{prefix}{node_id}'


def _kafka_listener(queue: Queue,
                    stop: Callable[[], bool],
                    timeout: int,
                    known_neighbors: Set[NodeID],
                    consumer: KafkaConsumer,
                    my_id: NodeID) -> None:
    '''Listen for messages on a Kafka topic and put them in a queue.'''
    log.debug('Starting Kafka listener for %s', my_id)
    while True:
        try:
            if stop():
                consumer.close()
                return
            topics = consumer.poll(timeout_ms=timeout)
            consumer.commit()
            for messages in topics.values():
                for message in messages:
                    log.debug('Received message from %s:%s',
                              str(message.key)[:256], str(message.value)[:256])
                    payload = message.value
                    endpoint = int(message.key)
                    neighbor = NodeID(endpoint)
                    # We do not want to read our own messages.
                    if neighbor == my_id:
                        log.debug('Ignoring message from self')
                        continue
                    if neighbor not in known_neighbors:
                        log.debug('Adding new neighbor %s', neighbor)
                        known_neighbors.add(neighbor)
                        queue.put(NewNeighbor(neighbor=neighbor), timeout=timeout)
                    queue.put(Recv(neighbor, payload), timeout=timeout)
        except Full:
            # If the queue fills, drop messages.
            log.debug('Queue is full, dropping message')


class KafkaCommunicator(Communicator):
    '''Sends and recieves messages using Kafka.'''
    name: str = 'kafka'
    tags: Dict[str, List[str]] = {}
    _stop: bool
    _distributed: DistributedConfig
    _admin: Optional[KafkaAdminClient]
    _client: Optional[KafkaClient]
    _consumer: Optional[KafkaConsumer]
    _producer: Optional[KafkaProducer]
    _listener: Optional[ExceptionThread] = None

    def __init__(self,
                 known_neighbors: Set[NodeID],
                 my_id: NodeID,
                 distributed: DistributedConfig):
        self._stop = False
        self._admin = None
        self._client = None
        self._consumer = None
        self._producer = None
        self._distributed = distributed

        super().__init__(my_id=my_id, known_neighbors=known_neighbors, distributed=distributed)

    def stop(self):
        '''Tell threads to terminate themselves.'''
        if self._listener is not None:
            log.debug('Stopping KafkaCommunicator: %s', self._listener)
            self._stop = True
            self._listener.join()
            self._listener = None
        if self._admin is None:
            self._admin.close()
            self._admin = None
        if self._client is not None:
            self._client.close()
            self._client = None
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None
        if self._producer is not None:
            self._producer.close()
            self._producer = None

    def start(self,
              queue: Queue,
              timeout: float = Defaults.LISTENER_TIMEOUT) -> None:
        '''Start the communicator.'''
        self._client = KafkaClient(
            bootstrap_servers=self._distributed.communicator.kafka.bootstrap_servers  # type: ignore[attr-defined] # pylint: disable=line-too-long
        )
        self._admin = KafkaAdminClient(
            bootstrap_servers=self._distributed.communicator.kafka.bootstrap_servers  # type: ignore[attr-defined] # pylint: disable=line-too-long
        )
        if self._distributed.communicator.strategy == 'broadcast':
            topic = self._distributed.communicator.kafka.topic  # type: ignore[attr-defined]
        else:
            topic = self._distributed.communicator.kafka.node_topic(self._my_id)  # type: ignore[attr-defined] # pylint: disable=line-too-long
        self._consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self._distributed.communicator.kafka.bootstrap_servers,  # type: ignore[attr-defined] # pylint: disable=line-too-long
            client_id=str(self._my_id),
            group_id=str(self._my_id),
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
        # Create the topics if they do not exist.
        if self._distributed.communicator.strategy == 'broadcast':
            topics = [self._distributed.communicator.kafka.topic]  # type: ignore[attr-defined]
        elif self._distributed.communicator.strategy == 'unicast':
            topics = [self._distributed.communicator.kafka.node_topic(self._my_id)]  # type: ignore[attr-defined] # pylint: disable=line-too-long
            neighbors = self._distributed.get_static_adjacency(self._my_id)
            assert neighbors is not None, 'No neighbors found when creating kafka topics.'
            topics.extend(
                self._distributed.communicator.kafka.node_topic(neighbor)  # type: ignore[attr-defined] # pylint: disable=line-too-long
                for neighbor in neighbors
            )
        for topic in topics:
            log.info('creating topic = %s', topic)
            new_topic = NewTopic(
                name=topic,
                num_partitions=1,
                replication_factor=1)
            future = self._client.cluster.request_update()
            self._client.poll(future=future,
                              timeout_ms=int(1000 * self._distributed.polling_interval))
            # while topic not in metadata.topics():
            startup_counter = 0
            log.debug('Waiting for topic %s to be created', topic)
            while topic not in self._consumer.topics() and startup_counter < 10:
                startup_counter += 1
                try:
                    self._admin.create_topics([new_topic])
                    future = self._client.cluster.request_update()
                    self._client.poll(future=future,
                                      timeout_ms=int(1000 * self._distributed.polling_interval))
                except TopicAlreadyExistsError:
                    break
                    # log.debug('Topic %s already exists, continuing', new_topic)
            if topic not in self._consumer.topics():
                raise RuntimeError(
                    f'Kafka topic {topic} could not be created after 10 attempts.')
            log.debug('Kafka topic %s created', topic)

        self._producer = KafkaProducer(
            bootstrap_servers=self._distributed.communicator.kafka.bootstrap_servers,  # type: ignore[attr-defined] # pylint: disable=line-too-long
            client_id=str(self._my_id),
        )
        self._stop = False

        self._listener = ExceptionThread(target=_kafka_listener, kwargs={
            'queue': queue,
            'stop': lambda: self._stop,
            'timeout': timeout,
            'known_neighbors': self._known_neighbors,
            'consumer': self._consumer,
            'my_id': self._my_id,
        })
        self._listener.start()

    def send(self,
             dest_ids: List[NodeID],
             payload: bytes) -> int:
        '''Send a message to the nodes with the given dest_ids.

        Return value is the total size of the messages sent.
        '''
        assert self._producer is not None, 'Producer is not initialized'
        retval = 0
        # TODO(piggy): If the python API is ever extended to support multiple destinations,
        # we should use it instead of looping.
        for dest_id in dest_ids:
            topic = self._distributed.communicator.kafka.node_topic(dest_id)  # type: ignore[attr-defined] # pylint: disable=line-too-long
            log.debug('sending to dest_id = %s (%s)', dest_id, topic)
            self._producer.send(topic,
                                key=str(self._my_id).encode('utf-8'),
                                value=payload)
            retval += 1
        return retval

    def send_all(self, payload: bytes) -> int:
        '''Send a message to all known neighbors.

        Return value is normally a count of neighbors we sent to,
        but this implementation always returns 1 because we don't know.
        '''
        assert self._producer is not None, 'Producer is not initialized'
        if self._distributed.communicator.strategy == 'broadcast':
            log.debug('sending to all neighbors')
            self._producer.send(self._distributed.communicator.kafka.topic,  # type: ignore[attr-defined] # pylint: disable=line-too-long
                                key=str(self._my_id).encode('utf-8'),
                                value=payload)
        elif self._distributed.communicator.strategy == 'unicast':
            return self.send(dest_ids=list(self.known_neighbors), payload=payload)
        else:
            raise ValueError(
                f'Unknown communicator strategy: {self._distributed.communicator.strategy}')
        return 1


def register(catalog: CommunicatorCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(KafkaCommunicator)
    CommunicatorConfig.register(name='kafka', config_type=KafkaConfig)
