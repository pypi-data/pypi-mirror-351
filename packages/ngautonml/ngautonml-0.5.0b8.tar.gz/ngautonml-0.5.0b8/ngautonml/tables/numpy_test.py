'''Tests for numpy.py.'''
import numpy as np
import pandas as pd

from .impl.table_auto import TableCatalogAuto
from .impl.table import TableFactory

from .numpy import NumpyTable


def test_numpy_table():
    '''Test the NumpyTable.'''
    _ = TableCatalogAuto()

    my_ndarray = np.array([[1, 2, 3, 7], [4, 5, 6, 8]])
    my_table = TableFactory(my_ndarray)  # pylint: disable=abstract-class-instantiated

    # assert isinstance(my_table, Table)
    assert isinstance(my_table, NumpyTable)

    np.testing.assert_array_equal(my_table.value(), my_ndarray)

    assert my_table[0].tolist() == [1, 2, 3, 7]
    assert my_table[1].tolist() == [4, 5, 6, 8]

    my_table[0] = my_table[0] + my_table[1]
    assert my_table[0].tolist() == [5, 7, 9, 15]

    got_ndarray = my_table.as_(np.ndarray)
    assert isinstance(got_ndarray, np.ndarray)
    assert got_ndarray[0, 2] == 9
    assert got_ndarray.shape == (2, 4)

    got_df = my_table.as_(pd.DataFrame)
    assert isinstance(got_df, pd.DataFrame)
    assert got_df.iloc[0, 2] == 9
    assert got_df.shape == (2, 4)
    assert all(got_df.columns == [0, 1, 2, 3])
