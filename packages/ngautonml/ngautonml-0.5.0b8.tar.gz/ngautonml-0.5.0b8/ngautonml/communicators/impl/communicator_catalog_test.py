'''Test the CommunicatorCatalog'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..stub_communicator import CommunicatorStub
from .communicator_catalog import CommunicatorCatalogStub

# pylint: disable=missing-function-docstring,duplicate-code


def test_register() -> None:
    dut = CommunicatorCatalogStub()
    assert 'stub_communicator' == dut.register(obj=CommunicatorStub)


def test_register_name() -> None:
    dut = CommunicatorCatalogStub()
    stub_communicator = CommunicatorStub
    assert 'somenamedcommunicator' == dut.register(
        obj=stub_communicator, name='SomeNamedCommunicator')


def test_lookup_by_name() -> None:
    dut = CommunicatorCatalogStub()
    some_communicator = CommunicatorStub
    dut.register(obj=some_communicator, name='SomeNamedCommunicator')
    assert dut.lookup_by_name('SomeNamedCommunicator') == some_communicator


def test_lookup_one_by_tag() -> None:
    dut = CommunicatorCatalogStub()
    dut.register(obj=CommunicatorStub, name='NamedStubCommunicator', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 1


def test_lookup_by_tag_fail() -> None:
    dut = CommunicatorCatalogStub()
    dut.register(obj=CommunicatorStub, name='NamedStubCommunicator', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='different_value')) == 0


def test_lookup_multi_by_tag() -> None:
    dut = CommunicatorCatalogStub()
    stub_communicator = CommunicatorStub
    dut.register(obj=stub_communicator, name="Name1", tags={'k1': ['v1']})
    stub_communicator2 = CommunicatorStub
    dut.register(obj=stub_communicator2, name="Name2", tags={'k1': ['v1']})
    stub_communicator3 = CommunicatorStub
    dut.register(obj=stub_communicator3, name="Name3", tags={'k1': ['different_value']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 2
