'''Test the TableCatalog'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..stub import StubTable
from .table_catalog import TableCatalogStub

# pylint: disable=missing-function-docstring,duplicate-code


def test_register() -> None:
    dut = TableCatalogStub()
    assert 'stub' == dut.register(obj=StubTable)


def test_register_name() -> None:
    dut = TableCatalogStub()
    stub_table = StubTable
    assert 'somenamedtable' == dut.register(
        obj=stub_table, name='SomeNamedTable')


def test_lookup_by_name() -> None:
    dut = TableCatalogStub()
    some_table = StubTable
    dut.register(obj=some_table, name='SomeNamedTable')
    assert dut.lookup_by_name('SomeNamedTable') == some_table


def test_lookup_one_by_tag() -> None:
    dut = TableCatalogStub()
    dut.register(obj=StubTable, name='NamedStubTable', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 1


def test_lookup_by_tag_fail() -> None:
    dut = TableCatalogStub()
    dut.register(obj=StubTable, name='NamedStubTable', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='different_value')) == 0


def test_lookup_multi_by_tag() -> None:
    dut = TableCatalogStub()
    stub_table = StubTable
    dut.register(obj=stub_table, name="Name1", tags={'k1': ['v1']})
    stub_table2 = StubTable
    dut.register(obj=stub_table2, name="Name2", tags={'k1': ['v1']})
    stub_table3 = StubTable
    dut.register(obj=stub_table3, name="Name3", tags={'k1': ['different_value']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 2
