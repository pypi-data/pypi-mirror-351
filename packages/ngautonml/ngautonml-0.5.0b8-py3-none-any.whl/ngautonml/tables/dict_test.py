'''Tests for dict.py.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import numpy as np
import pandas as pd

from .dict import DictTable
from .impl.table_auto import TableCatalogAuto
from .impl.table import TableFactory


def test_dataframe_table() -> None:
    '''Test the DataFrameTable.'''
    _ = TableCatalogAuto()

    my_dict = {'a': [1, 2, 3], 'b': [4, 5, 6]}
    my_table = TableFactory(my_dict)  # type: ignore[abstract] # pylint: disable=abstract-class-instantiated

    # assert isinstance(my_table, Table)
    assert isinstance(my_table, DictTable)

    assert list(my_table['a']) == [1, 2, 3]
    assert list(my_table['b']) == [4, 5, 6]

    # TODO(Merritt/Piggy): Make this test work. Possibly return a pd.Series instead of a list.
    # my_table['c'] = my_table['a'] + my_table['b']
    # assert list(my_table['c']) == [5, 7, 9]

    assert my_table.as_(dict) == my_dict

    assert my_table.as_(pd.DataFrame).iloc[1, 1] == 5

    my_ndarray = my_table.as_(np.ndarray)
    assert isinstance(my_ndarray, np.ndarray)
    assert my_ndarray.shape == (3, 2)
