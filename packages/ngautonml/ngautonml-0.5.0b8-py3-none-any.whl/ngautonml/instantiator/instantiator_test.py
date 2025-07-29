'''Tests for the Instantiator class implementations'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .instantiator import InstantiatorStub
from ..generator.bound_pipeline import BoundPipelineStub
from ..generator.designator import Designator

# pylint: disable=missing-function-docstring,duplicate-code
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


def test_sunny_day() -> None:
    dut = InstantiatorStub()
    bpl = BoundPipelineStub('bound_pipeline_stub')
    res = dut.instantiate(pipeline=bpl)
    assert res is not None
    assert 'bound_pipeline_stub' == res.name


def test_instantiate_all() -> None:
    dut = InstantiatorStub()
    bpl1 = BoundPipelineStub('bound_pipeline_stub_1')
    bpl2 = BoundPipelineStub('bound_pipeline_stub_2')
    des1 = Designator('des1')
    des2 = Designator('des2')
    res = dut.instantiate_all(pipelines={
        des1: bpl1,
        des2: bpl2})
    assert des1 in res and des2 in res
    assert 'bound_pipeline_stub_1' == res[des1].name
    assert 'bound_pipeline_stub_2' == res[des2].name
