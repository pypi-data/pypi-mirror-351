'''Tests for wrangler_base.py'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code
# pylint: disable=missing-class-docstring,protected-access


from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
import pytest

from ..executor.executor import ExecutorStub
from ..executor.simple.simple_executor import SimpleExecutor
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import (
    ExecutablePipeline, ExecutablePipelineStub, PipelineResult)
from ..metrics.impl.metric import MetricInvalidDatasetError
from ..problem_def.problem_def import ProblemDefinition
from ..tables.impl.table import TableFactory
from ..tables.impl.table_auto import TableCatalogAuto
from ..templates.impl.pipeline_template import PipelineTemplate
from ..templates.impl.template import TemplateCatalog

from .dataset import Column, Dataset, Metadata, RoleName
from .wrangler_base import WranglerBase, WranglerFailure

_ = TableCatalogAuto()  # pylint: disable=pointless-statement


# fakes -----------------------------------------------------

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


class FakeTemplateCatalog(TemplateCatalog):
    '''fake, no templates'''


class FakeWrangler(WranglerBase):

    def lookup_templates(self) -> Dict[str, PipelineTemplate]:
        return {}


# data -----------------------------------------------------


@pytest.fixture(scope='session')
def classification_results() -> Tuple[Dataset, Dataset]:
    metadata = Metadata(
        roles={RoleName.TARGET: [Column('target')]},
        pos_labels={RoleName.TARGET: 'a'})
    pred = Dataset(metadata=metadata)
    pred.predictions_table = TableFactory({'target': ['a', 'b', 'b', 'a']})
    pred.probabilities = TableFactory({'target': [.3, .4, .5, .5]})

    ground_truth = Dataset(metadata=metadata)
    ground_truth.ground_truth_table = TableFactory({'target': ['a', 'a', 'b', 'a']})
    return (pred, ground_truth)


def get_data() -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    data = pd.DataFrame(
        {
            'a': range(1, 21),
            'b': range(1, 21),
            'c': range(1, 21)
        }
    )
    return (data, data)

# problem def -----------------------------------------------------


def memory_problem_def() -> ProblemDefinition:
    return ProblemDefinition(clause={
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
        }
    })

# tests ----------------------------------------------------------


def test_init_default() -> None:
    '''Test the components that wrangler defaults to.'''
    (train_data, test_data) = get_data()  # noqa: F841  # pylint: disable=unused-variable
    dut = FakeWrangler(problem_definition=memory_problem_def())
    assert dut._generator.__class__.__name__ == "GeneratorImpl"
    assert dut._template_catalog.__class__.__name__ == "TemplateCatalogAuto"


def test_init_custom() -> None:
    '''Test that overriding components when initializing the wrangler works.'''
    (train_data, test_data) = get_data()  # noqa: F841  # pylint: disable=unused-variable
    dut = FakeWrangler(
        problem_definition=memory_problem_def(),
        executor=FakeExecutor,
        template_catalog=FakeTemplateCatalog)
    assert dut._executor.__class__.__name__ == "FakeExecutor"
    assert dut._template_catalog.__class__.__name__ == "FakeTemplateCatalog"

    # Testing that non-set arguments are still default
    assert dut._generator.__class__.__name__ == "GeneratorImpl"


def test_wrangler_dataset() -> None:
    '''Test wrangler.dataset(), which takes a dataframe and returns a
    dataset containing the dataframe with metadata matching the problem definition.'''
    (train_data, test_data) = get_data()  # noqa: F841 pylint: disable=unused-variable
    problem_def = memory_problem_def()
    new_data = {
        'a': range(1, 31),
        'b': range(1, 31),
        'c': range(1, 31),
    }

    dut = FakeWrangler(
        problem_definition=problem_def,
        executor=FakeExecutor)

    got = dut.ez_dataset(new_data)

    # Confirm that the dataframe matches
    pd.testing.assert_frame_equal(
        got.dataframe_table.as_(pd.DataFrame),
        pd.DataFrame(new_data))

    # Confirm that at least part of the metadata matches.
    assert set(got.metadata.roles[RoleName.ATTRIBUTE]) == {Column('a'), Column('b')}


def test_predict_bad_executor_kind() -> None:
    (train_data, test_data) = get_data()  # pylint: disable=unused-variable
    problem_def = memory_problem_def()
    executor = SimpleExecutor
    dut = FakeWrangler(
        problem_definition=problem_def,
        executor=executor)

    fake_des = Designator('fake_des')
    stub_pipeline = ExecutablePipelineStub(trained=True)

    with pytest.raises(WranglerFailure, match=r'(fake_des.*simple)|(simple.*fake_des)/i'):
        dut.predict(
            new_data=Dataset(),
            trained_pipelines={fake_des: stub_pipeline})


def test_predict_untrained_pipeline() -> None:
    (train_data, test_data) = get_data()  # pylint: disable=unused-variable
    problem_def = memory_problem_def()
    executor = FakeExecutor  # executor kind is 'stub_executor_kind', should match stub pipeline.
    dut = FakeWrangler(
        problem_definition=problem_def,
        executor=executor)

    fake_des = Designator('fake_des')
    stub_pipeline = ExecutablePipelineStub(trained=False)

    with pytest.raises(WranglerFailure, match=r'(fake_des.*trained)|(trained.*fake_des)/i'):
        dut.predict(
            new_data=Dataset(),
            trained_pipelines={fake_des: stub_pipeline})


def test_roc_curve(classification_results: Tuple[Dataset, Dataset]) -> None:
    pred, ground_truth = classification_results
    pred_no_proba = Dataset(pred, metadata=pred.metadata)
    del pred_no_proba['probabilities']
    dut = FakeWrangler(problem_definition=ProblemDefinition({
        "dataset": {
            "config": "ignore"
        },
        "problem_type": {
            "task": "test_task"
        },
    }))
    designator1 = Designator("fake_algorithm1")
    designator2 = Designator("fake_algorithm2")
    designator3 = Designator("fake_algorithm3")
    results: Dict[Designator, Optional[Dataset]] = {
        designator1: pred,
        designator2: None,
        designator3: pred_no_proba
    }
    got = dut.roc_curve(results=results, ground_truth=ground_truth)
    want = TableFactory({
        'fpr': [0.0, 1.0 / 3.0, 1.0],
        'thresholds': [np.inf, 0.5, 0.3],
        'tpr': [0.0, 1.0, 1.0],
    })

    got_designator1 = got[designator1]
    assert isinstance(got_designator1, Dataset)
    pd.testing.assert_frame_equal(got_designator1.dataframe_table.as_(pd.DataFrame),
                                  want.as_(pd.DataFrame))

    got_designator2 = got[designator2]
    assert got_designator2 is None

    got_designator3 = got[designator3]
    assert isinstance(got_designator3, MetricInvalidDatasetError)
