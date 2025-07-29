'''Tests for auton_lr.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,duplicate-code,protected-access,too-many-locals
# pylint: disable=too-many-lines

from copy import deepcopy
import pickle
import socket
import time
from typing import Tuple

import numpy as np
import pandas as pd
import pytest
from sklearn import datasets  # type: ignore[import]


from ...config_components.distributed_config import DistributedConfig
from ...conftest import Clearer, Waiter
from ...metrics.impl.metric_auto import MetricCatalogAuto
from ...problem_def.task import TaskType
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.base_port import BasePort
from ...wrangler.dataset import Column, Dataset, Metadata, RoleName, TableFactory
from ...wrangler.logger import Logger

from ..impl.algorithm_auto import AlgorithmCatalogAuto
from ..impl.synchronous import advance, read_from_neighbors
from ..sklearn.sklearn_algorithm import SklearnAlgorithm

from .auton_logistic_regression import (
    AutonLogisticRegression, AutonLogisticRegressionInstance, AutonLogisticRegressionNeighbor)

_ = TableCatalogAuto()
log = Logger(__file__, to_stdout=False).logger()

base_port = BasePort()


CORRECT_V = np.array([-0.5086, 2.3477, -0.2656, 19.2694])

CORRECT_V_L2 = 10.0
CORRECT_DIST_PARAMS = {
    'L2': CORRECT_V_L2,
    'Lambda': 100,
    'omega': 0.6
}
CORRECT_V_ACC = 0.86
GOOD_ENOUGH_ACC = 0.79


def load_classification_dataset() -> Tuple[Dataset, Dataset, Dataset, Dataset]:
    # Load the breast cancer dataset
    bc_x_full, bc_y_series = datasets.load_breast_cancer(return_X_y=True, as_frame=True)
    assert isinstance(bc_x_full, pd.DataFrame)
    assert isinstance(bc_y_series, pd.Series)
    bc_y = pd.DataFrame({'target': bc_y_series})

    # restrict number of attributes for wider variability of results
    bc_x = bc_x_full.iloc[:, :3]

    test_size = 50
    bc = pd.concat([bc_x, bc_y], axis=1)
    bc_train = bc[:-test_size]
    bc_test = bc[-test_size:].reset_index(drop=True)

    metadata = Metadata(
        roles={RoleName.TARGET: [Column('target')]},
        task=TaskType.BINARY_CLASSIFICATION
    )

    dataset_train = Dataset(metadata=metadata)
    dataset_train.dataframe_table = TableFactory(bc_train)

    dataset_test = Dataset(metadata=metadata)
    dataset_test.dataframe_table = TableFactory(bc_test).drop(['target'])

    ground_truth = Dataset(metadata=metadata)
    ground_truth.dataframe_table = TableFactory({'target': bc_test[['target']]})

    # Create a reduced dataset with only one sample from each class
    train_0_df = dataset_train.dataframe_table[dataset_train.target_table.as_(np.ndarray) == 0]
    train_1_df = dataset_train.dataframe_table[dataset_train.target_table.as_(np.ndarray) == 1]

    reduced_train_df = pd.concat([train_0_df.iloc[-10:-2], train_1_df.iloc[-10:-2]],
                                 axis=0, ignore_index=True)
    reduced_train = Dataset(metadata=metadata)
    reduced_train.dataframe_table = TableFactory(reduced_train_df)

    return (dataset_train, dataset_test, ground_truth, reduced_train)


LOOPBACK = '127.0.0.1'
SUNNY_DAY_PORT = base_port.next()


def test_sunny_day(assert_no_exceptions: Clearer) -> None:
    '''Sunny day with no neighbors produces the same result as sklearn.'''
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

    sklearn_alg = AlgorithmCatalogAuto().lookup_by_name('sklearn.linear_model.LogisticRegression')
    alg = AutonLogisticRegression()

    # Setting Lambda and L2 values to make our results similar to
    #   sklearn's logistic regression, in order to be more certain
    #   that our algorithm is reasonable.
    dut = alg.instantiate(
        distributed=distributed_config,
        L2=CORRECT_V_L2)
    assert isinstance(dut, AutonLogisticRegressionInstance)

    sklearn_dut = sklearn_alg.instantiate(
        C=1 / CORRECT_V_L2,
        penalty='l2',
        fit_intercept=True,
    )

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()

    try:
        dut.start()
        dut.fit(train)
        sklearn_dut.fit(train)

        # sklearn_dut_v = np.array(list(sklearn_dut.impl.coef_.ravel())
        #                          + [sklearn_dut.impl.intercept_[0]])
        # dut_v = dut.params

        result_train = dut.predict(train)
        sklearn_result_train = sklearn_dut.predict(train)
        sklearn_train_acc = metric.calculate(
            pred=sklearn_result_train,
            ground_truth=Dataset(metadata=train.metadata, ground_truth=train['target']))
        result_train_acc = metric.calculate(
            pred=result_train,
            ground_truth=Dataset(metadata=train.metadata, ground_truth=train['target']))

        assert result_train_acc == pytest.approx(expected=sklearn_train_acc, abs=0.01)

        result_test = dut.predict(test)
        sklearn_result_test = sklearn_dut.predict(test)
        sklearn_test_acc = metric.calculate(pred=sklearn_result_test,
                                            ground_truth=ground_truth)
        result_test_acc = metric.calculate(pred=result_test,
                                           ground_truth=ground_truth)

        assert result_test_acc == pytest.approx(expected=sklearn_test_acc, abs=0.01)
        assert result_test_acc == CORRECT_V_ACC
        assert_no_exceptions([dut])

    finally:
        dut.stop()


RECEIVE_EVENT_SENDER_PORT = base_port.next()
RECEIVE_EVENT_RECEIVER_PORT = base_port.next()


def test_receive_event(assert_no_exceptions: Clearer) -> None:
    '''Poor training is improved with information from a neighbor.'''
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
    metric = metric_catalog.lookup_by_name('accuracy_score')

    _, test, ground_truth, reduced_train = load_classification_dataset()

    dut = AutonLogisticRegression().instantiate(distributed=distributed_config, synchronous=True)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, RECEIVE_EVENT_SENDER_PORT))

    # These parameters were hand-extracted from a successful fit.
    message = pickle.dumps((
        1,
        CORRECT_V,
        None
    ))

    try:
        dut.start()
        dut.fit(reduced_train)
        advance([dut])
        check = dut.predict(test)

        # Confirm that the training is bad.
        pretrain_metric = metric.calculate(pred=check, ground_truth=ground_truth)
        assert pretrain_metric < 0.81

        sock.sendto(message, (LOOPBACK, RECEIVE_EVENT_RECEIVER_PORT))

        # Wait for the message to arrive and get processed.
        time.sleep(1.0)

        read_from_neighbors([dut])
        dut.fit(reduced_train)  # fit again on same data to incorporate info from neighbor

        advance([dut])
        # Confirm that we learned from our neighbor.
        got = dut.predict(test)

        posttrain_metric = metric.calculate(pred=got, ground_truth=ground_truth)
        # Did it get better?
        assert posttrain_metric > 0.81

        assert_no_exceptions([dut])
    finally:
        dut.stop()
        sock.close()


SEND_SENDER_PORT = base_port.next()
SEND_RECEIVER_PORT = base_port.next()


def test_send(assert_no_exceptions: Clearer) -> None:
    '''We share our coefficients with a neighbor.'''
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
                    ('1', (LOOPBACK, SEND_SENDER_PORT)),
                    ('2', (LOOPBACK, SEND_RECEIVER_PORT)),
                ],
            },
        },
        'my_id': 1,
    })

    train, _, _, _ = load_classification_dataset()

    receiver = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    receiver.bind((LOOPBACK, SEND_RECEIVER_PORT))
    dut = None

    try:
        dut = AutonLogisticRegression().instantiate(distributed=distributed_config)
        dut.start()
        dut.fit(train)

        got_raw = receiver.recv(1024)  # Wait for the message to arrive and get processed.
        got = AutonLogisticRegressionNeighbor.decode(got_raw)

        assert got.v == pytest.approx(CORRECT_V, abs=0.001)
        assert_no_exceptions([dut])

    finally:
        receiver.close()
        if dut is not None:
            dut.stop()


TWO_SAME_RECEIVER_PORT = base_port.next()
TWO_SAME_SENDER_PORT = base_port.next()


def test_two_same(wait_til_all_fit: Waiter,
                  assert_no_exceptions: Clearer) -> None:
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
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()

    distributed_receiver_clause = deepcopy(distributed_clause)
    distributed_receiver_clause['my_id'] = 1
    distributed_sender_clause = deepcopy(distributed_clause)
    distributed_sender_clause['my_id'] = 2

    alg = AutonLogisticRegression()
    dut_receiver = alg.instantiate(
        distributed=DistributedConfig(distributed_receiver_clause),
        **CORRECT_DIST_PARAMS)
    dut_sender = None
    try:
        dut_receiver.start()
        dut_receiver.fit(train)

        dut_sender = alg.instantiate(
            distributed=DistributedConfig(distributed_sender_clause),
            **CORRECT_DIST_PARAMS)
        dut_sender.start()
        dut_sender.fit(train)

        # Wait for the message to arrive and get processed.
        wait_til_all_fit([dut_receiver, dut_sender], convergence_check=True)

        # Confirm that neighbor optimization doesn't mess up result.
        got_receiver = dut_receiver.predict(test)
        got_sender = dut_sender.predict(test)

        assert metric.calculate(pred=got_receiver,
                                ground_truth=ground_truth
                                ) == CORRECT_V_ACC

        assert metric.calculate(pred=got_sender,
                                ground_truth=ground_truth
                                ) == CORRECT_V_ACC

        assert got_receiver is not None
        assert got_sender is not None

        pd.testing.assert_frame_equal(got_receiver.predictions_table.as_(pd.DataFrame),
                                      got_sender.predictions_table.as_(pd.DataFrame))

        assert dut_sender.params == pytest.approx(dut_receiver.params, abs=0.001)
        assert_no_exceptions([dut_sender, dut_receiver])
    finally:
        dut_receiver.stop()
        if dut_sender is not None:
            dut_sender.stop()


INTEGRATED_RECEIVER_PORT = base_port.next()
INTEGRATED_SENDER_PORT = base_port.next()


def test_integrated(assert_no_exceptions: Clearer) -> None:
    ''''Two nodes talking to each other.

    One gets poor taining, the other gets full training.
    We see that both nodes eventually get good results.
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
        'fit_eps': 0.01
    }

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, reduced_train = load_classification_dataset()
    # TODO(Dan) Catch the case where there is only 1 class in the training data.
    distributed_receiver_clause = deepcopy(distributed_clause)
    distributed_receiver_clause['my_id'] = 1
    distributed_sender_clause = deepcopy(distributed_clause)
    distributed_sender_clause['my_id'] = 2

    alg = AutonLogisticRegression()
    receiver = alg.instantiate(
        distributed=DistributedConfig(distributed_receiver_clause),
        synchronous=True,
        **CORRECT_DIST_PARAMS)

    dut = None
    try:
        receiver.start()
        receiver.fit(reduced_train)

        check = receiver.predict(test)

        pretrain_metric = metric.calculate(pred=check,
                                           ground_truth=ground_truth)
        # Confirm that the training is bad.
        assert pretrain_metric < 0.81

        dut = alg.instantiate(
            distributed=DistributedConfig(distributed_sender_clause),
            synchronous=True,
            **CORRECT_DIST_PARAMS)
        dut.start()
        dut.fit(train)

        # Wait for the message to arrive and get processed.
        for _ in range(3):
            advance([dut, receiver])

        got = receiver.predict(test)

        # Did it get better?
        posttrain_metric = metric.calculate(pred=got,
                                            ground_truth=ground_truth)
        assert posttrain_metric > 0.81
        assert_no_exceptions([dut, receiver])
    finally:
        receiver.stop()
        if dut is not None:
            dut.stop()


