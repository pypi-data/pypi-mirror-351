'''Tests for auton_mean.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring, duplicate-code, protected-access

from copy import deepcopy
import pickle
import socket
import time

import numpy as np
import pandas as pd


from ...config_components.distributed_config import DistributedConfig
from ...conftest import Clearer, Waiter
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.base_port import BasePort
from ...wrangler.dataset import Dataset, TableFactory
from ...wrangler.logger import Logger

from ..impl.synchronous import advance

from .auton_mean import AutonMean, AutonMeanInstance

logger = Logger(__file__).logger()
_ = TableCatalogAuto()  # pylint: disable=pointless-statement

base_port = BasePort()


receiver_train = Dataset(
    covariates_table=TableFactory({'a': [1, 2, 3], 'b': [2, 3, 4], 'c': [3, 4, 5]}))

sender_train = Dataset(
    covariates_table=TableFactory({'a': [7, 8, 9], 'b': [8, 9, 10], 'c': [9, 10, 11]}))

empty_dataset = receiver_train.output()


LOOPBACK = '127.0.0.1'
SUNNY_DAY_PORT = base_port.next()


def test_sunny_day(assert_no_exceptions: Clearer) -> None:
    '''Sunny day with no neighbors produces the simple mean.'''
    distributed_config = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '2': [],
                }
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('2', (LOOPBACK, SUNNY_DAY_PORT)),
                ]
            },
        },
        'my_id': 2,
    })

    alg = AutonMean()
    train = receiver_train

    dut = alg.instantiate(
        distributed=distributed_config,
    )
    assert isinstance(dut, AutonMeanInstance)

    try:
        dut.start()
        dut.fit(train)

        result_mean = dut.predict(train)
        assert result_mean is not None
        pd.testing.assert_frame_equal(
            result_mean.predictions_table.as_(pd.DataFrame),
            pd.DataFrame({'a': [2.0], 'b': [3.0], 'c': [4.0]}))
        assert_no_exceptions([dut])

    finally:
        dut.stop()


INTEGRATED_RECEIVER_PORT = base_port.next()
INTEGRATED_SENDER_PORT = base_port.next()


def test_integrated(wait_til_all_fit: Waiter,
                    assert_no_exceptions: Clearer) -> None:
    ''''Two nodes talking to each other.

    One has one set of means, the other has another set.
    We see that both nodes eventually get the same (correct) means.
    '''
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
                    ('1', (LOOPBACK, INTEGRATED_RECEIVER_PORT)),
                    ('2', (LOOPBACK, INTEGRATED_SENDER_PORT)),
                ]
            }
        },
        'my_id': 0,
    }

    # TODO(Dan) Catch the case where there is only 1 class in the training data.
    distributed_receiver_clause = deepcopy(distributed_clause)
    distributed_receiver_clause['my_id'] = 1
    distributed_sender_clause = deepcopy(distributed_clause)
    distributed_sender_clause['my_id'] = 2

    alg = AutonMean()
    receiver = alg.instantiate(
        distributed=DistributedConfig(distributed_receiver_clause)
    )

    sender = None
    try:
        receiver.start()
        receiver.fit(receiver_train)

        check = receiver.predict(empty_dataset)

        # Confirm that the training is as expected.
        assert check is not None
        assert check.has_predictions()
        assert check.predictions_table.shape[0] == 1
        pd.testing.assert_frame_equal(check.predictions_table.as_(pd.DataFrame),
                                      pd.DataFrame({'a': [2.0], 'b': [3.0], 'c': [4.0]}))

        sender = alg.instantiate(distributed=DistributedConfig(distributed_sender_clause))
        sender.start()
        sender.fit(sender_train)

        # Wait for the message to arrive and get processed.
        wait_til_all_fit([sender, receiver], convergence_check=True)

        receiver_got = receiver.predict(empty_dataset)
        sender_got = sender.predict(empty_dataset)

        assert receiver_got is not None
        assert sender_got is not None

        r_got_a = receiver_got.predictions_table.as_(pd.DataFrame)['a'].iloc[0]
        r_got_b = receiver_got.predictions_table.as_(pd.DataFrame)['b'].iloc[0]
        r_got_c = receiver_got.predictions_table.as_(pd.DataFrame)['c'].iloc[0]

        s_got_a = sender_got.predictions_table.as_(pd.DataFrame)['a'].iloc[0]
        s_got_b = sender_got.predictions_table.as_(pd.DataFrame)['b'].iloc[0]
        s_got_c = sender_got.predictions_table.as_(pd.DataFrame)['c'].iloc[0]

        assert 2.0 <= r_got_a <= 8.0
        assert 3.0 <= r_got_b <= 9.0
        assert 4.0 <= r_got_c <= 10.0

        assert 2.0 <= s_got_a <= 8.0
        assert 3.0 <= s_got_b <= 9.0
        assert 4.0 <= s_got_c <= 10.0

        assert_no_exceptions([sender, receiver])

    finally:
        receiver.stop()
        if sender is not None:
            sender.stop()


TEST_N_SAME_N = 5
TEST_N_SAME_PORTS = [base_port.next() for _ in range(TEST_N_SAME_N)]


def test_n_same(wait_til_all_fit: Waiter,
                assert_no_exceptions: Clearer) -> None:
    '''N nodes fully connected with the same training match the non-distributed result.'''
    n = TEST_N_SAME_N

    adjacency = {f'{k}': [j for j in range(1, n + 1) if j != k] for k in range(1, n + 1)}
    nodes_and_endpoints = [(f'{k}', (LOOPBACK, TEST_N_SAME_PORTS[k - 1])) for k in range(1, n + 1)]

    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': adjacency
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': nodes_and_endpoints
            }
        },
        'my_id': 0,
    }

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonMean()

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc)) for dc in distributed_clauses]

    try:
        for dut in duts:
            dut.start()

        for dut in duts:
            dut.fit(receiver_train)

        # Wait for the message to arrive and get processed.
        wait_til_all_fit(duts, convergence_check=True)

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(empty_dataset) for dut in duts]

        for got_prediction in got_predictions:
            assert got_prediction is not None
            pd.testing.assert_frame_equal(
                got_prediction.predictions_table.as_(pd.DataFrame),
                pd.DataFrame({'a': [2.0], 'b': [3.0], 'c': [4.0]}))

        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            dut.stop()


TEST_TELEPHONE_N = 5
TEST_TELEPHONE_PORTS = [base_port.next() for _ in range(TEST_TELEPHONE_N)]


def test_telephone(wait_til_all_fit: Waiter,
                   assert_no_exceptions: Clearer) -> None:
    '''Whisper down the lane test. Nodes connected in a line.
    The only node that has data is one at the end '''
    n = TEST_TELEPHONE_N

    adjacency = {f'{k}': [k - 1, k + 1] for k in range(2, n)}
    adjacency['1'] = [2]
    adjacency[f'{n}'] = [n - 1]
    nodes_and_endpoints = [(f'{k}', (LOOPBACK, TEST_TELEPHONE_PORTS[k - 1]))
                           for k in range(1, n + 1)]

    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': adjacency
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': nodes_and_endpoints
            }
        },
        'my_id': 0,
    }

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonMean()

    telephone_params = dict(alg._default_hyperparams, Lambda=1000000)

    params = [dict(telephone_params) if k == 0 else dict(telephone_params) for k in range(n)]

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc),
        **ps) for (dc, ps) in zip(distributed_clauses, params)]
    try:
        for dut in duts:
            dut.start()

        duts[0].fit(receiver_train)

        # Wait for the message to arrive and get processed.
        time.sleep(1)
        assert wait_til_all_fit(duts, convergence_check=True, max_time=60.0), (
            'Failed to converge in time. Check for exceptions.')

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(empty_dataset) for dut in duts]

        for got_prediction in got_predictions:
            assert got_prediction is not None
            pd.testing.assert_frame_equal(
                got_prediction.predictions_table.as_(pd.DataFrame),
                pd.DataFrame({'a': [2.0], 'b': [3.0], 'c': [4.0]}))

        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            dut.stop()


COLS_SENDER_PORT = base_port.next()
COLS_RECEIVER_PORT = base_port.next()


def test_columns(assert_no_exceptions: Clearer) -> None:
    '''Test that columns are handled in data loading, sending and receiving.'''
    distributed_config = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [2],
                    '2': [1],
                },
            },
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, COLS_SENDER_PORT)),
                    ('2', (LOOPBACK, COLS_RECEIVER_PORT)),
                ],
            },
        },
        'my_id': 2,
    })

    dut = AutonMean().instantiate(distributed=distributed_config, synchronous=True)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, COLS_SENDER_PORT))

    # These parameters were hand-extracted from a successful fit.
    match_message = pickle.dumps((
        np.array([1, 2, 3]), ['a', 'b', 'c']
    ))

    mismatch_message = pickle.dumps((
        np.array([1, 2, 3]), ['a', 'b', 'c', 'hamster']
    ))

    try:
        dut.start()
        dut.fit(sender_train)

        advance([dut])

        sock.sendto(match_message, (LOOPBACK, COLS_RECEIVER_PORT))

        advance([dut])
        assert_no_exceptions([dut])

        sock.sendto(mismatch_message, (LOOPBACK, COLS_RECEIVER_PORT))

        advance([dut])

        got = dut.poll_exceptions()
        assert got is not None
        assert isinstance(got[0], NotImplementedError)
        assert 'mismatch' in str(got[1])
        assert 'hamster' in str(got[1])

        # make sure there are no other exceptions we don't expect
        assert_no_exceptions([dut])

    finally:
        dut.stop()
        sock.close()


def test_none_values(wait_til_all_fit: Waiter,
                     assert_no_exceptions: Clearer) -> None:
    '''Auton mean can accept None values'''
    distributed_config = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '2': [],
                }
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('2', (LOOPBACK, base_port.next())),
                ]
            },
        },
        'my_id': 2,
    })

    alg = AutonMean()
    train = Dataset(
        covariates_table=TableFactory(
            {
                'a': [None, None, None],
                'b': [None, 2, 3],
                'c': [4, 5, 6]
            }
        )
    )

    dut = alg.instantiate(
        distributed=distributed_config,
    )
    assert isinstance(dut, AutonMeanInstance)

    try:
        dut.start()
        dut.fit(train)
        wait_til_all_fit([dut], convergence_check=False)
        result_mean = dut.predict(train)
        assert result_mean is not None
        pd.testing.assert_frame_equal(
            result_mean.predictions_table.as_(pd.DataFrame),
            pd.DataFrame({'a': [np.nan], 'b': [2.5], 'c': [5.0]}))

        assert_no_exceptions([dut])

    finally:
        dut.stop()


NAN_PORT = base_port.next()
NO_NAN_PORT = base_port.next()


def test_nans(assert_no_exceptions: Clearer) -> None:
    ''''Two nodes talking to each other where one has a nan.
    '''
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
                    ('1', (LOOPBACK, NAN_PORT)),
                    ('2', (LOOPBACK, NO_NAN_PORT)),
                ]
            }
        },
        'my_id': 0,
    }

    # TODO(Dan) Catch the case where there is only 1 class in the training data.
    distributed_nan_clause = deepcopy(distributed_clause)
    distributed_nan_clause['my_id'] = 1
    nan_hyperparams = {
        'Lambda': 100000,
        'omega': .7,
    }
    distributed_no_nan_clause = deepcopy(distributed_clause)
    distributed_no_nan_clause['my_id'] = 2
    no_nan_hyperparams = {
        'Lambda': 100000,
        'omega': .7,
    }

    alg = AutonMean()
    nan_node = alg.instantiate(
        distributed=DistributedConfig(distributed_nan_clause),
        synchronous=True,
        **nan_hyperparams
    )

    nan_train = Dataset(
        covariates_table=TableFactory({
            'a': [np.nan, np.nan, np.nan],
            'b': [8, 9, 10],
            'c': [9, 10, 11]}))

    no_nan_train = Dataset(
        covariates_table=TableFactory({
            'a': [7, 8, 9],
            'b': [8, 9, 10],
            'c': [9, 10, 11]}))

    no_nan_node = alg.instantiate(distributed=DistributedConfig(distributed_no_nan_clause),
                                  synchronous=True,
                                  **no_nan_hyperparams)
    try:
        nan_node.start()
        no_nan_node.start()

        nan_node.fit(nan_train)
        no_nan_node.fit(no_nan_train)

        # Wait for the message to arrive and get processed.
        advance([no_nan_node, nan_node])

        nan_got = nan_node.predict(empty_dataset)
        no_nan_got = no_nan_node.predict(empty_dataset)

        assert nan_got is not None
        assert no_nan_got is not None

        pd.testing.assert_frame_equal(nan_got.predictions_table.as_(pd.DataFrame),
                                      pd.DataFrame({'a': [8.0], 'b': [9.0], 'c': [10.0]}))

        pd.testing.assert_frame_equal(no_nan_got.predictions_table.as_(pd.DataFrame),
                                      pd.DataFrame({'a': [8.0], 'b': [9.0], 'c': [10.0]}))

        assert_no_exceptions([no_nan_node, nan_node])

    finally:
        nan_node.stop()
        if no_nan_node is not None:
            no_nan_node.stop()
