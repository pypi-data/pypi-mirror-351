'''Object in charge of neighbor management for distributed algorithms.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from queue import Queue
from typing import Any, Dict, List, Optional, Set

import mlflow  # type: ignore

from ..discoverers.impl.discoverer import Discoverer, DiscovererStub
from .event import Event, Recv, NewNeighbor, NeighborTimeout
from .node_id import NodeID


class NeighborManager(metaclass=abc.ABCMeta):
    '''Object in charge of neighbor management for a distributed algorithm.

    It performs neighbor discovery, communication management, synchronization and logging.
    '''
    _default_timeout: Optional[float]
    _discoverer: Discoverer
    _queue: Queue
    name: str
    tags: Dict[str, Any]

    def __init__(self,
                 discoverer: Discoverer,
                 timeout: Optional[float] = None
                 ):
        self._discoverer = discoverer
        self._default_timeout = timeout
        self._queue = Queue()

    def stop(self) -> None:
        '''Stop all supporting threads.'''
        self._discoverer.stop()

    def start(self) -> None:
        '''Start all supporting threads.'''
        self._discoverer.start(queue=self._queue)

    @property
    def known_neighbors(self) -> Set[NodeID]:
        '''Return the set of known neighbors.'''
        return self._discoverer.communicator.known_neighbors

    def laplacian(self) -> List[List[int]]:
        '''Return the Laplacian of the network.'''
        return self._discoverer.laplacian()

    @abc.abstractmethod
    def synchronize(self) -> None:
        '''Synchronize with all peers.

        This function blocks until all neighbors have called synchonize.

        This is for starting tests at approximately the same time.
        '''

    def send_all(self, payload: bytes) -> None:
        '''Send a payload to all my neighbors, with logging.'''
        # I do not understand why, but this line appears to hang in
        # ngautonml/wrangler/distributed_wrangler_test.py::test_server_sunny_day.
        if mlflow.active_run() is not None:
            mlflow.log_metric(key='PayloadSize', value=len(payload))
        self._send_all(payload)

    @abc.abstractmethod
    def _send_all(self, payload: bytes) -> None:
        '''Send a payload to all my neighbors.

        The sending algorithm is responsible for creating the payload.
        '''

    def send(self, nodes: List[NodeID], payload: bytes) -> None:
        '''Send a paylod to a specific set of neighbors, with logging.'''
        mlflow.log_metric(key='PayloadSize', value=len(payload))
        self._send(nodes=nodes, payload=payload)

    @abc.abstractmethod
    def _send(self, nodes: List[NodeID], payload: bytes) -> None:
        '''Send a payload to a specific set of neighbors.'''

    def poll_for_events(self, timeout: Optional[float] = None) -> List[Event]:
        '''Check for any pending events, with logging.

        If timeout is not None, wait up to timeout for the next event to arrive.

        Events can be a payload arrives, a neighbor shows up or becomes unreachable,
        or other error conditions.
        '''

        retval = self._poll_for_events(timeout=timeout)
        for e in retval:
            if isinstance(e, Recv):
                mlflow.log_metric(key='RecvLen', value=len(e.payload))
                mlflow.log_metric(key='RecvNeighbor', value=e.neighbor)
            elif isinstance(e, NewNeighbor):
                mlflow.log_metric(key='NewNeighbor', value=e.neighbor)
            elif isinstance(e, NeighborTimeout):
                mlflow.log_metric(key='NeighborTimeout', value=e.neighbor)
            else:
                mlflow.log_metric(key='UnknownEvent', value=e.neighbor)
        return retval

    @abc.abstractmethod
    def _poll_for_events(self, timeout: Optional[float] = None) -> List[Event]:
        '''Check for any pending events.

        If timeout is not None, wait up to timeout for the next event to arrive.

        Events can be a payload arrives, a neighbor shows up or becomes unreachable,
        or other error conditions.
        '''


class NeighborManagerStub(NeighborManager):
    '''stub'''
    name = 'stub_neighbor_manager'
    tags: Dict[str, Any] = {}

    def __init__(self):
        super().__init__(discoverer=DiscovererStub())

    def synchronize(self) -> None:
        pass

    def _send_all(self, payload: bytes) -> None:
        pass

    def _send(self, nodes: List[NodeID], payload: bytes) -> None:
        pass

    def _poll_for_events(self, timeout: Optional[float] = None) -> List[Event]:
        return [Recv(neighbor=NodeID(1), payload=b'hello, world!')]
