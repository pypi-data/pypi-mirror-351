'''Tests for SimpleStep'''
# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import re

from ...algorithms.connect import ConnectorModel
from ...algorithms.impl.fake_algorithm import FakeAlgorithm, FAKE_SERIALIZED
from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import StepDesignator
from ...templates.impl.pipeline_template import PipelineTemplate
from ...wrangler.dataset import Dataset
from .simple_executable_step import SimpleExecutableStep


# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code,protected-access

REFERENCE_DATASET = Dataset(
    a_key='a_value',
    another_key='another_value',
    ignored_key='ignored_value'
)


def strip_serial(key: StepDesignator) -> str:
    return re.sub('[0-9]+', 'NUM', key)


def test_sunny_day() -> None:
    pipe = PipelineTemplate(name='foo', tags={})
    model = ConnectorModel()
    step = pipe.step(model=model, new_key='a_key', another_key='another_key')
    dut = SimpleExecutableStep(bound_step=step)
    got = dut.predict(dataset=REFERENCE_DATASET)
    want = {
        'new_key': 'a_value',
        'another_key': 'another_value',
    }
    assert got == want


def test_name_propagation() -> None:
    '''Test that when you create an executable pipeline from a bound pipeline,
    the name and serial number propagates correctly.
    '''
    pipe = PipelineTemplate(name='foo', tags={})
    model = ConnectorModel()
    step = pipe.step(model=model).set_name('the_name_we_want')
    dut = SimpleExecutableStep(bound_step=step)
    assert dut.opt_name == 'the_name_we_want'
    assert dut.filename == step.filename
    assert dut.filename is not None
    assert strip_serial(dut.filename) == '@connect_NUM@the_name_we_want'


def test_cucumberize_all() -> None:
    pipe = BoundPipeline(name='foo', tags={})
    model = ConnectorModel(some_param='some_value')
    step = pipe.step(model=model,
                     bound_added_param='bound_added_value').set_name('the_name_we_want')
    dut = SimpleExecutableStep(
        bound_step=step)

    got_jar = dut.cucumberize_all(pipeline_designator=pipe.designator)
    assert len(got_jar) == 1
    got_cucumber = list(got_jar.values())[0]
    assert strip_serial(got_cucumber.filename) == '@connect_NUM@the_name_we_want'
    assert got_cucumber.catalog_name == 'connect'
    assert got_cucumber.pipeline_designator == pipe.designator
    assert got_cucumber.hyperparams == {
        'some_param': 'some_value',
        'bound_added_param': 'bound_added_value'}


def test_serialize_deserialize_instance():
    pipe = BoundPipeline(name='foo', tags={})
    model = FakeAlgorithm(some_param='some_value')
    instance = model.instantiate()
    serialized_model = instance.serialize()
    assert instance.evidence_of_deserialize is None
    step = pipe.step(model=model,
                     serialized_model=serialized_model)
    dut = SimpleExecutableStep(bound_step=step)
    assert dut._model_instance.evidence_of_deserialize == FAKE_SERIALIZED
