'''Tests for cucumber.py'''
# pylint: disable=missing-class-docstring, missing-function-docstring,duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pytest

from ..algorithms.connect import ConnectorModel
from ..algorithms.impl.fake_algorithm import (FakeAlgorithm, FakeInstance,
                                              FAKE_SERIALIZED)
from ..generator.designator import Designator, StepDesignator

from .cucumber import Cucumber, DeserializationError


def test_cucumber_sunny_day() -> None:

    dut = Cucumber(
        impl=FakeAlgorithm().instantiate(),
        filename=StepDesignator('test_filename'),
        pipeline_designator=Designator('test_pipeline_designator'),
        hyperparams={'param 1': 'value_1'})

    got: Cucumber = Cucumber.deserialize(dut.serialize())

    assert got.filename == StepDesignator('test_filename')
    assert got.pipeline_designator == Designator('test_pipeline_designator')
    assert got.hyperparams['param 1'] == 'value_1'
    assert got.catalog_name == 'fake_algorithm'
    inst = got.deserialize_model(alg=FakeAlgorithm())
    assert isinstance(inst, FakeInstance)
    assert inst.evidence_of_deserialize == FAKE_SERIALIZED

    # We want deserialize_model() to create the instance with hyperparams saved from the cucumber,
    # instead of relying on the serialized model to hold its own hyperparams properly.
    assert inst.hyperparams() == {'param 1': 'value_1'}


def test_cucumber_deserialize_with_incorrect_alg() -> None:
    dut = Cucumber(
        impl=FakeAlgorithm().instantiate(),
        filename=StepDesignator('test_filename'),
        pipeline_designator=Designator('test_pipeline_designator'),
        hyperparams={})

    got: Cucumber = Cucumber.deserialize(dut.serialize())
    with pytest.raises(DeserializationError,
                       match=r'(connect.*fake_algorithm)|(fake_algorithm.*connect)'):
        got.deserialize_model(alg=ConnectorModel())
