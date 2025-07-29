'''Tests for BoundPipeline'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pytest

from ..algorithms.impl.algorithm import AlgorithmStub
from ..generator.designator import Designator
from ..searcher.frozen_overrides import FrozenOverrides

from .bound_pipeline import BoundPipelineStub, ValidationError

# pylint: disable=missing-function-docstring,duplicate-code


def test_empty_pipeline_is_valid() -> None:
    dut = BoundPipelineStub(name='Fake_Template', tags={'DATATYPE': 'IMAGE'})
    dut.validate()


def test_step() -> None:
    dut = BoundPipelineStub(name='Fake_Template', tags={'DATATYPE': 'IMAGE'})
    dut.step(model=AlgorithmStub('A'))
    dut.step(model=AlgorithmStub('T'))
    dut.validate()


def test_invalid() -> None:
    dut = BoundPipelineStub(name='Fake_Template', tags={'DATATYPE': 'IMAGE'})
    dut.step()
    dut.step().set_name("step2")
    with pytest.raises(ValidationError, match='step2'):
        dut.validate()


def test_parallel() -> None:
    dut = BoundPipelineStub(name='Fake_Template')
    pipe1 = dut.new(name='at')
    pipe1.step(AlgorithmStub('A'))
    pipe1.step(AlgorithmStub('T'))
    pipe2 = dut.new(name='dt')
    pipe2.step(AlgorithmStub('D'))
    pipe2.step(AlgorithmStub('T'))
    dut.parallel(left=pipe1, right=pipe2)
    dut.validate()


def test_parallel_invalid() -> None:
    '''Confirm that errors on multiple pipelines are all reported.

    The errors here are both missing models, but on separate pipelines.
    '''
    dut = BoundPipelineStub(name='Fake_Template')
    pipe1 = dut.new(name='at')
    pipe1.step(AlgorithmStub('A'))
    pipe1.step().set_name('missing_t')
    pipe2 = dut.new(name='dt')
    pipe2.step().set_name('missing_d')
    pipe2.step(AlgorithmStub('T'))
    dut.parallel(left=pipe1, right=pipe2)
    with pytest.raises(ValidationError, match='missing_.*missing_'):
        dut.validate()


def test_designator_generation() -> None:
    dut = BoundPipelineStub(name='opt_name')
    dut.step(AlgorithmStub('query1')).mark_queried()
    dut.step(AlgorithmStub('nonquery2'))
    dut.step(AlgorithmStub('query3')).mark_queried()
    dut.step(AlgorithmStub('nonquery4'))

    assert str(dut.designator) == 'opt_name@query1@query3'

    frozen_overrides = FrozenOverrides.freeze({
        'query3': {'h': 'v'},
        'nonquery4': {'h1': 'v1', 'h2': 'v2'}})
    got = BoundPipelineStub.build(
        steps=dut.steps,
        template_name=Designator("new_template_name"),
        frozen_overrides=frozen_overrides)

    want = 'new_template_name@query1@query3:h=v@nonquery4:h1=v1,h2=v2'
    assert str(got.designator) == want

    want_family = 'new_template_name@query1@query3'
    assert str(got.family_designator) == want_family
