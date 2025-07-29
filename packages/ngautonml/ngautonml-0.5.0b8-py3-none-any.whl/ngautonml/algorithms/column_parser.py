'''
A model that takes a dataset and parses its columns
by data type (int, float, string, datetime)

Currently only parses object columns into categorical.
'''
# pylint: disable=duplicate-code
from typing import Optional
import pandas as pd

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..catalog.catalog import upcast
from ..tables.impl.table import TableFactory
from ..wrangler.dataset import Dataset, RoleName


class ColumnParserInstance(AlgorithmInstance):
    '''Parses columns of dataset by data type'''

    def __init__(self, parent: Algorithm):
        super().__init__(parent=parent)

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        '''Parses columns of dataset by data type'''
        if dataset is None:
            return None

        retval = dataset.output()

        data = dataset.dataframe_table.as_(pd.DataFrame)

        if RoleName.TIME in dataset.metadata.roles:
            assert len(dataset.metadata.roles[RoleName.TIME]) == 1, (
                'BUG: dataset must have exactly 1 time column in roles metadata.')
            time_col_name = dataset.metadata.roles[RoleName.TIME][0].name
            assert time_col_name is not None, (
                'BUG: time column in roles metadata must have name'
            )
            if str(time_col_name) in data.columns:
                # Note: time column also gets parsed in forecasting_splitter.py
                # TODO(Merritt): remove this redundancy once it is no longer needed
                data[time_col_name] = pd.to_datetime(data[time_col_name])

        object_cols_df = data.select_dtypes(['object'])
        data[object_cols_df.columns] = object_cols_df.apply(
            lambda x: x.astype('category'))
        retval.dataframe_table = TableFactory(data)
        return retval


class ColumnParser(Algorithm):
    '''Parses columns of dataset by data type'''
    _name: str = 'Column Parser'
    _instance_constructor: type = ColumnParserInstance
    _tags = {
        'source': ['auton_lab'],
        'preprocessor': ['true'],
    }


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = ColumnParser(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
