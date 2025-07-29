'''Tests for dataframe.py.'''
import numpy as np
import tensorflow as tf

from .impl.table_auto import TableCatalogAuto
from .impl.table import TableFactory

from .tensor import TensorTable


def test_tensor_table():
    '''Test the TensorTable.'''
    _ = TableCatalogAuto()

    my_ten = tf.constant([[1, 2, 3], [4, 5, 6]])
    my_table = TableFactory(my_ten)  # pylint: disable=abstract-class-instantiated

    # assert isinstance(my_table, Table)
    assert isinstance(my_table, TensorTable)

    assert all(my_table[0] == [1, 2, 3])
    assert all(my_table[1] == [4, 5, 6])

    my_answer = my_table[0] + my_table[1]
    assert all(my_answer == [5, 7, 9])

    print("DEBUG: my_table", my_table)

    assert my_table[[0, 2]] == 3

    my_ndarray = my_table.as_(np.ndarray)
    assert isinstance(my_ndarray, np.ndarray)
    assert my_table.shape == (2, 3)
