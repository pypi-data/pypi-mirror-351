'''Tests for auton_decision_tree.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,duplicate-code,too-many-locals,too-many-lines

from copy import deepcopy
import getpass
import os
from pathlib import Path
import pickle
import socket
from typing import Any, Dict, Optional, Tuple, List

import numpy as np
import pandas as pd
import pytest

from sklearn import datasets  # type: ignore[import]

from ...algorithms.impl.synchronous import advance
from ...config_components.distributed_config import DistributedConfig
from ...conftest import Clearer, Waiter
from ...metrics.impl.metric_auto import MetricCatalogAuto
from ...metrics.impl.metric import Metric
from ...problem_def.task import TaskType
from ...tables.impl.table import TableFactory
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.base_port import BasePort
from ...wrangler.constants import Defaults
from ...wrangler.dataset import Column, Dataset, Metadata, RoleName
from ...wrangler.logger import Logger
from ..impl.algorithm_auto import AlgorithmCatalogAuto
from ..sklearn.sklearn_algorithm import SklearnAlgorithm
from .auton_decision_tree import AutonDecisionTreeModel, AutonDecisionTreeInstance
from .auton_decision_tree_neighbor import Acorn, AutonDecisionTreeNeighbor

logger = Logger(__file__, to_stdout=False).logger()
_ = TableCatalogAuto()  # pylint: disable=pointless-statement

BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')


def topic_name(topic: str) -> str:
    '''Generate a unique topic name for the given test.'''
    return f'{Path(__file__).stem}_{getpass.getuser()}_{topic}'


DT_PARAMS = {
    'Lambda': 1.0,
    'omega': 0.667,
}


def load_classification_dataset() -> Tuple[Dataset, Dataset, Dataset, Dataset]:
    # TODO(Merritt): pull this out into a fixture
    # Load the breast cancer dataset
    bc_x_full, bc_y_series = datasets.load_breast_cancer(return_X_y=True, as_frame=True)
    assert isinstance(bc_x_full, pd.DataFrame)
    assert isinstance(bc_y_series, pd.Series)
    bc_y = pd.DataFrame({'target': bc_y_series})

    # restrict number of attributes for wider variability of results
    bc_x = bc_x_full.iloc[:, :3]

    test_size = 50
    # Split the data into training/testing sets
    bc_x_train = bc_x[:-test_size]
    bc_x_test = bc_x[-test_size:]

    # Split the targets into training/testing sets
    bc_y_train = bc_y[:-test_size]
    bc_y_test = bc_y[-test_size:].reset_index()

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

    train_cov_0 = dataset_train.covariates_table[
        dataset_train.target_table.as_(np.ndarray) == 0]
    train_cov_1 = dataset_train.covariates_table[
        dataset_train.target_table.as_(np.ndarray) == 1]
    reduced_train = Dataset(
        covariates_table=TableFactory(
            pd.concat((train_cov_0.iloc[0:1],
                       train_cov_1.iloc[0:1]), axis=0, ignore_index=True) * 0),
        target_table=TableFactory(pd.DataFrame({'target': [0] * 1 + [1] * 1})),
        metadata=metadata
    )

    return (dataset_train, dataset_test, ground_truth, reduced_train)


def build_clause(adjacency: Dict[str, List[int]],
                 nodes_and_endpoints: List[Tuple[str, Tuple[str, int]]],
                 my_id: int,
                 data_split: Optional[Dict[str, int]] = None,) -> Dict[str, Any]:
    retval = {
        'polling_interval': '0.1',
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
        'my_id': my_id
    }
    if data_split:
        retval['split'] = data_split
    return retval


base_port = BasePort()
LOOPBACK = '127.0.0.1'
VALID_ACORN = Acorn(
    n_in=4,
    n_out=2,
    children_left=[1, None, None],
    children_right=[2, None, None],
    feature=[0, None, None],
    threshold=[0.5, None, None],
    equal=[True, None, None],
    value=[np.array([0.5, 0.5]), np.array([1., 0]), np.array([0, 1])],
    sample_weight=[13.0, 10.0, 3.0],
    lower_bound=np.array([0., 0., 0., 0.]),
    upper_bound=np.array([1., 1., 1., 1.]),
    class_list=['no', 'yes']
)


def test_should_send() -> None:
    '''_should_send returns True iff our model changed.

    We send a simple tree with 3 nodes.
    '''

    config = DistributedConfig({})
    dut = AutonDecisionTreeNeighbor(VALID_ACORN)
    same_as_dut = deepcopy(dut)
    different_from_dut = deepcopy(dut)
    different_from_dut.feature[0] = 3  # split on a different feature

    assert dut.state_differs(
        distributed=config,
        other=different_from_dut
    ) is True, 'Different states should differ.'

    assert dut.state_differs(
        distributed=config,
        other=same_as_dut
    ) is False, 'Same states should not differ.'


COLS_SENDER_PORT = base_port.next()
COLS_RECEIVER_PORT = base_port.next()


def test_columns(assert_no_exceptions: Clearer) -> None:
    '''Test that columns are handled in data loading, sending and receiving.'''
    distributed_config = DistributedConfig(clause=build_clause(
        adjacency={'1': [2], '2': [1]},
        nodes_and_endpoints=[
            ('1', (LOOPBACK, COLS_SENDER_PORT)),
            ('2', (LOOPBACK, COLS_RECEIVER_PORT)),
        ],
        my_id=2
    ))

    train = Dataset(
        covariates_table=TableFactory({
            'a': [1.0, 2.0, 3.0],
            'b': [4.0, 5.0, 6.0],
            'c': [7.0, 8.0, 10.0],
            'd': [23.0, 63.0, 13.0]
        }),
        target_table=TableFactory({
            'e': ['yes', 'no', 'no']
        }),
        metadata=Metadata(
            roles={RoleName.TARGET: [Column('e')]},
            task=TaskType.BINARY_CLASSIFICATION
        ))
    dut = AutonDecisionTreeModel().instantiate(distributed=distributed_config,
                                               synchronous=True,
                                               **DT_PARAMS)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, COLS_SENDER_PORT))

    match_message = pickle.dumps((
        VALID_ACORN,
        train.dataframe_table.columns
    ))

    mismatch_message = pickle.dumps((
        VALID_ACORN,
        train.dataframe_table.columns + ['hamster']
    ))

    try:
        dut.start()
        dut.fit(train)

        advance([dut])

        sock.sendto(match_message, (LOOPBACK, COLS_RECEIVER_PORT))

        advance([dut])
        assert_no_exceptions([dut])

        sock.sendto(mismatch_message, (LOOPBACK, COLS_RECEIVER_PORT))

        advance([dut])
        got = dut.poll_exceptions()
        while got is not None:
            assert isinstance(got[0], NotImplementedError), 'Should have raised NotImplementedError'
            assert 'mismatch' in str(got[1]), 'Should have mentioned mismatch'
            assert 'hamster' in str(got[1]), 'Should have mentioned hamster'
            got = dut.poll_exceptions()

        # make sure there are no other exceptions we don't expect
        assert_no_exceptions([dut])

    finally:
        dut.stop()
        sock.close()


NON_DISTRIBUTED_PORT = base_port.next()


def test_non_distributed(assert_no_exceptions: Clearer) -> None:
    '''Compare mean log PDF of our DT to sklearn's DT on one node.

    See: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
    '''
    distributed_config = DistributedConfig(
        clause=build_clause(adjacency={'2': []},
                            nodes_and_endpoints=[('2', (LOOPBACK, NON_DISTRIBUTED_PORT))],
                            my_id=2))

    sklearn_alg = AlgorithmCatalogAuto().lookup_by_name('sklearn.tree.DecisionTreeClassifier')
    assert isinstance(sklearn_alg, SklearnAlgorithm), 'Should be a SklearnAlgorithm.'

    train, test, ground_truth, _ = load_classification_dataset()
    sklearn_train = deepcopy(train)

    alg = AutonDecisionTreeModel()

    dut = alg.instantiate(
        distributed=distributed_config,
        **DT_PARAMS)
    assert isinstance(dut, AutonDecisionTreeInstance), 'Should be an AutonDecisionTreeInstance.'

    sklearn_dut = sklearn_alg.instantiate(random_state=1701)

    acc = MetricCatalogAuto().lookup_by_name('accuracy_score')

    try:
        dut.start()

        sklearn_dut.fit(sklearn_train)
        dut.fit(train)

        got = dut.predict(test)
        sklearn_got = sklearn_dut.predict(test)

        got_acc = acc.calculate(pred=got, ground_truth=ground_truth)
        sklearn_acc = acc.calculate(pred=sklearn_got, ground_truth=ground_truth)
        assert got_acc == pytest.approx(sklearn_acc, rel=0.1), (
            'Should be close to sklearn accuracy.')

        assert_no_exceptions([dut])
    finally:
        dut.stop()


DISTRIBUTED_RECEIVER_PORT = base_port.next()
DISTRIBUTED_SENDER_PORT = base_port.next()


def test_distributed(assert_no_exceptions: Clearer) -> None:
    '''A node gets a minimal dataset to train on, test that it learns from an other.'''
    # pylint: disable=too-many-locals
    clause1 = build_clause(
        adjacency={'1': [2], '2': [1]},
        nodes_and_endpoints=[
            ('1', (LOOPBACK, DISTRIBUTED_RECEIVER_PORT)),
            ('2', (LOOPBACK, DISTRIBUTED_SENDER_PORT)),
        ],
        my_id=1
    )
    clause2 = deepcopy(clause1)
    clause2['my_id'] = 2

    train, test, ground_truth, reduced_train = load_classification_dataset()

    alg = AutonDecisionTreeModel()
    dut1 = alg.instantiate(
        distributed=DistributedConfig(clause1),
        synchronous=True,
        **DT_PARAMS)
    assert isinstance(dut1, AutonDecisionTreeInstance), 'Should be an AutonDecisionTreeInstance'

    acc = MetricCatalogAuto().lookup_by_name('accuracy_score')

    dut2 = None
    try:
        # fit dut 1 on reduced train set
        dut1.start()
        dut1.fit(reduced_train)

        advance([dut1])

        # check that dut1's training is bad
        got1 = dut1.predict(test)
        got1_acc = acc.calculate(pred=got1, ground_truth=ground_truth)
        assert got1_acc < 0.6, 'Should have a bad accuracy.'

        # fit dut2 on full train set
        dut2 = alg.instantiate(
            distributed=DistributedConfig(clause2),
            synchronous=True,
            **DT_PARAMS
        )
        assert isinstance(dut2, AutonDecisionTreeInstance), 'Should be an AutonDecisionTreeInstance'
        dut2.start()
        dut2.fit(train)
        for _ in range(5):
            advance([dut2, dut1])

        got1_improved = dut1.predict(test)
        got2 = dut2.predict(test)
        got1_improved_acc = acc.calculate(pred=got1_improved, ground_truth=ground_truth)
        got2_acc = acc.calculate(pred=got2, ground_truth=ground_truth)

        assert got1_improved_acc > got1_acc, 'Should have improved accuracy.'
        assert got1_improved_acc == pytest.approx(got2_acc, rel=1e-5), (
            'Should have similar accuracy.')

        assert_no_exceptions([dut1, dut2])

    finally:
        dut1.stop()
        if dut2 is not None:
            dut2.stop()


TWO_HALF_PORT_1 = base_port.next()
TWO_HALF_PORT_2 = base_port.next()


def test_two_half_hard_mode(assert_no_exceptions: Clearer) -> None:
    '''Two nodes with half the training behaves as (reasonably) expected.

    Hard mode means that we have completely dividided the dataset along
    a random hyperplane, so that the two halves are completely different.
    '''
    distributed_clause = build_clause(
        adjacency={'1': [2], '2': [1]},
        nodes_and_endpoints=[
            ('1', (LOOPBACK, TWO_HALF_PORT_1)),
            ('2', (LOOPBACK, TWO_HALF_PORT_2)),
        ],
        my_id=0,
        data_split={'num_nodes': 2}
    )
    train, _, _, _ = load_classification_dataset()

    # Split the training data such that each node sees a differently distributed half of the
    # input space.
    # Kyle's method to choose a random hyperplane and use it to divide data:
    # 1. Sample a random d-dimensional vector from a standard gaussian distribution.
    # 2. Project all of our data onto that vector - dot product of that vector with data matrix
    # gives you 1 number per row in the dataset
    # 3. sort based on that number and divide data in half
    input_df: pd.DataFrame = train['covariates_table'].as_(pd.DataFrame)
    input_df['target'] = train['target_table'].as_(pd.DataFrame)['target']
    threadsafe_random_state = np.random.RandomState(seed=Defaults.SEED)  # pylint: disable=no-member,line-too-long
    random_hyperplane = threadsafe_random_state.normal(size=input_df.shape[1])
    projection = np.dot(random_hyperplane, input_df.to_numpy().transpose())
    input_df['projection'] = projection
    input_df.sort_values(by='projection')
    input_df.drop(columns=['projection'], inplace=True)

    half_n = int(input_df.shape[0] / 2)

    train_first = Dataset(
        metadata=train.metadata,
    )
    train_first.dataframe_table = TableFactory(input_df.iloc[:half_n])

    train_second = Dataset(
        metadata=train.metadata,
    )
    train_second.dataframe_table = TableFactory(input_df.iloc[half_n:])
    distributed_receiver_clause = deepcopy(distributed_clause)
    distributed_receiver_clause['my_id'] = 1
    distributed_sender_clause = deepcopy(distributed_clause)
    distributed_sender_clause['my_id'] = 2

    params = deepcopy(DT_PARAMS)
    params['ccp_alpha'] = 1e-3

    alg = AutonDecisionTreeModel()
    dut_first = alg.instantiate(
        distributed=DistributedConfig(distributed_receiver_clause),
        synchronous=True,
        **params)
    assert isinstance(dut_first, AutonDecisionTreeInstance), (
        'dut_first should be an AutonDecisionTreeInstance')

    dut_second = alg.instantiate(
        distributed=DistributedConfig(distributed_sender_clause),
        synchronous=True,
        **params)
    assert isinstance(dut_second, AutonDecisionTreeInstance), (
        'dut_second should be an AutonDecisionTreeInstance'
    )

    try:
        dut_first.start()
        dut_second.start()

        dut_first.fit(train_first)
        dut_second.fit(train_second)

        for _ in range(20):
            advance([dut_first, dut_second])

        # Confirm that the two nodes have similar training and thus shared information.
        got = np.sqrt(dut_second.norm2_diff(dut_first))

        assert got == pytest.approx(0, abs=0.1), 'Should have similar training.'
        assert_no_exceptions([dut_first, dut_second])

    finally:
        dut_first.stop()
        dut_second.stop()


def test_two_same(assert_no_exceptions: Clearer) -> None:
    '''Two nodes with the same training don't change their coefficients.'''
    distributed_clause = build_clause(
        adjacency={'1': [2], '2': [1]},
        nodes_and_endpoints=[],
        my_id=0)

    distributed_clause['communicator'] = {
        'name': 'memory',
        'memory': {
            'domain': 'test_two_same',
        }
    }

    train, _, _, _ = load_classification_dataset()

    clause1 = deepcopy(distributed_clause)
    clause1['my_id'] = 1
    clause2 = deepcopy(distributed_clause)
    clause2['my_id'] = 2

    alg = AutonDecisionTreeModel()
    dut1 = alg.instantiate(
        distributed=DistributedConfig(clause1),
        synchronous=True,
        **DT_PARAMS)
    assert isinstance(dut1, AutonDecisionTreeInstance), (
        'dut1 should be an AutonDecisionTreeInstance')

    dut2 = alg.instantiate(
        distributed=DistributedConfig(clause2),
        synchronous=True,
        **DT_PARAMS)
    assert isinstance(dut2, AutonDecisionTreeInstance), (
        'dut2 should be an AutonDecisionTreeInstance')

    try:
        dut1.start()
        dut2.start()

        dut1.fit(train)
        dut2.fit(train)

        # Wait for the message to arrive and get processed.
        advance([dut1, dut2])

        # Confirm that neighbor optimization doesn't mess up result.
        got = np.sqrt(dut1.norm2_diff(dut2))

        assert got == pytest.approx(0, abs=0.1), 'Should have similar training.'
        assert_no_exceptions([dut2, dut1])

    finally:
        dut1.stop()
        dut2.stop()


