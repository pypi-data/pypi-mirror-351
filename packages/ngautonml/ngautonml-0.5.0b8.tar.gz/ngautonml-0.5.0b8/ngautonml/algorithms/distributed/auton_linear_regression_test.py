'''Tests for auton_linear_regression.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,duplicate-code,too-many-locals

from copy import deepcopy
import pickle
import socket
from typing import Tuple

import numpy as np
import pandas as pd
import pytest
from sklearn import datasets  # type: ignore[import]

from ...algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ...algorithms.impl.synchronous import advance
from ...config_components.distributed_config import DistributedConfig
from ...conftest import Clearer, Waiter
from ...metrics.impl.metric_auto import MetricCatalogAuto
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.base_port import BasePort  # type: ignore[import]
from ...wrangler.dataset import Column, Dataset, Metadata, RoleName, TableFactory
from .auton_linear_regression import (
    AutonLinearRegression,
    AutonLinearRegressionInstance,
    AutonLinearRegressionNeighbor)

from ...wrangler.logger import Logger
_ = TableCatalogAuto()

logger = Logger(__file__, to_stdout=False).logger()


CORRECT_V_L2 = 10
CORRECT_V = np.array([
    19.80426349, -1.23138257, 71.81414651,
    52.85306555, 19.89796648, 14.13228464, -45.26142198,
    47.34059162, 67.39734652, 43.43461662, 153.30386624])
CORRECT_V_MSE = 4436.62
GOOD_ENOUGH_MSE = 4300.0
BAD_MSE = 5000
CORRECT_DIST_PARAMS = {
    'L2': CORRECT_V_L2,
    'Lambda': 100000000,
    'omega': .9
}


def load_regression_dataset() -> Tuple[Dataset, Dataset, Dataset, Dataset]:
    # Load the diabetes dataset
    diabetes_x, diabetes_y = datasets.load_diabetes(return_X_y=True)

    # Use only one feature
    # diabetes_x = diabetes_x[:, np.newaxis, 2]

    # Split the data into training/testing sets
    diabetes_x_train = diabetes_x[:-20]
    diabetes_x_test = diabetes_x[-20:]

    # Split the targets into training/testing sets
    diabetes_y_train = diabetes_y[:-20]
    diabetes_y_test = diabetes_y[-20:]
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    metadata = Metadata(roles={RoleName.TARGET: [Column('target')]})
    dataset_train = Dataset(
        metadata=metadata,
        covariates_table=TableFactory(pd.DataFrame(diabetes_x_train, columns=columns)),
        target_table=TableFactory({'target': diabetes_y_train})
    )
    dataset_test = Dataset(
        metadata=metadata,
        covariates_table=TableFactory(pd.DataFrame(diabetes_x_test, columns=columns))
    )
    ground_truth = Dataset(
        metadata=metadata,
        ground_truth=pd.DataFrame({'target': diabetes_y_test})
    )

    reduced_train = Dataset(
        covariates_table=TableFactory(
            pd.DataFrame(np.zeros((2, len(columns))), columns=columns)),
        target_table=TableFactory(pd.DataFrame({'target': diabetes_y_train[:2]})),
        metadata=metadata
    )
    return (dataset_train, dataset_test, ground_truth, reduced_train)


base_port = BasePort()

LOOPBACK = '127.0.0.1'
SUNNY_DAY_PORT = base_port.next()


def test_sunny_day(assert_no_exceptions: Clearer) -> None:
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

    sklearn_alg = AlgorithmCatalogAuto().lookup_by_name('sklearn.linear_model.Ridge')

    alg = AutonLinearRegression()

    # Setting Lambda and L2 values to make our results similar to
    #   sklearn's logistic regression, in order to be more certain
    #   that our algorithm is reasonable.
    dut = alg.instantiate(
        distributed=distributed_config,
        Lambda=0.0, L2=CORRECT_V_L2)
    assert isinstance(dut, AutonLinearRegressionInstance)
    sklearn_dut = sklearn_alg.instantiate(
        alpha=CORRECT_V_L2
    )

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    train, test, ground_truth, _ = load_regression_dataset()

    try:
        dut.start()
        dut.fit(train)
        sklearn_dut.fit(train)

        sklearn_dut_v = np.array(list(sklearn_dut.impl.coef_) + [sklearn_dut.impl.intercept_])
        dut_v = dut.params

        result = dut.predict(test)
        sklearn_result = sklearn_dut.predict(test)

        sklearn_mse = metric.calculate(pred=sklearn_result,
                                       ground_truth=ground_truth
                                       )

        result_mse = metric.calculate(pred=result,
                                      ground_truth=ground_truth
                                      )

        assert dut_v == pytest.approx(sklearn_dut_v, abs=0.01)
        assert result_mse == pytest.approx(expected=sklearn_mse, abs=0.01)
        assert result_mse == pytest.approx(CORRECT_V_MSE, abs=0.1)
        assert_no_exceptions([dut])
    finally:
        dut.stop()


SELF_CONVERGENCE_PORT = base_port.next()


# TODO(Merritt): fix this
@pytest.mark.skip(
    reason='This does not currently work as linear regression has no self-regularization '
    'with no neighbors.  It should be reworked to use 2 nodes, or removed.')
def test_self_convergence(wait_til_all_fit: Waiter) -> None:
    '''Refit if our own state changes, even if we don't see a message from a neighbor.

    Scenario: there is one node with high self-regularization (low omega) that fits on dataset A.
    Then it additionally fits on dataset B, which changes the model enough to send.
    Fitting a third time on dataset B would once again change the model enough to send, due
    to the high self-regularization priotitizing the training from dataset A.
    We would like to continue refitting on dataset B until the model converges with itself.
    '''

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
                    ('2', (LOOPBACK, SELF_CONVERGENCE_PORT)),
                ]
            },
        },
        'my_id': 2,
    })

    alg = AutonLinearRegression()

    dut = alg.instantiate(
        distributed=distributed_config,
        Lambda=1.0, L2=CORRECT_V_L2, omega=0.1)
    assert isinstance(dut, AutonLinearRegressionInstance)

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    train, test, ground_truth, reduced_train = load_regression_dataset()

    try:
        dut.start()
        dut.fit(reduced_train)

        wait_til_all_fit([dut])

        unconverged_result = dut.predict(test)

        unconverged_result_mse = metric.calculate(
            pred=unconverged_result,
            ground_truth=ground_truth
        )

        assert unconverged_result_mse != pytest.approx(
            expected=CORRECT_V_MSE, abs=100)

        dut.fit(train)

        wait_til_all_fit([dut], convergence_check=True)

        converged_result = dut.predict(test)

        conv_result_mse = metric.calculate(
            pred=converged_result,
            ground_truth=ground_truth
        )

        assert conv_result_mse == pytest.approx(CORRECT_V_MSE, abs=0.1)
    finally:
        dut.stop()


RECEIVE_EVENT_SENDER_PORT = base_port.next()
RECEIVE_EVENT_RECEIVER_PORT = base_port.next()


def test_receive_event(assert_no_exceptions: Clearer) -> None:
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
                    ('1', (LOOPBACK, RECEIVE_EVENT_SENDER_PORT)),
                    ('2', (LOOPBACK, RECEIVE_EVENT_RECEIVER_PORT)),
                ],
            },
        },
        'my_id': 2,
    })

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    _, test, ground_truth, reduced_train = load_regression_dataset()

    dut = AutonLinearRegression().instantiate(
        distributed=distributed_config, synchronous=True, **CORRECT_DIST_PARAMS)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, RECEIVE_EVENT_SENDER_PORT))

    # These parameters were hand-extracted from a successful fit.
    message = pickle.dumps((
        CORRECT_V, None
    ))

    try:
        dut.start()
        dut.fit(reduced_train)
        advance([dut])
        got_reduced = dut.predict(test)

        reduced_metric = metric.calculate(pred=got_reduced,
                                          ground_truth=ground_truth
                                          )
        assert reduced_metric > BAD_MSE

        sock.sendto(message, (LOOPBACK, RECEIVE_EVENT_RECEIVER_PORT))

        # Wait for the message to arrive and get processed.
        for _ in range(5):
            advance([dut])

        # Confirm that we learned from our neighbor.
        got = dut.predict(test)

        assert metric.calculate(pred=got,
                                ground_truth=ground_truth
                                ) < reduced_metric - 50
        assert_no_exceptions([dut])
    finally:
        dut.stop()
        sock.close()


SEND_SENDER_PORT = base_port.next()
SEND_RECEIVER_PORT = base_port.next()


def test_send(assert_no_exceptions: Clearer) -> None:
    distributed_config = DistributedConfig(clause={
        'polling_interval': '1.0',  # formerly 0.1
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
                    ('1', (LOOPBACK, SEND_SENDER_PORT)),
                    ('2', (LOOPBACK, SEND_RECEIVER_PORT)),
                ],
            },
        },
        'my_id': 1,
    })

    train, _, _, _ = load_regression_dataset()

    receiver = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    receiver.bind((LOOPBACK, SEND_RECEIVER_PORT))

    dut = None
    try:
        dut = AutonLinearRegression().instantiate(distributed=distributed_config,
                                                  **CORRECT_DIST_PARAMS)
        dut.start()
        dut.fit(train)

        got_raw = receiver.recv(1024)  # Wait for the message to arrive and get processed.
        got = AutonLinearRegressionNeighbor.decode(got_raw)

        assert got.v == pytest.approx(CORRECT_V, abs=0.001)
        assert_no_exceptions([dut])

    finally:
        receiver.close()
        if dut is not None:
            dut.stop()


INTEGRATED_RECEIVER_PORT = base_port.next()
INTEGRATED_SENDER_PORT = base_port.next()


def test_integrated(assert_no_exceptions: Clearer) -> None:
    distributed_clause = {
        'polling_interval': '0.1',
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
        'fit_eps': .01
    }

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    train, test, ground_truth, reduced_train = load_regression_dataset()

    distributed_receiver_clause = deepcopy(distributed_clause)
    distributed_receiver_clause['my_id'] = 1
    distributed_sender_clause = deepcopy(distributed_clause)
    distributed_sender_clause['my_id'] = 2

    alg = AutonLinearRegression()
    bad_data_node = alg.instantiate(distributed=DistributedConfig(distributed_receiver_clause),
                                    synchronous=True,
                                    **CORRECT_DIST_PARAMS)

    good_data_node = None
    try:
        bad_data_node.start()
        bad_data_node.fit(reduced_train)

        advance([bad_data_node])

        check = bad_data_node.predict(test)

        # Confirm that the training is very bad.
        assert metric.calculate(pred=check,
                                ground_truth=ground_truth
                                ) > BAD_MSE

        good_data_node = alg.instantiate(distributed=DistributedConfig(distributed_sender_clause),
                                         synchronous=True,
                                         **CORRECT_DIST_PARAMS)
        good_data_node.start()
        good_data_node.fit(train)

        # Wait for the message to arrive and get processed.
        advance([good_data_node, bad_data_node])

        # Confirm that we learned from our neighbor.
        got_receiver = bad_data_node.predict(test)
        got_sender = good_data_node.predict(test)

        assert metric.calculate(pred=got_receiver,
                                ground_truth=ground_truth
                                ) < BAD_MSE, 'receiver MSE not good enough'
        assert metric.calculate(pred=got_sender,
                                ground_truth=ground_truth
                                ) < BAD_MSE, 'sender MSE not good enough'
        assert_no_exceptions([good_data_node, bad_data_node])
    finally:
        bad_data_node.stop()
        if good_data_node is not None:
            good_data_node.stop()


NO_FIT_RECEIVER_PORT = base_port.next()
NO_FIT_SENDER_PORT = base_port.next()


def test_receive_no_fit(assert_no_exceptions: Clearer) -> None:
    '''Test that we spontaneously fit on a message from a neighbor without having seen data.'''
    distributed_config = DistributedConfig(clause={
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
                    ('1', (LOOPBACK, NO_FIT_SENDER_PORT)),
                    ('2', (LOOPBACK, NO_FIT_RECEIVER_PORT)),
                ],
            },
        },
        'my_id': 2,
    })

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    _, test, ground_truth, _ = load_regression_dataset()

    dist_params = dict(CORRECT_DIST_PARAMS)
    dist_params['omega'] = 1.0  # zeros out self-regularization term

    dut = AutonLinearRegression().instantiate(distributed=distributed_config,
                                              synchronous=True,
                                              **dist_params)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        sock.bind((LOOPBACK, NO_FIT_SENDER_PORT))
    except OSError as err:
        raise OSError(f'{LOOPBACK}:{NO_FIT_SENDER_PORT}') from err

    # These parameters were hand-extracted from a successful fit.
    message = pickle.dumps((
        CORRECT_V, None
    ))

    try:
        dut.start()
        sock.sendto(message, (LOOPBACK, NO_FIT_RECEIVER_PORT))

        # Wait for the message to arrive and get processed.
        for _ in range(5):
            advance([dut])

        # Confirm that we learned from our neighbor.
        got = dut.predict(test)

        assert metric.calculate(pred=got,
                                ground_truth=ground_truth
                                ) == pytest.approx(expected=CORRECT_V_MSE, abs=0.1)
        assert_no_exceptions([dut])
    finally:
        dut.stop()
        sock.close()


TWO_HALF_RECEIVER_PORT = base_port.next()
TWO_HALF_SENDER_PORT = base_port.next()


def test_two_half() -> None:
    '''Two nodes with half the training behaves as (reasonably) expected.'''
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
                    ('1', (LOOPBACK, TWO_HALF_RECEIVER_PORT)),
                    ('2', (LOOPBACK, TWO_HALF_SENDER_PORT)),
                ]
            }
        },
        'my_id': 0,
        'fit_eps': .001
    }

    train, test, ground_truth, _ = load_regression_dataset()

    half_n = int(train['covariates_table'].shape[0] / 2)
    train_first = Dataset(
        metadata=train.metadata,
        covariates_table=TableFactory(train['covariates_table'].as_(pd.DataFrame).iloc[0:half_n]),
        target_table=TableFactory(train['target_table'].as_(pd.DataFrame).iloc[0:half_n])
    )
    train_second = Dataset(
        metadata=train.metadata,
        covariates_table=TableFactory(train['covariates_table'].as_(pd.DataFrame).iloc[half_n:]),
        target_table=TableFactory(train['target_table'].as_(pd.DataFrame).iloc[half_n:])
    )

    distributed_receiver_clause = deepcopy(distributed_clause)
    distributed_receiver_clause['my_id'] = 1
    distributed_sender_clause = deepcopy(distributed_clause)
    distributed_sender_clause['my_id'] = 2

    dist_params_first = dict(CORRECT_DIST_PARAMS)
    dist_params_first['Lambda'] = 100000
    dist_params_second = dict(dist_params_first)

    alg = AutonLinearRegression()
    dut_first = alg.instantiate(
        distributed=DistributedConfig(distributed_receiver_clause),
        synchronous=True,
        **dist_params_first)

    dut_second = alg.instantiate(
        distributed=DistributedConfig(distributed_sender_clause),
        synchronous=True,
        **dist_params_second)

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    try:
        dut_first.start()
        dut_second.start()

        dut_first.fit(train_first)
        dut_second.fit(train_second)

        # Wait for the message to arrive and get processed.
        for _ in range(20):
            advance([dut_first, dut_second])

        # Confirm that neighbor optimization doesn't mess up result.
        got_receiver = dut_first.predict(test)
        got_sender = dut_second.predict(test)

        assert dut_second.params == pytest.approx(dut_first.params, rel=.1), (
            f'params mismatch: {dut_second.params} vs {dut_first.params}'
        )

        assert metric.calculate(pred=got_receiver,
                                ground_truth=ground_truth
                                ) >= GOOD_ENOUGH_MSE, (
            'receiver MSE mismatch: '
            f'{metric.calculate(pred=got_receiver, ground_truth=ground_truth)}')

        assert metric.calculate(pred=got_sender,
                                ground_truth=ground_truth
                                ) >= GOOD_ENOUGH_MSE, (
            'sender MSE mismatch: '
            f'{metric.calculate(pred=got_sender, ground_truth=ground_truth)}')

    finally:
        dut_first.stop()
        if dut_second is not None:
            dut_second.stop()


TWO_SAME_RECEIVER_PORT = base_port.next()
TWO_SAME_SENDER_PORT = base_port.next()


def test_two_same(assert_no_exceptions: Clearer) -> None:
    '''Two nodes with the same training don't change their coefficients.'''
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
                    ('1', (LOOPBACK, TWO_SAME_RECEIVER_PORT)),
                    ('2', (LOOPBACK, TWO_SAME_SENDER_PORT)),
                ]
            }
        },
        'my_id': 0,
    }

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    train, test, ground_truth, _ = load_regression_dataset()

    distributed_receiver_clause = deepcopy(distributed_clause)
    distributed_receiver_clause['my_id'] = 1
    distributed_sender_clause = deepcopy(distributed_clause)
    distributed_sender_clause['my_id'] = 2

    alg = AutonLinearRegression()
    dut_receiver = alg.instantiate(
        distributed=DistributedConfig(distributed_receiver_clause),
        synchronous=True,
        **CORRECT_DIST_PARAMS)

    dut_sender = alg.instantiate(
        distributed=DistributedConfig(distributed_sender_clause),
        synchronous=True,
        **CORRECT_DIST_PARAMS)
    try:

        dut_receiver.start()
        dut_sender.start()

        dut_receiver.fit(train)
        dut_sender.fit(train)

        # Wait for the message to arrive and get processed.
        advance([dut_receiver, dut_sender])

        # Confirm that neighbor optimization doesn't mess up result.
        got_receiver = dut_receiver.predict(test)
        got_sender = dut_sender.predict(test)

        assert metric.calculate(pred=got_receiver,
                                ground_truth=ground_truth
                                ) == pytest.approx(CORRECT_V_MSE, abs=0.1), (
            'receiver MSE mismatch')

        assert metric.calculate(pred=got_sender,
                                ground_truth=ground_truth
                                ) == pytest.approx(CORRECT_V_MSE, abs=0.1), (
            'sender MSE mismatch')

        assert got_receiver is not None
        assert got_sender is not None

        pd.testing.assert_frame_equal(got_receiver.predictions_table.as_(pd.DataFrame),
                                      got_sender.predictions_table.as_(pd.DataFrame))

        assert dut_sender.params == pytest.approx(dut_receiver.params, abs=0.001), (
            f'receiver params mismatch: {dut_sender.params} vs {dut_receiver.params}')
        assert dut_sender.params == pytest.approx(CORRECT_V, abs=0.001), (
            f'correct params mismatch: {dut_sender.params} vs {CORRECT_V}')
        assert_no_exceptions([dut_sender, dut_receiver])
    finally:
        dut_receiver.stop()
        if dut_sender is not None:
            dut_sender.stop()


