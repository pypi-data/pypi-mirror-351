'''Tests for fittable_algorithm_instance.py'''
import pickle
from typing import Optional
import pytest

from ...wrangler.dataset import Dataset

from .algorithm import Algorithm
from .fake_algorithm import FakeAlgorithm
from .fittable_algorithm_instance import (FittableAlgorithmInstance,
                                          UntrainedError,
                                          DeserializationError)

# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=protected-access,duplicate-code


class FakeFitterInstance(FittableAlgorithmInstance):
    _some_attr: str

    def __init__(self, parent: Algorithm):
        super().__init__(parent=parent)
        self._some_attr = '1'

    def fit(self, dataset: Optional[Dataset]) -> None:
        self._some_attr = '2'
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        dataset['some_attr'] = self._some_attr
        return dataset


def test_serialize_deserialize_round_trip() -> None:
    dut = FakeFitterInstance(parent=FakeAlgorithm())
    dut.fit(dataset=Dataset())
    got = dut.deserialize(dut.serialize())
    assert isinstance(got, FakeFitterInstance)
    assert got._some_attr == '2'


def test_serialize_not_trained() -> None:
    dut = FakeFitterInstance(parent=FakeAlgorithm())
    with pytest.raises(UntrainedError, match='serialize'):
        _ = dut.serialize()


def test_deserialize_not_pickle() -> None:
    dut = FakeFitterInstance(parent=FakeAlgorithm())
    with pytest.raises(DeserializationError, match='pickle'):
        _ = dut.deserialize(b'not a pickle')


def test_deserialize_not_pickled_instance() -> None:
    dut = FakeFitterInstance(parent=FakeAlgorithm())
    with pytest.raises(DeserializationError, match='float'):
        _ = dut.deserialize(pickle.dumps(1.234))
