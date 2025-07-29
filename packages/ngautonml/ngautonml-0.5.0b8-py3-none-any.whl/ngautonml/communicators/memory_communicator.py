'''Sends and recieves messages using queues in memory.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from collections import defaultdict
from enum import Enum
from queue import Queue
from typing import Any, Dict, List, Optional, Set

from aenum import Enum as AEnum  # type: ignore[import-untyped]


from ..config_components.impl.config_component import ConfigComponent
from ..config_components.distributed_config import CommunicatorConfig, DistributedConfig
from ..neighbor_manager.event import NewNeighbor, Recv
from ..neighbor_manager.node_id import NodeID
from ..wrangler.constants import Defaults
from ..wrangler.logger import Level, Logger

from .impl.communicator import Communicator
from .impl.communicator_catalog import CommunicatorCatalog

logger = Logger(__file__, level=Level.INFO).logger()


class MemoryConfig(ConfigComponent):
    '''Specifies Memory configuration in a distributed AI setting.'''
    name = 'memory'
    tags: Dict[str, Any] = {}
    _my_id: NodeID

    def __init__(self, clause: Dict[str, Any], my_id: NodeID, name: Optional[str] = None) -> None:
        super().__init__(clause)
        if name is not None:
            self.name = name
        self._my_id = my_id

    class Constants(Enum):
        '''Keys below the top level.'''

    class Keys(AEnum):
        '''Valid keys for the top level.'''
        DOMAIN = 'domain'

    class Defaults(Enum):
        '''Default values'''

    def required_keys(self) -> Set[str]:
        return {
            self.Keys.DOMAIN.value,  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        }

    @property
    def domain(self) -> str:
        '''Communication Domain for memory.

        All nodes in the same network need to pick the same domain.
        '''
        return self._get(self.Keys.DOMAIN)


class MemoryCommunicator(Communicator):
    '''Sends and recieves messages using UDP memory.'''
    name: str = 'memory'
    tags: Dict[str, List[str]] = {}

    # Class variables
    # Neighbors should introduce themselves to us before communicating.
    # First key is domain, second key is node ID.
    _introductions: Dict[str, Dict[NodeID, Set[NodeID]]] = defaultdict(dict)
    # These are the queues that the receiving nodes will listen to.
    # First key is domain, second key is node ID.
    _queues: Dict[str, Dict[NodeID, Queue]] = defaultdict(dict)

    _domain: str = 'default'
    _timeout: Optional[float] = None

    def __init__(self,
                 known_neighbors: Set[NodeID],
                 my_id: NodeID,
                 distributed: DistributedConfig):
        super().__init__(my_id=my_id, known_neighbors=known_neighbors, distributed=distributed)
        self._domain = self._distributed.communicator.memory.domain  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        self._introductions[self._domain][self._my_id] = known_neighbors

    def stop(self):
        '''Purge our queue.'''
        del self._queues[self._domain][self._my_id]
        if not self._queues[self._domain]:
            del self._queues[self._domain]
        self._timeout = None

    def start(self,
              queue: Queue,
              timeout: float = Defaults.LISTENER_TIMEOUT) -> None:
        '''Start the communicator.'''
        self._timeout = timeout
        self._queues[self._domain][self._my_id] = queue

    def send(self,
             dest_ids: List[NodeID],
             payload: bytes) -> int:
        '''Send a message to the nodes in dest_ids.

        Return value is the size of the messages sent.
        '''
        retval = 0
        assert self._timeout is not None, 'Communicator not started'
        for dest_id in dest_ids:
            try:
                d_queue = self._queues[self._domain][dest_id]
                d_introductions = self._introductions[self._domain][dest_id]
            except KeyError:
                logger.error('Unknown destination ID: %s. Has desination been started?', dest_id)
                continue
            retval += len(payload)
            if self._my_id not in d_introductions:
                d_introductions.add(self._my_id)
                d_queue.put(NewNeighbor(neighbor=self._my_id), timeout=self._timeout)
            d_queue.put(Recv(self._my_id, payload), timeout=self._timeout)

        return retval

    def send_all(self, payload: bytes) -> int:
        '''Send a message to all started neighbors.

        Return value is a count of neighbors we sent to.
        '''
        dest_ids = [dest_id
                    for dest_id in self._queues[self._domain].keys()
                    if dest_id != self._my_id]
        self.send(dest_ids=dest_ids, payload=payload)
        return len(dest_ids)


def register(catalog: CommunicatorCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(MemoryCommunicator)
    CommunicatorConfig.register(name="memory", config_type=MemoryConfig)
