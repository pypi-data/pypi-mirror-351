'''Tests from ColumnParser'''
# pylint: disable=missing-function-docstring, duplicate-code
import os
from pathlib import Path
from typing import Dict, Any

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pandas as pd

from .column_parser import ColumnParser
from ..tables.impl.table import TableFactory
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Dataset

_ = TableCatalogAuto()  # noqa: F841


def valid_csv() -> str:
    '''Returns a path (in the form of a string) to a valid csv file.'''
    current_path = str(os.getenv('PYTEST_CURRENT_TEST')).split('::', maxsplit=1)[0]
    pathobj = Path(current_path).resolve()
    module_parent = pathobj.parents[2]
    path = module_parent / 'examples' / 'regression' / 'diabetes.csv'
    return str(path)


def make_dataset_clause() -> Dict[str, Any]:
    retval = {
        'config': 'local',
        'train_path': valid_csv(),
        'column_roles': {
            'target': {
                'name': 'Prog'
            },
            'index': {
                'id': 0
            }
        }
    }
    return retval


def test_parse_trivial_dataset() -> None:
    triv = Dataset()
    triv.dataframe_table = TableFactory({
        'a': ['cat_one', 'cat_two', 'cat_two'],
        'b': [22.1, 22.3, 22.7]})
    assert triv.dataframe_table.as_(pd.DataFrame).dtypes['a'] == 'object'
    dut = ColumnParser().instantiate()
    got = dut.predict(dataset=triv)
    assert got.dataframe_table.as_(pd.DataFrame).dtypes['a'] == 'category'
