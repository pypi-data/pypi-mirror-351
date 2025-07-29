'''Test the DeciderCatalog'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..stub_decider import DeciderStub
from .decider_catalog import DeciderCatalogStub

# pylint: disable=missing-function-docstring,duplicate-code


def test_register() -> None:
    dut = DeciderCatalogStub()
    assert 'stub_decider' == dut.register(obj=DeciderStub)


def test_register_name() -> None:
    dut = DeciderCatalogStub()
    stub_decider = DeciderStub
    assert 'somenameddecider' == dut.register(
        obj=stub_decider, name='SomeNamedDecider')


def test_lookup_by_name() -> None:
    dut = DeciderCatalogStub()
    some_decider = DeciderStub
    dut.register(obj=some_decider, name='SomeNamedDecider')
    assert dut.lookup_by_name('SomeNamedDecider') == some_decider


def test_lookup_one_by_tag() -> None:
    dut = DeciderCatalogStub()
    dut.register(obj=DeciderStub, name='NamedStubDecider', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 1


def test_lookup_by_tag_fail() -> None:
    dut = DeciderCatalogStub()
    dut.register(obj=DeciderStub, name='NamedStubDecider', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='different_value')) == 0


def test_lookup_multi_by_tag() -> None:
    dut = DeciderCatalogStub()
    stub_decider = DeciderStub
    dut.register(obj=stub_decider, name="Name1", tags={'k1': ['v1']})
    stub_decider2 = DeciderStub
    dut.register(obj=stub_decider2, name="Name2", tags={'k1': ['v1']})
    stub_decider3 = DeciderStub
    dut.register(obj=stub_decider3, name="Name3", tags={'k1': ['different_value']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 2