TWO_HALF_RECEIVER_PORT = base_port.next()
TWO_HALF_SENDER_PORT = base_port.next()


def test_two_half(assert_no_exceptions: Clearer) -> None:
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
        'fit_eps': 0.001
    }

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()

    n = train['covariates_table'].shape[0]
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
    dist_params_first.update(
        L2=(half_n / n) * CORRECT_DIST_PARAMS['L2'],
        Lambda=10000000)
    dist_params_second = dict(dist_params_first)
    dist_params_second.update(L2=((n - half_n) / n) * CORRECT_DIST_PARAMS['L2'])

    alg = AutonLogisticRegression()
    dut_first = alg.instantiate(
        distributed=DistributedConfig(distributed_receiver_clause),
        synchronous=True,
        **dist_params_first)
    dut_second = None

    try:
        dut_first.start()
        dut_first.fit(train_first)

        advance([dut_first])

        dut_second = alg.instantiate(
            distributed=DistributedConfig(distributed_sender_clause),
            synchronous=True,
            **dist_params_second)
        dut_second.start()
        dut_second.fit(train_second)

        # Wait for the message to arrive and get processed.
        for _ in range(10):
            advance([dut_first, dut_second], min_time=1_000)

        # Confirm that neighbor optimization doesn't mess up result.
        got_receiver = dut_first.predict(test)
        got_sender = dut_second.predict(test)

        assert metric.calculate(pred=got_receiver,
                                ground_truth=ground_truth
                                ) > GOOD_ENOUGH_ACC

        assert metric.calculate(pred=got_sender,
                                ground_truth=ground_truth
                                ) > GOOD_ENOUGH_ACC

        assert got_receiver is not None
        assert got_sender is not None
        pd.testing.assert_frame_equal(got_receiver.predictions_table.as_(pd.DataFrame),
                                      got_sender.predictions_table.as_(pd.DataFrame))

        assert dut_second.params == pytest.approx(dut_first.params, rel=0.01)
        assert_no_exceptions([dut_first, dut_second])
    finally:
        dut_first.stop()
        if dut_second is not None:
            dut_second.stop()


