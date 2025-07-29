'''Test the DiscovererCatalog'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .discoverer import DiscovererStub
from .discoverer_catalog import DiscovererCatalogStub

# pylint: disable=missing-function-docstring,duplicate-code


def test_register() -> None:
    dut = DiscovererCatalogStub()
    assert 'stub_discoverer' == dut.register(obj=DiscovererStub)


def test_register_name() -> None:
    dut = DiscovererCatalogStub()
    stub_discoverer = DiscovererStub
    assert 'somenameddiscoverer' == dut.register(
        obj=stub_discoverer, name='SomeNamedDiscoverer')


def test_lookup_by_name() -> None:
    dut = DiscovererCatalogStub()
    some_discoverer = DiscovererStub
    dut.register(obj=some_discoverer, name='SomeNamedDiscoverer')
    assert dut.lookup_by_name('SomeNamedDiscoverer') == some_discoverer


def test_lookup_one_by_tag() -> None:
    dut = DiscovererCatalogStub()
    dut.register(obj=DiscovererStub, name='NamedStubDiscoverer', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 1


def test_lookup_by_tag_fail() -> None:
    dut = DiscovererCatalogStub()
    dut.register(obj=DiscovererStub, name='NamedStubDiscoverer', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='different_value')) == 0


def test_lookup_multi_by_tag() -> None:
    dut = DiscovererCatalogStub()
    stub_discoverer = DiscovererStub
    dut.register(obj=stub_discoverer, name="Name1", tags={'k1': ['v1']})
    stub_discoverer2 = DiscovererStub
    dut.register(obj=stub_discoverer2, name="Name2", tags={'k1': ['v1']})
    stub_discoverer3 = DiscovererStub
    dut.register(obj=stub_discoverer3, name="Name3", tags={'k1': ['different_value']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 2
