'''Interface to metadata for a neighbor node.

This augments the NeighborState object.
'''
import abc
from typing import Any, Dict, Optional

from .neighbor_state_interface import NeighborStateInterface


class ForceFalse(Exception):
    '''Force the decider to return False.'''


class NeighborMetadataInterface(metaclass=abc.ABCMeta):
    '''Interface for metadata for a neighbor node.'''

    _current_state: Optional[NeighborStateInterface] = None
    _scratch: Dict[str, Any]

    def __init__(self, my_state: Optional[NeighborStateInterface] = None):
        '''Initialize the metadata.'''
        super().__init__()
        self._current_state = my_state
        self._scratch = {}

    @property
    def scratch(self) -> Dict[str, Any]:
        '''Get the scratch space.

        This is a dictionary that can be used by deciders to store
        data that persists from one call to the next.

        The recommendation is to add a subdictionary keyed by the
        name of the decider, which can contain whatever the decider
        needs. Values from other deciders should be considered
        read only.
        '''
        return self._scratch

    @property
    @abc.abstractmethod
    def current_state(self) -> Optional[NeighborStateInterface]:
        '''The current state of the neighbor.'''

    @current_state.setter
    @abc.abstractmethod
    def current_state(self, state: Optional[NeighborStateInterface]):
        '''Set the current state of the neighbor.'''

    @property
    @abc.abstractmethod
    def last_state(self) -> Optional[NeighborStateInterface]:
        '''The last state of the neighbor.'''

    @property
    @abc.abstractmethod
    def last_state_update_time(self) -> float:
        '''The time the neighbor was last updated.'''

    @property
    @abc.abstractmethod
    def time_since_last_state_update(self) -> float:
        '''The time since the neighbor was last updated.'''

    @property
    @abc.abstractmethod
    def last_state_sent(self) -> Optional[NeighborStateInterface]:
        '''The last state that was sent to the neighbor.'''

    @last_state_sent.setter
    @abc.abstractmethod
    def last_state_sent(self, state: Optional[NeighborStateInterface]):
        '''Set the last state that was sent to the neighbor.'''

    @abc.abstractmethod
    def sent_current_state(self):
        '''Mark the current state as sent.'''

    @property
    @abc.abstractmethod
    def last_state_sent_time(self) -> float:
        '''The time the last state was sent to the neighbor.'''

    @property
    @abc.abstractmethod
    def time_since_last_state_sent(self) -> float:
        '''The time since the last state was sent to the neighbor.'''

    @property
    @abc.abstractmethod
    def cumulative_payload_sent(self) -> int:
        '''The total payload sent to the neighbor.'''
