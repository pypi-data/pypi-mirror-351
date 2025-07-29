'''Tests for list.py.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import List

import numpy as np
import pandas as pd

from .list import ListTable
from .impl.table_auto import TableCatalogAuto
from .impl.table import TableFactory


def test_list_table() -> None:
    '''Test the ListTable.'''
    _ = TableCatalogAuto()

    my_list = [1, 2, 3]
    my_table = TableFactory(my_list)

    assert isinstance(my_table, ListTable)

    assert my_table.value() == [1, 2, 3]
    assert my_table.as_(list) == [1, 2, 3]

    assert my_table.as_dict() == {0: {0: 1, 1: 2, 2: 3}}

    assert my_table.as_(pd.DataFrame).iloc[1].equals(pd.Series([2]))

    my_ndarray = my_table.as_(np.ndarray)
    assert isinstance(my_ndarray, np.ndarray)
    assert my_ndarray.shape == (3, 1)

    assert my_table.as_(pd.Series).equals(pd.Series([1, 2, 3]))


def test_2d_list_table() -> None:
    '''Test a 2d ListTable.'''
    _ = TableCatalogAuto()

    my_list = [[1, 2, 3], [4, 5, 6]]
    my_table = TableFactory(my_list)  # type: ignore[abstract] # pylint: disable=abstract-class-instantiated

    assert isinstance(my_table, ListTable)

    assert my_table.value() == [[1, 2, 3], [4, 5, 6]]

    assert my_table.as_(list) == [[1, 2, 3], [4, 5, 6]]

    assert my_table.as_dict() == {0: {0: 1, 1: 4}, 1: {0: 2, 1: 5}, 2: {0: 3, 1: 6}}

    assert my_table.as_(pd.DataFrame).iloc[1].equals(pd.Series([4, 5, 6]))

    my_ndarray = my_table.as_(np.ndarray)
    assert isinstance(my_ndarray, np.ndarray)
    assert my_ndarray.shape == (2, 3)
    assert my_ndarray[1, 1] == 5

    assert my_table.as_(pd.Series).equals(pd.Series([[1, 2, 3], [4, 5, 6]]))


def test_empty_list_table() -> None:
    '''Test an empty ListTable.'''
    _ = TableCatalogAuto()

    my_list: List[int] = []
    my_table = TableFactory(my_list)

    assert isinstance(my_table, ListTable)

    assert my_table.value() == []
    assert my_table.as_(list) == []

    assert my_table.as_dict() == {}

    assert my_table.as_(pd.DataFrame).empty


def test_empty_2d_list_table() -> None:
    '''Test an empty ListTable.'''
    _ = TableCatalogAuto()

    my_list: List[List[int]] = [[], [], []]
    my_table = TableFactory(my_list)

    assert isinstance(my_table, ListTable)
    assert my_table.value() == [[], [], []]
    assert my_table.as_(list) == [[], [], []]
    assert my_table.as_dict() == {}
    assert my_table.empty