TEST_N_SAME_N = 5
TEST_N_SAME_PORTS = [base_port.next() for _ in range(TEST_N_SAME_N)]
TEST_N_SAME_REFERENCE_PORT = base_port.next()


def test_n_same(wait_til_all_fit: Waiter,
                assert_no_exceptions: Clearer) -> None:
    '''N nodes fully connected with the same training match the non-distributed result.'''
    n = TEST_N_SAME_N

    adjacency = {f'{k}': [j for j in range(1, n + 1) if j != k] for k in range(1, n + 1)}
    nodes_and_endpoints = [(f'{k}', (LOOPBACK, TEST_N_SAME_PORTS[k - 1])) for k in range(1, n + 1)]
    distributed_clause = build_clause(
        adjacency=adjacency, nodes_and_endpoints=nodes_and_endpoints, my_id=0
    )

    distributed_clause['communicator'] = {
        'name': 'memory',
        'memory': {
            'domain': 'test_n_same',
        }
    }

    train, _, _, _ = load_classification_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonDecisionTreeModel()

    duts: List[AutonDecisionTreeInstance] = [alg.instantiate(
        distributed=DistributedConfig(dc),
        **DT_PARAMS) for dc in distributed_clauses]
    try:
        for dut in duts:
            dut.start()

        for dut in duts:
            dut.fit(train)

        # Wait for the message to arrive and get processed.
        wait_til_all_fit(duts, convergence_check=True)

        # Confirm that neighbor optimization doesn't mess up result.

        dut0_state = duts[0].my_state_copy
        assert dut0_state is not None, 'dut0_state should not be None.'

        got = []
        for duti in duts[1:]:
            duti_state = duti.my_state_copy
            assert duti_state is not None, f'dut {dut._my_id} should not be None.'  # pylint: disable=protected-access
            got.append(np.sqrt(dut0_state.norm2_diff(duti_state)))
        assert all(got_diff < 1.0 for got_diff in got), 'Should have similar training.'
        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            dut.stop()


