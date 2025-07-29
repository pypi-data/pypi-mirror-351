'''Tests for neighbor_metadata.py'''

import time

import pytest

from .toy_neighbor_state import ToyNeighborState

from .neighbor_metadata import NeighborMetadata


ANCIENT_DURATION = 100.0  # seconds since the start of the monotonic clock.
SHORT_SLEEP = 0.1  # seconds


def test_neighbor_metadata():
    '''Test the NeighborMetadata class.'''
    metadata = NeighborMetadata()

    # We start out with reasonable defaults.
    assert metadata.current_state is None
    assert metadata.last_state is None
    assert metadata.last_state_sent is None
    assert metadata.cumulative_payload_sent == 0
    # Times have not been updated and are initialized to 0.0.
    assert metadata.time_since_last_state_update > ANCIENT_DURATION
    assert metadata.time_since_last_state_sent > ANCIENT_DURATION

    state = ToyNeighborState(['a', 'b'], 0.0)
    new_state = ToyNeighborState(['a', 'b'], 1.0)

    # Does the current state migrate to the last state?
    metadata.current_state = state
    assert metadata.current_state == state
    assert metadata.last_state is None

    # Does setting the last state send time update the time?
    metadata.last_state_sent = state
    assert metadata.cumulative_payload_sent == state.payload_size
    assert metadata.last_state_sent == state
    duration1 = metadata.time_since_last_state_sent
    assert duration1 == pytest.approx(0.0, abs=0.01)  # BUG: This might be a source of flakiness.
    time.sleep(SHORT_SLEEP)
    duration2 = metadata.time_since_last_state_sent
    assert duration2 > duration1

    # Can we set the current state to None?
    metadata.current_state = None
    assert metadata.last_state == state
    assert metadata.current_state is None
    duration3 = metadata.time_since_last_state_update
    # BUG: This might be a source of flakiness. Set abs higher if this flakes.
    assert duration3 == pytest.approx(0.0, abs=0.01)
    # Can we set the last state sent to None?
    metadata.last_state_sent = None
    assert metadata.last_state_sent is None
    duration4 = metadata.time_since_last_state_sent
    assert duration4 == pytest.approx(0.0, abs=0.01)  # BUG: This might be a source of flakiness.
    assert metadata.cumulative_payload_sent == state.payload_size

    # Can we set the current state to a new state?
    metadata.current_state = state
    metadata.last_state_sent = state
    assert metadata.last_state is None
    assert metadata.current_state == state
    assert metadata.cumulative_payload_sent == 2 * state.payload_size

    # Let's send a different state.
    metadata.current_state = new_state
    metadata.last_state_sent = new_state
    assert metadata.last_state_sent == new_state
    assert metadata.cumulative_payload_sent == 2 * state.payload_size + new_state.payload_size


def test_scratch():
    '''Test the scratchpad.'''
    metadata = NeighborMetadata()
    assert len(metadata.scratch) == 0
    metadata.scratch['a'] = 1
    assert metadata.scratch['a'] == 1
