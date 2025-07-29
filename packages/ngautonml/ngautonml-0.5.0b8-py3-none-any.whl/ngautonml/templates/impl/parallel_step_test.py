'''Tests for ParallelStep'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any

from ...algorithms.impl.algorithm import Algorithm
from .parallel_step import ParallelStep
from .pipeline_template import PipelineTemplate

# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code,protected-access


class ModelStub(Algorithm):
    def instantiate(self, **unused_kwargs) -> Any:
        return None


def test_parallel() -> None:
    dut = PipelineTemplate(name='Fake_Template')
    pipe1 = dut.new(name='at')
    step1a = pipe1.step(ModelStub('A'))
    step1t = pipe1.step(ModelStub('T'))
    pipe2 = dut.new(name='dt')
    step2d = pipe2.step(ModelStub('D'))
    step2t = pipe2.step(ModelStub('T'))
    parallel_step = dut.parallel(left=pipe1, right=pipe2)
    assert len(dut._steps) == 1
    assert isinstance(parallel_step, ParallelStep)
    assert set(parallel_step.subpipeline_keys) == set(['left', 'right'])
    assert parallel_step.subpipeline('left')._steps == [step1a, step1t]
    assert parallel_step.subpipeline('right')._steps == [step2d, step2t]