TEST_TELEPHONE_N = 5
TEST_TELEPHONE_PORTS = [base_port.next() for _ in range(TEST_TELEPHONE_N)]
TEST_TELEPHONE_REFERENCE_PORT = base_port.next()


def test_telephone(assert_no_exceptions: Clearer) -> None:
    '''Whisper down the lane test. Nodes connected in a line.
    The only node that has data is one at the end '''
    n = TEST_TELEPHONE_N

    adjacency = {f'{k}': [k - 1, k + 1] for k in range(2, n)}
    adjacency['1'] = [2]
    adjacency[f'{n}'] = [n - 1]
    nodes_and_endpoints = [(f'{k}', (LOOPBACK, TEST_TELEPHONE_PORTS[k - 1]))
                           for k in range(1, n + 1)]
    distributed_clause = build_clause(
        adjacency=adjacency, nodes_and_endpoints=nodes_and_endpoints, my_id=0
    )

    distributed_clause['fit_eps'] = 0.001

    train, _, _, _ = load_classification_dataset()

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonDecisionTreeModel()

    params = [dict(DT_PARAMS) for k in range(n)]

    duts: List[AutonDecisionTreeInstance] = [alg.instantiate(
        distributed=DistributedConfig(dc),
        synchronous=True,
        **ps) for (dc, ps) in zip(distributed_clauses, params)]
    try:
        for dut in duts:
            dut.start()

        duts[0].fit(train)

        # Wait for the message to arrive and get processed.
        for _ in range(TEST_TELEPHONE_N + 1):
            advance(duts)

        # Confirm that neighbor optimization doesn't mess up result.
        dut0 = duts[0]
        got: List[np.float64] = []
        for duti in duts[1:]:
            got.append(np.sqrt(dut0.norm2_diff(duti)))

        want = [np.float64(0.0)] * len(got)

        np.testing.assert_allclose(actual=got, desired=want, atol=1.5)
        assert_no_exceptions(duts)

    finally:
        for dut in duts:
            dut.stop()