NO_FIT_RECEIVER_PORT = base_port.next()
NO_FIT_SENDER_PORT = base_port.next()


def test_receive_no_fit(wait_til_all_fit: Waiter,
                        assert_no_exceptions: Clearer) -> None:
    '''Test that we spontaneously fit on a message from a neighbor without having seen data.'''
    distributed_config = DistributedConfig(clause={
        'polling_interval': '0.2',
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
    metric = metric_catalog.lookup_by_name('accuracy_score')

    _, test, ground_truth, _ = load_classification_dataset()

    dut = AutonLogisticRegression().instantiate(distributed=distributed_config)
    sorted_ground_truth = ground_truth.sorted_columns()

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, NO_FIT_SENDER_PORT))

    # These parameters were hand-extracted from a successful fit.
    message = pickle.dumps((
        1,
        CORRECT_V,
        None
    ))

    try:
        dut.start()
        sock.sendto(message, (LOOPBACK, NO_FIT_RECEIVER_PORT))

        # Wait for the message to arrive and get processed.
        wait_til_all_fit([dut])

        # Confirm that we learned from our neighbor.
        got = dut.predict(test)

        assert metric.calculate(pred=got,
                                ground_truth=sorted_ground_truth
                                ) > GOOD_ENOUGH_ACC
        assert_no_exceptions([dut])
    finally:
        dut.stop()
        sock.close()


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

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonLogisticRegression()

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc),
        **CORRECT_DIST_PARAMS) for dc in distributed_clauses]
    try:
        for dut in duts:
            dut.start()

        for dut in duts:
            dut.fit(train)

        # Wait for the message to arrive and get processed.
        wait_til_all_fit(duts, convergence_check=True)

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(test) for dut in duts]

        for got_prediction in got_predictions:
            assert metric.calculate(pred=got_prediction,
                                    ground_truth=ground_truth
                                    ) == pytest.approx(CORRECT_V_ACC, rel=0.05)

        gp0 = got_predictions[0]
        assert gp0 is not None
        for i in range(1, n):
            gpi = got_predictions[i]
            assert gpi is not None
            np.testing.assert_array_equal(gp0.predictions_table.as_(np.ndarray),
                                          gpi.predictions_table.as_(np.ndarray))

        for i in range(1, n):
            assert duts[0].params == pytest.approx(duts[i].params, rel=0.05)

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

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonLogisticRegression()

    telephone_params = dict(CORRECT_DIST_PARAMS, Lambda=1)
    telephone_params['omega'] = .5

    params = [dict(telephone_params) if k == 0 else dict(telephone_params) for k in range(n)]

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc),
        **ps) for (dc, ps) in zip(distributed_clauses, params)]
    try:
        for dut in duts:
            dut.start()

        duts[0].fit(train)

        # Wait for the message to arrive and get processed.
        assert wait_til_all_fit(duts, convergence_check=True, min_time=1.0, max_time=60.0), (
            'Timeout waiting for convergence')

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(test) for dut in duts]

        for got_prediction in got_predictions:
            assert metric.calculate(pred=got_prediction,
                                    ground_truth=ground_truth
                                    ) == CORRECT_V_ACC

        gp0 = got_predictions[0]
        assert gp0 is not None
        for i in range(1, n):
            gpi = got_predictions[i]
            assert gpi is not None
            np.testing.assert_array_equal(gp0.predictions_table.as_(np.ndarray),
                                          gpi.predictions_table.as_(np.ndarray))

        for i in range(n - 1):
            assert duts[i].params == pytest.approx(duts[i + 1].params, rel=0.01), (
                f'Node {i} and Node {i + 1} have different parameters'
            )

        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            dut.stop()