TEST_N_SAME_N = 5
TEST_N_SAME_PORTS = [base_port.next() for _ in range(TEST_N_SAME_N)]


def test_n_same(assert_no_exceptions: Clearer) -> None:
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

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    train, test, ground_truth, _ = load_regression_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonLinearRegression()

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc),
        synchronous=True,
        **CORRECT_DIST_PARAMS) for dc in distributed_clauses]
    try:
        for dut in duts:
            dut.start()

        for dut in duts:
            dut.fit(train)

        # Wait for the message to arrive and get processed.
        for _ in range(20):
            advance(duts)

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(test) for dut in duts]

        scores = np.array([metric.calculate(pred=pred, ground_truth=ground_truth)
                           for pred in got_predictions])
        want = np.array([CORRECT_V_MSE] * len(scores))
        np.testing.assert_allclose(scores, want, rtol=0.1)

        gp0 = got_predictions[0]
        assert gp0 is not None
        for i in range(1, n):
            gpi = got_predictions[i]
            assert gpi is not None
            np.testing.assert_allclose(gp0.predictions_table.as_(pd.DataFrame),
                                       gpi.predictions_table.as_(pd.DataFrame), rtol=0.1)

        for i in range(1, n):
            assert duts[0].params == pytest.approx(duts[i].params, rel=0.1)

        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            dut.stop()