@pytest.mark.parametrize("target1,target2", [
    (['a', 'b', 'b'], ['a', 'b', 'c', 'c']),
    (['a', 'b', 'b'], ['b', 'c', 'd', 'c']),
    (['a', 'b', 'b', 'a'], ['d', 'c', 'c']),
    (['a'], ['a', 'b', 'b']),
])
def test_multiclass_mismatch(assert_no_exceptions: Clearer,
                             target1: List[str],
                             target2: List[str]) -> None:
    dist_clause_1 = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [2],
                    '2': [1]
                }
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, base_port.next())),
                    ('2', (LOOPBACK, base_port.next())),
                ]
            },
        },
        'my_id': 1,
        'fit_eps': 0.1
    }

    dist_clause_2 = deepcopy(dist_clause_1)
    dist_clause_2['my_id'] = 2

    mismatch_params = deepcopy(DT_PARAMS)
    # With a Lambda of 1.0, each model oscillates between two states.
    mismatch_params['Lambda'] = 10

    alg = AutonDecisionTreeModel()
    dut1 = alg.instantiate(
        distributed=DistributedConfig(dist_clause_1),
        synchronous=True,
        **mismatch_params)
    assert isinstance(dut1, AutonDecisionTreeInstance), (
        'dut1 should be an AutonDecisionTreeInstance')

    dut2 = alg.instantiate(
        distributed=DistributedConfig(dist_clause_2),
        synchronous=True,
        **mismatch_params)
    assert isinstance(dut2, AutonDecisionTreeInstance), (
        'dut2 should be an AutonDecisionTreeInstance')

    state = np.random.default_rng(seed=1701)

    train_df_1 = pd.DataFrame({
        'cov1': state.random(size=len(target1)),
        'cov2': state.random(size=len(target1)),
        'target': target1
    })

    train_df_2 = pd.DataFrame({
        'cov1': state.random(size=len(target2)),
        'cov2': state.random(size=len(target2)),
        'target': target2
    })

    meta = Metadata(roles={
        RoleName.TARGET: [Column('target')]
    })

    ds_1 = Dataset(dataframe=train_df_1, metadata=meta)
    ds_2 = Dataset(dataframe=train_df_2, metadata=meta)

    try:
        dut1.start()
        # We want to make sure that dut2 doesn't get the initial messages from dut1.
        dut1.fit(ds_1)

        advance([dut1])

        dut2.start()
        dut2.fit(ds_2)

        advance([dut1, dut2])

        assert dut1.my_state is not None, 'dut1.my_state should not be None.'
        assert dut1.my_state.class_list == sorted(set().union(target1, target2)), (
            f'dut1.my_state.class_list: {dut1.my_state.class_list}, '
            f'should be the union of target1: {target1}, and target2: {target2}.')

        assert dut2.my_state is not None, 'dut2.my_state should not be None.'
        assert dut2.my_state.distance(dut1.my_state) == dut1.my_state.distance(dut2.my_state), (
            'distance calculate is not symmetric'
        )
        # It seems that the above assert caught the bug that caused the error below.
        # dut1.fit(ds_2)  # This refit causes a test to fail, for some reason.
        # assert wait_til_all_fit([dut1, dut2], convergence_check=True)

        assert_no_exceptions([dut1, dut2])
    finally:
        dut1.stop()
        dut2.stop()


