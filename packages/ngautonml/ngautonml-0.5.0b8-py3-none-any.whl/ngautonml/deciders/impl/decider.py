'''Object that listens for inbound messages and sends outbound messages'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.
import abc
from typing import Dict, List, Mapping, Optional

from ...algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ...config_components.distributed_config import DeciderConfig
from ...neighbor_manager.node_id import NodeID


class Decider(metaclass=abc.ABCMeta):
    '''Object that decides if we should send our state to a neighbor.'''
    name: str
    tags: Dict[str, List[str]]
    _config: Optional[DeciderConfig] = None

    # All subclasses must implement this __init__ signature.
    # When we get something from a catalog we don't otherwise know what
    # arguments it needs.
    def __init__(self,
                 name: Optional[str] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 config: Optional[DeciderConfig] = None
                 ) -> None:
        self._config = config
        self.name = name if name is not None else self.name
        self.tags = tags if tags is not None else self.tags

    @abc.abstractmethod
    def decide(self, my_meta: NeighborMetadataInterface,
               neighbor_id: NodeID, neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> bool:
        '''Decide if we should send to neighbor.'''
