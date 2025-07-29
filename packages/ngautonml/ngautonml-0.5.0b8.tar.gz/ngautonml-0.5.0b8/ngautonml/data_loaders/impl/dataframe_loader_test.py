""" Tests for dataframe_loader.py"""
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring, missing-class-docstring, duplicate-code

import copy
from typing import Dict, List, Optional, Union

import pandas as pd
import pytest

from ...config_components.dataset_config import DatasetConfig
from ...config_components.impl.config_component import ValidationErrors
from ...problem_def.problem_def import ProblemDefinition
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.constants import JSONKeys
from ...wrangler.dataset import ColumnError, Dataset, RoleName, TableFactory
from .dataframe_loader import DataframeLoader
_ = TableCatalogAuto()  # pylint: disable=pointless-statement


CLAUSE = {
    'column_roles': {
        'target': {
            'name': 'a',
            'pos_label': 1
        }
    }
}


class FakeDataframeLoader(DataframeLoader):
    _train_df: Optional[pd.DataFrame] = None
    _test_df: Optional[pd.DataFrame] = None

    def __init__(self,
                 train_df: Optional[pd.DataFrame] = None,
                 test_df: Optional[pd.DataFrame] = None,
                 **kwargs):
        self._train_df = train_df
        self._test_df = test_df
        super().__init__(**kwargs)

    def _load_train(self) -> Dataset:
        if self._train_df is not None:
            return Dataset(dataframe=self._train_df)

        train_table = TableFactory({
            'a': [1, 2],
            'b': [3, 4],
            'c': [5, 6],
            'd': [7, 8]})
        retval = Dataset()
        retval.dataframe_table = train_table
        return retval

    def _load_test(self) -> Optional[Dataset]:
        if self._test_df is None:
            return self._load_train()
        retval = Dataset()
        retval.dataframe_table = TableFactory(self._test_df)
        return retval

    def _poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        return Dataset(dataframe=self._train_df)


def test_attribute_role_default() -> None:
    config = DatasetConfig(clause=CLAUSE)
    dut = FakeDataframeLoader(config=config)
    dataset = dut.load_train()
    assert dataset is not None
    result = dataset.metadata.roles[RoleName.ATTRIBUTE]

    assert {n.name for n in result} == {'b', 'c', 'd'}


def test_no_target() -> None:
    '''Test that data with no target is acceptable'''
    clause_without_target = CLAUSE.copy()
    del clause_without_target['column_roles']
    config = DatasetConfig(clause=clause_without_target)
    dut = FakeDataframeLoader(config=config)

    dataset = dut.load_train()
    assert dataset is not None
    assert dataset.metadata.target is None


def test_validate_missing_col() -> None:
    '''Check for missing columns.

    If a role references a column that doesn't exist in the data,
    we want to throw a ValidationError.'''
    missing_col_clause = copy.deepcopy(CLAUSE)
    missing_col_clause['column_roles']['attribute'] = {
        'name': 'nonexistent_col'
    }
    config = DatasetConfig(clause=missing_col_clause)
    with pytest.raises(ValidationErrors, match='nonexistent_col'):
        FakeDataframeLoader(config=config)


def test_dataset_cols() -> None:
    config = DatasetConfig(clause=CLAUSE)
    dut = FakeDataframeLoader(config=config)
    got = dut.ez_dataset(
        pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        }),
        cols=['a']
    )

    want = pd.DataFrame({
        'a': [1, 2, 3]
    })

    pd.testing.assert_frame_equal(want, got.dataframe_table.as_(pd.DataFrame))


def test_dataset_roles() -> None:
    dut = FakeDataframeLoader(
        config=DatasetConfig({
            'column_roles': {
                'target': {'name': 'a'},
                'test_role': {'name': 'b'},
                'attribute': {'name': 'c'},
            }
        })
    )
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9],
        'd': [10, 11, 12]
    })
    got1 = dut.ez_dataset(data=df, roles=[RoleName.TARGET])
    want1 = pd.DataFrame({
        'a': [1, 2, 3]})
    pd.testing.assert_frame_equal(got1.dataframe_table.as_(pd.DataFrame), want1)

    got2 = dut.ez_dataset(data=df, roles=['attribute', RoleName.TEST_ROLE])
    want2 = pd.DataFrame({
        'b': [4, 5, 6],
        'c': [7, 8, 9],
        'd': [10, 11, 12],
    })
    pd.testing.assert_frame_equal(got2.dataframe_table.as_(pd.DataFrame), want2)


