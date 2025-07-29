'''Tests for linear_distributed_algorithm_instance.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=duplicate-code

import numpy as np

from ...config_components.distributed_config import DistributedConfig

from .linear_distributed_algorithm_instance import (
    LinearNeighborState)


class FakeLinearNeighborState(LinearNeighborState):
    '''Linear neighbor state that does not care about encode() and decode()'''

    def encode(self) -> bytes:
        '''Encode message for distributed neighbors.'''
        return b'fake message'

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'FakeLinearNeighborState':
        '''Decode a message from a neighbor.'''
        return FakeLinearNeighborState(np.array([1, 2, 3]))


def test_should_send() -> None:
    '''_should_send returns True iff our model changed.'''

    config = DistributedConfig({})
    dut = FakeLinearNeighborState(v=np.asarray([1.0, 2.0, 3.0]))
    same_as_dut = FakeLinearNeighborState(v=np.asarray([1.0, 2.0, 3.0]))
    different_from_dut = FakeLinearNeighborState(v=np.asarray([0.1, 0.2, 0.3]))

    assert dut.state_differs(
        distributed=config,
        other=different_from_dut
    ) is True

    assert dut.state_differs(
        distributed=config,
        other=same_as_dut
    ) is False
