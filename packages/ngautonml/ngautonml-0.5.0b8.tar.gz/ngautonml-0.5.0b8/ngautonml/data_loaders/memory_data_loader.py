'''Loads an in-memory pandas DataFrame'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, Optional, List

import pandas as pd

from ..wrangler.dataset import Dataset
from ..config_components.dataset_config import DatasetConfig
from ..config_components.impl.config_component import (
    InvalidValueError, MissingKeyError)
from ..wrangler.dataset import TableFactory
from .impl.dataframe_loader import DataframeLoader
from .impl.data_loader_catalog import DataLoaderCatalog


class MemoryDataLoader(DataframeLoader):
    '''Loads an in-memory pandas DataFrame'''

    name: str = 'memory'
    tags: Dict[str, List[str]] = {
        'input_format': ['pandas_dataframe'],
        'loaded_format': ['pandas_dataframe'],
    }

    def __init__(self, config: DatasetConfig):
        if DatasetConfig.Keys.TRAIN_DATA.value not in config.params:  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
            # TODO(Merritt/Piggy): add test for this error state
            raise MissingKeyError(
                'Attempt to create a memory dataloader, but train_data is not provided.'
            )

        train_df_var_name = config.params[DatasetConfig.Keys.TRAIN_DATA.value]   # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        self._train_df = self._lookup_var(train_df_var_name)
        if not isinstance(self._train_df, pd.DataFrame):
            # TODO(Merritt/Piggy): add test for this error state
            raise InvalidValueError(
                f'Expecting local variable {train_df_var_name} to be '
                f'a pandas.DataFrame; instead found {type(self._train_df)}'
            )

        self._test_df = None
        if DatasetConfig.Keys.TEST_DATA.value in config.params:  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
            test_df_var_name = config.params[DatasetConfig.Keys.TEST_DATA.value]  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
            self._test_df = self._lookup_var(test_df_var_name)
            if not isinstance(self._test_df, pd.DataFrame):
                # TODO(Merritt/Piggy): add test for this error state
                raise InvalidValueError(
                    f'Expecting local variable {test_df_var_name} to be '
                    f'a pandas.DataFrame; instead found {type(self._test_df)}'
                )

        super().__init__(config=config)

    def _load_train(self) -> Dataset:
        retval = Dataset(metadata=self._metadata)
        retval.dataframe_table = TableFactory(self._train_df)
        # TODO(Piggy/Merritt): this is a hack for forecasting,
        # replace with something that can be used by both memory and local
        # to load additional data requested by a plugin
        retval['static_exogenous'] = None

        return retval

    def _load_test(self) -> Optional[Dataset]:
        if self._test_df is None:
            return None

        retval = Dataset(metadata=self._metadata)
        retval.dataframe_table = TableFactory(self._test_df)

        # TODO(Piggy/Merritt): this is a hack for forecasting,
        # replace with something that can be used by both memory and local
        # to load additional data requested by a plugin
        retval['static_exogenous'] = None

        return retval


def register(catalog: DataLoaderCatalog):
    '''Register all the objects in this file.'''
    catalog.register(MemoryDataLoader)
