'''Data loader for tests that ignores the data and returns an empty dataset.'''

from typing import Optional

from ..wrangler.dataset import Dataset

from .impl.dataframe_loader import DataframeLoader
from .impl.data_loader_catalog import DataLoaderCatalog

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


class IgnoreDataLoader(DataframeLoader):
    '''Data loader for tests that ignores the data and returns a None dataset.'''
    name = 'ignore'
    tags = {
        'input_format': ['ignore'],
        'loaded_format': ['ignore'],
    }

    def _load_train(self) -> Optional[Dataset]:
        return None

    def _load_test(self) -> Optional[Dataset]:
        return None

    def poll(self, timeout: Optional[float] = 0) -> Optional[Dataset]:
        return None


def register(catalog: DataLoaderCatalog):
    '''Register all the objects in this file.'''
    catalog.register(IgnoreDataLoader)
