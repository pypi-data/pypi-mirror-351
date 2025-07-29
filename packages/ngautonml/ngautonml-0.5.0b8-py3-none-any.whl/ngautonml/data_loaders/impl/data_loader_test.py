""" Tests for data_loader.py"""
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Optional

import pandas as pd
import pytest

from ...config_components.dataset_config import DatasetConfig
from ...problem_def.problem_def import ProblemDefinition
from ...wrangler.dataset import Column, Dataset, DataType, RoleName, TaskType
from .data_loader import DataLoader

# Note that we disable flake8 error F841 (# noqa F841)
# because we have a local variable which is used
# but which static analysis can't tell is used.

# pylint: disable=redefined-outer-name, missing-function-docstring, duplicate-code


class FakeDataLoader(DataLoader):
    '''Fake Data Loader'''
    name: str = 'fake_data_loader'
    tags: Dict[str, List[str]] = {
        'input_format': ['fake_input_format'],
        'loaded_format': ['fake_loaded_format'],
    }

    def _load_train(self) -> Optional[Dataset]:
        return Dataset(metadata=self._metadata)

    def _load_test(self) -> Optional[Dataset]:
        return Dataset(metadata=self._metadata)

    def _load_ground_truth(self) -> Optional[Dataset]:
        return Dataset(metadata=self._metadata)

    def _dataset(self, data: Any, **kwargs) -> Dataset:
        return Dataset(metadata=self._metadata)

    def validate(self, dataset: Optional[Dataset]) -> None:
        pass

    def poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        return Dataset(metadata=self._metadata)

    def build_dataset_from_json(self, json_data: Dict) -> Dataset:
        return Dataset(metadata=self._metadata)


CLAUSE = {
    'dataset': {
        'config': 'fake_data_loader',
        'column_roles': {
            'target': {
                'name': 'a',
                'pos_label': 1
            }
        },
        'params': {
            'train_data': 'train_df'
        }
    },
    'problem_type': {
        'task': 'binary_classification'
    }
}


@pytest.fixture(scope='session')
def fake_data_loader() -> FakeDataLoader:
    pdef = ProblemDefinition(CLAUSE)
    train_df = pd.DataFrame()  # noqa: F841 pylint: disable=unused-variable
    dataset_config = pdef.get_conf(pdef.Keys.DATASET)
    assert isinstance(dataset_config, DatasetConfig)
    return FakeDataLoader(config=dataset_config)


def test_metadata_train(fake_data_loader: FakeDataLoader) -> None:
    got = fake_data_loader.load_train()
    assert got is not None
    assert got.metadata.roles == {RoleName.TARGET: [Column('a')]}
    assert got.metadata.pos_labels == {RoleName.TARGET: 1}
    assert got.metadata.task == TaskType.BINARY_CLASSIFICATION
    assert got.metadata.data_type == DataType.TABULAR


def test_metadata_test(fake_data_loader: FakeDataLoader) -> None:
    got = fake_data_loader.load_test()
    assert got is not None
    metadata = got.metadata
    assert metadata.roles == {RoleName.TARGET: [Column('a')]}
    assert metadata.pos_labels == {RoleName.TARGET: 1}
    assert metadata.task == TaskType.BINARY_CLASSIFICATION
    assert metadata.data_type == DataType.TABULAR