TEST_TELEPHONE_N = 5
TEST_TELEPHONE_PORTS = [base_port.next() for _ in range(TEST_TELEPHONE_N)]


def test_telephone(assert_no_exceptions: Clearer) -> None:
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

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    train, test, ground_truth, _ = load_regression_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonLinearRegression()

    telephone_params = dict(CORRECT_DIST_PARAMS, Lambda=1)
    telephone_params['omega'] = .5

    params = [dict(telephone_params) if k == 0 else dict(telephone_params) for k in range(n)]

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc), synchronous=True,
        **ps) for (dc, ps) in zip(distributed_clauses, params)]
    try:
        for dut in duts:
            dut.start()

        duts[0].fit(train)

        # Wait for the message to arrive and get processed.
        for _ in range(10 * TEST_TELEPHONE_N):
            advance(duts)

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(test) for dut in duts]

        for got_prediction in got_predictions:
            assert metric.calculate(pred=got_prediction,
                                    ground_truth=ground_truth
                                    ) == pytest.approx(CORRECT_V_MSE, abs=1), (
                f'got {metric.calculate(pred=got_prediction, ground_truth=ground_truth)}, '
                f'not {CORRECT_V_MSE}')

        gp0 = got_predictions[0]
        assert gp0 is not None, 'No predictions from node 0'
        for i in range(1, n):
            gpi = got_predictions[i]
            assert gpi is not None, f'No predictions from node {i}'
            np.testing.assert_allclose(gp0.predictions_table.as_(pd.DataFrame),
                                       gpi.predictions_table.as_(pd.DataFrame), rtol=.01)

        for i in range(n - 1):
            assert duts[i].params == pytest.approx(duts[i + 1].params, rel=0.01), (
                f'Node {i} and {i + 1} have different parameters')

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

    _, _, _, reduced_train = load_regression_dataset()

    dut = AutonLinearRegression().instantiate(distributed=distributed_config,
                                              synchronous=True,
                                              **CORRECT_DIST_PARAMS)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, COLS_SENDER_PORT))

    # These parameters were hand-extracted from a successful fit.
    match_message = pickle.dumps((
        CORRECT_V, reduced_train.dataframe_table.columns
    ))

    mismatch_message = pickle.dumps((
        CORRECT_V, reduced_train.dataframe_table.columns + ['hamster']
    ))

    try:
        dut.start()
        dut.fit(reduced_train)

        advance([dut])

        sock.sendto(match_message, (LOOPBACK, COLS_RECEIVER_PORT))

        advance([dut])
        assert_no_exceptions([dut])

        sock.sendto(mismatch_message, (LOOPBACK, COLS_RECEIVER_PORT))
        advance([dut])

        got = dut.poll_exceptions()
        assert got is not None
        assert isinstance(got[0], NotImplementedError)
        assert 'mismatch' in str(got[1]), f'Expected "mismatch" in {got[1]}'
        assert 'hamster' in str(got[1]), f'Expected "hamster" in {got[1]}'

        # make sure there are no other exceptions we don't expect
        assert_no_exceptions([dut])

    finally:
        dut.stop()
        sock.close()
