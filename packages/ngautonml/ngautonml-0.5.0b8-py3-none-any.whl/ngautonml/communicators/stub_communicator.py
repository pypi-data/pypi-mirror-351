'''Communicator for tests where we don't communicate.'''

from queue import Queue
from typing import List, Optional, Set

from ..config_components.distributed_config import DistributedConfig
from ..neighbor_manager.node_id import NodeID
from ..wrangler.constants import Defaults

from .impl.communicator import Communicator
from .impl.communicator_catalog import CommunicatorCatalog


class CommunicatorStub(Communicator):
    '''Stub Communicator.'''
    name = 'stub_communicator'
    tags = {}

    def __init__(self,
                 distributed: Optional[DistributedConfig] = None,
                 known_neighbors: Optional[Set[NodeID]] = None,
                 my_id: Optional[NodeID] = None):
        node = my_id or NodeID(0)
        super().__init__(my_id=node,
                         known_neighbors=set(),
                         distributed=DistributedConfig(clause={}))

    def start(self,
              queue: Queue,
              timeout: float = Defaults.LISTENER_TIMEOUT
              ) -> None:
        pass

    def stop(self) -> None:
        pass

    def send(self,
             dest_ids: List[NodeID],
             payload: bytes) -> int:
        return 0

    def send_all(self, payload: bytes) -> int:
        return 0


def register(catalog: CommunicatorCatalog) -> None:
    '''Register all objects in this file.'''
    catalog.register(CommunicatorStub)
