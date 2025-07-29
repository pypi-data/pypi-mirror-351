'''Tests for abstractor.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=protected-access,too-many-statements,duplicate-code,too-many-locals

from copy import deepcopy
import getpass
import os
from pathlib import Path

import pandas as pd

from ....config_components.distributed_config import DistributedConfig
from ....conftest import Clearer, Waiter
from ....problem_def.problem_def import ProblemDefinition
from ....tables.impl.table import TableFactory
from ....tables.impl.table_auto import TableCatalogAuto
from ....wrangler.base_port import BasePort
from ....wrangler.dataset import Dataset
from ....wrangler.logger import Logger
from ....wrangler.wrangler import Wrangler

from ...distributed.auton_decision_tree import AutonDecisionTreeModel
from ...impl.synchronous import advance

from ..share import ShareAbstractor

_ = TableCatalogAuto()
logger = Logger(__file__, to_stdout=False).logger()


base_port = BasePort()


LOOPBACK = '127.0.0.1'
SUNNY_DAY_SENDER = base_port.next()
SUNNY_DAY_RECEIVER = base_port.next()


def test_sunny_day(wait_til_all_fit: Waiter,
                   assert_no_exceptions: Clearer) -> None:
    '''One node shares its data to its neighbor.'''
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
                    ('1', (LOOPBACK, SUNNY_DAY_SENDER)),
                    ('2', (LOOPBACK, SUNNY_DAY_RECEIVER))
                ]
            }
        },
        'my_id': 1,
    }

    dut_sender = ShareAbstractor().instantiate(
        distributed=DistributedConfig(clause=distributed_clause))

    sender_dataset = Dataset()
    sender_dataset.dataframe_table = TableFactory({'a': [1], 'b': [2], 'c': [5]})

    receiver_clause = deepcopy(distributed_clause)
    receiver_clause['my_id'] = 2
    dut_receiver = ShareAbstractor().instantiate(
        distributed=DistributedConfig(clause=receiver_clause))

    try:
        dut_sender.start()
        dut_receiver.start()
        dut_sender.fit(sender_dataset)

        # Wait for the message to arrive and get processed.
        wait_til_all_fit([dut_sender, dut_receiver])

        assert_no_exceptions([dut_sender, dut_receiver])

        result = dut_receiver.synthesize()

        assert result.dataframe_table == sender_dataset.dataframe_table

    finally:
        dut_sender.stop()
        dut_receiver.stop()


BIDIRECTIONAL_SENDER = base_port.next()
BIDIRECTIONAL_RECEIVER = base_port.next()


def test_bidirectional(assert_no_exceptions: Clearer) -> None:
    '''One node shares its data to its neighbor.'''
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
                    ('1', (LOOPBACK, BIDIRECTIONAL_SENDER)),
                    ('2', (LOOPBACK, BIDIRECTIONAL_RECEIVER))
                ]
            }
        },
        'my_id': 1,
    }

    dut_sender = ShareAbstractor().instantiate(
        distributed=DistributedConfig(clause=distributed_clause), synchronous=True)

    sender_dataset = Dataset()
    sender_dataset.dataframe_table = TableFactory({'a': [1], 'b': [2]})

    receiver_clause = deepcopy(distributed_clause)
    receiver_clause['my_id'] = 2
    dut_receiver = ShareAbstractor().instantiate(
        distributed=DistributedConfig(clause=receiver_clause), synchronous=True)

    receiver_dataset = Dataset()
    receiver_dataset.dataframe_table = TableFactory({'a': [3], 'b': [4]})

    try:
        dut_sender.start()
        dut_receiver.start()
        dut_sender.fit(sender_dataset)
        dut_receiver.fit(receiver_dataset)

        # Wait for the messages to arrive and get processed.
        for _ in range(10):
            advance([dut_sender, dut_receiver])

        assert_no_exceptions([dut_sender, dut_receiver])

        result_sender = dut_sender.synthesize()
        result_sender_df = result_sender.dataframe_table.as_(pd.DataFrame)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
        result_sender_df = result_sender_df.sort_values(
            by=result_sender_df.columns.tolist(), ignore_index=True)

        result_receiver = dut_receiver.synthesize()
        result_receiver_df = result_receiver.dataframe_table.as_(pd.DataFrame)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
        result_receiver_df = result_receiver_df.sort_values(
            by=result_receiver_df.columns.tolist(), ignore_index=True)

        pd.testing.assert_frame_equal(result_receiver_df, result_sender_df)

        want_df = pd.DataFrame({'a': [1, 3], 'b': [2, 4]})
        want_df = want_df.sort_values(
            by=want_df.columns.tolist(), ignore_index=True)

        pd.testing.assert_frame_equal(want_df, result_receiver_df)
        pd.testing.assert_frame_equal(want_df, result_sender_df)

    finally:
        dut_sender.stop()
        dut_receiver.stop()


BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')


def topic_name(topic: str) -> str:
    '''Generate a unique topic name for the given test.'''
    return f'{Path(__file__).stem}_{getpass.getuser()}_{topic}'


TWO_ALG_ALG1 = base_port.next()
TWO_ALG_SHARE1 = base_port.next()
TWO_ALG_SHARE2 = base_port.next()

TWO_ALG_ALG1_DISTRIBUTED_CLAUSE = {
    'my_id': 1,
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
                ('1', (LOOPBACK, TWO_ALG_ALG1)),
            ],
        }
    },
}

TWO_ALG_ABSTRACTOR_DISTRIBUTED_CLAUSE = {
    'my_id': -1,
    'discoverer': {
        'name': 'static',
        'static': {
            'adjacency': {'1': [2], '2': [1]}
        }
    },
    'communicator': {
        'name': 'memory',
        'memory': {
            'domain': 'two_algorithms',
        }
    },
}

TWO_ALG_PDEF = {
    "dataset": {
        "input_format": ["sklearn.datasets.load_breast_cancer"],
        "loaded_format": ["pandas_dataframe"],
        "column_roles": {
            "target": {
                "name": "target"
            }
        },
        "params": {
            "test_size": 30,
        }
    },
    'problem_type': {
        'task': 'binary_classification'
    }
}


def test_two_algorithms(wait_til_all_fit: Waiter,
                        assert_no_exceptions: Clearer) -> None:
    '''Two different algorithms share data space.

    This is an integration test to show how to use an abstractor to share training between
    two disparate algorithms.

    This is intended as a model for integration tests for other abstractors.

    The ShareAbstractor just shares and concatenates data, so both Algorithms should see the same
    input data and thus make similar predictions.
    '''

    # The abstractor network has 2 nodes.
    distributed_clause_share1 = deepcopy(TWO_ALG_ABSTRACTOR_DISTRIBUTED_CLAUSE)
    distributed_clause_share1['my_id'] = 1
    distributed_clause_share2 = deepcopy(TWO_ALG_ABSTRACTOR_DISTRIBUTED_CLAUSE)
    distributed_clause_share2['my_id'] = 2

    wrangler = Wrangler(problem_definition=ProblemDefinition(TWO_ALG_PDEF))

    sklearn_svm_svc = wrangler.algorithm_catalog.lookup_by_name('sklearn.svm.SVC')

    dut_alg1 = AutonDecisionTreeModel().instantiate(
        distributed=DistributedConfig(clause=TWO_ALG_ALG1_DISTRIBUTED_CLAUSE),
        Lambda=10000000, omega=0.6)
    dut_share1 = ShareAbstractor().instantiate(
        distributed=DistributedConfig(clause=distributed_clause_share1),
        Lambda=10000000, omega=0.6)
    dut_share2 = ShareAbstractor().instantiate(
        distributed=DistributedConfig(clause=distributed_clause_share2),
        Lambda=10000000, omega=0.6)
    dut_alg2 = sklearn_svm_svc.instantiate(C=1.0)

    train = wrangler.load_train_dataset()
    assert train is not None
    train = train.sorted_columns()
    train_df = train.dataframe_table.as_(pd.DataFrame)  # type: ignore[attr-defined]  # pylint: disable=line-too-long

    # Set up a pair of disjoint datasets.
    data_1_df = train_df.iloc[:270]
    data_2_df = train_df.iloc[270:]

    data_1 = train.output()
    data_1.dataframe_table = TableFactory(data_1_df)  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated,line-too-long

    data_2 = train.output()
    data_2.dataframe_table = TableFactory(data_2_df)

    test = wrangler.load_test_dataset()
    assert test is not None
    test = test.sorted_columns()

    ground_truth = wrangler.load_ground_truth_dataset()
    assert ground_truth is not None
    ground_truth = ground_truth.sorted_columns()

    dut_alg1.start()
    dut_share1.start()
    dut_share2.start()
    try:
        dut_share1.fit(data_1)
        dut_share2.fit(data_2)

        wait_til_all_fit([dut_share1, dut_share2])

        dut_alg1.fit(dut_share1.synthesize())
        dut_alg2.fit(dut_share2.synthesize())
        wait_til_all_fit([dut_alg1])

    finally:
        dut_alg1.stop()
        dut_share1.stop()
        dut_share2.stop()

    assert_no_exceptions([dut_alg1, dut_share1, dut_share2])

    result1 = dut_alg1.predict(test)
    result2 = dut_alg2.predict(test)

    acc = wrangler.metric_catalog.lookup_by_name('accuracy_score')
    assert acc.calculate(result1, ground_truth) > 0.75
    assert acc.calculate(result2, ground_truth) > 0.75
    assert acc.calculate(result1, result2) > 0.73
