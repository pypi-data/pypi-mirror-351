'''Provide threads that report exceptions back to the main thread.'''

from threading import Thread
from typing import Optional


class ExceptionThread(Thread):
    '''A thread that reports exceptions back to the main thread.'''
    _exc: Optional[BaseException] = None

    def run(self) -> None:
        try:
            super().run()
        except BaseException as e:  # pylint: disable=broad-exception-caught
            self._exc = e

    def join(self, timeout=None):
        super().join(timeout=timeout)
        if self._exc:
            raise self._exc
