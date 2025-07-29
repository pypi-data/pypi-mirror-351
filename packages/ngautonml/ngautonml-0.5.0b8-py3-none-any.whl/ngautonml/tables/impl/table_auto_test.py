'''Tests for table_auto.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pandas as pd
import pytest

from ...wrangler.constants import PACKAGE_NAME

from .table import Table
from .table_auto import TableCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code


FAKE_TABLE_SOURCE = '''
import pandas as pd

from queue import Queue
from typing import Any, List, Optional
from ngautonml.tables.impl.table import TableWarehouse, Table
from ngautonml.tables.impl.table_catalog import TableCatalog
from ngautonml.tables.dataframe import DataFrameTable


class FakeType():
    def __init__(self, token: str = 'fake'):
        self._token = token


class FakeTable(Table):
    name = 'fake_table'
    tags = {
        'some_tag': ['some_value']
    }
    my_type = FakeType

    def to_csv(self, *args, **kwargs) -> str:
        return 'fake_table'

    def as_dict(self) -> dict:
        return {'fake_table': [1, 2, 3]}

    def to_list(self) -> list[int]:
        return [1, 2, 3]


def from_dataframe(table: DataFrameTable) -> FakeType:
    return table._as(pd.DataFrame).tolist()


def register(catalog: TableCatalog):
    catalog.register(FakeTable)
    TableWarehouse.register_constructor(FakeType, FakeTable)
    TableWarehouse.register_exporter(from_type=FakeType, to_type=list, exporter=FakeTable.to_list)
    TableWarehouse.register_exporter(from_type=pd.DataFrame, to_type=FakeType, exporter=from_dataframe)
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = (retval / f'.{PACKAGE_NAME}' / 'plugins'
                   / 'tables' / 'fake_table.py')
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_TABLE_SOURCE)
    return retval


def test_table_catalog_auto() -> None:
    dut = TableCatalogAuto()

    got = dut.lookup_by_name('dataframe')(
        value=pd.DataFrame(),
    )
    assert isinstance(got, Table)


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)

    dut = TableCatalogAuto()
    got = dut.lookup_by_name('fake_table')
    assert callable(got)
    # We need a FakeType object to create a FakeTable, so we're kind of stuck here.
