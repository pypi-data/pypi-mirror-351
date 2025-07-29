'''Tests for the AlgorithmInstance class implementations'''
from typing import Optional

import pandas as pd

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.dataset import Dataset, ez_dataset

from .algorithm import Algorithm
from .sklearn_like_algorithm_instance import SklearnLikeAlgorithmInstance

# pylint: disable=missing-function-docstring,duplicate-code
# pylint: disable=missing-class-docstring
TableCatalogAuto()


class FakeImpl():
    '''Fake implementation of a model.'''
    dataset: Optional[Dataset] = None

    def __init__(self, **kwargs):
        pass

    def fit(self, dataset: Optional[Dataset]) -> None:
        self.dataset = dataset

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        return dataset


class FakeFitter(Algorithm):
    '''Pretend to do something with data.'''
    _name = 'fake_model'

    def instantiate(self, **kwargs) -> 'FakeFitterInstance':
        return FakeFitterInstance(parent=self, **kwargs)


class FakeFitterInstance(SklearnLikeAlgorithmInstance):
    '''Pretend to fit data.'''
    _impl = FakeImpl()
    _constructor = FakeImpl

    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)

    def fit(self, dataset: Optional[Dataset]) -> None:
        '''Fit a model based on train data.'''
        self._impl.fit(dataset)
        self._trained = True

    @property
    def dataset(self) -> Optional[Dataset]:
        return self._impl.dataset


REFERENCE_DATASET = Dataset(
    a_key='a_value',
    another_key='another_value',
)


PREDICT_DATASET = ez_dataset({'covariate1': [1, 2, 3]})


PREDICTED_DATASET = Dataset(
    predictions=pd.DataFrame({'covariate1': [1, 2, 3]}))


def test_serialize_round_trip() -> None:
    dut = FakeFitter()
    inst = dut.instantiate()
    assert inst.dataset is None
    inst.fit(dataset=REFERENCE_DATASET)
    saved = inst.serialize()
    inst = dut.instantiate()
    loaded_inst = inst.deserialize(serialized_model=saved)
    assert isinstance(loaded_inst, FakeFitterInstance)
    assert loaded_inst.dataset == REFERENCE_DATASET


def test_predict_sunny_day() -> None:
    dut = FakeFitter()
    inst = dut.instantiate()

    inst.fit(dataset=REFERENCE_DATASET)
    got = inst.predict(dataset=PREDICT_DATASET)
    assert got is not None
    pd.testing.assert_frame_equal(got.predictions_table.as_(pd.DataFrame),
                                  PREDICTED_DATASET.predictions_table.as_(pd.DataFrame))
