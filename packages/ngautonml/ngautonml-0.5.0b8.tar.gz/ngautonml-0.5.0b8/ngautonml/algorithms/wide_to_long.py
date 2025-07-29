'''A model that transforms time series forecasting data from wide format to long format.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional
import pandas as pd

from ..algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..catalog.catalog import upcast
from ..wrangler.dataset import Column, Dataset, RoleName, TableFactory


class WideToLongModelInstance(AlgorithmInstance):
    '''A model that transforms time series forecasting data from wide format to long format.'''

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        '''Transform time series dataset from wide to long format.'''
        if dataset is None:
            return None

        input_roles = dataset.metadata.roles

        # Ensure the dataset has exactly 1 time column and at least 1 target column.
        assert RoleName.TIME in input_roles, (
            'BUG: input to WideToLongModel has no time column. \n'
            f'Roles: {input_roles}'
        )
        assert 1 == len(input_roles[RoleName.TIME]), (
            'BUG: input to WideToLongModel must have exactly 1 time column. '
            f'Roles: {input_roles}'
        )
        assert RoleName.TARGET in input_roles, (
            'BUG: input to WideToLongModel has no target column. \n'
            f'Roles: {input_roles}'
        )

        # If dataset is already in long format, return a copy of it.
        if RoleName.TIMESERIES_ID in input_roles:

            assert len(input_roles[RoleName.TIMESERIES_ID]) == 1, (
                'BUG: dataset has more than 1 grouping key. \n'
                f'Roles: {input_roles}'
            )
            assert len(input_roles[RoleName.TARGET]) == 1, (
                'BUG: dataset has a grouping key but multiple targets. \n'
                f'Roles: {input_roles}'
            )
            copy_dataset = dataset.output()
            copy_dataset.dataframe_table = dataset.dataframe_table
            return copy_dataset

        if RoleName.PAST_EXOGENOUS in input_roles or RoleName.FUTURE_EXOGENOUS in input_roles:
            raise NotImplementedError(
                'Cannot transform dataset from wide to long format with exogenous variables. \n'
                f'Roles: {input_roles}')

        olddf = dataset.get_dataframe()
        newdf = pd.melt(
            olddf,
            id_vars=[str(col.name) for col in dataset.roles[RoleName.TIME]],
            var_name='unique_id',
            value_name='y'
        )

        roles = dataset.metadata.roles.copy()
        roles.update({
            RoleName.TIMESERIES_ID: [Column('unique_id')],
            RoleName.TARGET: [Column('y')]
        })

        new_dataset = dataset.output(
            override_metadata=dataset.metadata.override_roles(roles=roles)
        )
        new_dataset.dataframe_table = TableFactory(newdf)
        return new_dataset


class WideToLongModel(Algorithm):
    '''A model that transforms time series forecasting data from wide format to long format.

    If input data is already long, it will return output as input.

    Wide format means multiple time series are in different columns, such as:
    time   ts1     ts2
    1      1.1     2.1
    2      1.2     2.2
    3      1.3     2.3

    Long format means multiple time series are in the same column,
    distinguished by a grouping key.  An example:
    time   key     value
    1      ts1     1.1
    2      ts1     1.2
    3      ts1     1.3
    1      ts2     2.1
    2      ts2     2.2
    3      ts3     2.3
    '''
    _name = 'wide_to_long'
    _instance_constructor = WideToLongModelInstance
    _tags = {
        'source': ['pandas'],
        'preprocessor': ['true'],
    }


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = WideToLongModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