def test_dataset_roles_cols() -> None:
    dut = FakeDataframeLoader(
        config=DatasetConfig(clause={
            'column_roles': {
                'target': {'name': 'a'},
                'attribute': {'name': 'c'},
                'test_role': {'name': 'd'},
            }
        })
    )
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9],
        'd': [10, 12, 13]  # ROFL
    })
    got = dut.ez_dataset(data=df, roles=['target'], cols=['c'])
    want = pd.DataFrame({
        'a': [1, 2, 3],
        'c': [7, 8, 9]
    })
    pd.testing.assert_frame_equal(got.dataframe_table.as_(pd.DataFrame), want)


def test_missing_columns() -> None:
    '''Because column d is present in the data but not assigned a role,
    it automatically gets assigned the attribute role.

    When we ask for a subset of the dataset containing all columns with
    the attribute role, we will try to select d, and we expect to raise an
    error because it is not present.
    '''
    dut = FakeDataframeLoader(
        config=DatasetConfig({
            'column_roles': {
                'target': {'name': 'a'},
                'test_role': {'name': 'b'},
            }
        })
    )
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9],
    })
    with pytest.raises(ColumnError, match="'d"):
        dut.ez_dataset(data=df, roles=['attribute', RoleName.TEST_ROLE])


@pytest.mark.parametrize('argname,method,want_dict', [
    ('train_df', 'poll', {'a': [3], 'b': [6], 'c': [9]}),
    ('test_df', 'load_test', {'b': [4, 5, 6], 'c': [7, 8, 9]}),
    ('train_df', 'load_train', {'a': [3], 'b': [6], 'c': [9]}),
])
def test_split_dataset(argname: str, method: str, want_dict: Dict[str, List[int]]) -> None:
    '''Test that we split data properly in a distributed setting.

    Each node gets a subset of the data based on its node ID.
    '''
    pdef = ProblemDefinition({
        'dataset': {
            'column_roles': {
                'target': {'name': 'a'},
            }
        },
        'distributed': {
            'my_id': 3,
            'split': {
                'num_nodes': 3,
                'seed': 1234
            }
        },
        'problem_type': {
            'task': 'regression'
        }
    })
    config = pdef.get_conf('dataset')
    assert isinstance(config, DatasetConfig)
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9],
    })
    kwargs: Dict[str, Union[pd.DataFrame, DatasetConfig]] = {
        argname: df,
        'config': config
    }
    dut = FakeDataframeLoader(**kwargs)  # type: ignore[arg-type]

    want_df = pd.DataFrame(want_dict)
    # This is the test.
    got = getattr(dut, method)()
    assert got is not None
    pd.testing.assert_frame_equal(want_df, got.dataframe_table.as_(pd.DataFrame))


def test_build_dataset_from_json_predict() -> None:
    '''Test that we can build a dataset from a JSON object.'''
    pdef = ProblemDefinition({
        'dataset': {
            'column_roles': {
                'target': {'name': 'a'},
            }
        },
        'problem_type': {
            'task': 'regression'
        }
    })
    config = pdef.get_conf('dataset')
    assert isinstance(config, DatasetConfig)
    dut = FakeDataframeLoader(config=config)
    got = dut.build_dataset_from_json({'data': {'dataframe': {'a': [1, 2, 3], 'b': [4, 5, 6]}}})
    want = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
    })
    pd.testing.assert_frame_equal(want, got.dataframe_table.as_(pd.DataFrame))


def test_build_dataset_from_json_fit() -> None:
    '''Test that we can build a fit dataset from a JSON object.'''
    pdef = ProblemDefinition({
        'dataset': {
            'column_roles': {
                'target': {'name': 'a'},
            }
        },
        'problem_type': {
            'task': 'regression'
        }
    })

    request = {
        'data': {
            JSONKeys.COVARIATES.value: {'b': [1, 2, 3], 'c': [4, 5, 6]},
            JSONKeys.TARGET.value: {'a': [7, 8, 9]}
        },
    }
    config = pdef.get_conf('dataset')
    assert isinstance(config, DatasetConfig)
    dut = FakeDataframeLoader(config=config)
    got = dut.build_dataset_from_json(request)
    want_covariates = pd.DataFrame({
        'b': [1, 2, 3],
        'c': [4, 5, 6],
    })
    want_target = pd.DataFrame({
        'a': [7, 8, 9],
    })
    assert set(got.keys()) == {'covariates_table', 'target_table'}
    pd.testing.assert_frame_equal(got['covariates_table'].as_(pd.DataFrame), want_covariates)
    pd.testing.assert_frame_equal(got['target_table'].as_(pd.DataFrame), want_target)


def test_load_ground_truth() -> None:
    config = DatasetConfig(clause=CLAUSE)
    dut = FakeDataframeLoader(config=config)
    got = dut.load_ground_truth()
    assert got is not None
    pd.testing.assert_frame_equal(got.ground_truth_table.as_(pd.DataFrame),
                                  pd.DataFrame({'a': [1, 2]}))
