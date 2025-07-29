'''A Table representing a None object.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from .impl.table import TableWarehouse, Table
from .impl.table_catalog import TableCatalog


class NoneTable(Table):
    '''A Table representing a None type.'''
    name = 'none'
    _value: None
    my_type = type(None)

    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table as a CSV string.'''
        raise NotImplementedError('Cannot convert None to CSV')

    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''
        return None  # type: ignore[return-value]

    def drop(self, columns: List[Union[int, str]]) -> Table:
        '''Return a copy of this table with selected columns dropped.'''
        return self

    def drop_duplicates(self):
        '''Return a copy of this table with duplicates removed.'''
        return self

    @property
    def empty(self) -> bool:
        '''Return True if the table is empty.'''
        return True

    @property
    def size(self) -> int:
        '''Return the size of the table in elements.'''
        return 0

    @property
    def shape(self) -> tuple:
        '''Get the shape of the table.'''
        return (0, 0)

    @property
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.'''
        return []

    @columns.setter
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names of the table.'''
        # TODO(Merritt/Piggy): We can get a sorted list of the current column names,
        # then iterate over the new column names and update the dictionary.
        raise NotImplementedError('Cannot set columns for a NoneTable')

    def head(self, n: int) -> 'Table':
        '''Return the first n rows of the table.'''
        _ = n
        return self


def as_dataframe(from_table: Table) -> pd.DataFrame:  # pylint: disable=useless-return
    '''Export a NoneTable to a pandas DataFrame.'''
    assert isinstance(from_table, NoneTable)
    return None  # type: ignore[return-value]


def as_numpy(from_table: Table) -> np.ndarray:  # pylint: disable=useless-return
    '''Export a NoneTable to a numpy array.'''
    assert isinstance(from_table, NoneTable)
    return None  # type: ignore[return-value]


def as_series(from_table: Table) -> pd.Series:  # pylint: disable=useless-return
    '''Export a NoneTable to a pandas Series.'''
    assert isinstance(from_table, NoneTable)
    return None  # type: ignore[return-value]


def register(catalog: TableCatalog):
    '''Register the NoneTable with the catalog.'''
    catalog.register(NoneTable)
    TableWarehouse.register_constructor(type(None), NoneTable)
    TableWarehouse.register_exporter(
        from_type=type(None), to_type=type(None), exporter=NoneTable.value)
    TableWarehouse.register_exporter(
        from_type=type(None), to_type=pd.DataFrame, exporter=as_dataframe)
    TableWarehouse.register_exporter(
        from_type=type(None), to_type=np.ndarray, exporter=as_numpy)
    TableWarehouse.register_exporter(
        from_type=type(None), to_type=pd.Series, exporter=as_series)
