'''A Table representing a numpy ndarray.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Union

from io import BytesIO

import numpy as np
import pandas as pd

from .impl.table import TableWarehouse, TableFactory, Table, TableValueError
from .impl.table_catalog import TableCatalog


class NumpyTable(Table):
    '''A Table representing a numpy ndarray.'''
    name = 'numpy'
    _value: np.ndarray
    my_type = np.ndarray

    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table as a CSV string.

        Extra parameters are passed to np.savetxt.
        '''
        # BUG: This is supposed to output to a file and return the path.
        # BUG: We do not emit column names, but numpy structured arrays (which have names)
        # are relatively niche.
        retval = BytesIO()
        np.savetxt(retval, self._value, *args, **kwargs)
        return retval.getvalue().decode()

    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''
        return {name: self._value[i].tolist() for i, name in enumerate(self.columns)}

    def drop(self, columns: List[Union[int, str]]) -> Table:
        '''Return a copy of this table with selected columns dropped.'''
        if isinstance(columns[0], str):
            columns = [self.columns.index(c) for c in columns]
        return TableFactory(self._value[:, [i for i in range(self._value.shape[1])
                                            if i not in columns]])

    def drop_duplicates(self) -> Table:
        '''Return a copy of this table with duplicates removed.'''
        return TableFactory(np.unique(self._value, axis=0))

    @property
    def empty(self) -> bool:
        '''Return True if the table is empty.

        For ndarrays, if any dimension is 0, it must be empty.
        '''
        return 0 in self._value.shape

    @property
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.'''
        if self._value.dtype.names is not None:
            return self._value.dtype.names
        return list(str(i) for i, _ in enumerate(self._value, 1))

    @columns.setter
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names of the table.'''
        raise TableValueError('Cannot set columns on a NumpyTable.')

    def head(self, n: int) -> Table:
        '''Return the first n rows of the table.'''
        return TableFactory(self._value[:n])


def as_dataframe(from_table: Table) -> pd.DataFrame:
    '''Export a NumpyTable to a pandas DataFrame.'''
    assert isinstance(from_table, NumpyTable)
    return pd.DataFrame(data=from_table.value())


def register(catalog: TableCatalog):
    '''Register the NumpyTable with the catalog.'''
    catalog.register(NumpyTable)
    TableWarehouse.register_constructor(NumpyTable.my_type, NumpyTable)
    TableWarehouse.register_exporter(
        from_type=np.ndarray, to_type=pd.DataFrame, exporter=as_dataframe)
    TableWarehouse.register_exporter(
        from_type=np.ndarray, to_type=np.ndarray, exporter=NumpyTable.value)
