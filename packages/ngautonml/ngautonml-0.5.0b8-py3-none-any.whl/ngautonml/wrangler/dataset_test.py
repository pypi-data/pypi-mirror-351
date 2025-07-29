'''Tests for the Dataset class'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pandas as pd
import pytest

from ..tables.impl.table import TableFactory, CanNotInstantiate
from ..tables.impl.table_auto import TableCatalogAuto

from .dataset import Dataset, Metadata, RoleName, Column, ez_dataset
from .dataset import DatasetKeys

# pylint: disable=missing-function-docstring,pointless-statement,duplicate-code

_ = TableCatalogAuto()


def test_output():
    roles = {RoleName.TIME: Column('bug')}
    dut = Dataset(metadata=Metadata(roles=roles))
    dut['some_key'] = 'some_val'
    got = dut.output().roles
    assert Column('bug') == got[RoleName.TIME]
    with pytest.raises(KeyError):
        got['some_key']


def test_output_overrides():
    roles = {RoleName.TIME: Column('bug')}
    roles2 = {RoleName.TIME: Column('bugs')}
    dut = Dataset(metadata=Metadata(roles=roles))
    dut['some_key'] = 'some_val'
    got = dut.output(override_metadata=Metadata(roles=roles2))
    assert Column('bugs') == got.roles[RoleName.TIME]
    with pytest.raises(KeyError):
        got['some_key']


def test_output_overrides_role():
    roles = {RoleName.TIME: Column('bug')}
    roles2 = {RoleName.TIME: Column('bugs')}
    dut = Dataset(metadata=Metadata(roles=roles))
    dut['some_key'] = 'some_val'
    got = dut.output(override_metadata=dut.metadata.override_roles(roles=roles2))
    assert Column('bugs') == got.roles[RoleName.TIME]


def test_get_dataframe():
    dut = Dataset()
    dataframe = pd.DataFrame({'bug': [1, 2], 'bug2': ['a', 'b']})
    dut.dataframe_table = TableFactory(dataframe)

    assert 'bug' == dut.get_dataframe().columns[0]


def test_df_setters_and_getters() -> None:
    dut = Dataset()
    df1 = pd.DataFrame({'a': [1]})
    df2 = pd.DataFrame({'b': [2]})
    df3 = pd.DataFrame({'c': [3]})
    dut.dataframe_table = TableFactory(df1)
    dut.ground_truth_table = TableFactory(df2)
    dut.predictions_table = TableFactory(df3)
    pd.testing.assert_frame_equal(df1, dut.dataframe_table.as_(pd.DataFrame))
    pd.testing.assert_frame_equal(df2, dut.ground_truth_table.as_(pd.DataFrame))
    pd.testing.assert_frame_equal(df3, dut.predictions_table.as_(pd.DataFrame))


def test_df_getters_proper_errors() -> None:
    dut = Dataset()

    with pytest.raises(KeyError):
        dut[DatasetKeys.DATAFRAME_TABLE.value]

    with pytest.raises(CanNotInstantiate, match='hamster'):
        dut[DatasetKeys.DATAFRAME_.value] = 'hamster'

    with pytest.raises(CanNotInstantiate, match='gerbil'):
        dut[DatasetKeys.GROUND_TRUTH_.value] = 'gerbil'

    with pytest.raises(CanNotInstantiate, match='skink'):
        dut[DatasetKeys.PREDICTIONS_.value] = 'skink'


def test_sorted_columns() -> None:
    '''Test _sort_columns()'''
    input_df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]})

    input_df = input_df.reindex(columns=['c', 'b', 'a'])
    want_df = input_df.reindex(columns=['a', 'b', 'c'])

    input_covariates_df = input_df[['c', 'b']]
    want_covariates_df = input_covariates_df.reindex(columns=['b', 'c'])

    # Confirm that it matters that the columns are out of order.
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(input_df, want_df)

    dut1 = Dataset(dataframe_table=TableFactory(input_df))
    dut2 = Dataset(covariates_table=TableFactory(input_covariates_df),
                   target_table=TableFactory(input_df['a']))

    got1 = dut1.sorted_columns()

    got2 = dut2.sorted_columns()

    dut3 = dut2.output()
    dut3.dataframe_table = dut2.dataframe_table
    print("DEBUG: dut3: ", dut3)
    got3 = dut3.sorted_columns()
    print("DEBUG: got3: ", got3)

    pd.testing.assert_frame_equal(got1['dataframe_table'].as_(pd.DataFrame), want_df)
    pd.testing.assert_frame_equal(got2['covariates_table'].as_(pd.DataFrame), want_covariates_df)
    pd.testing.assert_frame_equal(got3['dataframe_table'].as_(pd.DataFrame), want_df)


def test_table_trio() -> None:
    '''Test dataframe_table, covariates_table, target_table'''
    input_df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]})
    want_covariates_df = input_df[['b', 'c']]
    want_target_df = input_df['a']

    dut = Dataset(metadata=Metadata(roles={RoleName.TARGET: [Column('a')]}))
    dut.dataframe_table = TableFactory(input_df)

    pd.testing.assert_frame_equal(dut.dataframe_table.as_(pd.DataFrame), input_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    pd.testing.assert_frame_equal(dut.covariates_table.as_(pd.DataFrame), want_covariates_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    pd.testing.assert_series_equal(dut.target_table.as_(pd.Series), want_target_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long


def test_table_trio_dataframe() -> None:
    '''Test dataframe_table, covariates_table, target_table with dataframe input.'''
    input_df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]})
    want_covariates_df = input_df[['b', 'c']]
    want_target_df = input_df['a']

    dut = Dataset(metadata=Metadata(roles={RoleName.TARGET: [Column('a')]}))
    dut.dataframe_table = TableFactory(input_df)

    pd.testing.assert_frame_equal(dut.dataframe_table.as_(pd.DataFrame), input_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    pd.testing.assert_frame_equal(dut.covariates_table.as_(pd.DataFrame), want_covariates_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    pd.testing.assert_series_equal(dut.target_table.as_(pd.Series), want_target_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long


def test_table_trio_dataframe_no_target() -> None:
    '''Test dataframe_table, covariates_table, target_table with dataframe input and no target.'''
    input_df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]})
    want_covariates_df = input_df[['a', 'b', 'c']]

    dut = Dataset()
    dut.dataframe_table = TableFactory(input_df)

    pd.testing.assert_frame_equal(dut.dataframe_table.as_(pd.DataFrame), input_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    pd.testing.assert_frame_equal(dut.covariates_table.as_(pd.DataFrame), want_covariates_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    assert dut.target_table.as_(pd.Series) is None


def test_trio_dataframe_from_table() -> None:
    '''Test dataframe, covariates_table, target_table with dataframe input from dataframe_table.'''
    input_df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]})
    want_covariates_df = input_df[['b', 'c']]
    want_target_df = input_df['a']

    dut = Dataset(metadata=Metadata(roles={RoleName.TARGET: [Column('a')]}))
    dut.dataframe_table = TableFactory(input_df)

    pd.testing.assert_frame_equal(dut.dataframe_table.as_(pd.DataFrame), input_df)
    pd.testing.assert_frame_equal(dut.covariates_table.as_(pd.DataFrame), want_covariates_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    pd.testing.assert_series_equal(dut.target_table.as_(pd.Series), want_target_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long


def test_ez_dataset() -> None:
    '''Test dataframe, covariates_table, target_table with dataframe input from dataframe_table.'''
    dut = ez_dataset({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]}, target='a')

    want_covariates_df = pd.DataFrame({
        'b': [4, 5, 6],
        'c': [7, 8, 9]})
    want_target_df = pd.Series([1, 2, 3], name=None)

    pd.testing.assert_frame_equal(dut.dataframe_table.as_(pd.DataFrame), pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]}))
    pd.testing.assert_frame_equal(dut.covariates_table.as_(pd.DataFrame), want_covariates_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
    pd.testing.assert_series_equal(dut.target_table.as_(pd.Series), want_target_df)  # type: ignore[attr-defined]  # pylint: disable=line-too-long
