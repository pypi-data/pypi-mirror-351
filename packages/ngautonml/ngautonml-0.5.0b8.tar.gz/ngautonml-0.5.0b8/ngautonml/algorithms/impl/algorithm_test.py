'''Tests for Algorithm object'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional
import pytest

from ...problem_def.task import TaskType
from ...wrangler.dataset import Dataset
from .algorithm import Algorithm, AlgorithmCatalogStub
from .algorithm_instance import AlgorithmInstance

# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=protected-access, duplicate-code


class FakeAlgorithmInstance(AlgorithmInstance):
    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        return Dataset(dataset.copy())


class FakeAlgorithm(Algorithm):
    _name = 'fake algorithm'
    _default_hyperparams = {
        'base_param': 'base_value',
        'param_to_override': 'value_to_override',
    }
    _tags = {
        'task': [
            TaskType.REGRESSION.name,
            TaskType.BINARY_CLASSIFICATION.name,
        ]
    }
    _hyperparam_lookup = {
        'typed_param': {
            '<class \'float\'>': float,
            '<class \'int\'>': int,
        }
    }

    def instantiate(self, **hyperparams) -> FakeAlgorithmInstance:
        return FakeAlgorithmInstance(parent=self, **hyperparams)


class FakeAlgorithm2(Algorithm):
    _name = 'fake algorithm with different tags'
    _default_hyperparams = {
        'base_param': 'base_value',
        'param_to_override': 'value_to_override',
    }
    _tags = {
        'task': [
            TaskType.BINARY_CLASSIFICATION.name,
            TaskType.MULTICLASS_CLASSIFICATION.name,
        ]
    }

    def instantiate(self, **hyperparams) -> FakeAlgorithmInstance:
        return FakeAlgorithmInstance(parent=self, **hyperparams)


def test_hyperparams_at_construction() -> None:
    algorithm = FakeAlgorithm(param_to_override='overridden_value')
    assert algorithm.hyperparams(instantiation_time_param='instantiation_value') == {
        'base_param': 'base_value',
        'param_to_override': 'overridden_value',
        'instantiation_time_param': 'instantiation_value',
    }

    algorithm2 = FakeAlgorithm()
    assert algorithm2.hyperparams() == {
        'base_param': 'base_value',
        'param_to_override': 'value_to_override',
    }


def test_algorithm_catalog_basic() -> None:
    dut = AlgorithmCatalogStub()
    fm1 = FakeAlgorithm()
    fm2 = FakeAlgorithm()
    output = dut.register(obj=fm1)
    print(f'register output: {output}')
    assert output == 'fake algorithm'
    assert dut.register(obj=fm2, name='override name') == 'override name'
    assert dut.lookup_by_name('fake algorithm') == fm1
    assert dut.lookup_by_name('override name') == fm2


def test_algorithm_catalog_lookup_by_tags() -> None:
    dut = AlgorithmCatalogStub()
    fm1 = FakeAlgorithm()
    fm2 = FakeAlgorithm2()
    dut.register(fm1)
    dut.register(fm2)
    assert len(dut.lookup_by_tag_and(
        task=TaskType.BINARY_CLASSIFICATION.name)) == 2
    assert len(dut.lookup_by_tag_and(
        task=TaskType.MULTICLASS_CLASSIFICATION.name)) == 1
    assert len(dut.lookup_by_tag_and(
        task=TaskType.FORECASTING.name)) == 0


def test_algorithm_catalog_get_tag_types() -> None:
    dut = AlgorithmCatalogStub()
    dut.register(FakeAlgorithm())
    assert dut.tagtypes == {'task'}


def test_algorithm_catalog_get_tag_values() -> None:
    dut = AlgorithmCatalogStub()
    dut.register(FakeAlgorithm())
    dut.register(FakeAlgorithm2())
    want = {TaskType.BINARY_CLASSIFICATION.name.lower(),
            TaskType.MULTICLASS_CLASSIFICATION.name.lower(),
            TaskType.REGRESSION.name.lower()}
    assert dut.tagvals('task') == want


def test_algorithm_parse_and_repr() -> None:
    dut = FakeAlgorithm()
    assert dut._param_from_json('typed_param', '<class \'float\'>') == float
    assert dut.param_to_json('typed_param', float) == '<class \'float\'>'


def test_algorithm_parse_and_repr_default() -> None:
    dut = FakeAlgorithm()
    assert dut._param_from_json('some_param', 'some_value') == 'some_value'
    assert dut.param_to_json('some_param', 'some_value') == 'some_value'


def test_algorithm_parse_fail() -> None:
    dut = FakeAlgorithm()
    with pytest.raises(KeyError, match='typed_param'):
        _ = dut._param_from_json('typed_param', 'missing_value')


def test_algorithm_repr_fail() -> None:
    dut = FakeAlgorithm()
    with pytest.raises(KeyError, match='typed_param'):
        _ = dut.param_to_json('typed_param', 'missing_value')
