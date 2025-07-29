'''Tests for k_fold_cross_validator.py'''
# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring, missing-class-docstring
# pylint: disable=redefined-outer-name,duplicate-code
from typing import Dict, List

import pandas as pd
import pytest


from ..executor.executor import ExecutorStub
from ..generator.bound_pipeline import BoundPipeline, BoundPipelineStub
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import (ExecutablePipeline,
                                                PipelineResult,
                                                PredictError)
from ..instantiator.instantiator_factory import InstantiatorFactory
from ..splitters.impl.splitter import Fold, SplitDataset
from ..tables.impl.table import TableFactory
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Dataset, Metadata, RoleName, Column
from .k_fold_cross_validator import KFoldCrossValidator

_ = TableCatalogAuto()  # pylint: disable=pointless-statement


class FakeExecutor(ExecutorStub):
    _return_proba: bool

    def __init__(self,
                 return_proba: bool = False,
                 error: bool = False,
                 order_test: bool = False,
                 **kwargs) -> None:
        self._return_proba = return_proba
        self._error = error
        self._order_test = order_test
        super().__init__(**kwargs)

    def predict(self,
                dataset: Dataset,
                pipelines: Dict[Designator, ExecutablePipeline]
                ) -> Dict[Designator, PipelineResult]:
        '''Use a list of pipelines to predict from a dataset.'''

        predictions = dataset.output()
        predictions.predictions_table = dataset.dataframe_table

        if self._order_test:
            target = TableFactory({'target': dataset.dataframe_table['other_column'] + 1})
            predictions.predictions_table = target

        if self._return_proba:
            probabilities_df = pd.DataFrame(
                {'prob': [0.5, 0.6, 0.7],
                    'id': [0, 1, 2]})
            probabilities_df.set_index('id', inplace=True)
            predictions.probabilities = TableFactory(probabilities_df)
        retval = {d: PipelineResult(executable_pipeline=p, prediction=predictions)
                  for d, p in pipelines.items()}

        if self._error:
            error_predictions = predictions.output()
            error_predictions['error'] = PredictError('there was an error')
            first = sorted(list(retval.keys()))[0]
            retval[first] = PipelineResult(
                executable_pipeline=pipelines[first],
                prediction=error_predictions)

        return retval


@pytest.fixture(scope='session')
def split_dataset() -> SplitDataset:
    fake_dataset = Dataset()
    df = pd.DataFrame(
        {'a': [53, 4, 5030],
         'id': [0, 1, 2]}).set_index('id')
    fake_dataset.dataframe_table = TableFactory(df)
    folds = [
        Fold(train=fake_dataset, validate=fake_dataset),
        Fold(train=fake_dataset, validate=fake_dataset)]
    return SplitDataset(folds)


def test_sunny_day(split_dataset: SplitDataset) -> None:
    bp1 = BoundPipelineStub('bound_pipeline_stub_1')
    bp2 = BoundPipelineStub('bound_pipeline_stub_2')
    des1 = Designator('des1')
    des2 = Designator('des2')
    bound_pipelines: Dict[Designator, BoundPipeline] = {
        des1: bp1, des2: bp2}

    dut = KFoldCrossValidator()
    got = dut.validate_pipelines(
        split_dataset=split_dataset,
        bound_pipelines=bound_pipelines,
        instantiator=InstantiatorFactory(),
        executor=FakeExecutor(return_proba=False))

    assert des1 in got and des2 in got
    assert len(got) == 2
    assert got[des1].bound_pipeline.name == bp1.name
    assert got[des2].bound_pipeline.name == bp2.name
    assert got[des1].split_dataset == split_dataset
    assert got[des2].split_dataset == split_dataset
    expected_frame = pd.DataFrame({'a': [53, 4, 5030, 53, 4, 5030]})

    got_des1 = got[des1]
    got_des2 = got[des2]
    assert got_des1.prediction is not None
    assert got_des2.prediction is not None

    pd.testing.assert_frame_equal(
        got_des1.prediction.predictions_table.as_(pd.DataFrame), expected_frame)
    pd.testing.assert_frame_equal(
        got_des2.prediction.predictions_table.as_(pd.DataFrame), expected_frame)