CONFLICT_RECEIVER_PORT = base_port.next()
CONFLICT_SENDER_PORT = base_port.next()


# TODO(Merritt/Piggy): investigate this.
@pytest.mark.skip('failing in CI but not locally.  Training gets worse when adding new data.')
def test_node_id_conflict_ok(wait_til_all_fit: Waiter,
                             assert_no_exceptions: Clearer) -> None:
    '''Nodes don't need to agree about which node has which ID.

    In this test, both nodes think they are Node 1.
    '''
    distributed_clause = {
        'polling_interval': '0.1',
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                ]
            }
        },
        'my_id': 1,  # This is the same for both nodes.
        'fit_eps': 0.01
    }

    receiver_clause = deepcopy(distributed_clause)
    assert isinstance(receiver_clause['communicator'], dict)  # to make mypy happy
    assert isinstance(receiver_clause['communicator']['sockets'], dict)  # to make mypy happy
    receiver_clause['communicator']['sockets']['nodes_and_endpoints'] = [
        ('1', (LOOPBACK, CONFLICT_RECEIVER_PORT))
    ]
    receiver_clause['discoverer'] = {
        'name': 'dynamic'
    }

    sender_clause = deepcopy(distributed_clause)
    assert isinstance(sender_clause['communicator'], dict)  # to make mypy happy
    assert isinstance(sender_clause['communicator']['sockets'], dict)  # to make mypy happy
    sender_clause['communicator']['sockets']['nodes_and_endpoints'] = [
        ('1', (LOOPBACK, CONFLICT_SENDER_PORT)),
        ('2', (LOOPBACK, CONFLICT_RECEIVER_PORT))
    ]
    sender_clause['discoverer'] = {
        'name': 'static',
        'static': {
            'adjacency': {
                '1': [2],
            }
        }
    }

    receiver_config = DistributedConfig(receiver_clause)
    sender_config = DistributedConfig(sender_clause)

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()
    reduced_train = Dataset({
        'covariates_table': TableFactory(
            train['covariates_table'].as_(pd.DataFrame).iloc[516:517] * 0),
        'target_table': TableFactory(
            train['target_table'].as_(pd.DataFrame).iloc[516:517])
    }, metadata=train.metadata)

    alg = AutonLogisticRegression()
    receiver = alg.instantiate(distributed=receiver_config)
    sender = None
    try:
        receiver.start()
        receiver.fit(reduced_train)

        assert wait_til_all_fit([receiver], convergence_check=False), (
            'Timeout waiting for fit'
        )

        check = receiver.predict(test)

        # Confirm that the training is very bad.
        assert metric.calculate(pred=check,
                                ground_truth=ground_truth
                                ) == pytest.approx(expected=0.8, abs=0.01)

        sender = alg.instantiate(distributed=sender_config)
        sender.start()
        sender.fit(train)

        # Wait for the message to arrive and get processed.
        assert wait_til_all_fit([sender, receiver]), (
            'Timeout waiting for fit'
        )

        # Confirm that we learned from our neighbor.
        got = receiver.predict(test)

        assert metric.calculate(pred=got,
                                ground_truth=ground_truth
                                ) > 0.8
        assert_no_exceptions([sender, receiver])
    finally:
        receiver.stop()
        if sender is not None:
            sender.stop()


