'''Sends and recieves messages using UDP sockets.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
from queue import Queue
import socket
from typing import Callable, Dict, List, Optional, Set, Tuple

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..config_components.distributed_config import CommunicatorConfig, DistributedConfig
from ..config_components.impl.config_component import ConfigComponent
from ..neighbor_manager.event import NewNeighbor, Recv
from ..neighbor_manager.node_id import NodeID
from ..wrangler.exception_thread import ExceptionThread
from ..wrangler.logger import Level, Logger

from .impl.endpoint import Endpoint
from .impl.ip_endpoint import IPEndpoint
from .impl.communicator import Communicator
from .impl.communicator_catalog import CommunicatorCatalog

logger = Logger(__file__, level=Level.DEBUG).logger()


class SocketsConfig(ConfigComponent):
    '''Configuration for the SocketsCommunicator.'''
    name: str = 'sockets'
    tags: Dict[str, List[str]] = {}

    class Constants(Enum):
        '''Keys below the top level.'''

    class Keys(AEnum):
        '''Valid keys for the top level.'''
        NODES_AND_ENDPOINTS = 'nodes_and_endpoints'
        LISTENER_TIMEOUT = 'listener_timeout'

    class Defaults(Enum):
        '''Default values'''
        LISTENER_TIMEOUT = 2.0

    def required_keys(self) -> Set[str]:
        return set()

    @property
    def nodes_and_endpoints(self) -> List[Tuple[NodeID, Endpoint]]:
        '''Get a preconfigured relationship between nodes and endpoints.'''
        retval: List[Tuple[NodeID, Endpoint]] = []
        if not self._exists(
            self.Keys.NODES_AND_ENDPOINTS
        ):
            return retval
        for node, endpoint in self._get(
            self.Keys.NODES_AND_ENDPOINTS
        ):
            node_id = NodeID(int(node))
            # We only know how to build IP endpoints at the moment.
            ip, port = endpoint
            retval.append(
                (node_id, IPEndpoint(ip, int(port)))
            )
        return retval

    @property
    def listener_timeout(self) -> float:
        '''Get the listener timeout.'''
        return float(self._get_with_default(
            self.Keys.LISTENER_TIMEOUT,
            dflt=self.Defaults.LISTENER_TIMEOUT.value
        ))


def _socket_listener(queue: Queue,
                     sock: socket.socket,
                     assign_node_id: Callable[[IPEndpoint], NodeID],
                     stop: Callable[[], bool],
                     timeout: int,
                     known_neighbors: Set[NodeID]):

    while True:
        try:
            if stop():
                sock.close()
                return
            payload, addr = sock.recvfrom(65536)
            endpoint = IPEndpoint(host=addr[0], port=addr[1])
            neighbor = assign_node_id(endpoint)
            if neighbor not in known_neighbors:
                known_neighbors.add(neighbor)
                queue.put(NewNeighbor(neighbor=neighbor), timeout=timeout)
            queue.put(Recv(neighbor, payload), timeout=timeout)
        except socket.timeout:
            pass


class SocketsCommunicator(Communicator):
    '''Sends and recieves messages using UDP sockets.'''
    name: str = 'sockets'
    tags: Dict[str, List[str]] = {}
    _stop: bool
    _node_to_endpoint: Dict[NodeID, IPEndpoint]
    _endpoint_to_node: Dict[IPEndpoint, NodeID]
    _sock: Optional[socket.socket]
    _next_node_id: NodeID
    _listener: Optional[ExceptionThread] = None

    def __init__(self,
                 known_neighbors: Set[NodeID],
                 my_id: NodeID,
                 distributed: DistributedConfig):
        self._node_to_endpoint = {}
        self._endpoint_to_node = {}
        self._stop = False
        self._sock = None
        self._next_node_id = NodeID(1)
        for (node, endpoint) in distributed.communicator.sockets.nodes_and_endpoints:  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
            assert isinstance(endpoint, IPEndpoint), (
                f'BUG: endpoint={endpoint} is if type={type(endpoint)}, not IPEndpoint'
            )
            self._node_to_endpoint[node] = endpoint
            self._endpoint_to_node[endpoint] = node
            if node >= self._next_node_id:
                self._next_node_id = NodeID(node + 1)

        super().__init__(my_id=my_id, known_neighbors=known_neighbors, distributed=distributed)

    def stop(self):
        '''Tell threads to terminate themselves.'''
        if self._listener is not None:
            logger.debug('Stopping SocketsCommunicator: %s', self._listener)
            self._stop = True
            self._listener.join()
            self._listener = None

    def assign_node_id(self, endpoint: IPEndpoint) -> NodeID:
        '''Assign a node ID to the given endpoint (or find one that was already assigned).'''
        if endpoint not in self._endpoint_to_node:
            node = self._next_node_id
            self._next_node_id = NodeID(self._next_node_id + 1)
            self._endpoint_to_node[endpoint] = node
            self._node_to_endpoint[node] = endpoint
        if self._endpoint_to_node[endpoint] not in self._known_neighbors:
            logger.debug(
                'Node %s on port %s discovered neighbor node %s on port %s',
                self._my_id, self._node_to_endpoint[self._my_id],
                self._endpoint_to_node[endpoint], endpoint)
        return self._endpoint_to_node[endpoint]

    def lookup_endpoint(self, node: NodeID) -> IPEndpoint:
        '''Find the IPEndpoint that corresponds to the node.'''
        return self._node_to_endpoint[node]

    def start(self,
              queue: Queue,
              timeout: Optional[float] = None) -> None:
        '''Start the communicator.'''
        if timeout is None:
            timeout = self._distributed.communicator.sockets.listener_timeout  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        self._sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self._sock.settimeout(timeout)
        my_endpoint = self._node_to_endpoint[self._my_id]
        logger.debug('UDP SocketsCommunicator binding to %s:%s', my_endpoint.host, my_endpoint.port)
        try:
            self._sock.bind((my_endpoint.host, my_endpoint.port))
        except OSError as err:
            raise OSError(f'Error binding to {my_endpoint.host}:{my_endpoint.port}') from err
        self._stop = False
        self._listener = ExceptionThread(target=_socket_listener, kwargs={
            'queue': queue,
            'sock': self._sock,
            'assign_node_id': self.assign_node_id,
            'stop': lambda: self._stop,
            'timeout': timeout,
            'known_neighbors': self._known_neighbors,
        })
        self._listener.start()

    def send(self,
             dest_ids: List[NodeID],
             payload: bytes) -> int:
        '''Send a message to the node with dest_id.

        Return value is the size of the message sent.
        '''
        assert self._sock is not None, (
            'BUG: send() called before start().'
        )
        retval = 0
        for dest_id in dest_ids:
            dest_endpoint = self._node_to_endpoint[dest_id]
            logger.debug('UDP sockets sending to dest_id=%s, dest_endpoint=%s',
                         dest_id, dest_endpoint)
            try:
                retval += self._sock.sendto(payload, dest_endpoint.as_tuple)
                logger.log(Level.VERBOSE, 'payload size: %s', len(payload))
            # PermissionError can occur during shutdown. Just absorb it.
            except PermissionError as err:
                logger.error('%s: permission error sending payload: %s', err, len(payload))
            except OSError as err:
                logger.error('payload size too large to send: %s', len(payload))
                raise err

        return retval

    def send_all(self, payload: bytes) -> int:
        '''Send a message to all known neighbors.

        Return value is a count of neighbors we sent to.
        '''
        dest_ids = list(self._known_neighbors)
        logger.debug('UDP Socket sending to dest_ids = %s', dest_ids)
        self.send(dest_ids=dest_ids, payload=payload)
        return len(dest_ids)


def register(catalog: CommunicatorCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(SocketsCommunicator)
    CommunicatorConfig.register(name="sockets", config_type=SocketsConfig)
