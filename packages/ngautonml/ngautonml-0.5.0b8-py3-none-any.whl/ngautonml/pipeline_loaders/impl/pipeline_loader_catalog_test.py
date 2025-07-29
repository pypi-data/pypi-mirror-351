'''Test the PipelineLoaderCatalog'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .pipeline_loader import PipelineLoaderStub
from .pipeline_loader_catalog import PipelineLoaderCatalogStub

# pylint: disable=missing-function-docstring,duplicate-code


def test_register() -> None:
    dut = PipelineLoaderCatalogStub()
    assert 'stub_pipeline_loader' == dut.register(obj=PipelineLoaderStub())


def test_register_name() -> None:
    dut = PipelineLoaderCatalogStub()
    stub_pipeline_loader = PipelineLoaderStub()
    assert 'somenamedpipelineloader' == dut.register(
        obj=stub_pipeline_loader, name='SomeNamedPipelineLoader')


def test_lookup_by_name() -> None:
    dut = PipelineLoaderCatalogStub()
    some_pipeline_loader = PipelineLoaderStub()
    dut.register(obj=some_pipeline_loader, name='SomeNamedPipelineLoader')
    assert dut.lookup_by_name('SomeNamedPipelineLoader') == some_pipeline_loader


def test_lookup_one_by_tag() -> None:
    dut = PipelineLoaderCatalogStub()
    dut.register(obj=PipelineLoaderStub(), name='NamedStubPipelineLoader', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 1


def test_lookup_by_tag_fail() -> None:
    dut = PipelineLoaderCatalogStub()
    dut.register(obj=PipelineLoaderStub(), name='NamedStubPipelineLoader', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='different_value')) == 0


def test_lookup_multi_by_tag() -> None:
    dut = PipelineLoaderCatalogStub()
    stub_pipeline_loader = PipelineLoaderStub()
    dut.register(obj=stub_pipeline_loader, name="Name1", tags={'k1': ['v1']})
    stub_pipeline_loader2 = PipelineLoaderStub()
    dut.register(obj=stub_pipeline_loader2, name="Name2", tags={'k1': ['v1']})
    stub_pipeline_loader3 = PipelineLoaderStub()
    dut.register(obj=stub_pipeline_loader3, name="Name3", tags={'k1': ['different_value']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 2
