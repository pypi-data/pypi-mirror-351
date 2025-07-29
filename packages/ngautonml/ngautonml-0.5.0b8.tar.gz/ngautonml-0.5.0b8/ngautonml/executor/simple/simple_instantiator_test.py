'''Tests for SimpleInstantiator'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import Designator
from ...algorithms.connect import ConnectorModel
from ...wrangler.dataset import Dataset

from .simple_instantiator import SimpleInstantiator

# pylint: disable=missing-function-docstring,duplicate-code


REFERENCE_DATASET = Dataset(
    a_key='a_value',
    another_key='another_value',
)


def test_sunny_day() -> None:
    pipe = BoundPipeline(name=Designator('foo'), tags={})
    connector = ConnectorModel()
    pipe.step(model=connector, new_key='a_key', another_key='another_key').set_name('connector1')
    pipe.step(model=connector,
              twice_transformed_key='new_key', another_key='another_key').set_name('connector2')

    dut = SimpleInstantiator()

    executable = dut.instantiate(pipeline=pipe)

    executable.fit(dataset=REFERENCE_DATASET)

    got_predict = executable.predict(dataset=REFERENCE_DATASET)
    want_predict = {
        'twice_transformed_key': 'a_value',
        'another_key': 'another_value',
    }
    assert got_predict.prediction is not None
    assert set(got_predict.prediction) == set(want_predict)