def load_multiclass_dataset() -> Tuple[Dataset, Dataset, Dataset]:
    # Load the iris dataset
    bc_x_full, bc_y_series = datasets.load_iris(return_X_y=True, as_frame=True)
    assert isinstance(bc_x_full, pd.DataFrame)
    assert isinstance(bc_y_series, pd.Series)
    bc_y = pd.DataFrame({'target': bc_y_series})

    # restrict number of attributes for wider variability of results
    bc_x = bc_x_full.iloc[:, :3]

    # shuffle our data
    bc_x = bc_x.sample(frac=1, random_state=1701)
    bc_y = bc_y.sample(frac=1, random_state=1701)

    test_size = 50
    # Split the data into training/testing sets
    bc_x_train = bc_x[:-test_size]
    bc_x_test = bc_x[-test_size:]

    # Split the targets into training/testing sets
    bc_y_train = bc_y[:-test_size]
    bc_y_test = bc_y[-test_size:]

    metadata = Metadata(
        roles={RoleName.TARGET: [Column('target')]},
        task=TaskType.BINARY_CLASSIFICATION
    )

    dataset_train = Dataset(
        metadata=metadata,
        covariates_table=TableFactory(bc_x_train),
        target_table=TableFactory(bc_y_train)
    )

    dataset_test = Dataset(
        metadata=metadata,
        covariates_table=TableFactory(bc_x_test)
    )
    ground_truth = Dataset(
        metadata=metadata,
        ground_truth=bc_y_test
    )
    return (dataset_train, dataset_test, ground_truth)


