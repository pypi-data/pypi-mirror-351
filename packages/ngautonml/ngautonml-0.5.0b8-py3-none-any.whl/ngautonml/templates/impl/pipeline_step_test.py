'''Tests for PipelineStep and friends.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pytest

from ...algorithms.connect import ConnectorModel
from .pipeline_step import AlreadyDefinedError, PipelineStep
from .pipeline_template import PipelineTemplate

# pylint: disable=missing-function-docstring,protected-access,duplicate-code


def test_name_sunny_day() -> None:
    pipe = PipelineTemplate(name='foo')
    dut = pipe.step()
    assert dut.pipeline_designator_component == '_'
    dut.set_name('Some_Designator')
    assert dut.pipeline_designator_component == 'some_designator'


def test_name_already_defined() -> None:
    pipe = PipelineTemplate(name='foo')
    dut = pipe.step()
    dut.set_name('Some_Designator')
    with pytest.raises(AlreadyDefinedError, match=r'another_designator.*some_designator'):
        dut.set_name('Another_Designator')


def test_nominate_chains() -> None:
    pipe = PipelineTemplate(name='foo')
    dut = pipe.step()
    with pytest.raises(AlreadyDefinedError, match=r'another_designator.*some_designator'):
        dut.set_name('Some_Designator').set_name('Another_Designator')


def test_no_model() -> None:
    pipe = PipelineTemplate(name='foo', tags={})
    step = pipe.step()
    assert not step.has_model()


def test_has_model() -> None:
    pipe = PipelineTemplate(name='foo', tags={})
    step = pipe.step(model=ConnectorModel())
    assert step.has_model()


def test_args_override() -> None:
    pipe = PipelineTemplate(name='foo', tags={})
    step = pipe.step(model=ConnectorModel(), some_arg='some_value', another_arg='another_value')
    assert step.hyperparams(some_arg='different_value', third_arg=3) == {
        'some_arg': 'different_value',
        'another_arg': 'another_value',
        'third_arg': 3,
    }


def test_serialized_model() -> None:
    pipe = PipelineTemplate(name='foo')
    step = pipe.step(model=ConnectorModel(), serialized_model=b'pretend serialized model')
    assert step.serialized_model == b'pretend serialized model'


def test_filename() -> None:
    PipelineStep.reset_serial_number()
    pipe = PipelineTemplate(name='foo', tags={})
    unnamed_step = pipe.step()
    assert unnamed_step.filename is None

    model_step1 = pipe.step(model=ConnectorModel())
    model_step2 = pipe.step(model=ConnectorModel())

    assert model_step1.filename == '@connect_1@'
    assert model_step2.filename == '@connect_2@'

    named_step = pipe.step(model=ConnectorModel()).set_name('frob')
    assert named_step.filename == '@connect_3@frob'

    model_step4 = pipe.step(model=ConnectorModel())
    assert model_step4.filename == '@connect_4@'

    # Make sure that names are stable.
    assert model_step1.filename == '@connect_1@'
