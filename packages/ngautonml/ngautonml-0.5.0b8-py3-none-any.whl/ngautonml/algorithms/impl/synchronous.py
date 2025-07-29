'''Utility functions for managing DistributedAlgorithm synchronous mode.'''
# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import time
from typing import Optional, Sequence

from .distributed_algorithm_instance import DistributedAlgorithmInstance


class NotSynchronousError(Exception):
    '''The method is not available in asynchronous mode.'''


def fit_now(duts: Sequence[DistributedAlgorithmInstance]) -> None:
    '''Fit the models now.

    This is a convenience function to fit all the models in a list of DistributedAlgorithmInstances.
    '''
    for d in duts:
        if not d.synchronous:
            raise NotSynchronousError(
                f'Node {d.my_id} (algorithm {d.catalog_name}) is attempted synchronous fit_now,'
                ' but is not running synchronously.')
        d.fit_now()


def read_from_neighbors(duts: Sequence[DistributedAlgorithmInstance],
                        min_time: int = 100_000_000,
                        timeout_ns: Optional[int] = None) -> None:
    '''Wait for pending messages from neighbors to be processed.

    We wait for at least min_time nanoseconds (default 0.1 sec), and at most
    timeout_ns nanoseconds. If timeout_ns is None (default), we wait indefinitely.
    '''
    _ = timeout_ns  # BUG: We need to extend the Communicator API to support this.
    time.sleep(min_time / 1_000_000_000)  # Allow for propagation delay.
    for d in duts:
        # BUG: We could theoretically wait len(duts) * timeout_ns, but we expect
        # that messages should mostly get processed during the first delay and
        # that subsequent calls will be much faster.
        if not d.synchronous:
            raise NotSynchronousError(
                f'Node {d.my_id} (algorithm {d.catalog_name}) is attempted synchronous read,'
                ' but is not running synchronously.')
        d.read_from_neighbors()


def advance(duts: Sequence[DistributedAlgorithmInstance],
            min_time: int = 100_000_000,
            timeout_ns: Optional[int] = None) -> None:
    '''Advance the models by one step.

    This is a convenience function to advance all the models in a list of
    DistributedAlgorithmInstances.
    '''
    read_from_neighbors(duts=duts, min_time=min_time, timeout_ns=timeout_ns)
    fit_now(duts=duts)
