'''Tests for execption_thread.py.'''

import pytest
from .exception_thread import ExceptionThread


def test_sunny_day() -> None:
    '''Test the ExceptionThread class.'''

    class TestException(Exception):
        '''Test exception class.'''

    def raising_function(should_raise: bool = False):
        '''Conditionally raise an exception.'''
        if should_raise:
            raise TestException('This is a test exception.')

    et = ExceptionThread(target=raising_function, kwargs={'should_raise': True})
    et.start()
    with pytest.raises(TestException, match='This is a test exception'):
        et.join()

    et2 = ExceptionThread(target=raising_function, kwargs={'should_raise': False})
    et2.start()
    et2.join()
