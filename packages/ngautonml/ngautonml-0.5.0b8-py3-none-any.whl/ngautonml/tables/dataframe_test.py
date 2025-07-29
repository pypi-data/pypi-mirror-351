'''Tests for dataframe.py.'''
import numpy as np
import pandas as pd

from .impl.table_auto import TableCatalogAuto
from .impl.table import TableFactory

from .dataframe import DataFrameTable


def test_dataframe_table():
    '''Test the DataFrameTable.'''
    _ = TableCatalogAuto()

    my_df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    my_table = TableFactory(my_df)  # pylint: disable=abstract-class-instantiated

    # assert isinstance(my_table, Table)
    assert isinstance(my_table, DataFrameTable)

    assert my_table['a'].tolist() == [1, 2, 3]
    assert my_table['b'].tolist() == [4, 5, 6]

    my_table['c'] = my_table['a'] + my_table['b']
    assert my_table['c'].tolist() == [5, 7, 9]

    assert my_table.as_(pd.DataFrame).iloc[0, 2] == 5

    my_ndarray = my_table.as_(np.ndarray)
    assert isinstance(my_ndarray, np.ndarray)
    assert my_ndarray.shape == (3, 3)
