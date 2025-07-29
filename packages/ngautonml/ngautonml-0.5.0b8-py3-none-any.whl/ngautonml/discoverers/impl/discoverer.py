'''Base class for neighbor discoverers'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from queue import Queue
from typing import Dict, List

from ...config_components.distributed_config import DistributedConfig
from ...communicators.impl.communicator import Communicator
from ...communicators.stub_communicator import CommunicatorStub


class Discoverer(metaclass=abc.ABCMeta):
    '''Base class for neighbor discoverers'''
    name: str
    tags: Dict[str, List[str]]
    _config: DistributedConfig
    _communicator: Communicator

    def __init__(self,
                 config: DistributedConfig,
                 communicator: Communicator,
                 ):
        self._config = config
        self._communicator = communicator

    @property
    def communicator(self) -> Communicator:
        '''Object that listens for inbound messages'''
        return self._communicator

    @abc.abstractmethod
    def laplacian(self) -> List[List[int]]:
        '''Return the Laplacian of the network.'''

    @abc.abstractmethod
    def start(self, queue: Queue) -> None:
        '''Start up the discover.

        The queue is our link to the NeighborManager.
        '''

    def stop(self) -> None:
        '''Stop all supporting threads.'''
        # The default implementation only stops communicator threads.
        self._communicator.stop()


class DiscovererStub(Discoverer):
    '''Stub Discoverer'''
    name = 'stub_discoverer'
    tags = {}

    def __init__(self):
        super().__init__(
            config=DistributedConfig({}),
            communicator=CommunicatorStub())

    def start(self, queue: Queue) -> None:
        pass

    def laplacian(self) -> List[List[int]]:
        return []
