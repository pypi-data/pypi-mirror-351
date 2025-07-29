'''Test the binarizer model.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pandas as pd

from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Column, Dataset, Metadata, RoleName

from .binarizer import BinarizerModel
# pylint: disable=missing-function-docstring,duplicate-code
_ = TableCatalogAuto()  # noqa: F841


def test_sunny_day() -> None:
    model = BinarizerModel()

    metadata = Metadata(
        roles={RoleName.TARGET: [Column('target')]},
        pos_labels={RoleName.TARGET: 'good'})

    dataset = Dataset(
        metadata=metadata,
        dataframe=pd.DataFrame({
            'target': [b'good', b'bad', b'good'],
            'other': [b'good', b'indifferent', b'middlin'],
        })
    )

    dut = model.instantiate()
    got = dut.predict(dataset)

    want = Dataset(
        metadata=metadata,
        dataframe=pd.DataFrame({
            'target': [True, False, True],
            'other': [b'good', b'indifferent', b'middlin'],
        })
    )

    pd.testing.assert_frame_equal(got.get_dataframe(), want.get_dataframe())


def test_set_pos_from_constructor() -> None:
    model = BinarizerModel(target='good')

    metadata = Metadata(roles={RoleName.TARGET: [Column('target')]})

    dataset = Dataset(
        metadata=metadata,
        dataframe=pd.DataFrame({
            'target': [b'good', b'bad', b'good'],
            'other': [b'good', b'indifferent', b'middlin'],
        })
    )

    dut = model.instantiate()
    got = dut.predict(dataset)

    want = Dataset(
        metadata=metadata,
        dataframe=pd.DataFrame({
            'target': [True, False, True],
            'other': [b'good', b'indifferent', b'middlin'],
        })
    )

    pd.testing.assert_frame_equal(got.get_dataframe(), want.get_dataframe())
