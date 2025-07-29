'''Tests for wrangler.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,duplicate-code,protected-access,too-many-ancestors
# pylint: disable=missing-class-docstring,redefined-outer-name,unused-variable

import glob
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from numpy.random import RandomState  # pylint: disable=no-name-in-module  # This just isn't true.
import pandas as pd
import pytest

from ..aggregators.impl.aggregator import AggregatorStub
from ..algorithms.impl.algorithm import Algorithm
from ..algorithms.impl.algorithm_auto import FakeAlgorithmCatalogAuto
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..algorithms.impl.fake_algorithm import FakeInstance
from ..executor.cucumber import Cucumber
from ..executor.executor import ExecutorStub
from ..executor.simple.simple_executor import SimpleExecutor
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import (ExecutablePipeline,
                                                PipelineResult)
from ..problem_def.problem_def import ProblemDefinition
from ..templates.impl.pipeline_step import PipelineStep
from ..templates.impl.pipeline_template import PipelineTemplate
from ..templates.impl.template import TemplateCatalog

from .constants import Defaults
from .dataset import Dataset, RoleName, TableFactory
from .wrangler import Wrangler


class FakeExecutor(ExecutorStub):

    def predict(self,
                dataset: Dataset,
                pipelines: Dict[Designator, ExecutablePipeline]
                ) -> Dict[Designator, PipelineResult]:
        '''Use a list of pipelines to predict from a dataset.'''
        predictions = dataset.output()
        # create a dataframe with the shape we expect predictions to be:
        # 1 column (the target) and a number of rows equal to the size of the input
        predictions.predictions_table = TableFactory({
            dataset.metadata.roles[RoleName.TARGET][0].name:
                range(0, dataset.dataframe_table.shape[0])})
        return {d: PipelineResult(executable_pipeline=p, prediction=predictions)
                for d, p in pipelines.items()}


MEMORY_PROBLEM_DEF = '''
{
    "dataset": {
        "config": "memory",
        "column_roles": {
            "target": {
                "name": "c"
            }
        },
        "params": {
            "train_data": "train_data",
            "test_data": "test_data"
        }
    },
    "problem_type": {
        "task": "regression"
    },
    "cross_validation": {
        "k": 10
    },
    "metrics" : {
        "root_mean_squared_error" : {}
    },
    "hyperparams": ["disable_grid_search"]
}
'''

AGGREGATION_PROBLEM_DEF = '''
{
    "dataset": {
        "config": "memory",
        "column_roles": {
            "target": {
                "name": "c"
            }
        },
        "params": {
            "train_data": "train_data",
            "test_data": "test_data"
        }
    },
    "problem_type": {
        "task": "regression"
    },
    "cross_validation": {
        "k": 10
    },
    "metrics": {
        "root_mean_squared_error" : {},
        "mean_squared_error": {},
        "mean_absolute_error": {}
    },
    "aggregation": {
        "method": ["method1", "method2"]
    },
    "hyperparams": ["disable_grid_search"]
}
'''


def get_data() -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    data = pd.DataFrame(
        {
            'a': range(1, 21),
            'b': range(1, 21),
            'c': range(1, 21)
        }
    )
    return (data, data)


def memory_problem_def(has_aggregation: bool = False) -> ProblemDefinition:
    problem_def = MEMORY_PROBLEM_DEF
    if has_aggregation:
        problem_def = AGGREGATION_PROBLEM_DEF

    return ProblemDefinition(clause=problem_def)


def test_wrangler_split() -> None:
    (train_data, test_data) = get_data()  # noqa: F841
    problem_def = memory_problem_def()
    dut = Wrangler(
        problem_definition=problem_def,
        algorithm_catalog=FakeAlgorithmCatalogAuto,
        executor=FakeExecutor)

    train_result = dut.fit_predict_rank()

    # we expect 10 folds because k=10 was set in the problem definition
    assert len(train_result.split_dataset.folds) == 10
    # we expect each fold's validate set to have 2 rows,
    #    because there are 10 folds and the dataset is 20 rows long,
    #    and 2 columns, because it contains the attributes but not the target.
    assert train_result.split_dataset.folds[0].validate.dataframe_table.shape == (2, 2)
    # we expect each fold's train set to have 18 rows,
    #    because it is composed of 9 folds of 2 rows each,
    #    and 3 columns, becase it contains the attributes and the target.
    assert train_result.split_dataset.folds[0].train.dataframe_table.shape == (18, 3)
    # we expect the ground truth to have 20 rows,
    #    because it covers the whole dataset,
    #    and 1 col, because it only has the target.
    assert train_result.split_dataset.ground_truth is not None
    assert train_result.split_dataset.ground_truth.ground_truth_table.shape == (20, 1)


def test_fit_predict_rank() -> None:
    (train_data, test_data) = get_data()  # noqa: F841
    problem_def = memory_problem_def()

    dut = Wrangler(
        problem_definition=problem_def,
        algorithm_catalog=FakeAlgorithmCatalogAuto)

    got = dut.fit_predict_rank()

    # we expect pipelines to be named according to thier template (tabular regression)
    #    and the model that was chosen from thier query step.
    #    in the case of random forest regressor, wrangler will do grid search,
    #    and thus hyperparam values will also be in the designator.
    random_forest_des = Designator('tabular_regression@sklearn.ensemble.randomforestregressor:'
                                   'max_depth=none,min_samples_split=2')
    linear_regression_des = Designator('tabular_regression@sklearn.linear_model.linearregression')
    assert {random_forest_des, linear_regression_des} == set(got.executable_pipelines.keys())

    assert len(got.train_results) == 2  # 2 pipelines
    got_result = got.train_results.predictions[random_forest_des]
    assert got_result is not None
    assert got_result.predictions_table is not None
    assert got_result.predictions_table.shape == (20, 2)

    assert len(got.rankings) == 1  # 1 metric
    assert 'root_mean_squared_error' in got.rankings

    assert got.test_results is not None
    assert len(got.test_results) == 2  # 2 pipelines

    # executable pipelines associated with the test results should be identical
    assert set(got.executable_pipelines.keys()) == set(got.test_results.executable_pipelines.keys())
    got_result = got.test_results.predictions[random_forest_des]
    assert got_result is not None
    assert got_result.predictions_table is not None
    assert got_result.predictions_table.shape == (20, 1)


def test_fit_predict_rank_with_aggregation() -> None:
    (train_data, test_data) = get_data()  # noqa: F841
    problem_def = memory_problem_def(has_aggregation=True)

    dut = Wrangler(
        problem_definition=problem_def,
        algorithm_catalog=FakeAlgorithmCatalogAuto)

    dut.aggregator_catalog.register(AggregatorStub(name="method1"))
    dut.aggregator_catalog.register(AggregatorStub(name="method2"))

    got = dut.fit_predict_rank()

    assert len(got.rankings) == 5  # 3 metrics, and 2 aggregate metrics
    want = {
        'root_mean_squared_error', 'mean_squared_error', 'mean_absolute_error',
        'method1', 'method2'
    }
    assert want == set(got.rankings.keys())


class FakeTemplateCatalog(TemplateCatalog):
    '''fake, no templates'''


def memory_test_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'a': range(1, 11),
            'b': range(1, 11)
        }
    )


def memory_train_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'a': range(1, 21),
            'b': range(1, 21),
            'c': range(1, 21)
        }
    )


def test_predict() -> None:
    (train_data, test_data) = get_data()  # noqa: F841
    problem_def = memory_problem_def()
    executor = SimpleExecutor
    alg_catalog = FakeAlgorithmCatalogAuto
    dut = Wrangler(
        problem_definition=problem_def,
        executor=executor,
        algorithm_catalog=alg_catalog)
    got = dut.fit_predict_rank()

    fake_des = Designator('fake_des')

    testset = dut.ez_dataset(memory_test_df())
    got_result = list(got.train_results.values())[0]
    pipeline = got_result.executable_pipeline
    assert pipeline is not None
    test_got = dut.predict(
        new_data=testset,
        trained_pipelines={fake_des: pipeline})
    got_result = test_got[fake_des]
    assert got_result is not None
    assert got_result.prediction is not None
    predictions = got_result.prediction.predictions_table

    # we expect 10 rows (length of test dataframe) and 1 col (target)
    assert predictions.shape == (10, 1)
    # we expect to be able to predict perfectly since test data is identical to train data.
    assert predictions['c'][9] == 10.0


def test_predict_defaulted() -> None:
    (train_data, test_data) = get_data()  # noqa: F841
    problem_def = memory_problem_def()
    executor = SimpleExecutor
    alg_catalog = FakeAlgorithmCatalogAuto
    dut = Wrangler(
        problem_definition=problem_def,
        executor=executor,
        algorithm_catalog=alg_catalog)
    _ = dut.fit_predict_rank()

    testset = dut.ez_dataset(memory_test_df())
    test_got = dut.predict(
        new_data=testset)
    assert {
        'tabular_regression@sklearn.linear_model.linearregression',
        'tabular_regression@sklearn.ensemble.randomforestregressor:'
        'max_depth=none,min_samples_split=2',
    } == set(test_got.keys())


def test_set_current_predict() -> None:
    (train_data, test_data) = get_data()  # noqa: F841
    problem_def = memory_problem_def()
    executor = SimpleExecutor
    alg_catalog = FakeAlgorithmCatalogAuto
    dut = Wrangler(
        problem_definition=problem_def,
        executor=executor,
        algorithm_catalog=alg_catalog)
    _ = dut.fit_predict_rank()

    testset = dut.ez_dataset(memory_test_df())

    # Pick one pipeline.
    dut.set_current('tabular_regression@sklearn.ensemble.randomforestregressor:'
                    'max_depth=none,min_samples_split=2')
    test_got = dut.predict(new_data=testset)
    assert set(test_got.keys()) == {
        'tabular_regression@sklearn.ensemble.randomforestregressor:'
        'max_depth=none,min_samples_split=2',
    }

    # Reset to all known pipelines.
    dut.set_current()

    test_got = dut.predict(new_data=testset)
    assert {
        'tabular_regression@sklearn.linear_model.linearregression',
        'tabular_regression@sklearn.ensemble.randomforestregressor:'
        'max_depth=none,min_samples_split=2',
    } == set(test_got.keys())


def test_set_current_fit() -> None:
    (train_data, test_data) = get_data()
    problem_def = memory_problem_def()
    executor = SimpleExecutor
    alg_catalog = FakeAlgorithmCatalogAuto
    dut = Wrangler(
        problem_definition=problem_def,
        executor=executor,
        algorithm_catalog=alg_catalog)
    _ = dut.fit_predict_rank()

    testset = dut.ez_dataset(memory_train_df())

    # Pick one pipeline.
    dut.set_current('tabular_regression@sklearn.ensemble.randomforestregressor:'
                    'max_depth=none,min_samples_split=2')

    test_got = dut.fit(dataset=testset)
    assert set(test_got.keys()) == {
        'tabular_regression@sklearn.ensemble.randomforestregressor:'
        'max_depth=none,min_samples_split=2',
    }

    # Reset to all known pipelines.
    dut.set_current()

    test_got = dut.fit(dataset=testset)
    assert {
        'tabular_regression@sklearn.linear_model.linearregression',
        'tabular_regression@sklearn.ensemble.randomforestregressor:'
        'max_depth=none,min_samples_split=2',
    } == set(test_got.keys())


@pytest.fixture(scope='session')
def saver_problem_def(tmp_path_factory: pytest.TempPathFactory) -> ProblemDefinition:
    tmp_path = tmp_path_factory.mktemp('data')
    tmp_dir = tmp_path / 'sub'
    tmp_dir.mkdir()
    config = {
        "dataset": {
            "config": "memory",
            "column_roles": {
                "target": {
                    "name": "c"
                }
            },
            "params": {
                "train_data": "train_data",
                "test_data": "test_data"
            }
        },
        "problem_type": {
            "task": "regression"
        },
        "cross_validation": {
            "k": 10
        },
        "metrics": {
            "root_mean_squared_error": {}
        },
        "output": {
            "path": tmp_dir,
            "instantiations": [
                "json"
            ],
            "file_type": "csv"
        },
        "hyperparams": ["disable_grid_search"]
    }

    return ProblemDefinition(clause=config)


def test_save_filesystem(saver_problem_def: ProblemDefinition) -> None:
    PipelineStep.reset_serial_number()
    (train_data, test_data) = get_data()
    dut = Wrangler(
        problem_definition=saver_problem_def,
        algorithm_catalog=FakeAlgorithmCatalogAuto)
    _ = dut.fit_predict_rank()

    path = saver_problem_def.output.path
    assert path is not None
    filenames = glob.glob(str(path / 'models' / '*.linearregression' / '@connect_*@.pkl'))
    assert len(filenames) == 1
    with Path(filenames[0]).open(mode='rb') as filepointer:
        cucumber = Cucumber.deserialize(filepointer.read())
    assert cucumber.hyperparams == {
        'target_table': ['target_dataset', 'dataframe_table'],
        'covariates_table': ['attributes_dataset', 'dataframe_table']
    }

    pipelines = os.listdir(str(path / 'pipelines'))
    assert {'tabular_regression@sklearn.ensemble.randomforestregressor:'
            'max_depth=none,min_samples_split=2.json',
            'tabular_regression@sklearn.linear_model.linearregression.json',
            } == set(pipelines)

    with (path / 'pipelines' / 'tabular_regression@sklearn.linear_model.linearregression.json'
          ).open() as file_pointer:
        got = json.load(file_pointer)

    assert got['pipeline_designator'] == 'tabular_regression@sklearn.linear_model.linearregression'


@pytest.fixture(scope='session')
def search_problem_def() -> ProblemDefinition:
    config = '''
    {
        "dataset": {
            "config": "memory",
            "column_roles": {
                "target": {
                    "name": "c"
                }
            },
            "params": {
                "train_data": "train_data",
                "test_data": "test_data"
            }
        },
        "problem_type": {
            "task": "regression"
        },
        "cross_validation": {
            "k": 2
        },
        "metrics" : {
            "root_mean_squared_error" : {}
        },
        "hyperparams": [
            {
                "select": {
                    "algorithm": "sklearn.ensemble.RandomForestRegressor"
                },
                "params": {
                    "n_estimators": {
                        "list": [100, 200]
                    }
                }
            }
        ]
    }
    '''

    return ProblemDefinition(
        clause=config)


@pytest.mark.skipif(os.getenv("RUN_LONG_NGAUTONML_TESTS") == "",
                    reason="Takes 56 seconds to run, so skip on CI by default.")
def test_hyperparam_search(search_problem_def: ProblemDefinition) -> None:
    (train_data, test_data) = get_data()
    dut = Wrangler(
        problem_definition=search_problem_def,
        algorithm_catalog=FakeAlgorithmCatalogAuto)
    got = dut.fit_predict_rank()
    assert len(got.executable_pipelines) == 25
    assert {
        'tabular_regression@sklearn.linear_model.linearregression',
        'tabular_regression@sklearn.ensemble.randomforestregressor:'
        'max_depth=8,min_samples_split=10,n_estimators=100',
        'tabular_regression@sklearn.ensemble.randomforestregressor:'
        'max_depth=15,min_samples_split=10,n_estimators=200',
    }.issubset(got.executable_pipelines.keys())


@pytest.fixture(scope='session')
def order_problem_def() -> ProblemDefinition:
    config = '''
    {
        "dataset": {
            "config": "memory",
            "column_roles": {
                "target": {
                    "name": "c"
                }
            },
            "params": {
                "train_data": "train_data",
                "test_data": "test_data"
            }
        },
        "problem_type": {
            "task": "test_task"
        },
        "cross_validation": {
            "k": 3
        },
        "metrics" : {
            "root_mean_squared_error" : {}
        },
        "hyperparams": ["disable_grid_search"]
    }
    '''

    return ProblemDefinition(clause=config)


class FakeInst(FakeInstance):
    '''The instance of a fake algorithm for order tests.'''
    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        retval = dataset.output()
        retval.predictions_table = TableFactory({'c': dataset.dataframe_table['a'] + 1})
        return retval


class FakeAlg(Algorithm):
    '''A fake algorithm used for order tests.'''
    _name = 'fake_algorithm'

    def instantiate(self, **hyperparams) -> 'FakeInstance':
        return FakeInst(parent=self, **hyperparams)


def test_order(order_problem_def) -> None:
    train_data = pd.DataFrame(
        {
            'a': range(1, 22),
            'b': range(1, 22),
            'c': range(2, 23)
        }
    )
    test_data = train_data  # noqa: F841 pylint: disable=unused-variable
    dut = Wrangler(
        problem_definition=order_problem_def)

    fake_template = PipelineTemplate(
        name='test_template',
        tags={
            'task': ['test_task'],
            'data_type': ['tabular']},
        generator=dut.generator
    )
    fake_template.step(model=FakeAlg())
    dut.template_catalog.register(fake_template)

    got = dut.fit_predict_rank()
    results = got.train_results.predictions[Designator('test_template')]
    assert results is not None
    assert results.predictions_table is not None
    predictions = results.predictions_table
    assert got.split_dataset.ground_truth is not None
    ground_truth_df = got.split_dataset.ground_truth.ground_truth_table.as_(pd.DataFrame)
    pd.testing.assert_frame_equal(predictions[['c']], ground_truth_df)
    assert all(predictions['c'] == predictions['ground truth'])


def non_seeded_problem_def() -> ProblemDefinition:
    config = '''
    {
        "dataset": {
            "config": "memory",
            "column_roles": {
                "target": {
                    "name": "c"
                }
            },
            "params": {
                "train_data": "train_data",
                "test_data": "test_data"
            }
        },
        "problem_type": {
            "task": "test_task"
        },
        "cross_validation": {
            "k": 2
        },
        "metrics" : {
            "root_mean_squared_error" : {}
        },
        "hyperparams": ["disable_grid_search"]
    }
    '''
    train_data = pd.DataFrame(  # noqa: F841 pylint: disable=unused-variable
        {
            'a': range(1, 21),
            'b': range(1, 21),
            'c': range(2, 22)
        }
    )

    return ProblemDefinition(clause=config)


def seeded_problem_def(seed: int) -> ProblemDefinition:
    config = {
        "dataset": {
            "config": "memory",
            "column_roles": {
                "target": {
                    "name": "c"
                }
            },
            "params": {
                "train_data": "train_data",
                "test_data": "test_data"
            }
        },
        "problem_type": {
            "task": "test_task"
        },
        "cross_validation": {
            "k": 2
        },
        "metrics": {
            "root_mean_squared_error": {}
        },
        "hyperparams": [
            "disable_grid_search",
            {
                "select": {
                    "tags": {
                        "supports_random_seed": "true"
                    }
                },
                "params": {
                    "random_seed": {
                        "fixed": seed
                    }
                }
            }
        ]
    }
    train_data = pd.DataFrame(  # noqa: F841 pylint: disable=unused-variable
        {
            'a': range(1, 21),
            'b': range(1, 21),
            'c': range(2, 22)
        }
    )

    return ProblemDefinition(clause=config)


class RandomAlgorithmInstance(AlgorithmInstance):
    _rng: RandomState

    def __init__(self, parent: Algorithm, **hyperparams):
        super().__init__(parent)
        if 'random_seed' in hyperparams:
            self._rng = RandomState(hyperparams['random_seed'])

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        retval = dataset.output()
        retval.predictions_table = TableFactory({
            'c': list(self._rng.randint(0, 10, len(dataset.dataframe_table)))
        })
        return retval


class RandomAlgorithm(Algorithm):
    _name = 'random_algorithm'
    _tags = {
        'task': ['test_task'],
        'data_type': ['tabular'],
        'supports_random_seed': ['true']
    }
    _default_hyperparams = {
        'random_seed': Defaults.SEED,
    }

    def instantiate(self, **hyperparams) -> RandomAlgorithmInstance:
        return RandomAlgorithmInstance(parent=self, **self.hyperparams(**hyperparams))


def test_set_seed() -> None:
    (train_data, test_data) = get_data()
    dut_def = Wrangler(problem_definition=non_seeded_problem_def())
    dut5678 = Wrangler(problem_definition=seeded_problem_def(5678))

    pipe_def = PipelineTemplate(
        name='test_template',
        tags={
            'task': ['test_task'],
            'data_type': ['tabular']},
        generator=dut_def.generator
    )
    pipe_def.step(model=RandomAlgorithm())
    dut_def.template_catalog.register(pipe_def)

    pipe5678 = PipelineTemplate(
        name='test_template',
        tags={
            'task': ['test_task'],
            'data_type': ['tabular']},
        generator=dut5678.generator
    )
    pipe5678.step(model=RandomAlgorithm())
    dut5678.template_catalog.register(pipe5678)

    got_def = dut_def.fit_predict_rank()
    got5678 = dut5678.fit_predict_rank()

    des_def = Designator('test_template')
    des5678 = Designator('test_template@random_algorithm:random_seed=5678')

    got_def_train_results_des_def = got_def.train_results[des_def]
    got5678_train_results_des5678 = got5678.train_results[des5678]

    assert got_def_train_results_des_def.prediction is not None
    assert got5678_train_results_des5678.prediction is not None

    predictions_def = got_def_train_results_des_def.prediction.predictions_table[['c']]
    predictions5678 = got5678_train_results_des5678.prediction.predictions_table[['c']]

    # The k-fold-cross-validator instantiates the algorithm separately
    # for each fold, so in this special case, we expect to see the same
    # sequence twice.

    want_def = pd.DataFrame({'c': [3, 3, 6, 2, 1, 8, 5, 1, 7, 3, 3, 3, 6, 2, 1, 8, 5, 1, 7, 3]})
    want5678 = pd.DataFrame({'c': [5, 3, 6, 9, 3, 3, 9, 8, 3, 3, 5, 3, 6, 9, 3, 3, 9, 8, 3, 3]})
    pd.testing.assert_frame_equal(predictions_def, want_def)
    pd.testing.assert_frame_equal(predictions5678, want5678)


@pytest.fixture(scope='session')
def disable_grid_search_problem_def() -> ProblemDefinition:
    config = '''
    {
        "dataset": {
            "config": "memory",
            "column_roles": {
                "target": {
                    "name": "c"
                }
            },
            "params": {
                "train_data": "train_data",
                "test_data": "test_data"
            }
        },
        "problem_type": {
            "task": "regression"
        },
        "cross_validation": {
            "k": 2
        },
        "metrics" : {
            "root_mean_squared_error" : {}
        },
        "hyperparams": [
            "disable_grid_search",
            {
                "select": {
                    "algorithm": "sklearn.ensemble.RandomForestRegressor"
                },
                "params": {
                    "n_estimators": {
                        "list": [100, 200],
                        "default": 100
                    }
                }
            }
        ],
        "output": {}
    }
    '''

    return ProblemDefinition(clause=config)


def test_disable_grid_search(disable_grid_search_problem_def: ProblemDefinition) -> None:
    (train_data, test_data) = get_data()
    dut = Wrangler(
        problem_definition=disable_grid_search_problem_def,
        algorithm_catalog=FakeAlgorithmCatalogAuto)
    got = dut.fit_predict_rank()
    assert {
        'tabular_regression@sklearn.linear_model.linearregression',
        'tabular_regression@sklearn.ensemble.randomforestregressor'
        ':max_depth=none,min_samples_split=2,n_estimators=100'
    } == set(got.executable_pipelines.keys())
