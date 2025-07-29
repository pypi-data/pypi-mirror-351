'''Subset of NeighborState needed by deciders.'''

import abc
from typing import Generic, List, Optional, TypeVar, Union

from ...config_components.distributed_config import DistributedConfig


NeighborStateSubclass = TypeVar('NeighborStateSubclass', bound='NeighborStateInterface')


class NeighborStateInterface(abc.ABC, Generic[NeighborStateSubclass]):
    '''Subset of NeighborState needed by deciders.'''
    @property
    @abc.abstractmethod
    def columns(self) -> Optional[List[Union[int, str]]]:
        '''The column names.'''

    @columns.setter
    @abc.abstractmethod
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names.'''

    @abc.abstractmethod
    def state_differs(self,
                      distributed: DistributedConfig,
                      other: Optional[NeighborStateSubclass]) -> bool:
        '''Decide if our state differs meaningfully from another.

        :distributed: contains information from the problem definition, including fit_eps
        :other: is an instance of type(self) or None. It is often the last state we sent.
        '''

    @abc.abstractmethod
    def distance(self, other: NeighborStateSubclass) -> float:
        '''A numerical measure of the distance between this state and another.'''

    @property
    @abc.abstractmethod
    def payload_size(self) -> int:
        '''The size of the payload to send this state.'''

    @abc.abstractmethod
    def encode(self) -> bytes:
        '''Encode a message for distributed neighbors. '''

    @classmethod
    @abc.abstractmethod
    def decode(cls, serialized_model: bytes) -> NeighborStateSubclass:
        '''Decode a message from distributed neighbors.

        This should just redirect to the relevant NeighborState subclass.
        '''
