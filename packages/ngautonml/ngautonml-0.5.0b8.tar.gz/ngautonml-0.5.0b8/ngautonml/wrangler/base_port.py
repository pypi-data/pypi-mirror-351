'''Generate port numbers for tests.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
import threading

import filelock

from .logger import Logger, Level

log = Logger(from_filename=__file__, to_filename=__file__, level=Level.VERBOSE).logger()

START_BASE_PORT = 49200
MAX_PORT = 65535
LOCK_FILE = '/var/lock/base_port.lock'
PORT_NUMBER = '/var/lock/base_port_port'


class BasePort():
    '''Generate unique port numbers for a test file.'''
    _base_port: int = START_BASE_PORT  # class property
    _base_port_inc: int = 100   # class property
    _lock_base_port: filelock.FileLock = filelock.FileLock(
        LOCK_FILE, thread_local=False)  # class property
    _lock_next_port: threading.Lock  # instance property
    _current_port: int  # instance property

    def __init__(self) -> None:
        with self._lock_base_port:
            self._current_port = self._next_base_port()
        self._lock_next_port = threading.Lock()

    @classmethod
    def _next_base_port(cls) -> int:
        if not os.path.exists(PORT_NUMBER):
            log.log(Level.VERBOSE, 'Creating port file at %s', PORT_NUMBER)
            with open(PORT_NUMBER, 'w', encoding='utf-8') as port_file:
                port_file.write(f'{START_BASE_PORT}\n')

        with open(PORT_NUMBER, 'r', encoding='utf-8') as port_file:
            line = port_file.readline()
            cls._base_port = int(line)
            if cls._base_port + cls._base_port_inc > MAX_PORT:
                log.log(Level.VERBOSE, "Resetting baseport")
                cls._base_port = START_BASE_PORT

        cls._base_port += cls._base_port_inc

        with open(PORT_NUMBER, 'w', encoding='utf-8') as port_file:
            port_file.write(f'{cls._base_port}\n')

        log.log(Level.VERBOSE, 'Creating base port on %s', cls._base_port)

        return cls._base_port

    def next(self) -> int:
        '''Return the next port number.'''
        with self._lock_next_port:
            retval = self._current_port
            log.log(Level.VERBOSE, 'next port: %s', retval)
            self._current_port += 1
        return retval
