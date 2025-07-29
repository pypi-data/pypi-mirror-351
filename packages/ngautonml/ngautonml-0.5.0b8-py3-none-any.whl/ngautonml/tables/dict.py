'''A Table representing a dictionary from str to list-like.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import statistics
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from .impl.table import TableWarehouse, TableFactory, Table
from .impl.table_catalog import TableCatalog


class DictTable(Table):
    '''A Table representing a dictionary from str to list-like.'''
    name = 'dict'
    _value: Dict[Union[str, int], List]
    my_type = dict

    def __getitem__(self, key: Union[List[Union[int, str]], int, str]) -> Any:
        if isinstance(key, list):
            return {k: self._value[k] for k in key}
        return self._value[key]

    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table to a path and return that path.'''
        return pd.DataFrame(self._value).to_csv(*args, **kwargs)

    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''
        return self._value

    def mean(self, *args, **kwargs) -> 'Table':
        '''Return a table containing the column-wise means of this table.'''
        retval = {k: [statistics.mean(v)] for k, v in self._value.items()}
        return TableFactory(retval)

    def sum(self, *args, **kwargs) -> 'Table':
        '''Return a table containing the column-wise sums of this table.'''
        retval = {k: [sum(v)] for k, v in self._value.items()}
        return TableFactory(retval)

    def drop(self, columns: List[Union[int, str]]) -> Table:
        '''Return a copy of this table with selected columns dropped.'''
        return TableFactory(
            {k: v for k, v in self._value.items()
             if k not in columns})

    def drop_duplicates(self):
        '''Return a copy of this table with duplicates removed.'''
        return TableFactory(np.unique(as_numpy(self), axis=0))

    @property
    def empty(self) -> bool:
        '''Return True if the table is empty.'''
        return len(self._value) == 0 or all(
            len(v) == 0 for v in self._value.values()
        )

    def head(self, n: int) -> 'Table':
        '''Return the first n rows of the table.'''
        return TableFactory({k: v[:n] for k, v in self._value.items()})

    @property
    def size(self) -> int:
        '''Return the size of the table in elements.'''
        return sum(len(v) for v in self._value.values())

    @property
    def shape(self) -> tuple:
        '''Get the shape of the table.'''
        try:
            return (len(next(iter(self._value.values()))), len(self.columns))
        except StopIteration:
            return (0, len(self.columns))

    @property
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.'''
        return sorted(list(self._value.keys()))

    @columns.setter
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names of the table.'''
        if len(value) != len(self._value):
            raise ValueError(
                'Cannot set columns to a different length than the table.'
                f'trying to set {len(self._value)} columns but dataset has {len(value)} columns.'
            )
        self._value = {new_col: self._value[old_col]
                       for old_col, new_col in zip(self.columns, value)}


def as_dataframe(from_table: Table) -> pd.DataFrame:
    '''Export a DictTable to a pandas DataFrame.'''
    assert isinstance(from_table, DictTable)
    retval = pd.DataFrame(from_table.value())
    # Make sure columns are in a predictable order.
    return retval.reindex(from_table.columns, axis=1)


def as_numpy(from_table: Table) -> np.ndarray:
    '''Export a DictTable to a numpy array.'''
    df_table = as_dataframe(from_table)
    if df_table.shape[1] == 1:
        return df_table.to_numpy().flatten()
    return df_table.to_numpy()


def as_series(from_table: Table) -> pd.Series:
    '''Export a DictTable to a pandas Series.'''
    assert isinstance(from_table, DictTable)
    assert len(from_table.columns) in {0, 1}, (
        'Cannot convert a DictTable with more than one column to a Series.'
    )
    if len(from_table.columns) == 0:
        return pd.Series()
    return pd.Series(next(iter(from_table.value().values())), name=from_table.columns[0])


def register(catalog: TableCatalog):
    '''Register the DataFrameTable with the catalog.'''
    catalog.register(DictTable)
    TableWarehouse.register_constructor(dict, DictTable)
    TableWarehouse.register_exporter(
        from_type=dict, to_type=dict, exporter=DictTable.value)
    TableWarehouse.register_exporter(
        from_type=dict, to_type=pd.DataFrame, exporter=as_dataframe)
    TableWarehouse.register_exporter(
        from_type=dict, to_type=np.ndarray, exporter=as_numpy)
    TableWarehouse.register_exporter(
        from_type=dict, to_type=pd.Series, exporter=as_series)
