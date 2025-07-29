'''Unix Domain Connection endpoint representing host and port number.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any

from .endpoint import Endpoint


class UDEndpoint(Endpoint):
    '''Unix Domain Connection endpoint representing host and port number.'''
    _path: str

    def __init__(self, path: str):
        self._path = path

    def __str__(self) -> str:
        return f'({self._path})'

    def __repr__(self) -> str:
        return f'({self._path})'

    def __hash__(self) -> int:
        return self._path.__hash__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._path == other._path

    @property
    def path(self) -> str:
        '''Unix Domain Address of this endpoint.'''
        return self._path
