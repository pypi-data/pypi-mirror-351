'''Object that listens for inbound messages and sends outbound messages'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.
import abc
from queue import Queue
from typing import Dict, List, Set

from ...config_components.distributed_config import DistributedConfig
from ...neighbor_manager.node_id import NodeID
from ...wrangler.constants import Defaults


class Communicator(metaclass=abc.ABCMeta):
    '''Object that listens for inbound messages and sends outbound messages'''
    name: str
    tags: Dict[str, List[str]]
    _known_neighbors: Set[NodeID]
    _my_id: NodeID
    _distributed: DistributedConfig

    # All subclasses must implement this __init__ signature.
    # When we get something from a catalog we don't otherwise know what
    # arguments it needs.
    def __init__(self,
                 my_id: NodeID,
                 known_neighbors: Set[NodeID],
                 distributed: DistributedConfig
                 ):
        self._my_id = my_id
        self._known_neighbors = known_neighbors
        self._distributed = distributed

    @abc.abstractmethod
    def start(self,
              queue: Queue,
              timeout: float = Defaults.LISTENER_TIMEOUT
              ) -> None:
        '''Start listening.'''

    @abc.abstractmethod
    def stop(self) -> None:
        '''Stop the listener'''

    @abc.abstractmethod
    def send(self,
             dest_ids: List[NodeID],
             payload: bytes) -> int:
        '''Send a message to the nodes with the given dest_ids.

        Return value is the size of the message sent.
        '''

    @abc.abstractmethod
    def send_all(self, payload: bytes) -> int:
        '''Send a message to all known neighbors.

        Return value is a count of neighbors we sent to.
        '''

    @property
    def known_neighbors(self) -> Set[NodeID]:
        '''Provide a modifiable set of neighbor NodeIDs.

        This is how the communicator tells the discoverer
        about new neighbors.
        '''
        return self._known_neighbors

    @property
    def my_id(self) -> NodeID:
        '''What do I think my own ID is?'''
        return self._my_id
