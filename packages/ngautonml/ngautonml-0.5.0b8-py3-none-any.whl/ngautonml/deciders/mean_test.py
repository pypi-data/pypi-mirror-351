'''Tests for auton_mean with deciders'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring, duplicate-code, protected-access

import os
import pandas as pd
import pytest


from ..algorithms.impl.synchronous import advance
from ..config_components.distributed_config import DistributedConfig
from ..conftest import Clearer
from ..deciders.impl.decider_auto import DeciderCatalogAuto
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.base_port import BasePort
from ..wrangler.dataset import Dataset, TableFactory
from ..wrangler.logger import Logger

from ..algorithms.distributed.auton_mean import AutonMean

_ = DeciderCatalogAuto()  # pylint: disable=pointless-statement
TableCatalogAuto()  # pylint: disable=pointless-statement

logger = Logger(__file__).logger()

base_port = BasePort()


receiver_train = Dataset(
    covariates_table=TableFactory({'a': [1, 2, 3], 'b': [2, 3, 4], 'c': [3, 4, 5]}))

sender_train = Dataset(
    covariates_table=TableFactory({'a': [7, 8, 9], 'b': [8, 9, 10], 'c': [9, 10, 11]}))

empty_dataset = receiver_train.output()


LOOPBACK = '127.0.0.1'

TEST_TELEPHONE_N = 5
TEST_TELEPHONE_PORTS = [base_port.next() for _ in range(TEST_TELEPHONE_N)]


@pytest.mark.skipif(os.getenv("RUN_LONG_NGAUTONML_TESTS") == "",
                    reason="Takes about 160 seconds to run, so skip on CI by default.")
@pytest.mark.parametrize('strategy,distance_enabled', [
    ('broadcast', False),
    ('broadcast', True),
    ('unicast', False),
    ('unicast', True),
])
def test_telephone(strategy, distance_enabled,
                   assert_no_exceptions: Clearer) -> None:
    '''Whisper down the lane test. Nodes connected in a line.
    The only node that has data is one at the end '''
    n = TEST_TELEPHONE_N

    adjacency = {f'{k}': [k - 1, k + 1] for k in range(2, n)}
    adjacency['1'] = [2]
    adjacency[f'{n}'] = [n - 1]

    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': adjacency
            }
        },
        'communicator': {
            'name': 'memory',
            'memory': {
                'domain': f'test_telephone_{strategy}_{distance_enabled}',
            },
            'strategy': strategy,
        },
        'decider': {
            'distance': {
                'threshold': 0.1,
                'enabled': distance_enabled,
            },
        },
        'my_id': 0,
    }

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonMean()

    telephone_params = dict(alg._default_hyperparams, Lambda=1000000)

    params = [dict(telephone_params) if k == 0 else dict(telephone_params) for k in range(n)]

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc),
        synchronous=True,
        **ps) for (dc, ps) in zip(distributed_clauses, params)]
    try:
        for dut in duts:
            dut.start()

        duts[0].fit(receiver_train)

        # Wait for the message to arrive and get processed.
        for _ in range(3 * TEST_TELEPHONE_N):
            advance(duts)

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


TEST_N_SAME_N = 5
TEST_N_SAME_PORTS = [base_port.next() for _ in range(TEST_N_SAME_N)]


@pytest.mark.parametrize('strategy,distance_enabled', [
    ('broadcast', False),
    ('broadcast', True),
    ('unicast', False),
    ('unicast', True),
])
def test_n_same(strategy, distance_enabled,
                assert_no_exceptions: Clearer) -> None:
    '''N nodes fully connected with the same training match the non-distributed result.'''
    n = TEST_N_SAME_N

    adjacency = {f'{k}': [j for j in range(1, n + 1) if j != k] for k in range(1, n + 1)}

    distributed_clause = {
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': adjacency
            }
        },
        'communicator': {
            'name': 'memory',
            'memory': {
                'domain': f'test_n_same_{strategy}_{distance_enabled}',
            },
            'strategy': strategy,
        },
        'decider': {
            'distance': {
                'threshold': 0.1,
                'enabled': distance_enabled,
            },
        },
        'my_id': 0,
    }

    distributed_clauses = [dict(distributed_clause, my_id=k) for k in range(1, n + 1)]

    alg = AutonMean()

    duts = [alg.instantiate(
        distributed=DistributedConfig(dc), synchronous=True) for dc in distributed_clauses]

    try:
        for dut in duts:
            dut.start()

        for dut in duts:
            dut.fit(receiver_train)

        # Wait for the messages to arrive and get processed.
        for _ in range(3):
            advance(duts)

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
