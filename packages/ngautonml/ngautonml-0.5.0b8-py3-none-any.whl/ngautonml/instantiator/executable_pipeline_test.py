'''Tests for pipeline_result.py'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pandas as pd
import pytest

from ..generator.bound_pipeline import BoundPipelineStub
from ..generator.designator import Designator
from ..splitters.impl.splitter import SplitDataset, Fold
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Dataset, Metadata, RoleName, Column, TableFactory
from .executable_pipeline import ExecutablePipelineStub
from .executable_pipeline import PipelineResult, PipelineResultError, PipelineResults

# pylint: disable=missing-function-docstring,duplicate-code
TableCatalogAuto()  # pylint: disable=pointless-statement


def test_executable_pipelines_sunny_day() -> None:
    pr1 = PipelineResult(
        prediction=Dataset(),
        executable_pipeline=ExecutablePipelineStub(
            pipeline=BoundPipelineStub(name='stub pipeline 1'),
            trained=True))
    pr2 = PipelineResult(
        prediction=Dataset(),
        executable_pipeline=ExecutablePipelineStub(
            pipeline=BoundPipelineStub(name='stub pipeline 2'),
            trained=True))
    des1 = Designator('des1')
    des2 = Designator('des2')
    dut = PipelineResults({
        des1: pr1, des2: pr2})
    assert des1 in dut.executable_pipelines
    assert des2 in dut.executable_pipelines
    assert dut.executable_pipelines[des1].name == 'stub pipeline 1'
    assert dut.executable_pipelines[des2].name == 'stub pipeline 2'


def test_executable_pipelines_fail() -> None:
    '''Test that PipelineResult properly raises an error
    if executable_pipelines property is called when not all
    results have executable pipelines.
    '''
    pr1 = PipelineResult(
        prediction=Dataset(),
        executable_pipeline=ExecutablePipelineStub(
            pipeline=BoundPipelineStub(name='stub pipeline 1'),
            trained=True))
    bound_only = PipelineResult(
        prediction=Dataset(),
        bound_pipeline=BoundPipelineStub(
            name='bound stub pipeline'))
    des1 = Designator('des1')
    des2 = Designator('des2')
    dut = PipelineResults({
        des1: pr1, des2: bound_only})

    with pytest.raises(PipelineResultError, match='bound stub pipeline'):
        _ = dut.executable_pipelines


def test_add_ground_truth() -> None:
    empty = Dataset(
        dataframe=pd.DataFrame(),
        metadata=Metadata(
            roles={RoleName.TARGET: [Column('a')]}
        )
    )
    pred = empty.output()
    pred.predictions_table = TableFactory(
        {'a': [1, 2, 3]})
    gt = empty.output()
    gt.ground_truth_table = TableFactory(
        {'a': [4, 5, 6]}
    )
    dut = PipelineResult(
        prediction=pred,
        bound_pipeline=BoundPipelineStub('stub bound pipeline'),
        split_dataset=SplitDataset([
            Fold(
                train=empty,
                validate=empty,
                ground_truth=gt
            )
        ]))
    assert dut.prediction is not None
    got = dut.prediction.predictions_table
    want = pd.DataFrame({
        'a': [1, 2, 3],
        'ground truth': [4, 5, 6]
    })
    pd.testing.assert_frame_equal(got.as_(pd.DataFrame), want)
