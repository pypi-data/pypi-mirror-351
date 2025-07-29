'''Tests for data_loader_auto.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pandas as pd
import pytest

from ...config_components.dataset_config import DatasetConfig
from ...wrangler.constants import PACKAGE_NAME
from ..memory_data_loader import MemoryDataLoader
from .data_loader import DataLoader
from .data_loader_auto import DataLoaderCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code
# Note that we disable flake8 error F841 (# noqa F841)
# because we have a local variable which is used
# but which static analysis can't tell is used.


FAKE_DATA_LOADER_SOURCE = '''
from typing import Any, Dict, List, Optional
from ngautonml.wrangler.dataset import Dataset
from ngautonml.data_loaders.impl.data_loader import DataLoader
from ngautonml.data_loaders.impl.data_loader_catalog import DataLoaderCatalog

class FakeDataLoader(DataLoader):
    name = 'fake_data_loader'
    tags = {
        'input_format': ['some_input_format'],
        'loaded_format': ['some_loaded_format']
    }

    def _load_train(self) -> Dataset:
        return Dataset()

    def _load_test(self) -> Optional[Dataset]:
        return None

    def _load_ground_truth(self) -> Optional[Dataset]:
        return None

    def _dataset(self, data: Any, **kwargs) -> Dataset:
        return Dataset()

    def validate(self, dataset: Dataset) -> None:
        pass

    def poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        return Dataset()

    def build_dataset_from_json(self, json_data: Dict) -> Dataset:
        return Dataset()


def register(catalog: DataLoaderCatalog):
    catalog.register(FakeDataLoader)
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = (retval / f'.{PACKAGE_NAME}' / 'plugins'
                   / 'data_loaders' / 'fake_data_loader.py')
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_DATA_LOADER_SOURCE)
    return retval


def test_data_loader_catalog_auto() -> None:
    config = DatasetConfig(clause={
        'params': {
            'train_data': 'train_df'
        }
    })
    train_df = pd.DataFrame()  # noqa: F841 pylint: disable=unused-variable
    dut = DataLoaderCatalogAuto()

    got = dut.lookup_by_name('memory')(config=config)
    assert isinstance(got, MemoryDataLoader)


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)
    config = DatasetConfig(clause={
        'params': {
            'train_data': 'train_df'
        }
    })
    train_df = pd.DataFrame()  # noqa: F841 pylint: disable=unused-variable

    dut = DataLoaderCatalogAuto()
    got = dut.lookup_by_name('fake_data_loader')(config=config)
    assert isinstance(got, DataLoader)
    assert got.tags['input_format'] == ['some_input_format']


def test_lookup_by_formats() -> None:
    config = DatasetConfig(clause={
        'params': {
            'train_data': 'train_df'
        }
    })
    train_df = pd.DataFrame()  # noqa: F841 pylint: disable=unused-variable

    dut = DataLoaderCatalogAuto()
    got = dut.lookup_by_formats(input_format='pandas_dataframe', loaded_format='pandas_dataframe')
    assert any(isinstance(cons(config=config), MemoryDataLoader) for cons in got.values())


def test_construct_instance() -> None:
    config = DatasetConfig(clause={
        'config': 'memory',
        'params': {
            'train_data': 'train_df'
        }
    })
    train_df = pd.DataFrame()  # noqa: F841 pylint: disable=unused-variable

    dut = DataLoaderCatalogAuto()
    got = dut.construct_instance(config=config)
    assert isinstance(got, MemoryDataLoader)
