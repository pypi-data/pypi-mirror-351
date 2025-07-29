'''Tests for pipeline_loader_auto.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pytest

from ...algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ...generator.bound_pipeline import BoundPipeline
from ...wrangler.constants import PACKAGE_NAME

from .pipeline_loader import PipelineLoader
from .pipeline_loader_auto import PipelineLoaderCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code


FAKE_PIPELINE_LOADER_SOURCE = '''
from typing import Any, List, Optional
from ngautonml.generator.bound_pipeline import BoundPipeline
from ngautonml.generator.designator import Designator
from ngautonml.pipeline_loaders.impl.pipeline_loader import PipelineLoader
from ngautonml.pipeline_loaders.impl.pipeline_loader_catalog import PipelineLoaderCatalog

class FakePipelineLoader(PipelineLoader):
    name = 'fake_pipeline_loader'
    tags = {
        'some_tag': ['some_value']
    }

    def _load(self, name) -> BoundPipeline:
        return BoundPipeline(name=Designator(self.name))


def register(catalog: PipelineLoaderCatalog, **kwargs):
    catalog.register(FakePipelineLoader(**kwargs))
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = (retval / f'.{PACKAGE_NAME}' / 'plugins'
                   / 'pipeline_loaders' / 'fake_pipeline_loader.py')
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_PIPELINE_LOADER_SOURCE)
    return retval


def test_pipeline_loader_catalog_auto() -> None:
    dut = PipelineLoaderCatalogAuto(algorithm_catalog=AlgorithmCatalogAuto())
    got = dut.lookup_by_name('just').load('connect')
    assert isinstance(got, BoundPipeline)


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)
    dut = PipelineLoaderCatalogAuto(algorithm_catalog=AlgorithmCatalogAuto())
    got = dut.lookup_by_name('fake_pipeline_loader')
    assert isinstance(got, PipelineLoader)
    assert got.tags['some_tag'] == ['some_value']
