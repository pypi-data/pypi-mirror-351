'''A Table representing a pandas DataFrame.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from .impl.table import TableWarehouse, Table, TableFactory
from .impl.table_catalog import TableCatalog


class DataFrameTable(Table):
    '''A Table representing a pandas DataFrame.'''
    name = 'dataframe'
    _value: pd.DataFrame
    my_type = pd.DataFrame

    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table as a CSV string to a path and return that path.'''
        return self._value.to_csv(*args, **kwargs)

    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''
        return self._value.to_dict(*args, **kwargs)

    def drop(self, columns: List[Union[int, str]]) -> Table:
        '''Return a copy of this table with selected columns dropped.'''
        return TableFactory(self._value.drop(columns, axis=1))

    def drop_duplicates(self) -> Table:
        '''Return a copy of this table with duplicates removed.'''
        return TableFactory(self._value.drop_duplicates())

    @property
    def empty(self) -> bool:
        '''Return True if the table is empty.'''
        return self._value.empty

    @property
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.'''
        return list(self._value.columns)

    @columns.setter
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names of the table.'''
        self._value.columns = pd.Index(value)

    def sort_columns(self):
        '''Sort the columns of the table, returning a new Table.'''
        retval_df = self._value.sort_index(axis=1)
        return TableFactory(retval_df)

    def head(self, n: int) -> Table:
        return TableFactory(self._value.head(n))


def as_numpy(from_table: Table) -> np.ndarray:
    '''Export a DataFrameTable to a numpy array.'''
    assert isinstance(from_table, DataFrameTable)
    if from_table.shape[1] == 1:
        return from_table.value().to_numpy().flatten()
    return from_table.value().to_numpy()


def as_series(from_table: Table) -> pd.Series:
    '''Export a DataFrameTable to a pandas Series.'''
    assert isinstance(from_table, DataFrameTable)
    return from_table.value().iloc[:, 0]


def register(catalog: TableCatalog):
    '''Register the DataFrameTable with the catalog.'''
    catalog.register(DataFrameTable)
    TableWarehouse.register_constructor(pd.DataFrame, DataFrameTable)
    TableWarehouse.register_exporter(
        from_type=pd.DataFrame, to_type=pd.DataFrame, exporter=DataFrameTable.value)
    TableWarehouse.register_exporter(
        from_type=pd.DataFrame, to_type=np.ndarray, exporter=as_numpy)
    TableWarehouse.register_exporter(
        from_type=pd.DataFrame, to_type=pd.Series, exporter=as_series)