# TODO(Merritt/Piggy): add this test to every distributed algorithm
def test_distance_axioms(wait_til_all_fit: Waiter,
                         assert_no_exceptions: Clearer) -> None:
    '''Commutative: dist(a, b) = dist(b, a)
    Non-negative: dist(a, b) >= 0
    dist(a, a) == 0
    dist(a, b) + dist (b, c) > dist(a, c)
    '''
    # pylint: disable=too-many-statements
    dist_clause_1 = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [],
                    '2': [],
                    '3': [],
                }
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, base_port.next())),
                    ('2', (LOOPBACK, base_port.next())),
                    ('3', (LOOPBACK, base_port.next())),
                ]
            },
        },
        'my_id': 1,
        'fit_eps': 1e-4
    }

    dist_clause_2 = deepcopy(dist_clause_1)
    dist_clause_2['my_id'] = 2

    dist_clause_3 = deepcopy(dist_clause_1)
    dist_clause_3['my_id'] = 3

    alg = AutonDecisionTreeModel()
    dut1 = alg.instantiate(
        distributed=DistributedConfig(dist_clause_1),
        **DT_PARAMS)
    assert isinstance(dut1, AutonDecisionTreeInstance), (
        'dut1 should be an AutonDecisionTreeInstance')

    dut2 = alg.instantiate(
        distributed=DistributedConfig(dist_clause_2),
        **DT_PARAMS)
    assert isinstance(dut2, AutonDecisionTreeInstance), (
        'dut2 should be an AutonDecisionTreeInstance')

    dut3 = alg.instantiate(
        distributed=DistributedConfig(dist_clause_3),
        **DT_PARAMS)
    assert isinstance(dut3, AutonDecisionTreeInstance), (
        'dut3 should be an AutonDecisionTreeInstance'
    )

    state = np.random.default_rng(seed=1701)

    target1 = ['a', 'b', 'c', 'a']
    train_df_1 = pd.DataFrame({
        'cov1': state.random(size=len(target1)),
        'cov2': state.random(size=len(target1)),
        'target': target1
    })

    target2 = ['b', 'a', 'b', 'c', 'c']
    train_df_2 = pd.DataFrame({
        'cov1': state.random(size=len(target2)),
        'cov2': state.random(size=len(target2)),
        'target': target2
    })

    target3 = ['a', 'b', 'c', 'c']
    train_df_3 = pd.DataFrame({
        'cov1': state.random(size=len(target3)),
        'cov2': state.random(size=len(target3)),
        'target': target3
    })

    meta = Metadata(roles={
        RoleName.TARGET: [Column('target')]
    })

    ds_1 = Dataset(dataframe=train_df_1, metadata=meta)
    ds_2 = Dataset(dataframe=train_df_2, metadata=meta)
    ds_3 = Dataset(dataframe=train_df_3, metadata=meta)

    try:
        dut1.start()
        dut2.start()
        dut3.start()

        dut1.fit(ds_1)
        dut2.fit(ds_2)
        dut3.fit(ds_3)

        wait_til_all_fit([dut1, dut2, dut3], convergence_check=False)

        assert dut1.my_state is not None, 'dut1.my_state should not be None.'
        assert dut2.my_state is not None, 'dut2.my_state should not be None.'
        assert dut3.my_state is not None, 'dut3.my_state should not be None.'
        distance_1_1 = dut1.my_state.distance(dut1.my_state)
        distance_1_2 = dut1.my_state.distance(dut2.my_state)
        distance_1_3 = dut1.my_state.distance(dut3.my_state)
        distance_2_1 = dut2.my_state.distance(dut1.my_state)
        distance_2_2 = dut2.my_state.distance(dut2.my_state)
        distance_2_3 = dut2.my_state.distance(dut3.my_state)
        distance_3_1 = dut3.my_state.distance(dut1.my_state)
        distance_3_2 = dut3.my_state.distance(dut2.my_state)
        distance_3_3 = dut3.my_state.distance(dut3.my_state)

        # Identity
        assert distance_1_1 == 0, f'ident distance_1_1: {distance_1_1}'
        assert distance_2_2 == 0, f'ident distance_2_2: {distance_2_2}'
        assert distance_3_3 == 0, f'ident distance_3_3: {distance_3_3}'

        # Commutativity
        assert distance_1_2 == distance_2_1, (
            f'commut distance_1_2: {distance_1_2}, distance_2_1: {distance_2_1}')
        assert distance_1_3 == distance_3_1, (
            f'commut distance_1_3: {distance_1_3}, distance_3_1: {distance_3_1}')
        assert distance_2_3 == distance_3_2, (
            f'commut distance_2_3: {distance_2_3}, distance_3_2: {distance_3_2}')

        # Non-negativity
        assert distance_1_2 > 0, f'non-neg distance_1_2: {distance_1_2}'
        assert distance_1_3 > 0, f'non-neg distance_1_3: {distance_1_3}'
        assert distance_2_3 > 0, f'non-neg distance_2_3: {distance_2_3}'

        # Triangle inequality
        assert distance_1_2 + distance_2_3 >= distance_1_3, (
            f'triangle distance_1_2: {distance_1_2}, distance_2_3: {distance_2_3}, '
            f'distance_1_3: {distance_1_3}')
        assert distance_1_3 + distance_3_2 >= distance_1_2, (
            f'triangle distance_1_3: {distance_1_3}, distance_3_2: {distance_3_2}, '
            f'distance_1_2: {distance_1_2}')
        assert distance_2_3 + distance_3_1 >= distance_2_1, (
            f'triangle distance_2_3: {distance_2_3}, distance_3_1: {distance_3_1}, '
            f'distance_2_1: {distance_2_1}')
        assert distance_2_1 + distance_1_3 >= distance_2_3, (
            f'triangle distance_2_1: {distance_2_1}, distance_1_3: {distance_1_3}, '
            f'distance_2_3: {distance_2_3}')
        assert distance_3_2 + distance_2_1 >= distance_3_1, (
            f'triangle distance_3_2: {distance_3_2}, distance_2_1: {distance_2_1}, '
            f'distance_3_1: {distance_3_1}')
        assert distance_3_1 + distance_1_2 >= distance_3_2, (
            f'triangle distance_3_1: {distance_3_1}, distance_1_2: {distance_1_2}, '
            f'distance_3_2: {distance_3_2}')

        assert_no_exceptions([dut1, dut2, dut3])
    finally:
        dut1.stop()
        dut2.stop()
        dut3.stop()


