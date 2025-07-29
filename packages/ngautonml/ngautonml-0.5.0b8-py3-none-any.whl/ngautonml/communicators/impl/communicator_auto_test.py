'''Tests for communicator_auto.py.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pytest

from ...config_components.distributed_config import DistributedConfig
from ...neighbor_manager.node_id import NodeID
from ...wrangler.constants import PACKAGE_NAME

from ..sockets_communicator import SocketsCommunicator

from .communicator import Communicator
from .communicator_auto import CommunicatorCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code


FAKE_COMMUNICATOR_SOURCE = '''
from queue import Queue
from typing import Any, List, Optional
from ngautonml.communicators.impl.communicator import Communicator
from ngautonml.neighbor_manager.event import Event
from ngautonml.communicators.impl.communicator_catalog import CommunicatorCatalog
from ngautonml.neighbor_manager.node_id import NodeID


class FakeCommunicator(Communicator):
    name = 'fake_communicator'
    tags = {
        'some_tag': ['some_value']
    }

    def start(self,
              queue: Queue,
              timeout: float
              ) -> None:
        pass

    def send(self,
             dest_id: NodeID,
             payload: bytes) -> int:
        pass

    def send_all(self, payload: bytes) -> int:
        pass

    def stop(self) -> None:
        pass


def register(catalog: CommunicatorCatalog):
    catalog.register(FakeCommunicator)
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = (retval / f'.{PACKAGE_NAME}' / 'plugins'
                   / 'communicators' / 'fake_communicator.py')
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_COMMUNICATOR_SOURCE)
    return retval


def test_communicator_catalog_auto() -> None:
    dut = CommunicatorCatalogAuto()

    clause = {
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [],
            },
        },
    }

    got = dut.lookup_by_name('sockets')(
        my_id=NodeID(0),
        known_neighbors=set(),
        distributed=DistributedConfig(clause=clause)
    )
    assert isinstance(got, SocketsCommunicator)


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)

    dut = CommunicatorCatalogAuto()
    got = dut.lookup_by_name('fake_communicator')(
        my_id=NodeID(-1), known_neighbors=set(),
        distributed=DistributedConfig(clause={})
    )
    assert isinstance(got, Communicator)
    assert got.tags['some_tag'] == ['some_value']
