'''Metadata for a neighbor node.

This augments the NeighborState object.
'''

from copy import deepcopy
import time
from typing import Optional

from .neighbor_metadata_interface import NeighborMetadataInterface
from .neighbor_state_interface import NeighborStateInterface


class NeighborMetadata(NeighborMetadataInterface):
    '''Metadata for a neighbor node.'''

    def __init__(self, my_state: Optional[NeighborStateInterface] = None):
        '''Initialize the metadata.'''
        super().__init__()
        self._current_state = my_state

    _current_state: Optional[NeighborStateInterface] = None
    _last_state: Optional[NeighborStateInterface] = None
    _last_state_sent: Optional[NeighborStateInterface] = None

    _last_state_update_time: float = 0.0
    _last_state_sent_time: float = 0.0

    _cumulative_payload_sent: int = 0

    @property
    def current_state(self) -> Optional[NeighborStateInterface]:
        '''The current state of the neighbor.'''
        return self._current_state

    @current_state.setter
    def current_state(self, state: Optional[NeighborStateInterface]):
        '''Set the current state of the neighbor.'''
        self._last_state = self._current_state
        self._last_state_update_time = time.monotonic()
        self._current_state = state

    @property
    def last_state(self) -> Optional[NeighborStateInterface]:
        '''The last state of the neighbor.'''
        return self._last_state

    @property
    def last_state_update_time(self) -> float:
        '''The time the neighbor was last updated.'''
        return self._last_state_update_time

    @property
    def time_since_last_state_update(self) -> float:
        '''The time since the neighbor was last updated.'''
        return time.monotonic() - self._last_state_update_time

    @property
    def last_state_sent(self) -> Optional[NeighborStateInterface]:
        '''The last state that was sent to the neighbor.'''
        return self._last_state_sent

    @last_state_sent.setter
    def last_state_sent(self, state: Optional[NeighborStateInterface]):
        '''Set the last state that was sent to the neighbor.'''
        self._last_state_sent_time = time.monotonic()
        if state is not None:
            self._cumulative_payload_sent += state.payload_size
        self._last_state_sent = deepcopy(state)

    def sent_current_state(self):
        '''Mark the current state as sent.'''
        self.last_state_sent = self.current_state

    @property
    def last_state_sent_time(self) -> float:
        '''The time the last state was sent to any neighbor.'''
        return self._last_state_sent_time

    @property
    def time_since_last_state_sent(self) -> float:
        '''The time since the last state was sent to any neighbor.'''
        return time.monotonic() - self._last_state_sent_time

    @property
    def cumulative_payload_sent(self) -> int:
        '''The total payload sent to the neighbor.'''
        return self._cumulative_payload_sent
