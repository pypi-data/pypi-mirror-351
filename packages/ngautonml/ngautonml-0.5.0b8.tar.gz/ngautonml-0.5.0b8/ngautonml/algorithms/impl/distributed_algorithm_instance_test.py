'''Tests for distributed_algorithm_instance.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=protected-access,duplicate-code,missing-function-docstring,redefined-outer-name
# pylint: disable=too-many-locals

from copy import deepcopy
from pathlib import Path
import pickle
import shutil
import socket
import time
from typing import Any, Dict, List, Mapping

import pandas as pd
import pytest

from ...algorithms.impl.neighbor_metadata import NeighborMetadata
from ...algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ...config_components.distributed_config import DistributedConfig
from ...conftest import Clearer, Waiter
from ...neighbor_manager.node_id import NodeID
from ...tables.impl.table import TableFactory
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.base_port import BasePort
from ...wrangler.dataset import Dataset
from ...wrangler.logger import Logger

from ..distributed.auton_mean import AutonMean

from .distributed_algorithm_instance import DistributedAlgorithmInstance, Dropper
from .fake_distributed_algorithm import (
    FakeDistributedAlgorithm, FakeDistributedAlgorithmNeighbor, FitCountDistributedAlgorithm,
    FitCountDistributedAlgorithmNeighbor, FakeDistributedInstance)
from .synchronous import advance, fit_now, read_from_neighbors


logger = Logger(__file__, to_stdout=False).logger()
_ = TableCatalogAuto()


base_port = BasePort()


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("states")
    retval.mkdir(parents=True, exist_ok=True)
    return retval


LOOPBACK = '127.0.0.1'
SUNNY_DAY_SENDER = base_port.next()
SUNNY_DAY_RECIEVER = base_port.next()


def test_columns_sunny_day(wait_til_all_fit: Waiter,
                           assert_no_exceptions: Clearer) -> None:
    '''We get a neighbor report that has the same columns.'''
    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': [2], '2': [1]}
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, SUNNY_DAY_RECIEVER)),
                    ('2', (LOOPBACK, SUNNY_DAY_SENDER))
                ]
            }
        },
        'my_id': 1,
    }

    dut = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=distributed_clause))

    fake_data = Dataset()
    fake_data.dataframe_table = TableFactory({'a': [1], 'b': [2]})

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, SUNNY_DAY_SENDER))

    message = pickle.dumps(['a', 'b'])

    try:
        dut.start()
        dut.fit(fake_data)

        sock.sendto(message, (LOOPBACK, SUNNY_DAY_RECIEVER))

        # Wait for the message to arrive and get processed.
        wait_til_all_fit([dut])

        assert_no_exceptions([dut])

    finally:
        dut.stop()
        sock.close()


RAINY_DAY_SENDER = base_port.next()
RAINY_DAY_RECEIVER = base_port.next()


def test_columns_rainy_day(assert_no_exceptions: Clearer) -> None:
    '''We get a neighbor report that has mismatched columns.'''
    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': [2], '2': [1]}
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, RAINY_DAY_RECEIVER)),
                    ('2', (LOOPBACK, RAINY_DAY_SENDER))
                ]
            }
        },
        'my_id': 1,
    }

    dut = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=distributed_clause),
        synchronous=True)

    fake_data = Dataset()
    fake_data.dataframe_table = TableFactory({'a': [1], 'b': [2]})
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        sock.bind((LOOPBACK, RAINY_DAY_SENDER))
    except OSError as err:
        raise OSError(f'port: {RAINY_DAY_SENDER}') from err

    message = pickle.dumps(['a', 'b', 'c'])  # does not match

    try:
        dut.start()
        dut.fit(fake_data)

        sock.sendto(message, (LOOPBACK, RAINY_DAY_RECEIVER))

        # Wait for the message to arrive and get processed.
        advance([dut])

        got = dut.poll_exceptions()
        assert got is not None
        assert isinstance(got[0], NotImplementedError)
        assert 'mismatch' in str(got[1])

        assert_no_exceptions([dut])

    finally:
        dut.stop()
        sock.close()


REFIT_PORT = base_port.next()


def test_refit_with_no_message(wait_til_all_fit: Waiter,
                               assert_no_exceptions: Clearer) -> None:
    '''Distributed algs must refit if their state has changed, even if they receive no messages.

    Motivation: If a distributed algorithm has high self-regularization, its state may 'drift'
        when refit multiple times even with no new data or messages.
    If such an algorithm does not recieve messages for some reason (it has no neighbors or its
        neighbors are unresponsive), we still want to refit until its state is no longer changing.

    In FitCountDistributedAlgorithmInstance, the NeighborState has a property num_fits: int
    that changes on refit regardless of data or messages.

    should_send returns True if num_fits < 10.

    We create an instance with no neighbors and ensure that num_fits makes it to 10.
    '''
    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': []}
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, REFIT_PORT))
                ]
            }
        },
        'my_id': 1,
    }

    dut = FitCountDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=distributed_clause))

    try:
        dut.start()

        # The first fit doesn't trigger spontaneous refitting.
        dut.fit(None)

        # The second fit should trigger spontaneous refitting.
        dut.fit(None)
        # Convergence timer starts here since we have no neighbors

        assert wait_til_all_fit([dut], convergence_check=True), (
            'Timeout waiting for fit'
        )

        got = dut.my_state
        assert isinstance(got, FitCountDistributedAlgorithmNeighbor)
        assert got.fit_count == 3  # should_send = True if num_fits < 3

        assert_no_exceptions([dut])
    finally:
        dut.stop()


def test_synchronous(wait_til_all_fit: Waiter, assert_no_exceptions: Clearer) -> None:
    '''Test that setting 'synchronous=true' hyperparam causes nodes to not run fit loop.

    The FakeDistributedInstance will not set its state if it sees no data and no messages,
        but if fit on no data with a neighbor message will update its state to match the neighbor.

    We check that the neighbor message is not incorporated into the state
        until we tell the model to fit.
    '''

    sender_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': [2], '2': [1]}
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, base_port.next())),
                    ('2', (LOOPBACK, base_port.next()))
                ]
            }
        },
        'my_id': 1,
    }
    reciever_clause = deepcopy(sender_clause)
    reciever_clause['my_id'] = 2

    sender = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=sender_clause),
        synchronous=True)

    receiver = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=reciever_clause),
        synchronous=True)

    input_dataset = Dataset(
        dataframe=pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
    )

    try:
        sender.start()
        receiver.start()

        sender.fit(input_dataset)

        wait_til_all_fit([sender], convergence_check=False)

        # Make sure the receiver has received the message
        i: int = 0
        while not receiver._pending_message_from_neighbor:
            receiver.read_from_neighbors()
            assert i < 10, (
                'Timeout while waiting to recieve message. Probably a flake.'
            )
            time.sleep(0.5)
            i += 1

        # We have never told the receiver to fit.
        # Assuming fit_periodically is not running, it should not have fit or be fitting
        #   despite receiving a message.
        assert receiver.my_state is None
        assert not receiver._training

        receiver.fit(None)

        wait_til_all_fit([receiver], convergence_check=False)

        assert receiver.my_state
        assert receiver.my_state.columns == ['a', 'b', 'c']

        assert_no_exceptions([sender, receiver])
    finally:
        sender.stop()
        receiver.stop()


def test_synchronous_api(assert_no_exceptions: Clearer) -> None:
    '''Test synchronous API calls fit_now, and read_from_neighbors.'''

    sender_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': [2], '2': [1]}
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, base_port.next())),
                    ('2', (LOOPBACK, base_port.next()))
                ]
            }
        },
        'my_id': 1,
    }
    reciever_clause = deepcopy(sender_clause)
    reciever_clause['my_id'] = 2

    sender = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=sender_clause),
        synchronous=True)

    receiver = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=reciever_clause),
        synchronous=True)

    input_dataset = Dataset(
        dataframe=pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
    )

    try:
        sender.start()
        receiver.start()

        duts: List[DistributedAlgorithmInstance] = [sender, receiver]
        sender.fit(input_dataset)

        # Test read_from_neighbors.
        read_from_neighbors(duts, timeout_ns=1_000_000_000)

        # We have never told the receiver to fit.
        # Assuming fit_periodically is not running, it should not have fit or be fitting
        #   despite receiving a message.
        assert receiver.my_state is None
        assert not receiver._training

        # Test fit_now.
        fit_now(duts)

        assert receiver.my_state
        assert receiver.my_state.columns == ['a', 'b', 'c']

        assert sender.converged is False
        assert receiver.converged is False

        time.sleep(2.0)

        assert sender.converged is True
        assert receiver.converged is True

        assert_no_exceptions(duts)

    finally:
        sender.stop()
        receiver.stop()


def test_synchronous_advance(assert_no_exceptions: Clearer) -> None:
    '''Test synchronous API call advance.'''

    sender_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': [2], '2': [1]}
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, base_port.next())),
                    ('2', (LOOPBACK, base_port.next()))
                ]
            }
        },
        'my_id': 1,
    }
    reciever_clause = deepcopy(sender_clause)
    reciever_clause['my_id'] = 2

    sender = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=sender_clause),
        synchronous=True)

    receiver = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=reciever_clause),
        synchronous=True)

    input_dataset = Dataset(
        dataframe=pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
    )

    try:
        sender.start()
        receiver.start()

        duts: List[DistributedAlgorithmInstance] = [sender, receiver]
        # Test advance.
        advance(duts, timeout_ns=1_000_000_000)

        # Nobody had anythng to say.
        assert sender.my_state is None
        assert receiver.my_state is None

        sender.fit(input_dataset)

        assert sender.my_state is not None
        assert receiver.my_state is None

        advance(duts, min_time=1_000_000_000, timeout_ns=10_000_000_000)

        assert receiver.my_state == sender.my_state

        assert_no_exceptions(duts)

    finally:
        sender.stop()
        receiver.stop()


def _make_dropper(drop_rate: float, seed: int) -> Dropper:
    distributed_clause: Dict[str, Any] = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': [2], '2': [1]}
            }
        },
        'communicator': {
            'name': 'stub_communicator',
        },
        'my_id': 1,
        'dropper': {
            'drop_rate': drop_rate,
            'seed': seed,
        }
    }

    config = DistributedConfig(clause=distributed_clause)
    assert config.dropper is not None
    return Dropper(config.dropper)


def test_dropper() -> None:
    '''Test that the dropper configuration can drop messages.'''

    dut1 = _make_dropper(1.0, 42)
    trial1 = sum(dut1.drop() for _ in range(100))
    assert trial1 == 99

    dut2 = _make_dropper(0.0, 42)
    trial2 = sum(dut2.drop() for _ in range(100))
    assert trial2 == 0

    dut3 = _make_dropper(0.5, 42)
    trial3 = sum(dut3.drop() for _ in range(100))
    assert trial3 == 47


@pytest.mark.skip(reason="We changed the location of emit_on_fit to periodic fit.")
def test_emit_on_fit(tmp_path: Path,
                     wait_til_all_fit: Waiter) -> None:
    '''Test that the emit_on_fit happens.'''
    distributed_clause: Dict[str, Any] = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': []}
            }
        },
        'communicator': {
            'name': 'stub_communicator',
        },
        'my_id': 1,
        'dropper': {
            'drop_rate': 0.0,
            'seed': 42,
            'output_dir': tmp_path,
        },
    }

    dut = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=distributed_clause),
        synchronous=True)

    input_dataset = Dataset(
        dataframe=pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
    )

    try:
        dut.start()

        dut.fit(input_dataset)

        assert wait_til_all_fit([dut], convergence_check=False), 'Timeout waiting for fit'

        # Read in the file that was written by the dropper.
        got = list(tmp_path.glob('*.pkl'))
        assert len(got) == 1
        with open(got[0], 'rb') as f:
            data = pickle.load(f)
        assert data['now'] < time.monotonic_ns()
        assert data['fit_counter'] == 1
        assert data['fit_periodic_counter'] == 0
        assert data['predict_counter'] == 0
        assert data['dropper_tried_counter'] == 0
        assert data['dropper_dropped_counter'] == 0
        assert pickle.loads(data['my_state']) == ['a', 'b', 'c']
    finally:
        dut.stop()
        shutil.rmtree(tmp_path)


def test_multiple_emit_on_fit(tmp_path: Path,
                              wait_til_all_fit: Waiter,
                              assert_no_exceptions: Clearer) -> None:
    '''We generate a series of saved states.'''

    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': []}
            }
        },
        'communicator': {
            'name': 'stub_communicator',
        },
        'my_id': 1,
        'dropper': {
            'drop_rate': 0.0,
            'seed': 42,
            'output_dir': tmp_path,
        },
    }

    dut = FitCountDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=distributed_clause))

    try:
        dut.start()

        # The first fit doesn't trigger spontaneous refitting.
        dut.fit(None)
        dut.fit(None)
        # Convergence timer starts here since we have no neighbors

        assert wait_til_all_fit([dut], convergence_check=True), (
            'Timeout waiting for convergence'
        )

        assert_no_exceptions([dut])

        got = list(tmp_path.glob('*.pkl'))
        assert len(got) >= 3
        # emit moved to fit_periodic, so we cannot predict the output
        # want = [
        #     {
        #         'my_id': 1,
        #         'fit_counter': 1,
        #         'fit_periodic_counter': 0,
        #         'dropper_tried_counter': 0,
        #         'dropper_dropped_counter': 0,
        #         'my_state': 1,
        #     },
        #     {
        #         'my_id': 1,
        #         'fit_counter': 2,
        #         'fit_periodic_counter': 0,
        #         'dropper_tried_counter': 0,
        #         'dropper_dropped_counter': 0,
        #         'my_state': 2,
        #     },
        #     {
        #         'my_id': 1,
        #         'fit_counter': 3,
        #         'fit_periodic_counter': 1,
        #         'dropper_tried_counter': 0,
        #         'dropper_dropped_counter': 0,
        #         'my_state': 3,
        #     },
        # ]
        # n = 0
        # print("DEBUG: got:", got)
        # for filename in sorted(got):
        #     print("DEBUG: n:", n)
        #     with open(filename, 'rb') as f:
        #         data = pickle.load(f)
        #     assert data['my_id'] == want[n]['my_id'], 'my_id mismatch'
        #     assert data['fit_counter'] == want[n]['fit_counter']
        #     assert data['fit_periodic_counter'] == want[n]['fit_periodic_counter']
        #     assert data['dropper_tried_counter'] == want[n]['dropper_tried_counter']
        #     assert data['dropper_dropped_counter'] == want[n]['dropper_dropped_counter']
        #     assert pickle.loads(data['my_state']) == want[n]['my_state']
        #     n += 1

    finally:
        dut.stop()
        shutil.rmtree(tmp_path)


DROP_ALL_NODE_1_PORT = base_port.next()
DROP_ALL_NODE_2_PORT = base_port.next()


@pytest.mark.skip(reason="We changed the location of emit_on_fit to periodic fit.")
def test_emit_on_fit_drop_all(tmp_path: Path,
                              wait_til_all_fit: Waiter,
                              assert_no_exceptions: Clearer) -> None:
    '''Drop every packet from a neighbor, but still emit on fit.'''
    node_1_train = Dataset(
        covariates_table=TableFactory(
            {'a': [1.0, 2.0, 3.0], 'b': [2.0, 3.0, 4.0], 'c': [3.0, 4.0, 5.0]}))

    want_node_1 = pd.DataFrame({'a': [2.0], 'b': [3.0], 'c': [4.0]})

    node_2_train = Dataset(
        covariates_table=TableFactory(
            {'a': [7.0, 8.0, 9.0], 'b': [8.0, 9.0, 10.0], 'c': [9.0, 10.0, 11.0]}))

    want_node_2 = pd.DataFrame({'a': [8.0], 'b': [9.0], 'c': [10.0]})

    placeholder_dataset = Dataset(
        covariates_table=TableFactory(
            {'a': [0], 'b': [0], 'c': [0]}))

    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [2],
                    '2': [1],
                }
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, DROP_ALL_NODE_1_PORT)),
                    ('2', (LOOPBACK, DROP_ALL_NODE_2_PORT)),
                ]
            }
        },
        'my_id': 0,
        'dropper': {
            'drop_rate': 1.0,
            'output_dir': tmp_path,
        },

    }

    # TODO(Dan) Catch the case where there is only 1 class in the training data.
    distributed_node_1_clause = deepcopy(distributed_clause)
    distributed_node_1_clause['my_id'] = 1
    distributed_node_2_clause = deepcopy(distributed_clause)
    distributed_node_2_clause['my_id'] = 2

    alg = AutonMean()

    dut_node_1 = alg.instantiate(
        distributed=DistributedConfig(distributed_node_1_clause)
    )
    dut_node_2 = alg.instantiate(
        distributed=DistributedConfig(distributed_node_2_clause)
    )

    try:
        dut_node_1.start()
        dut_node_2.start()

        dut_node_1.fit(node_1_train)
        dut_node_2.fit(node_2_train)

        wait_til_all_fit([dut_node_1, dut_node_2], convergence_check=False)

        dut_node_1.fit(None)
        dut_node_2.fit(None)
        wait_til_all_fit([dut_node_1, dut_node_2], convergence_check=False)

        assert_no_exceptions([dut_node_1, dut_node_2])

        got_node_1 = dut_node_1.predict(placeholder_dataset)
        got_node_2 = dut_node_2.predict(placeholder_dataset)

        assert got_node_1 is not None
        assert got_node_2 is not None

        pd.testing.assert_frame_equal(got_node_1.predictions_table.as_(pd.DataFrame), want_node_1)
        pd.testing.assert_frame_equal(got_node_2.predictions_table.as_(pd.DataFrame), want_node_2)

        got_files = list(tmp_path.glob('*.pkl'))
        assert len(got_files) == 4
        n = 0
        want = [
            {'my_id': 1, 'dropper_dropped_counter': 0, 'dropper_tried_counter': 0},
            {'my_id': 1, 'dropper_dropped_counter': 1, 'dropper_tried_counter': 1},
            {'my_id': 2, 'dropper_dropped_counter': 0, 'dropper_tried_counter': 0},
            {'my_id': 2, 'dropper_dropped_counter': 1, 'dropper_tried_counter': 1},
        ]
        for filename in sorted(got_files):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            assert data['dropper_dropped_counter'] == want[n]['dropper_dropped_counter']
            assert data['dropper_tried_counter'] == want[n]['dropper_tried_counter']
            n += 1

    finally:
        dut_node_2.stop()
        dut_node_1.stop()
        shutil.rmtree(tmp_path)


def test_instantiate_with_state() -> None:
    '''Test that we can instantiate with a state.'''
    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': []}
            }
        },
        'communicator': {
            'name': 'stub_communicator',
        },
        'my_id': 1,
    }

    dataset = Dataset(
        dataframe=pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
    )

    src = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=distributed_clause))

    src.fit(dataset)

    assert src.my_state is not None
    assert src.my_state.columns == ['a', 'b', 'c']

    dut = FakeDistributedInstance.instantiate_with_state(
        state=src.my_state.encode(),
        parent=FakeDistributedAlgorithm(),
        distributed=DistributedConfig(clause=distributed_clause))
    assert dut.my_state is not None, 'my_state is None'
    assert dut.my_state.columns == ['a', 'b', 'c']
    got = dut.predict(dataset)
    assert got is not None, 'predict returned None'
    pd.testing.assert_frame_equal(got.dataframe_table.as_(pd.DataFrame),
                                  dataset.dataframe_table.as_(pd.DataFrame))


DECIDER_0_PORT = base_port.next()
DECIDER_1_PORT = base_port.next()
DECIDER_2_PORT = base_port.next()


@pytest.mark.skip('This test is incomplete.')
def test_3_node_deciders(wait_til_all_fit: Waiter,
                         assert_no_exceptions: Clearer) -> None:
    '''3 sockets communicators on different nodes make decisions on whether to update each other.'''

    distributed: Dict[str, Any] = {
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('0', (LOOPBACK, DECIDER_0_PORT)),
                    ('1', (LOOPBACK, DECIDER_1_PORT)),
                    ('2', (LOOPBACK, DECIDER_2_PORT)),
                ]
            },
            'strategy': 'unicast',
        },
        'decider': {
            # It’s been too long since we last sent or received a model.
            'timesince_send': {
                'timeout': 2.0,  # seconds
            },
            'timesince_recv': {
                'timeout': 2.0,  # seconds
            },
            'distance': {
                # Model distance metric is high.
                'threshold': 5.0,  # Value is specific to algorithm.
            },
            'basic_risk': {
                # Risk has reduced sufficiently to make communication safe.
                'threshold': 0.1,  # Value is specific to communicator.
            },
        },
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '0': [1, 2],
                    '1': [0, 2],
                    '2': [0, 1],
                }
            }
        },
        'my_id': None,
    }

    duts: List[FakeDistributedInstance] = []

    alg = FakeDistributedAlgorithm()
    for i in range(3):
        config = deepcopy(distributed)
        config['my_id'] = i
        duts.append(alg.instantiate(distributed=DistributedConfig(config)))

    for i in range(3):
        duts[i].start()

    try:
        duts[0].fit(None)  # Maybe provide a special dataset?
        wait_til_all_fit(duts, convergence_check=False)
        # TODO(piggy): Check that only one of the neighbors is updated.

        duts[1].fit(None)  # Version 2 of the special dataset?
        wait_til_all_fit(duts, convergence_check=False)
        for i in [0, 2]:
            pass
            # Confirm that both nodes have updated.

        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            if dut is not None:
                dut.stop()


@pytest.mark.parametrize(
    'threshold, enabled_distance, enabled_stub, result',
    [
        (0.5, False, False, False),
        (0.5, True, False, False),
        (-0.5, True, False, True),
        (0.5, False, True, True),
        (0.5, True, True, True),
    ]
)
def test_neighbor_decide(
        threshold: float, enabled_distance: bool, enabled_stub: bool, result: bool) -> None:

    config = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {'1': [2], '2': [1]}
            }
        },
        'communicator': {
            'name': 'stub_communicator',
        },
        'my_id': 1,
        'decider': {
            'distance': {
                'threshold': threshold,
                'enabled': enabled_distance,
            },
            'stub_decider': {
                'enabled': enabled_stub,
            },
        },
    }

    dut = FakeDistributedAlgorithm().instantiate(
        distributed=DistributedConfig(clause=config))
    dut._my_state_metadata = NeighborMetadata(my_state=FakeDistributedAlgorithmNeighbor())

    neighbor2_id = NodeID(2)
    neighbors: Mapping[NodeID, NeighborMetadataInterface] = {
        neighbor2_id: NeighborMetadata(my_state=FakeDistributedAlgorithmNeighbor()),
    }

    assert dut.decide(neighbor_id=neighbor2_id, neighbors=neighbors) == result
