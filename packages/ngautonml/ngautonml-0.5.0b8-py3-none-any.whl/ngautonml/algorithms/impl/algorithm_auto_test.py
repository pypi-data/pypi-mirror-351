'''Tests for model_auto.py'''
# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code
from .algorithm_auto import AlgorithmCatalogAuto
from ..sklearn.sklearn_algorithm import SklearnAlgorithm
from ..connect import ConnectorModel
from ..extract_columns_by_role import ExtractColumnsByRoleModel
from ...problem_def.task import TaskType

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


def test_linear_regression() -> None:
    dut = AlgorithmCatalogAuto()
    model = dut.lookup_by_name('sklearn.linear_model.LinearRegression')
    assert isinstance(model, SklearnAlgorithm)
    items = dut.lookup_by_tag_and(task=TaskType.REGRESSION.name)
    assert any(isinstance(item, SklearnAlgorithm) for _, item in items.items())


def test_connector() -> None:
    dut = AlgorithmCatalogAuto()
    item = dut.lookup_by_name(name='connect')
    assert isinstance(item, ConnectorModel)


def test_extract() -> None:
    dut = AlgorithmCatalogAuto()
    model = dut.lookup_by_name(name='Extract Columns by Role')
    assert isinstance(model, ExtractColumnsByRoleModel)


def test_classifiers() -> None:
    dut = AlgorithmCatalogAuto()

    algorithms = dut.lookup_by_tag_and(task=TaskType.MULTICLASS_CLASSIFICATION.name)
    names = [algo.name for algo in algorithms.values()]
    assert set({'sklearn.linear_model.logisticregression',
                'sklearn.ensemble.randomforestclassifier',
                'sklearn.svm.svc',
                'sklearn.svm.linearsvc',
                'sklearn.naive_bayes.multinomialnb',
                'sklearn.discriminant_analysis.lineardiscriminantanalysis',
                'sklearn.discriminant_analysis.quadraticdiscriminantanalysis',
                'sklearn.ensemble.adaboostclassifier',
                'sklearn.tree.extratreeclassifier',
                'sklearn.ensemble.baggingclassifier',
                'sklearn.linear_model.passiveaggressiveclassifier',
                'sklearn.neural_network.mlpclassifier',
                'sklearn.ensemble.gradientboostingclassifier'}).issubset(set(names))
