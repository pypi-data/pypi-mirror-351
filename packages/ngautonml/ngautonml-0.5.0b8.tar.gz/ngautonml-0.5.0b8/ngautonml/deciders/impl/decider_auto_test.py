'''Tests for decider_auto.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pytest

from ...config_components.distributed_config import DistributedConfig
from ...wrangler.constants import PACKAGE_NAME

from ..stub_decider import DeciderStub
from .decider import Decider
from .decider_auto import DeciderCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code

FAKE_DECIDER_SOURCE = '''
from ngautonml.algorithms.impl.distributed_algorithm_instance import NeighborState
from ngautonml.config_components.distributed_config import DecidersConfig, DeciderConfig
from ngautonml.deciders.impl.decider import Decider
from ngautonml.deciders.impl.decider_catalog import DeciderCatalog

class FakeDeciderConfig(DeciderConfig):
    'Configuration for FakeDecider.'

class FakeDecider(Decider):
    name = 'fake_decider'
    tags = {
        'some_tag': ['some_value']
    }

    def decide(self, my_state: NeighborState, neighbor: NeighborState) -> bool:
        return False


def register(catalog: DeciderCatalog):
    catalog.register(FakeDecider)
    DecidersConfig.register(name=FakeDecider.name, config_type=FakeDeciderConfig)
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = (retval / f'.{PACKAGE_NAME}' / 'plugins'
                   / 'deciders' / 'fake_decider.py')
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_DECIDER_SOURCE)
    return retval


def test_decider_catalog_auto() -> None:
    dut = DeciderCatalogAuto()

    distributed = DistributedConfig(
        clause={
            'decider': {
                'stub_decider': {}
            },
        }
    )

    got = dut.lookup_by_name('stub_decider')(
        config=distributed.decider.stub_decider  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
    )
    assert isinstance(got, DeciderStub)


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)

    distributed = DistributedConfig(
        clause={
            'decider': {
                'fake_decider': {}
            },
        }
    )

    dut = DeciderCatalogAuto()
    got = dut.lookup_by_name('fake_decider')(
        config=distributed.decider.fake_decider)  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
    assert isinstance(got, Decider)
    assert got.tags['some_tag'] == ['some_value']
