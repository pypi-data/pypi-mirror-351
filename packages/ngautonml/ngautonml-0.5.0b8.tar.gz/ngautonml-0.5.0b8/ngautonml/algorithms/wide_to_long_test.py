'''Tests for wide_to_long.py.'''
import pandas as pd

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Column, Dataset, RoleName, Metadata, TableFactory
from .wide_to_long import WideToLongModel
# pylint: disable=missing-function-docstring,duplicate-code
TableCatalogAuto()  # pylint: disable=pointless-statement


def test_wide_to_long_sunny_day() -> None:
    model = WideToLongModel()
    dut = model.instantiate()

    olddf = pd.DataFrame({
        'timestamp': [1, 2, 3, 4],
        'col_a': ['a1', 'a2', 'a3', 'a4'],
        'col_b': ['b1', 'b2', 'b3', 'b4'],
    })
    metadata = Metadata(
        roles={
            RoleName.TIME: [
                Column('timestamp')],
            RoleName.TARGET: [
                Column('col_a'),
                Column('col_b')],
        })
    old = Dataset(metadata=metadata)
    old.dataframe_table = TableFactory(olddf)

    got = dut.predict(old)
    gotdf = got.dataframe_table.as_(pd.DataFrame)
    gotdf.sort_values(by=['timestamp', 'y'])

    wantdf = pd.DataFrame({
        'timestamp': [1, 2, 3, 4, 1, 2, 3, 4],
        'unique_id': ['col_a', 'col_a', 'col_a', 'col_a',
                      'col_b', 'col_b', 'col_b', 'col_b'],
        'y': ['a1', 'a2', 'a3', 'a4',
              'b1', 'b2', 'b3', 'b4'],
    })
    wantdf.sort_values(by=['timestamp', 'y'])

    pd.testing.assert_frame_equal(gotdf, wantdf)

    got_roles = got.metadata.roles
    assert got_roles[RoleName.TIME] == [
        Column('timestamp')]
    assert got_roles[RoleName.TIMESERIES_ID] == [
        Column('unique_id')]
    assert got_roles[RoleName.TARGET] == [
        Column('y')]


def test_already_long() -> None:
    dut = WideToLongModel().instantiate()

    old_df = pd.DataFrame({
        'timestamp': [1, 2, 3, 4, 1, 2, 3, 4],
        'variable': ['col_a', 'col_a', 'col_a', 'col_a',
                     'col_b', 'col_b', 'col_b', 'col_b'],
        'value': ['a1', 'a2', 'a3', 'a4',
                  'b1', 'b2', 'b3', 'b4'],
    })

    metadata = Metadata(roles={
        RoleName.TIME: [
            Column('timestamp')],
        RoleName.TIMESERIES_ID: [
            Column('variable')],
        RoleName.TARGET: [
            Column('value')],
    })

    old_dataset = Dataset(metadata=metadata)
    old_dataset.dataframe_table = TableFactory(old_df)

    output = dut.predict(old_dataset)
    got_df = output.get_dataframe()
    pd.testing.assert_frame_equal(got_df, old_df)

    assert output.metadata == metadata
