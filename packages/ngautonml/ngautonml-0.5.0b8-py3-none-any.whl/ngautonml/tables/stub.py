'''A Stub Table.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Union

from .impl.table import TableWarehouse, Table
from .impl.table_catalog import TableCatalog


class StubType():
    '''A stub type.'''
    def __init__(self, token: str = 'stub'):
        self._token = token

    @property
    def token(self):
        '''Return the token.'''
        return self._token


class StubTable(Table):
    '''A Table representing a pandas Stub.'''
    name = 'stub'
    _value: StubType

    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table as a CSV string.'''
        return 'stub'

    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''
        return {'stub': StubType()}

    def drop(self, columns: List[Union[int, str]]) -> Table:
        '''Return a copy of this table with selected columns dropped.'''
        return self

    def drop_duplicates(self):
        '''Return a copy of this table with duplicates removed.'''
        return self

    @property
    def size(self) -> int:
        '''Return the size of the table in elements.'''
        return 0

    @property
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.'''
        return []

    @columns.setter
    def columns(self, value: List[Union[int, str]]):
        '''Set the column names of the table.'''
        _ = value

    @property
    def empty(self):
        '''Return True if the table is empty.'''
        return True

    def head(self, n: int) -> 'Table':
        '''Return the first n rows of the table.'''
        return self


def register(catalog: TableCatalog):
    '''Register the StubTable with the catalog.'''
    catalog.register(StubTable)
    TableWarehouse.register_constructor(StubType, StubTable)
    TableWarehouse.register_exporter(from_type=StubType, to_type=StubType, exporter=StubTable.value)
