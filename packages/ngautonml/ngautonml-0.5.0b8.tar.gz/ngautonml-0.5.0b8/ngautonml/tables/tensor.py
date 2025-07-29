'''A Table representing a pandas DataFrame.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
import tensorflow as tf

from .impl.table import TableValueError, TableWarehouse, Table, TableFactory
from .impl.table_catalog import TableCatalog


class TensorTable(Table):
    '''A Table representing a pandas DataFrame.'''
    name = 'tensor'
    _value: tf.Tensor
    my_type = tf.Tensor

    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table as a CSV string to a path and return that path.'''
        return pd.DataFrame(self._value.numpy()).to_csv(*args, **kwargs)

    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''
        npv = self._value.numpy()
        return {name: npv[i].tolist() for i, name in enumerate(self.columns)}

    def drop(self, columns: List[Union[int, str]]) -> Table:
        '''Return a copy of this table with selected columns dropped.'''
        idx = []
        for i, col in enumerate(self.columns):
            if i not in columns and col not in columns:
                idx.append(i)
        return TableFactory(tf.gather(self._value, idx, axis=1))

    def drop_duplicates(self) -> Table:
        '''Return a copy of this table with duplicates removed.'''
        unique_rows, _ = tf.raw_ops.UniqueV2(x=self._value, axis=[0])
        return TableFactory(unique_rows)

    @property
    def empty(self) -> bool:
        '''Return True if the table is empty.'''
        return tf.size(self._value) == 0

    @property
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.'''
        num_cols = self._value.shape[1]
        if num_cols is None or num_cols == 0:
            return []
        return list(str(i) for i in range(num_cols))

    @columns.setter
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names of the table.'''
        raise TableValueError('Cannot set columns on a TensorTable.')

    def head(self, n: int) -> Table:
        return TableFactory(self._value[:n])


def as_numpy(from_table: Table) -> np.ndarray:
    '''Export a DataFrameTable to a numpy array.'''
    assert isinstance(from_table, TensorTable)
    if from_table.shape[1] == 1:
        return from_table.value().numpy().flatten()
    return from_table.value().numpy()


def as_dataframe(from_table: Table) -> pd.DataFrame:
    '''Export a NumpyTable to a pandas DataFrame.'''
    assert isinstance(from_table, TensorTable)
    return pd.DataFrame(data=from_table.value())


def as_series(from_table: Table) -> pd.Series:
    '''Export a DataFrameTable to a pandas Series.'''
    assert isinstance(from_table, TensorTable)
    return pd.Series(from_table.value()[0])


def register(catalog: TableCatalog):
    '''Register the DataFrameTable with the catalog.'''
    catalog.register(TensorTable)
    TableWarehouse.register_constructor(tf.Tensor, TensorTable)
    TableWarehouse.register_exporter(
        from_type=tf.Tensor, to_type=tf.Tensor, exporter=TensorTable.value)
    TableWarehouse.register_exporter(
        from_type=tf.Tensor, to_type=np.ndarray, exporter=as_numpy)
    TableWarehouse.register_exporter(
        from_type=tf.Tensor, to_type=pd.Series, exporter=as_series)
    TableWarehouse.register_exporter(
        from_type=tf.Tensor, to_type=pd.DataFrame, exporter=as_dataframe)
