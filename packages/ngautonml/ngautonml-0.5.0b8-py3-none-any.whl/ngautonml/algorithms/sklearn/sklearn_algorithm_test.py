'''Tests for sklearn_model.py.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Tuple

import numpy as np
import pandas as pd
import pytest
from sklearn import datasets  # type: ignore[import-untyped]


from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import Designator
from ...metrics.impl.metric_auto import MetricCatalogAuto
from ...problem_def.hyperparam_config import HyperparamConfig
from ...problem_def.task import TaskType
from ...searcher.searcher import SearcherImpl
from ...tables.impl.table import Table, TableFactory
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.dataset import Column, Dataset, DatasetKeys, Metadata, RoleName
from ..connect import ConnectorModel
from ..impl.algorithm import Algorithm
from ..impl.algorithm_auto import AlgorithmCatalogAuto
from .sklearn_algorithm import SklearnAlgorithmInstance

# pylint: disable=missing-function-docstring, disable=super-init-not-called,duplicate-code
_ = TableCatalogAuto()  # pylint: disable=pointless-statement


def load_regression_dataset() -> Tuple[Dataset, Dataset, Dataset]:
    # Load the diabetes dataset
    diabetes_x, diabetes_y = datasets.load_diabetes(return_X_y=True)

    # Use only one feature
    diabetes_x = diabetes_x[:, np.newaxis, 2]

    # Split the data into training/testing sets
    diabetes_x_train = diabetes_x[:-20]
    diabetes_x_test = diabetes_x[-20:]

    # Split the targets into training/testing sets
    diabetes_y_train = diabetes_y[:-20]
    diabetes_y_test = diabetes_y[-20:]

    dataset_train = Dataset(
        metadata=Metadata(
            roles={RoleName.TARGET: [Column('target')]}
        ),
        covariates_table=TableFactory(pd.DataFrame(diabetes_x_train, columns=['attribute'])),
        target_table=TableFactory({'target': diabetes_y_train})
    )
    dataset_test = Dataset(
        metadata=Metadata(
            roles={RoleName.TARGET: [Column('target')]}
        ),
        covariates_table=TableFactory(pd.DataFrame(diabetes_x_test, columns=['attribute']))
    )
    ground_truth = Dataset(
        metadata=Metadata(
            roles={RoleName.TARGET: [Column('target')]}
        ),
        ground_truth=pd.DataFrame({'target': diabetes_y_test})
    )
    return (dataset_train, dataset_test, ground_truth)


def load_classification_dataset() -> Tuple[Dataset, Dataset, Dataset]:
    # Load the breast cander dataset
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


@pytest.mark.parametrize("name,value,precision", [
    ('sklearn.linear_model.LinearRegression', 2548.0723, 1e-6),
    ('sklearn.svm.SVR', 3252.0655, 1e-6),
    ('sklearn.svm.LinearSVR', 5089.4231, 1e-6),
    ('sklearn.ensemble.GradientBoostingRegressor', 2928.0825, 1e-6),
    ('sklearn.ensemble.RandomForestRegressor', 4641.0977, 1e-6),
    ('sklearn.linear_model.Ridge', 3604.2696, 1e-6),
    ('sklearn.linear_model.Lasso', 3482.7721, 1e-6),
    ('sklearn.linear_model.ElasticNet', 5551.8319, 1e-6),
    ('sklearn.linear_model.LassoCV', 2549.1403, 1e-6),
    ('sklearn.ensemble.AdaBoostRegressor', 2884.9437, 1e-6),
    ('sklearn.tree.ExtraTreeRegressor', 6374.6676, 1e-6),
    ('sklearn.ensemble.BaggingRegressor', 4861.7033, 1e-6),
])
def test_regression_sunny_day(name: str, value: float, precision: float) -> None:
    catalog = AlgorithmCatalogAuto()
    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('mean_squared_error')

    model = catalog.lookup_by_name(name)
    instance = model.instantiate()

    train, test, ground_truth = load_regression_dataset()

    instance.fit(train)

    result = instance.predict(test)
    assert metric.calculate(pred=result,
                            ground_truth=ground_truth
                            ) == pytest.approx(value, precision)


@pytest.mark.parametrize('name,value,precision', [
    ('sklearn.linear_model.LogisticRegression', 0.88, 1e-6),
    ('sklearn.ensemble.RandomForestClassifier', 0.94, 1e-6),
    ('sklearn.svm.SVC', 0.9, 1e-6),
    ('sklearn.svm.LinearSVC', 0.94, 1e-6),
    ('sklearn.naive_bayes.MultinomialNB', 0.86, 1e-6),
    ('sklearn.discriminant_analysis.LinearDiscriminantAnalysis', 0.92, 1e-6),
    ('sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis', 0.92, 1e-6),
    ('sklearn.ensemble.AdaBoostClassifier', 0.88, 0.03),
    ('sklearn.tree.ExtraTreeClassifier', 0.92, 1e-6),
    ('sklearn.ensemble.BaggingClassifier', 0.9, 1e-6),
    ('sklearn.linear_model.PassiveAggressiveClassifier', 0.48, 1e-6),
    ('sklearn.neural_network.MLPClassifier', 0.94, 1e-6),
    ('sklearn.ensemble.GradientBoostingClassifier', 0.92, 1e-6),
])
def test_classification_sunny_day(name: str, value: float, precision: float) -> None:
    catalog = AlgorithmCatalogAuto()
    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')

    model: Algorithm = catalog.lookup_by_name(name)
    instance = model.instantiate()

    train, test, ground_truth = load_classification_dataset()

    instance.fit(train)

    result = instance.predict(test)
    assert metric.calculate(pred=result,
                            ground_truth=ground_truth
                            ) == pytest.approx(value, precision)


class FakeSklearnImplementation:
    '''A fake Sklearn model implementation for testing purpose.'''

    def fit(self, _, __) -> None:
        return None

    def predict(self, _) -> np.ndarray:
        return np.array(["predict"])

    def predict_proba(self, _) -> np.ndarray:
        return np.array([["predict_proba", "predict_proba"],
                         ["predict_proba_row2", "predict_proba_row2"],
                         ["predict_proba_row3", "predict_proba_row3"]])


class FakeSklearnModelInstance(SklearnAlgorithmInstance):
    ''' Fake Sklearn model for testing purpose. '''

    def __init__(self):
        self._impl = FakeSklearnImplementation()
        self._algorithm = ConnectorModel()


def test_probability_output():
    fake_metadata = Metadata(
        roles={RoleName.TARGET: [Column('target')]},
        task=TaskType.BINARY_CLASSIFICATION)
    fake_dataset = Dataset(metadata=fake_metadata)
    # TODO(piggy): Figure out why this test fails if we use a
    # DictTable instead of a DataFrameTable.
    fake_dataset.dataframe_table = TableFactory(
        pd.DataFrame({'target': ['result'], 'a_covariate': [2]}))
    model = FakeSklearnModelInstance()
    model.fit(fake_dataset)

    got = model.predict(fake_dataset)

    assert DatasetKeys.PREDICTIONS_TABLE.value in got
    assert got.predictions_table.shape == (1, 1)
    assert got.predictions_table.as_(pd.DataFrame).iat[0, 0] == 'predict'

    assert 'probabilities' in got
    assert isinstance(got.probabilities, Table)
    assert got.probabilities.shape == (3, 1)
    assert got.probabilities.as_(pd.DataFrame).iat[0, 0] == 'predict_proba'  # type: ignore[attr-defined] # pylint: disable=line-too-long


def test_probability_output_for_non_binary_classification_task():
    ''' We only want to get probabilities output if it's a binary
        classification task.
    '''
    fake_metadata_regression = Metadata(
        roles={RoleName.TARGET: [Column('target')]},
        task=TaskType.REGRESSION)
    fake_dataset = Dataset(metadata=fake_metadata_regression)
    # TODO(piggy): Figure out why this test fails if we use a
    # DictTable instead of a DataFrameTable.
    fake_dataset.dataframe_table = TableFactory(pd.DataFrame(
        {'target': ['result'], 'a_covariate': [2]}))
    model = FakeSklearnModelInstance()
    model.fit(fake_dataset)

    got = model.predict(fake_dataset)

    assert 'probabilities' not in got

    assert DatasetKeys.PREDICTIONS_TABLE.value in got
    assert got.predictions_table.shape == (1, 1)
    assert got.predictions_table.as_(pd.DataFrame).iat[0, 0] == 'predict'


@pytest.mark.parametrize('name,want_number,want_des', [
    ('sklearn.linear_model.LogisticRegression',
     8,
     'test_pipe@sklearn.linear_model.logisticregression:c=0.1,class_weight=balanced'),
    ('sklearn.ensemble.RandomForestClassifier',
     24,
     'test_pipe@sklearn.ensemble.randomforestclassifier:'
     'class_weight=balanced,max_depth=none,min_samples_split=10'),
    ('sklearn.svm.SVC',
     10,
     'test_pipe@sklearn.svm.svc:c=0.01,class_weight=none'),
    ('sklearn.svm.LinearSVC',
     10,
     'test_pipe@sklearn.svm.linearsvc:c=0.01,class_weight=none'),
    ('sklearn.tree.ExtraTreeClassifier',
     24,
     'test_pipe@sklearn.tree.extratreeclassifier:'
     'class_weight=balanced,max_depth=8,min_samples_split=2'),
    ('sklearn.ensemble.GradientBoostingClassifier',
     90,
     'test_pipe@sklearn.ensemble.gradientboostingclassifier:'
     'max_depth=8,max_features=none,min_samples_leaf=2,min_samples_split=10'),
    ('sklearn.ensemble.GradientBoostingRegressor',
     90,
     'test_pipe@sklearn.ensemble.gradientboostingregressor:'
     'max_depth=10,max_features=none,min_samples_leaf=2,min_samples_split=10'),
    ('sklearn.svm.SVR',
     5,
     'test_pipe@sklearn.svm.svr:c=0.01'),
    ('sklearn.svm.LinearSVR',
     5,
     'test_pipe@sklearn.svm.linearsvr:c=0.1'),
    ('sklearn.ensemble.RandomForestRegressor',
     12,
     'test_pipe@sklearn.ensemble.randomforestregressor:max_depth=8,min_samples_split=2'),
    ('sklearn.linear_model.Ridge',
     5,
     'test_pipe@sklearn.linear_model.ridge:alpha=0.001'),
    ('sklearn.linear_model.Lasso',
     5,
     'test_pipe@sklearn.linear_model.lasso:alpha=5.0'),
    ('sklearn.tree.ExtraTreeRegressor',
     12,
     'test_pipe@sklearn.tree.extratreeregressor:max_depth=10,min_samples_split=2')
])
def test_grid_search(name: str, want_number: int, want_des: str) -> None:
    # make boundpipeline w random forest clf
    catalog = AlgorithmCatalogAuto()
    algorithm = catalog.lookup_by_name(name)
    bound_pipeline = BoundPipeline(name='test_pipe')
    bound_pipeline.step(model=algorithm)
    searcher = SearcherImpl(HyperparamConfig(clause={'hyperparams': []}))
    got = searcher.bind_hyperparams(bound_pipeline)
    assert len(got) == want_number
    assert Designator(want_des) in got
