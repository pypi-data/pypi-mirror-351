'''tests for distributed_config.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code

from pathlib import Path
import pytest

from ..neighbor_manager.node_id import NodeID

from .impl.config_component import ValidationErrors
from .distributed_config import DistributedConfig


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("distributed_config", numbered=True)
    return retval


def test_get_static_adjacency() -> None:
    dut = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [2, 4, 5],
                    '2': [1, 3, 5],
                    '3': [5, 2],
                    '4': [1],
                    '5': [1, 2, 3]
                }
            }
        }
    })

    static_adjacency = dut.get_static_adjacency(my_id=NodeID(3))
    assert static_adjacency is not None
    assert set(static_adjacency) == {NodeID(2), NodeID(5)}


def test_get_static_from_edges() -> None:
    dut = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'edges': [
                    [1, 2],
                    [1, 4],
                    [1, 5],
                    [2, 3],
                    [2, 5],
                    [3, 5]
                ]
            }
        }
    })

    assert dut.get_static_adjacency(my_id=NodeID(3)) == [NodeID(2), NodeID(5)]


def test_validation_edges_wrong_length() -> None:
    dut = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'edges': [
                    [1, 2],
                    [1, 4],
                    [1, 5],
                    [2, 3],
                    [2, 5],
                    [3, 5, 7]
                ]
            }
        }
    })
    with pytest.raises(ValidationErrors, match=r'\[3, 5, 7\]'):
        dut.validate()


def test_baseline_djam() -> None:
    dut = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '0': [1, 2],
                    '1': [0],
                    '2': [0]
                }
            }
        },
        'regularization': {
            'name': 'djam',
            'weight_matrix': [
                [0, .5, .7],
                [.5, 0, 0],
                [.7, 0, 0]
            ]
        },
        'my_id': 1
    })

    assert dut.regularization_type == 'djam'
    assert isinstance(dut.neighbor_weights, dict)
    assert dut.neighbor_weights[NodeID(0)] == 0.5
    assert dut.neighbor_weights[NodeID(1)] == 0.0


def test_dropper(tmp_path) -> None:
    dut = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [],
                }
            }
        },
        'communicator': {
            'name': 'stub_communicator',
        },
        'dropper': {
            'drop_rate': 0.9,
            'seed': 42,
            'output_dir': tmp_path,
        },
        'my_id': 1,
    })

    assert dut.dropper is not None
    assert dut.dropper.drop_rate == 0.9
    assert dut.dropper.seed == 42
    assert dut.dropper.output_dir == tmp_path


def test_unicast_kafka() -> None:
    dut = DistributedConfig(clause={
        'communicator': {
            'name': 'kafka',
            'kafka': {
                'bootstrap_servers': 'localhost:9092',
                'topic': 'test',
                'group_id': 'test',
                'topic_prefix': 'prefix_',
            },
            'strategy': 'unicast',
        },
        'my_id': 1,
    })

    assert dut.communicator.strategy == 'unicast'
    assert dut.communicator.kafka.node_topic() == 'prefix_1'  # type: ignore[attr-defined] # pylint: disable=no-member
