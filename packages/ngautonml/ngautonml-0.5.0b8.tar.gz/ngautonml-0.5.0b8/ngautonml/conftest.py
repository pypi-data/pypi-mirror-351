'''File defining global pytest fixtures.'''
import time
from typing import Iterable

import pytest

from .algorithms.impl.distributed_algorithm_instance import DistributedAlgorithmInstance
from .wrangler.logger import Level, Logger

log = Logger(__file__, to_stdout=False, level=Level.DEBUG).logger()


class Waiter():
    '''Wait until every distributed instance has been fit at least once, and none are locked.

    Also return if max_time has passed.

    Returns False if timed out, True if everything converged.

    Wait at least min_time.

    Convergence threshold is the min number of times we considered fitting
        on a unchanged state in order to be considered "converged".

    Only used by distributed algorithms.
    '''

    def _stop(self,
              models: Iterable[DistributedAlgorithmInstance],
              convergence_check: bool,
              pending_message_check: bool) -> bool:

        log.debug('CHECKING STOP CONDITON')

        models_copy = list(models)

        if not models_copy:
            log.debug('NO MODELS TO CHECK')

        locked = [m.locked for m in models_copy]
        trained = [m.trained for m in models_copy]
        converged = [m.converged for m in models_copy]
        pending_messages = [m._pending_message_from_neighbor for m in models_copy]  # pylint: disable=protected-access

        log.debug('locked models: %s', locked)
        log.debug('trained models: %s', trained)
        log.debug('pending message: %s', pending_messages)
        log.debug('converged: %s', converged)

        retval = (not any(locked)) and all(trained)
        if convergence_check:
            # We are specifically dropping locked as a check for convergence.
            # This allows for deciders that keep sending even after everybody has converged.
            retval = all(trained) and all(converged)

        if pending_message_check:
            retval = retval and not any(pending_messages)

        if retval:
            log.debug('STOP CONDITION MET')

        return retval

    def __call__(self,
                 models: Iterable[DistributedAlgorithmInstance],
                 interval: float = 0.5,
                 max_time: float = 20.0,
                 min_time: float = 0.5,
                 convergence_check: bool = False,
                 pending_message_check: bool = False) -> bool:
        log.log(Level.VERBOSE, 'STARTING WAITER')

        start = time.monotonic()

        time.sleep(min_time)

        log.log(Level.VERBOSE, 'ABOUT TO START LOOP')

        models_copy = list(models)

        while not self._stop(models_copy, convergence_check, pending_message_check):

            elapsed = time.monotonic() - start
            if elapsed > max_time:
                log.warning('Waiter timed out.')
                return False
            time.sleep(interval)

        return True


@pytest.fixture(scope='session')
def wait_til_all_fit() -> Waiter:
    '''Serves up a waiting function.

    Only used by distributed algorithms.
    '''
    return Waiter()


# TODO(Merritt): Clearer takes *args instead of a list
class Clearer():
    '''Asserts that there are no exceptions left in the exception queue for any model.

    If there are any left, provides a helpful error message.

    Only used by distributed algorithms.
    '''

    def __call__(
        self,
        models: Iterable[DistributedAlgorithmInstance]
    ) -> None:

        found = ''
        for model in models:
            next_exc = model.poll_exceptions()
            while next_exc is not None:
                found += f'{next_exc}'
                next_exc = model.poll_exceptions()
        assert found == ''  # There should be no additional exceptions


@pytest.fixture(scope='session')
def assert_no_exceptions() -> Clearer:
    '''Asserts that there are no elements left in the exception queue.

    If there are any left, provides a helpful error message.

    Only used by distributed algorithms.
    '''
    return Clearer()