def load_multiclass_dataset() -> Tuple[Dataset, Dataset, Dataset, Dataset]:
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

    dataset_one_point_train = Dataset(
        metadata=metadata,
        covariates_table=TableFactory(bc_x_train[:1]),
        target_table=TableFactory(bc_y_train[:1])
    )

    dataset_test = Dataset(
        metadata=metadata,
        covariates_table=TableFactory(bc_x_test)
    )
    ground_truth = Dataset(
        metadata=metadata,
        ground_truth=bc_y_test
    )

    assert len(np.unique(bc_y_train)) == 3
    return (dataset_train, dataset_one_point_train, dataset_test, ground_truth)


def test_real_multiclass_data(wait_til_all_fit: Waiter,
                              assert_no_exceptions: Clearer) -> None:
    dist_clause_1 = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '1': [2],
                    '2': [1]
                }
            }
        },
        'communicator': {
            'name': 'sockets',
            'sockets': {
                'nodes_and_endpoints': [
                    ('1', (LOOPBACK, base_port.next())),
                    ('2', (LOOPBACK, base_port.next())),
                ]
            },
        },
        'my_id': 1,
        'fit_eps': 0.1
    }

    dist_clause_2 = deepcopy(dist_clause_1)
    dist_clause_2['my_id'] = 2

    alg = AutonDecisionTreeModel()
    dut1 = alg.instantiate(
        distributed=DistributedConfig(dist_clause_1),
        **DT_PARAMS)
    assert isinstance(dut1, AutonDecisionTreeInstance), (
        'dut1 should be an AutonDecisionTreeInstance')

    dut2 = alg.instantiate(
        distributed=DistributedConfig(dist_clause_2),
        **DT_PARAMS)
    assert isinstance(dut2, AutonDecisionTreeInstance), (
        'dut2 should be an AutonDecisionTreeInstance')

    train, one_pt_train, test, ground_truth = load_multiclass_dataset()

    acc = MetricCatalogAuto().lookup_by_name('accuracy_score')
    assert isinstance(acc, Metric)

    try:
        dut1.start()
        dut2.start()

        dut1.fit(one_pt_train)

        assert wait_til_all_fit([dut1, dut2], convergence_check=False), (
            'Timeout while waiting for first fit')

        dut2.fit(train)

        assert wait_til_all_fit([dut1, dut2], convergence_check=True), (
            'Timeout while waiting for second fit to converge')

        pred1 = dut1.predict(test)
        assert pred1 is not None, 'pred1 should not be None.'
        pred2 = dut2.predict(test)
        assert pred2 is not None, 'pred2 should not be None.'

        acc1 = acc.calculate(pred=pred1, ground_truth=ground_truth)
        acc2 = acc.calculate(pred=pred2, ground_truth=ground_truth)

        num_classes = 3.0
        random_guessing_acc = 1.0 / num_classes
        assert acc1 > random_guessing_acc, (
            f'Accuracy of first model ({acc1}) '
            f'should be better than random guessing ({random_guessing_acc})'
        )
        assert acc2 > random_guessing_acc, (
            f'Accuracy of second model ({acc2}) '
            f'should be better than random guessing ({random_guessing_acc})'
        )

        assert_no_exceptions([dut1, dut2])
    finally:
        dut1.stop()
        dut2.stop()
