'''Tests for single_fold_validator.py'''
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=super-init-not-called,unused-argument,duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict

from ..executor.executor import ExecutorStub
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import (ExecutablePipeline,
                                                PipelineResult)
from ..instantiator.instantiator_factory import InstantiatorFactory
from ..splitters.impl.splitter import Fold, SplitDataset
from ..wrangler.dataset import Dataset
from .single_fold_validator import SingleFoldValidator


class FakeExecutor(ExecutorStub):

    def predict(self,
                dataset: Dataset,
                pipelines: Dict[Designator, ExecutablePipeline]
                ) -> Dict[Designator, PipelineResult]:
        '''Does not use pipeline, instead rewrites dataset to {'newkey': 'newval'}'''
        predictions = dataset.output()
        predictions['newkey'] = 'newval'
        return {d: PipelineResult(executable_pipeline=p, prediction=predictions)
                for d, p in pipelines.items()}


def test_sunny_day() -> None:
    pipe = BoundPipeline(name=Designator('des'), tags={})
    split_data = SplitDataset([Fold(
        train=Dataset({'k_tr': 'v_tr'}),
        validate=Dataset({'k_va': 'v_va'}))])
    dut = SingleFoldValidator()
    res = dut.validate_pipelines(
        split_dataset=split_data,
        bound_pipelines={Designator('des'): pipe},
        instantiator=InstantiatorFactory(),
        executor=FakeExecutor())

    assert Designator('des') in res
    single_res = res[Designator('des')]
    assert single_res.prediction == Dataset({'newkey': 'newval'})
    assert single_res.split_dataset is not None
    assert single_res.split_dataset.folds[0].train == Dataset({'k_tr': 'v_tr'})
    assert single_res.split_dataset.folds[0].validate == Dataset({'k_va': 'v_va'})
