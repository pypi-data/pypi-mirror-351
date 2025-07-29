'''Tests for queue_loader.py.'''

import queue

import pandas as pd

from ..config_components.dataset_config import DatasetConfig
from ..problem_def.problem_def import ProblemDefinition
from ..wrangler.dataset import Dataset, TableFactory

from .queue_loader import QueueLoader

# pylint: disable=missing-function-docstring, missing-class-docstring, duplicate-code


def test_sunny_day() -> None:
    '''Test the happy path for the QueueLoader.'''
    clause = {
        'config': 'queue',
        'column_roles': {
            'target': {
                'name': 'a',
                'pos_label': 1,
            },
        },
        'params': {
            'train_data': 'train_df',
            'test_data': 'test_df',
            'poll_queue': 'poll_queue',
            'timeout': 0.0,
        },
    }
    config = DatasetConfig(clause=clause)

    train_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]}) # noqa F841 pylint: disable=unused-variable
    test_df = pd.DataFrame({'a': [5, 6], 'b': [7, 8]}) # noqa F841 pylint: disable=unused-variable
    poll_data = Dataset(
        dataframe_table=TableFactory(pd.DataFrame({'a': [9, 10], 'b': [11, 12]})),
        metadata=config.metadata)

    poll_queue: queue.Queue[Dataset] = queue.Queue()

    dut = QueueLoader(config=config)

    assert dut.poll(timeout=0) is None

    poll_queue.put(poll_data)

    got_train = dut.load_train()
    got_test = dut.load_test()
    got_poll = dut.poll(timeout=0)

    assert got_train is not None
    assert got_test is not None
    assert got_poll is not None

    want_train = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    want_test = pd.DataFrame({'b': [7, 8]})
    want_poll = poll_data.dataframe_table.as_(pd.DataFrame)

    pd.testing.assert_frame_equal(got_train.dataframe_table.as_(pd.DataFrame), want_train)
    pd.testing.assert_frame_equal(got_test.dataframe_table.as_(pd.DataFrame), want_test)
    pd.testing.assert_frame_equal(got_poll.dataframe_table.as_(pd.DataFrame), want_poll)


def test_split() -> None:
    '''Allow for a split dataset.'''
    pdef = ProblemDefinition({
        'dataset': {
            'config': 'queue',
            'column_roles': {
                'target': {
                    'name': 'a',
                    'pos_label': 1,
                },
            },
            'params': {
                'train_data': 'train_df',
                'test_data': 'test_df',
                'poll_queue': 'poll_queue',
                'timeout': 0.0,
            },
        },
        'distributed': {
            'my_id': 1,
            'split': {
                'num_nodes': 3,
                'seed': 1234
            },
        },
        'problem_type': {
            'task': 'regression'
        }
    })
    config = pdef.get_conf('dataset')
    assert isinstance(config, DatasetConfig)
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9],
    })

    train_df = df # noqa F841 pylint: disable=unused-variable
    test_df = pd.DataFrame({'a': [10, 11, 12], 'b': [13, 14, 15], 'c': [16, 17, 18]}) # noqa F841 pylint: disable=unused-variable
    poll_data1 = Dataset(
        dataframe=pd.DataFrame({'a': [19, 20, 21], 'b': [22, 23, 24], 'c': [25, 26, 27]}),
        metadata=config.metadata)
    poll_data2 = Dataset(
        dataframe=pd.DataFrame({'a': [28, 29, 30], 'b': [31, 32, 33], 'c': [34, 35, 36]}),
        metadata=config.metadata)

    poll_queue: queue.Queue[Dataset] = queue.Queue()

    dut = QueueLoader(config=config)

    assert dut.poll(timeout=0) is None

    poll_queue.put(poll_data1)
    poll_queue.put(poll_data2)

    want_train = pd.DataFrame({'a': [1], 'b': [4], 'c': [7]})
    # Test data shouldn't be split, but it should have the target removed.
    want_test = pd.DataFrame({'b': [13, 14, 15], 'c': [16, 17, 18]})
    want_poll1 = pd.DataFrame({'a': [19], 'b': [22], 'c': [25]})
    want_poll2 = pd.DataFrame({'a': [28], 'b': [31], 'c': [34]})

    got_train = dut.load_train()
    got_test = dut.load_test()
    got_poll1 = dut.poll(timeout=0)
    got_poll2 = dut.poll(timeout=0)

    assert got_train is not None
    assert got_test is not None
    assert got_poll1 is not None
    assert got_poll2 is not None

    pd.testing.assert_frame_equal(got_train.dataframe_table.as_(pd.DataFrame), want_train)
    pd.testing.assert_frame_equal(got_test.dataframe_table.as_(pd.DataFrame), want_test)
    pd.testing.assert_frame_equal(got_poll1.dataframe_table.as_(pd.DataFrame), want_poll1)
    pd.testing.assert_frame_equal(got_poll2.dataframe_table.as_(pd.DataFrame), want_poll2)
