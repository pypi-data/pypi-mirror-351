'''Tests for discoverer_auto.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pytest

from ...communicators.stub_communicator import CommunicatorStub
from ...config_components.distributed_config import DistributedConfig
from ...wrangler.constants import PACKAGE_NAME

from ..static_discoverer import StaticDiscoverer
from .discoverer import Discoverer
from .discoverer_auto import DiscovererCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code


FAKE_DISCOVERER_SOURCE = '''
from typing import Any, List, Optional
from ngautonml.discoverers.impl.discoverer import Discoverer
from ngautonml.neighbor_manager.event import Event
from ngautonml.discoverers.impl.discoverer_catalog import DiscovererCatalog
from ngautonml.neighbor_manager.node_id import NodeID


class FakeDiscoverer(Discoverer):
    name = 'fake_discoverer'
    tags = {
        'some_tag': ['some_value']
    }

    def start(self):
        return

    def laplacian(self):
        return []


def register(catalog: DiscovererCatalog):
    catalog.register(FakeDiscoverer)
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = (retval / f'.{PACKAGE_NAME}' / 'plugins'
                   / 'discoverers' / 'fake_discoverer.py')
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_DISCOVERER_SOURCE)
    return retval


def test_discoverer_catalog_auto() -> None:
    config = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '0': [],
                }
            }
        }
    })
    dut = DiscovererCatalogAuto()

    got = dut.lookup_by_name('static')(
        config=config, communicator=CommunicatorStub()
    )
    assert isinstance(got, StaticDiscoverer)


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)
    config = DistributedConfig(clause={
        'static': {
            'adjacency': {
                '0': [],
            }
        }
    })

    dut = DiscovererCatalogAuto()
    got = dut.lookup_by_name('fake_discoverer')(
        config=config, communicator=CommunicatorStub()
    )
    assert isinstance(got, Discoverer)
    assert got.tags['some_tag'] == ['some_value']
