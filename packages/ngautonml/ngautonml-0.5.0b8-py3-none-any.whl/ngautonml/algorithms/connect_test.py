'''Tests for connect.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pytest

from ..algorithms.impl.algorithm import InputKeyError
from .connect import ConnectorModel
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Dataset
# pylint: disable=missing-function-docstring,duplicate-code
_ = TableCatalogAuto()


def test_sunny_day() -> None:
    model = ConnectorModel()
    instance = model.instantiate(b='a', c='b')

    dataset = Dataset(
        a=[1, 2, 3],
        b='something else'
    )

    got = instance.predict(dataset)
    want = Dataset(
        b=[1, 2, 3],
        c='something else'
    )

    assert got == want


def test_discard_key() -> None:
    model = ConnectorModel()
    instance = model.instantiate(b='a')
    dataset = Dataset(
        a=[1, 2, 3],
        x=[4, 5, 6]
    )

    got = instance.predict(dataset)
    want = Dataset(
        b=[1, 2, 3]
    )

    assert got == want


def test_key_missing() -> None:
    model = ConnectorModel()
    instance = model.instantiate(b='a', c='b')
    dataset = Dataset(
        a=[1, 2, 3]
    )

    with pytest.raises(InputKeyError):
        instance.predict(dataset)


LAYERS_DATASET = Dataset(
    base_key1='base_value1',
    base_key2='base_value2',
    base_key3='base_value3'
)


def test_layers_instance_only_selects() -> None:
    model1 = ConnectorModel(model_key1='base_key1')
    instance1 = model1.instantiate()
    got1 = instance1.predict(LAYERS_DATASET)
    assert got1 == Dataset(
        model_key1='base_value1'
    )


def test_layers_one_model_two_instances() -> None:
    model2 = ConnectorModel(model_key1='base_key1', model_key2='base_key2')
    instance2 = model2.instantiate()
    got2 = instance2.predict(LAYERS_DATASET)
    assert got2 == Dataset(
        model_key1='base_value1',
        model_key2='base_value2'
    )

    instance2a = model2.instantiate(model_key3='base_key3')
    got2a = instance2a.predict(LAYERS_DATASET)
    assert got2a == Dataset(
        model_key1='base_value1',
        model_key2='base_value2',
        model_key3='base_value3'
    )


def test_deep_connect_sunny_day() -> None:
    model = ConnectorModel()
    instance = model.instantiate(b=['a', 'aa'], c='d')

    dataset = Dataset(
        a=Dataset(
            aa=[1, 2, 3]
        ),
        d='something else'
    )

    got = instance.predict(dataset)
    want = Dataset(
        b=[1, 2, 3],
        c='something else'
    )

    assert got == want


def test_deep_dereference_fail() -> None:
    model = ConnectorModel()
    instance = model.instantiate(b=['bug', 'mismatch'], c='d')

    dataset = Dataset(
        bug=Dataset(
            mismatchedkey=[1, 2, 3]
        ),
        d='something else'
    )

    with pytest.raises(InputKeyError, match='bug.*mismatch'):
        instance.predict(dataset)


def test_deep_deep_dereference() -> None:
    model = ConnectorModel(
        foo=['timeseries', 'foo', 'bar'],
        static=['static', 'static']
    )
    instance = model.instantiate()

    dataset = Dataset(
        timeseries=Dataset(
            foo=Dataset(
                bar={'a': [1, 2, 3, 4]}
            )
        ),
        static=Dataset(
            static={'b': [5, 6, 7, 8]}
        )
    )
    got = instance.predict(dataset)

    want = Dataset(
        foo={'a': [1, 2, 3, 4]},
        static={'b': [5, 6, 7, 8]},
    )

    assert got == want
