'''Tests for local_data_loader.py'''
from pathlib import Path
from typing import Any, Dict, Optional

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..config_components.dataset_config import DatasetConfig
from ..problem_def.problem_def import ProblemDefinition
from ..problem_def.task import TaskType
from ..tables.impl.table_auto import TableCatalogAuto
from ..tables.dataframe import DataFrameTable
from ..wrangler.dataset import RoleName
from .local_data_loader import LocalDataLoader
_ = TableCatalogAuto()  # pylint: disable=pointless-statement


# pylint: disable=missing-function-docstring,duplicate-code


def valid_data_path(filename: Optional[str] = None) -> str:
    '''Returns a path (in the form of a string) to a valid csv file.'''
    module_parent = Path(__file__).parents[2]
    if filename is None:
        filename = 'credit.csv'
    path = module_parent / 'examples' / 'classification' / filename
    return str(path)


def make_dataset(train_path: str) -> Dict[str, Any]:
    retval = {
        'config': 'local',
        'train_path': train_path,
        'column_roles': {
            'target': {
                'name': 'class',
                'pos_label': 'good'
            }
        },
    }
    return retval


def test_load_simple_dataset() -> None:
    clause = make_dataset(valid_data_path())
    config = DatasetConfig(clause=clause)
    dut = LocalDataLoader(config=config)
    result = dut.load_train()

    assert result is not None
    traint_table = result.dataframe_table
    assert traint_table.shape == (1000, 21)
    assert traint_table.columns[0] == 'checking_status'
    assert traint_table.columns[20] == 'class'


def test_no_target() -> None:
    clause = {
        'config': 'local',
        'train_path': valid_data_path(),
        'column_roles': {
            'index': {
                'id': 0
            }
        }
    }
    config = DatasetConfig(clause=clause)
    dut = LocalDataLoader(config=config)
    dataset = dut.load_train()
    assert dataset is not None
    assert dataset.metadata.target is None


def test_arff() -> None:
    clause = {
        'config': 'local',
        'train_path': valid_data_path(filename='dataset_31_credit-g.arff'),
        'column_roles': {
            'target': {
                'name': 'class'
            }
        }
    }
    config = DatasetConfig(clause=clause)
    dut = LocalDataLoader(config=config)
    got = dut.load_train()
    assert got is not None
    target = got.metadata.target
    assert target is not None
    assert 'class' == target.name

    assert got.dataframe_table is not None

    train_table = got.dataframe_table
    assert isinstance(train_table, DataFrameTable)
    assert train_table.shape == (1000, 21)


def test_load_test() -> None:
    clause = {
        'config': 'simple',
        'train_path': valid_data_path(filename='credit-train.csv'),
        'test_path': valid_data_path(filename='credit-test.csv'),
        'column_roles': {
            'target': {
                'name': 'class'
            }
        },
    }
    config = DatasetConfig(clause=clause)
    dut = LocalDataLoader(config=config)
    result = dut.load_test()
    assert result is not None
    test_table = result.dataframe_table
    assert test_table.shape == (200, 20)
    assert 'class' not in test_table.columns
    assert 'own_telephone' in test_table.columns


def test_load_nonexistent_testdata() -> None:
    '''If there is no test data, load_test() returns None'''
    clause = make_dataset(valid_data_path())
    config = DatasetConfig(clause=clause)
    dut = LocalDataLoader(config=config)
    result = dut.load_test()
    assert result is None


CLASSIFICATION_TASK_CLAUSE = {
    'problem_type': {
        'task': 'binary_classification'
    },
    'dataset': {
        'config': 'ignore'
    }
}


def test_task_in_metadata_with_load_train() -> None:
    clause = make_dataset(valid_data_path())
    problem_def_for_task = ProblemDefinition(CLASSIFICATION_TASK_CLAUSE)
    config = DatasetConfig(clause=clause, problem_def=problem_def_for_task)
    dut = LocalDataLoader(config=config)
    result = dut.load_train()

    assert result is not None
    assert result.metadata.task == TaskType.BINARY_CLASSIFICATION


def test_task_in_metadata_with_load_test() -> None:
    clause = {
        'config': 'local',
        'train_path': valid_data_path(filename='credit-train.csv'),
        'test_path': valid_data_path(filename='credit-test.csv'),
        'column_roles': {
            'target': {
                'name': 'class'
            }
        },
    }
    problem_def_for_task = ProblemDefinition(CLASSIFICATION_TASK_CLAUSE)
    config = DatasetConfig(clause=clause, problem_def=problem_def_for_task)
    dut = LocalDataLoader(config=config)
    result = dut.load_test()

    assert result is not None
    assert result.metadata.task == TaskType.BINARY_CLASSIFICATION


def test_load_arbitrary_csv() -> None:
    clause = make_dataset(valid_data_path(filename='credit-train.csv'))
    config = DatasetConfig(clause=clause)
    dut = LocalDataLoader(config=config)

    got = dut.ez_dataset(data=valid_data_path(filename='credit-test.csv'),
                         cols=['class', 'own_telephone'])
    assert got.dataframe_table.shape == (200, 2)
    assert set(got.dataframe_table.columns) == {'class', 'own_telephone'}
    assert got.metadata.roles[RoleName.TARGET][0].name == 'class'
