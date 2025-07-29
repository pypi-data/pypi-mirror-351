'''Test the DataLoaderCatalog'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..stub_data_loader import DataLoaderStub
from .data_loader_catalog import DataLoaderCatalogStub

# pylint: disable=missing-function-docstring,duplicate-code


def test_register() -> None:
    dut = DataLoaderCatalogStub()
    assert 'stub' == dut.register(obj=DataLoaderStub)


def test_register_name() -> None:
    dut = DataLoaderCatalogStub()
    stub_data_loader = DataLoaderStub
    assert 'somenameddataloader' == dut.register(
        obj=stub_data_loader, name='SomeNamedDataLoader')


def test_lookup_by_name() -> None:
    dut = DataLoaderCatalogStub()
    some_data_loader = DataLoaderStub
    dut.register(obj=some_data_loader, name='SomeNamedDataLoader')
    assert dut.lookup_by_name('SomeNamedDataLoader') == some_data_loader


def test_lookup_one_by_tag() -> None:
    dut = DataLoaderCatalogStub()
    dut.register(obj=DataLoaderStub, name='NamedStubDataLoader', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 1


def test_lookup_by_tag_fail() -> None:
    dut = DataLoaderCatalogStub()
    dut.register(obj=DataLoaderStub, name='NamedStubDataLoader', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='different_value')) == 0


def test_lookup_multi_by_tag() -> None:
    dut = DataLoaderCatalogStub()
    stub_data_loader = DataLoaderStub
    dut.register(obj=stub_data_loader, name="Name1", tags={'k1': ['v1']})
    stub_data_loader2 = DataLoaderStub
    dut.register(obj=stub_data_loader2, name="Name2", tags={'k1': ['v1']})
    stub_data_loader3 = DataLoaderStub
    dut.register(obj=stub_data_loader3, name="Name3", tags={'k1': ['different_value']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 2

# TODO(Merritt): test for detection of tags in class variables as well as used when registering
