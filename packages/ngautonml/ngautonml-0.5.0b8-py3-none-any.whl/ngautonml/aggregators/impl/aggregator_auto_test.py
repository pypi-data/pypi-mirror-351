'''Tests for metric_auto.py.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pytest

from ...wrangler.constants import PACKAGE_NAME
from .aggregator import Aggregator
from .aggregator_auto import AggregatorCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code


FAKE_AGGREGATOR_SOURCE = '''
from ngautonml.aggregators.impl.aggregator import Aggregator, AggregatorStub
from ngautonml.aggregators.impl.aggregator_catalog import AggregatorCatalog


class FakeAggregator(AggregatorStub):
    _name = 'fake_aggregator'
    _tags = {
        'some_tag': ['some_value']
    }


def register(catalog: AggregatorCatalog):
    catalog.register(FakeAggregator())
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = retval / f'.{PACKAGE_NAME}' / 'plugins' / 'aggregators' / 'fake_aggregator.py'
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_AGGREGATOR_SOURCE)
    return retval


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)
    dut = AggregatorCatalogAuto()
    got = dut.lookup_by_name('fake_aggregator')
    assert isinstance(got, Aggregator)
    assert got.tags['some_tag'] == ['some_value']