@pytest.mark.skip(reason='Distributed logistic regression does not support multiclass yet.')
def test_multiclass(assert_no_exceptions: Clearer) -> None:
    '''Non-distributed multiclass classification.'''
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

    alg = AutonLogisticRegression()
    sklearn_alg = AlgorithmCatalogAuto().lookup_by_name('sklearn.linear_model.LogisticRegression')
    assert isinstance(sklearn_alg, SklearnAlgorithm)

    # Setting Lambda and L2 values to make our results similar to
    #   sklearn's logistic regression, in order to be more certain
    #   that our algorithm is reasonable.
    dut = alg.instantiate(
        distributed=distributed_config,
        L2=CORRECT_V_L2)
    sklearn_instance = sklearn_alg.instantiate(
        C=1 / CORRECT_V_L2,
        penalty='l2',
        fit_intercept=True,
    )

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth = load_multiclass_dataset()
    try:
        dut.start()
        dut.fit(train)
        sklearn_instance.fit(train)

        result = dut.predict(test)
        result_sklearn = sklearn_instance.predict(test)

        dut_acc = metric.calculate(pred=result,
                                   ground_truth=ground_truth)
        sklearn_acc = metric.calculate(pred=result_sklearn,
                                       ground_truth=ground_truth)
        assert dut_acc == pytest.approx(sklearn_acc, rel=.001)
        assert_no_exceptions([dut])
    finally:
        dut.stop()


TEST_N_SAME_N_DJAM = 5
TEST_N_SAME_PORTS_DJAM = [base_port.next() for _ in range(TEST_N_SAME_N_DJAM)]


def test_n_same_djam(assert_no_exceptions: Clearer) -> None:
    '''N nodes fully connected with the same training match the non-distributed result.'''
    n = TEST_N_SAME_N_DJAM

    adjacency = {f'{k}': [j for j in range(0, n) if j != k] for k in range(0, n)}
    nodes_and_endpoints = [(f'{k}', (LOOPBACK, TEST_N_SAME_PORTS_DJAM[k])) for k in range(0, n)]

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
        'regularization': {
            'name': 'djam',
            'weight_matrix': [
                [0, 1, 1, 1, 1],
                [1, 0, 1, 1, 1],
                [1, 1, 0, 1, 1],
                [1, 1, 1, 0, 1],
                [1, 1, 1, 1, 0]
            ]
        },
        'my_id': 0,
    }

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(0, n)]

    alg = AutonLogisticRegression()

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
        advance(duts)

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(test) for dut in duts]

        for got_prediction in got_predictions:
            assert metric.calculate(pred=got_prediction,
                                    ground_truth=ground_truth
                                    ) == pytest.approx(CORRECT_V_ACC, rel=0.01)

        gp0 = got_predictions[0]
        assert gp0 is not None
        for i in range(1, n):
            gpi = got_predictions[i]
            assert gpi is not None
            np.testing.assert_array_equal(gp0.predictions_table.as_(np.ndarray),
                                          gpi.predictions_table.as_(np.ndarray))

        for i in range(1, n):
            assert duts[0].params == pytest.approx(duts[i].params, rel=0.05)

        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            dut.stop()


