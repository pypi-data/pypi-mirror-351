'''IP Connection endpoint representing host and port number.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Tuple

from .endpoint import Endpoint


class IPEndpoint(Endpoint):
    '''IP Connection endpoint representing host and port number.'''
    _host: str
    _port: int

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    def __str__(self) -> str:
        return f'({self._host}, {self._port})'

    def __repr__(self) -> str:
        return f'({self._host}, {self._port})'

    def __hash__(self) -> int:
        return self.as_tuple.__hash__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self._host == other._host
                and self._port == other._port)

    @property
    def host(self) -> str:
        '''IP Address of this endpoint.'''
        return self._host

    @property
    def port(self) -> int:
        '''Port number of this endpoint'''
        return self._port

    @property
    def as_tuple(self) -> Tuple[str, int]:
        '''(host, port) as a tuple'''
        return (self._host, self._port)
