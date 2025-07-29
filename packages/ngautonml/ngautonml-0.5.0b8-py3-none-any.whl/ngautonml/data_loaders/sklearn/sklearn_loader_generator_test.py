'''Tests for sklearn_loader.py and sklearn_laoders.py'''
from copy import deepcopy

import pandas as pd

from ...config_components.dataset_config import DatasetConfig
from ...problem_def.problem_def import ProblemDefinition
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.dataset import TableFactory
from ...wrangler.wrangler import Wrangler
from ..impl.data_loader_auto import DataLoaderCatalogAuto
from ..impl.dataframe_loader import DataframeLoader
from .sklearn_loader_generator import SklearnLoaderGenerator
_ = TableCatalogAuto()  # pylint: disable=pointless-statement

# pylint: disable=missing-function-docstring, duplicate-code


MOONY_CLAUSE = {
    'input_format': 'sklearn.datasets.make_moons',
    'params': {
        'n_samples': 5,
        'shuffle': True,
        'noise': None
    }
}


def test_moony_day() -> None:
    dut = SklearnLoaderGenerator(
        name='sklearn.datasets.make_moons',
        tags={
            'input_format': ['sklearn.datasets.make_moons'],
            'loaded_format': ['pandas_dataframe'],
            'supports_random_seed': ['true']
        }
    )

    got = dut.new_class()

    config = DatasetConfig(clause=MOONY_CLAUSE)

    # pylint is wrong about this class not defining the abstract methods.
    inst = got(config=config)  # pylint: disable=abstract-class-instantiated

    assert isinstance(inst, DataframeLoader)

    got_data = inst.load_train()
    want_table = TableFactory({
        '0': [-1.0, 1, 1, 0, 2],
        '1': [0.0, 0, -0.5, 0.5, 0.5],
        'y': [0, 0, 1, 1, 1]
    })
    assert got_data is not None
    pd.testing.assert_frame_equal(got_data.dataframe_table.as_(pd.DataFrame),
                                  want_table.as_(pd.DataFrame))


def test_set_seed() -> None:
    dut = SklearnLoaderGenerator(
        name='sklearn.datasets.make_moons',
        tags={
            'input_format': ['sklearn.datasets.make_moons'],
            'loaded_format': ['pandas_dataframe'],
            'supports_random_seed': ['true']
        }
    )

    got = dut.new_class()

    clause = deepcopy(MOONY_CLAUSE)
    assert isinstance(clause['params'], dict)
    clause['params']['random_seed'] = 1337
    config = DatasetConfig(clause=clause)

    # ibid
    inst = got(config=config)  # pylint: disable=abstract-class-instantiated
    assert isinstance(inst, DataframeLoader)

    got_data = inst.load_train()
    want_table = TableFactory({
        '0': [1.0, 0, -1, 1, 2],
        '1': [-0.5, 0.5, 0, 0, 0.5],
        'y': [1, 1, 0, 0, 1]
    })
    assert got_data is not None
    pd.testing.assert_frame_equal(got_data.dataframe_table.as_(pd.DataFrame),
                                  want_table.as_(pd.DataFrame))


def test_lookup() -> None:
    config = DatasetConfig(clause=MOONY_CLAUSE)
    dut = DataLoaderCatalogAuto().construct_instance(config=config)

    got_data = dut.load_train()
    want_table = TableFactory({
        '0': [-1.0, 1, 1, 0, 2],
        '1': [0.0, 0, -0.5, 0.5, 0.5],
        'y': [0, 0, 1, 1, 1]
    })
    assert got_data is not None
    pd.testing.assert_frame_equal(got_data.dataframe_table.as_(pd.DataFrame),
                                  want_table.as_(pd.DataFrame))
    assert dut.__class__.__name__.startswith('GeneratedSklearnLoader')


DIABETES_CLAUSE = {
    'input_format': 'sklearn.datasets.load_diabetes',
    'params': {
        'scaled': True
    }
}


def test_diabetes() -> None:
    dut = SklearnLoaderGenerator(
        name='sklearn.datasets.load_diabetes',
        tags={
            'input_format': ['sklearn.datasets.load_diabetes'],
            'loaded_format': ['pandas_dataframe'],
            'supports_random_seed': ['false'],
            'uses_return_X_y': ['true'],
            'uses_as_frame': ['true']
        }
    )
    got = dut.new_class()

    clause = deepcopy(DIABETES_CLAUSE)
    config = DatasetConfig(clause=clause)

    # ibid
    inst = got(config=config)  # pylint: disable=abstract-class-instantiated
    assert isinstance(inst, DataframeLoader)

    got_data = inst.load_train()
    assert got_data is not None
    assert got_data.dataframe_table.shape == (442, 11)
    assert list(got_data.dataframe_table.columns) == [
        'age', 'sex', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6', 'y'
    ]


def test_restrict_features_integration() -> None:
    dut = Wrangler(ProblemDefinition(
        {
            "dataset": {
                "input_format": ["sklearn.datasets.load_breast_cancer"],
                "loaded_format": ["pandas_dataframe"],
                "column_roles": {
                    "target": {
                        "name": "target"
                    }
                },
                "params": {
                    "restrict_features": 2
                }
            },
            "problem_type": {
                "task": "binary_classification"
            }
        }
    ))
    got = dut.load_train_dataset()
    assert got is not None
    got_table = got.dataframe_table
    assert got_table.shape == (569, 3)
    got_cols = got_table.columns
    assert got_cols == ['mean radius', 'mean texture', 'target']

    assert dut.load_test_dataset() is None
    assert dut.load_ground_truth_dataset() is None


def test_train_test_split_integration() -> None:
    dut = Wrangler(ProblemDefinition(
        {
            "dataset": {
                "input_format": ["sklearn.datasets.load_breast_cancer"],
                "loaded_format": ["pandas_dataframe"],
                "column_roles": {
                    "target": {
                        "name": "target"
                    }
                },
                "params": {
                    "test_size": 2,
                }
            },
            "problem_type": {
                "task": "binary_classification"
            }
        }
    ))
    got_train = dut.load_train_dataset()
    assert got_train is not None
    got_train_table = got_train.dataframe_table
    assert got_train_table.shape == (567, 31)

    got_test = dut.load_test_dataset()
    assert got_test is not None
    got_test_table = got_test.dataframe_table
    assert got_test_table.shape == (2, 30)

    got_gt = dut.load_ground_truth_dataset()
    assert got_gt is not None
    got_gt_table = got_gt.ground_truth_table
    assert got_gt_table.shape == (2, 1)
