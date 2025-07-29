'''Test PipelineTemplate object.'''
from typing import Any

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


from ...algorithms.impl.algorithm import Algorithm
from .pipeline_template import PipelineTemplate

# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code,protected-access


class ModelStub(Algorithm):
    def instantiate(self, **unused_kwargs) -> Any:
        return None


def test_instantiate() -> None:
    dut = PipelineTemplate(name='Fake_Template')
    assert dut.name == 'fake_template'


def test_step() -> None:
    dut = PipelineTemplate(name='Fake_Template')
    step_a = dut.step(ModelStub('A'))
    step_t = dut.step(ModelStub('T'))
    assert dut._steps == [step_a, step_t]
