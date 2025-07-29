'''A NeighborState subclass for testing purposes.'''
# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import List, Optional, Union

from .distributed_algorithm_instance import NeighborState


class ToyNeighborState(NeighborState):
    '''Test class for NeighborState.'''
    _center: float

    def __init__(self,
                 columns: Optional[List[Union[int, str]]] = None, center: float = 0.0) -> None:
        super().__init__(columns=columns)
        self._center = center

    @property
    def center(self) -> float:
        '''Get the center.'''
        return self._center

    def encode(self) -> bytes:
        '''Encode a message for distributed neighbors. '''
        return b'test neighbor state'

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'ToyNeighborState':
        '''Decode a message from distributed neighbors.

        This should just redirect to the relevant NeighborState subclass.
        '''
        return cls(center=0.0)

    def distance(self, other: NeighborState) -> float:
        '''Return the distance between two states.'''
        assert isinstance(other, ToyNeighborState)
        return abs(self.center - other.center)
