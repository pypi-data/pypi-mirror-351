'''Tests from ExtractColumnsByRoleModel'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring, duplicate-code

from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import pandas as pd

from .extract_columns_by_role import ExtractColumnsByRoleModel, ExtractColumnsByRoleModelInstance
from ..config_components.dataset_config import DatasetConfig
from ..data_loaders.local_data_loader import LocalDataLoader
from ..wrangler.dataset import Dataset, RoleName, Metadata, Column


def valid_csv() -> str:
    '''Returns a path (in the form of a string) to a valid csv file.'''
    module_parent = Path(__file__).parents[2]
    path = module_parent / 'examples' / 'classification' / 'credit.csv'
    return str(path)


def make_dataset_clause() -> Dict[str, Any]:
    retval = {
        'config': 'local',
        'train_path': valid_csv(),
        'column_roles': {
            'target': {
                'name': 'class'
            },
            'index': {
                'name': 'checking_status'
            }
        }
    }
    return retval


def test_simple_extraction() -> None:
    clause: Dict[str, Any] = make_dataset_clause()
    dataset_config = DatasetConfig(clause=clause)
    data_loader = LocalDataLoader(dataset_config)
    dataset = data_loader.load_train()
    desired_role: RoleName = RoleName.TARGET

    dut: ExtractColumnsByRoleModelInstance = ExtractColumnsByRoleModel().instantiate(
        desired_roles=desired_role
    )
    dut_result: Optional[Dataset] = dut.predict(dataset=dataset)
    assert dut_result is not None
    result_cols: List[Union[int, str]] = dut_result.dataframe_table.columns
    assert len(result_cols) == 1
    assert result_cols[0] == 'class'


def test_nonexistent_role_extraction() -> None:
    desired_roles: List[RoleName] = [RoleName.TIME]

    fake_df = pd.DataFrame({
        'a': [1, 2], 'b': [3, 4]
    })
    fake_dataset = Dataset(
        dataframe=fake_df,
        metadata=Metadata(
            roles={
                RoleName.TARGET: [Column('a')]
            })
    )

    dut: ExtractColumnsByRoleModelInstance = ExtractColumnsByRoleModel().instantiate(
        desired_roles=desired_roles
    )
    got = dut.predict(dataset=fake_dataset)
    assert got is not None
    assert got.dataframe_table.shape == (0, 0)


def test_multi_role_extraction() -> None:
    clause: Dict[str, Any] = make_dataset_clause()
    dataset_config = DatasetConfig(clause=clause)
    data_loader = LocalDataLoader(dataset_config)
    dataset = data_loader.load_train()
    desired_roles: List[RoleName] = [RoleName.TARGET, RoleName.INDEX]

    dut: ExtractColumnsByRoleModelInstance = ExtractColumnsByRoleModel().instantiate(
        desired_roles=desired_roles
    )
    dut_result: Optional[Dataset] = dut.predict(dataset=dataset)
    assert dut_result is not None
    result_cols: List[Union[int, str]] = sorted(dut_result.dataframe_table.columns)
    assert len(result_cols) == 2
    assert result_cols[0] == 'checking_status'
    assert result_cols[1] == 'class'


def test_multi_role_extraction_with_one_nonexistent() -> None:
    clause: Dict[str, Any] = make_dataset_clause()
    dataset_config = DatasetConfig(clause=clause)
    data_loader = LocalDataLoader(dataset_config)
    dataset = data_loader.load_train()
    desired_roles: List[RoleName] = [RoleName.TARGET, RoleName.TIME]

    dut: ExtractColumnsByRoleModelInstance = ExtractColumnsByRoleModel().instantiate(
        desired_roles=desired_roles
    )
    dut_result: Optional[Dataset] = dut.predict(dataset=dataset)
    assert dut_result is not None
    result_cols: List[Union[int, str]] = dut_result.dataframe_table.columns
    assert len(result_cols) == 1
    assert result_cols[0] == 'class'
