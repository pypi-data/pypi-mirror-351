'''Tests for matchers.py'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional
from ..algorithms.impl.algorithm import Algorithm
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..generator.bound_pipeline import BoundPipeline
from ..wrangler.constants import Matcher
from ..wrangler.dataset import Dataset

from .matchers import MatcherFactory

# pylint: disable=missing-class-docstring, missing-function-docstring, duplicate-code


class FakeAlgorithmInstance(AlgorithmInstance):
    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        return Dataset(dataset.copy())


class FakeAlgorithm(Algorithm):
    _name = 'fake_algorithm'
    _default_hyperparams = {
        'base_param': 'base_value',
        'param_to_override': 'value_to_override',
    }
    _tags = {
        'some_tag': [
            'some_tag_value',
            'different_tag_value',
        ],
        'another_tag': [
            'another_tag_value',
        ]
    }

    def instantiate(self, **hyperparams) -> FakeAlgorithmInstance:
        return FakeAlgorithmInstance(parent=self, **hyperparams)


def test_algorithm_sunny_day():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm())

    factory = MatcherFactory()
    dut = factory.make(Matcher.ALGORITHM, args='fake_algorithm')
    assert dut.matches(step, pipeline)


def test_algorithm_no_match():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm())

    factory = MatcherFactory()
    dut = factory.make(Matcher.ALGORITHM, args='real_algorithm')
    assert not dut.matches(step, pipeline)


def test_algorithm_no_model():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step().set_name('some_name')

    factory = MatcherFactory()
    dut = factory.make(Matcher.ALGORITHM, args='some_name')
    assert not dut.matches(step, pipeline)


def test_designator_sunny_day():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm()).mark_queried()

    factory = MatcherFactory()
    dut = factory.make(Matcher.DESIGNATOR, args='a_pipeline@fake_algorithm')
    assert dut.matches(step, pipeline)


def test_designator_no_model():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step()

    factory = MatcherFactory()
    dut = factory.make(Matcher.DESIGNATOR, args='a_pipeline')
    assert dut.matches(step, pipeline)


def test_designator_no_match():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm())

    factory = MatcherFactory()
    dut = factory.make(Matcher.DESIGNATOR, args='fake_algorithm')
    assert not dut.matches(step, pipeline)


def test_name_sunny_day():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm()).set_name('fake_step')

    factory = MatcherFactory()
    dut = factory.make(Matcher.NAME, args='fake_step')
    assert dut.matches(step, pipeline)


def test_name_no_match():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm()).set_name('fake_step')

    factory = MatcherFactory()
    dut = factory.make(Matcher.NAME, args='real_step')
    assert not dut.matches(step, pipeline)


def test_name_no_model():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step().set_name('fake_step')

    factory = MatcherFactory()
    dut = factory.make(Matcher.NAME, args='fake_step')
    assert dut.matches(step, pipeline)


def test_tags_sunny_day():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm())

    factory = MatcherFactory()
    dut = factory.make(Matcher.TAGS, args={
        'some_tag': 'some_tag_value',
    })
    assert dut.matches(step, pipeline)


def test_tags_no_match():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(model=FakeAlgorithm())

    factory = MatcherFactory()
    dut = factory.make(Matcher.TAGS, args={
        'some_tag': 'nonmatching_tag_value',
    })
    assert not dut.matches(step, pipeline)


def test_tags_no_model():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step()

    factory = MatcherFactory()
    dut = factory.make(Matcher.TAGS, args={
        'some_tag': 'some_tag_value',
    })
    assert not dut.matches(step, pipeline)


def test_tags_all_must_match_failure():
    '''All the keys must have a matching value.'''
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(FakeAlgorithm())

    factory = MatcherFactory()
    dut = factory.make(Matcher.TAGS, args={
        'some_tag': 'some_tag_value',
        'another_tag': 'missing_tag_value',
    })
    assert not dut.matches(step, pipeline)


def test_tags_all_must_match_sunny():
    pipeline = BoundPipeline(name='a_pipeline')
    step = pipeline.step(FakeAlgorithm())

    factory = MatcherFactory()
    dut = factory.make(Matcher.TAGS, args={
        'some_tag': 'some_tag_value',
        'another_tag': 'another_tag_value',
    })
    assert dut.matches(step, pipeline)
