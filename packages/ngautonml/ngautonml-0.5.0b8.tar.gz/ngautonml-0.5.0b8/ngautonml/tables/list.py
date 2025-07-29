'''A Table representing a dictionary from str to list-like.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from .impl.table import TableWarehouse, TableFactory, Table
from .impl.table_catalog import TableCatalog


class ListTable(Table):
    '''A Table representing a list of one element rows.'''
    name = 'list'
    _value: List
    my_type = list

    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table as a CSV string.'''
        return pd.DataFrame(self._value).to_csv(*args, **kwargs)

    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''
        return pd.DataFrame(self._value).to_dict(*args, **kwargs)

    def drop(self, columns: List[Union[int, str]]) -> Table:
        '''Return a copy of this table with selected columns dropped.'''
        if 0 in columns:
            return TableFactory([])
        return self

    def drop_duplicates(self):
        '''Return a copy of this table with duplicates removed.'''
        return TableFactory(self._value)

    @property
    def empty(self) -> bool:
        '''Return True if the table is empty.'''
        if len(self._value) == 0:
            return True
        return sum(len(row) for row in self._value) == 0

    @property
    def size(self) -> int:
        '''Return the size of the table in elements.'''
        return len(self._value)

    @property
    def shape(self) -> tuple:
        '''Get the shape of the table.'''
        return (len(self._value), 1)

    @property
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.'''
        return [int(c) for c in pd.DataFrame(self._value).columns]

    @columns.setter
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names of the table.'''
        raise NotImplementedError('Cannot set columns for a ListTable')

    def head(self, n: int) -> Table:
        '''Return the first n rows of the table.'''
        return TableFactory(self._value[:n])


def as_dataframe(from_table: Table) -> pd.DataFrame:
    '''Export a ListTable to a pandas DataFrame.'''
    assert isinstance(from_table, ListTable)
    return pd.DataFrame(from_table.value())


def as_numpy(from_table: Table) -> np.ndarray:
    '''Export a ListTable to a numpy array.'''
    df_table = as_dataframe(from_table)
    return df_table.to_numpy()


def as_series(from_table: Table) -> pd.Series:
    '''Export a ListTable to a pandas Series.'''
    assert isinstance(from_table, ListTable)
    return pd.Series(from_table.value())


def register(catalog: TableCatalog):
    '''Register the DataFrameTable with the catalog.'''
    catalog.register(ListTable)
    TableWarehouse.register_constructor(list, ListTable)
    TableWarehouse.register_exporter(
        from_type=list, to_type=list, exporter=ListTable.value)
    TableWarehouse.register_exporter(
        from_type=list, to_type=pd.DataFrame, exporter=as_dataframe)
    TableWarehouse.register_exporter(
        from_type=list, to_type=np.ndarray, exporter=as_numpy)
    TableWarehouse.register_exporter(
        from_type=list, to_type=pd.Series, exporter=as_series)