def test_probabilities_preserved(
        split_dataset: SplitDataset) -> None:

    bp1 = BoundPipelineStub('bound_pipeline_stub_1')
    bp2 = BoundPipelineStub('bound_pipeline_stub_2')
    des1 = Designator('des1')
    des2 = Designator('des2')
    bound_pipelines: Dict[Designator, BoundPipeline] = {
        des1: bp1, des2: bp2}

    dut = KFoldCrossValidator()
    got = dut.validate_pipelines(
        split_dataset=split_dataset,
        bound_pipelines=bound_pipelines,
        instantiator=InstantiatorFactory(),
        executor=FakeExecutor(return_proba=True))

    expected_frame = pd.DataFrame({'prob': [0.5, 0.6, 0.7, 0.5, 0.6, 0.7]})
    got_des1 = got[des1]
    got_des2 = got[des2]
    assert got_des1.prediction is not None
    assert got_des2.prediction is not None

    pd.testing.assert_frame_equal(
        got_des1.prediction.probabilities.as_(pd.DataFrame),  # type: ignore[attr-defined]
        expected_frame)
    pd.testing.assert_frame_equal(
        got_des2.prediction.probabilities.as_(pd.DataFrame), expected_frame)  # type: ignore[attr-defined] # pylint: disable=line-too-long


def test_error_catching(split_dataset: SplitDataset) -> None:
    '''Properly handle pipeline errors that are caught by the executor

    We expect to find no 'predictions' key in the dataset, but an 'errors' key instead
    '''
    bp1 = BoundPipelineStub('bound_pipeline_stub_1')
    bp2 = BoundPipelineStub('bound_pipeline_stub_2')
    des1 = Designator('des1')
    des2 = Designator('des2')
    bound_pipelines: Dict[Designator, BoundPipeline] = {
        des1: bp1, des2: bp2}

    dut = KFoldCrossValidator()
    got = dut.validate_pipelines(
        split_dataset=split_dataset,
        bound_pipelines=bound_pipelines,
        instantiator=InstantiatorFactory(),
        executor=FakeExecutor(error=True))

    assert des1 in got and des2 in got
    assert len(got) == 2
    assert got[des1].bound_pipeline.name == bp1.name
    assert got[des2].bound_pipeline.name == bp2.name
    assert got[des1].split_dataset == split_dataset
    assert got[des2].split_dataset == split_dataset

    got_des1 = got[des1]
    assert got_des1.prediction is not None
    assert not got_des1.prediction.has_predictions()
    assert isinstance(got_des1.prediction['error'], PredictError)

    got_des2 = got[des2]
    assert got_des2.prediction is not None
    assert 'error' not in got_des2.prediction
    expected_frame = pd.DataFrame({'a': [53, 4, 5030, 53, 4, 5030]})
    pd.testing.assert_frame_equal(
        got_des2.prediction.predictions_table.as_(pd.DataFrame), expected_frame)  # type: ignore[attr-defined]  # pylint: disable=line-too-long


def test_order() -> None:
    bp1 = BoundPipelineStub('bound_pipeline_stub_1')
    des1 = Designator('des1')

    bound_pipelines: Dict[Designator, BoundPipeline] = {des1: bp1}

    met = Metadata(roles={RoleName.TARGET: [Column('target')]})
    empty_dataset = Dataset(metadata=met)
    folds: List[Fold] = []
    for vals in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
        folds.append(Fold(
            train=empty_dataset,
            validate=Dataset(
                dataframe=pd.DataFrame(
                    {'other_column': vals}
                ),
                metadata=met
            )
        ))

    split_dataset = SplitDataset(folds)

    dut = KFoldCrossValidator()
    got = dut.validate_pipelines(
        split_dataset=split_dataset,
        bound_pipelines=bound_pipelines,
        instantiator=InstantiatorFactory(),
        executor=FakeExecutor(order_test=True))

    result = got[des1]
    assert result.prediction is not None
    print(result.prediction.predictions_table)
    assert list(result.prediction.predictions_table['target']) == [2, 3, 4, 5, 6, 7, 8, 9, 10]
