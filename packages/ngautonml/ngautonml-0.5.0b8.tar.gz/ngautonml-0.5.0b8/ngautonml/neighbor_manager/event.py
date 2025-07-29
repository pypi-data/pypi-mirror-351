'''Events that a NeighborManager can report.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


from typing import Any

from .node_id import NodeID


class Event():
    '''Base class NeighborManager events.'''
    _neighbor: NodeID

    def __init__(self, neighbor: NodeID):
        self._neighbor = neighbor

    @property
    def neighbor(self):
        '''The relevant neighbor originating the event.'''
        return self._neighbor

    def __str__(self) -> str:
        return f'Event {self.__class__.__name__} from {self.neighbor}'

    def __repr__(self) -> str:
        return f'<Event {self.__class__.__name__} from {self.neighbor}>'


class Recv(Event):
    '''A received payload from a neighbor.'''
    _payload: bytes

    def __init__(self, neighbor: NodeID, payload: bytes):
        super().__init__(neighbor)
        self._payload = payload

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Recv):
            return self.neighbor == other.neighbor and self.payload == other.payload
        return False

    @property
    def payload(self) -> bytes:
        '''The inbound payload.'''
        return self._payload


class NewNeighbor(Event):
    '''A new neighbor has arrived.'''


class NeighborTimeout(Event):
    '''A neighbor has not been seen in a while.'''