TEST_TELEPHONE_N_DJAM = 5
TEST_TELEPHONE_PORTS_DJAM = [base_port.next() for _ in range(TEST_TELEPHONE_N_DJAM)]


def test_telephone_djam(wait_til_all_fit: Waiter,
                        assert_no_exceptions: Clearer) -> None:
    '''Whisper down the lane test. Nodes connected in a line.
    The only node that has data is one at the end '''
    n = TEST_TELEPHONE_N_DJAM

    adjacency = {f'{k}': [k - 1, k + 1] for k in range(1, n - 1)}
    adjacency['0'] = [1]
    adjacency[f'{n-1}'] = [n - 2]
    nodes_and_endpoints = [(f'{k}', (LOOPBACK, TEST_TELEPHONE_PORTS_DJAM[k]))
                           for k in range(0, n)]

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
        'regularization': {
            'name': 'djam',
            'weight_matrix': [
                [0, 1, 0, 0, 0],
                [1, 0, 1, 0, 0],
                [0, 1, 0, 1, 0],
                [0, 0, 1, 0, 1],
                [0, 0, 0, 1, 0]
            ]
        },
        'my_id': 0,
    }

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    train, test, ground_truth, _ = load_classification_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(0, n)]

    alg = AutonLogisticRegression()

    telephone_params = dict(CORRECT_DIST_PARAMS, Lambda=1)
    telephone_params['omega'] = .5

    params = [dict(telephone_params) if k == 0 else dict(telephone_params) for k in range(n)]

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc),
        **ps) for (dc, ps) in zip(distributed_clauses, params)]
    try:
        for dut in duts:
            dut.start()

        duts[0].fit(train)

        # Wait for the message to arrive and get processed.
        assert wait_til_all_fit(duts, convergence_check=True, min_time=1.0), (
            'Timeout waiting for convergence'
        )

        # Confirm that neighbor optimization doesn't mess up result.
        got_predictions = [dut.predict(test) for dut in duts]

        for got_prediction in got_predictions:
            assert metric.calculate(pred=got_prediction,
                                    ground_truth=ground_truth
                                    ) == CORRECT_V_ACC

        gp0 = got_predictions[0]
        assert gp0 is not None
        for i in range(1, n):
            gpi = got_predictions[i]
            assert gpi is not None
            np.testing.assert_array_equal(gp0.predictions_table.as_(np.ndarray),
                                          gpi.predictions_table.as_(np.ndarray))

        for i in range(n - 1):
            assert duts[i].params == pytest.approx(duts[i + 1].params, rel=0.01)

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

    _, _, _, reduced_train = load_classification_dataset()

    dut = AutonLogisticRegression().instantiate(
        distributed=distributed_config, synchronous=True, **CORRECT_DIST_PARAMS)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, COLS_SENDER_PORT))

    # These parameters were hand-extracted from a successful fit.
    match_message = pickle.dumps((
        1, CORRECT_V, reduced_train.dataframe_table.columns
    ))

    mismatch_message = pickle.dumps((
        1, CORRECT_V, reduced_train.dataframe_table.columns + ['hamster']
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
        assert 'mismatch' in str(got[1])
        assert 'hamster' in str(got[1])

        # make sure there are no other exceptions we don't expect
        assert_no_exceptions([dut])

    finally:
        dut.stop()
        sock.close()


def test_roc(assert_no_exceptions: Clearer) -> None:
    '''Test bug where distributed logistic regression fails for ranking with roc'''
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

    alg = AutonLogisticRegression()

    dut = alg.instantiate(
        distributed=distributed_config)
    assert isinstance(dut, AutonLogisticRegressionInstance)
    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('roc_auc_score')

    train, test, ground_truth, _ = load_classification_dataset()

    try:
        dut.start()
        dut.fit(train)

        result = dut.predict(test)

        metric.calculate(
            pred=result,
            ground_truth=ground_truth)

        assert_no_exceptions([dut])

    finally:
        dut.stop()
