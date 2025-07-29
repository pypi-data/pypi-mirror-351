""" Tests for memory_data_loader.py"""
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from copy import deepcopy
import pytest

import pandas as pd

from ..config_components.dataset_config import DatasetConfig
from ..config_components.impl.config_component import ConfigError
from ..wrangler.dataset import RoleName

from .memory_data_loader import MemoryDataLoader

# pylint: disable=missing-function-docstring,duplicate-code
# Note that we disable flake8 error F841 (# noqa F841)
# because we have a local variable which is used
# but which static analysis can't tell is used.


CLAUSE = {
    'config': 'memory',
    'column_roles': {
        'target': {
            'name': 'a',
            'pos_label': 1
        }
    },
    'params': {
        'train_data': 'train_df'
    }
}
TRAIN_DF = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})


def test_sunny_day():
    train_df = TRAIN_DF  # noqa F841 pylint: disable=unused-variable
    # this needs to be a local variable so the loader picks it up
    config = DatasetConfig(clause=CLAUSE)
    dut = MemoryDataLoader(config=config)
    result = dut.load_train()
    got_train_table = result.dataframe_table

    assert got_train_table.shape == (2, 2)
    assert RoleName.TARGET in result.metadata.roles.keys()
    assert len(result.metadata.roles[RoleName.TARGET]) == 1
    assert result.metadata.roles[RoleName.TARGET][0].name == 'a'


def test_no_target():
    '''Test that data with no target is acceptable'''
    train_df = TRAIN_DF  # noqa  F841 pylint: disable=unused-variable
    clause_without_target = CLAUSE.copy()
    del clause_without_target['column_roles']
    config = DatasetConfig(clause=clause_without_target)
    dut = MemoryDataLoader(config=config)

    assert dut.load_train().metadata.target is None


def test_load_testdata() -> None:
    train_df = TRAIN_DF  # noqa F841 pylint: disable=unused-variable
    load_test_df = pd.DataFrame(  # noqa F841 pylint: disable=unused-variable
        {'a': [1, 2, 2], 'b': [30, 40, 500]})
    clause = deepcopy(CLAUSE)
    assert isinstance(clause['params'], dict)
    clause['params']['test_data'] = 'load_test_df'
    config = DatasetConfig(clause=clause)
    dut = MemoryDataLoader(config=config)
    result = dut.load_test()

    assert result is not None   # needed to make pylint happy
    got_test_table = result.dataframe_table

    assert got_test_table.shape == (3, 1)
    assert 'a' not in got_test_table.columns
    assert 'b' in got_test_table.columns


def test_load_nonexistent_testdata() -> None:
    train_df = TRAIN_DF  # noqa F841 pylint: disable=unused-variable
    config = DatasetConfig(clause=CLAUSE)
    dut = MemoryDataLoader(config=config)
    result = dut.load_test()

    assert result is None


MEMORY_CONFIG = {
    "config": "memory",
    "column_roles": {
        "target": {
            "name": "c"
        }
    },
}


def test_missing_dataframe() -> None:
    config = DatasetConfig(clause=MEMORY_CONFIG)
    with pytest.raises(ConfigError, match=r'(memory.*train_data)|(train_data.*memory)/i'):
        MemoryDataLoader(config=config)
