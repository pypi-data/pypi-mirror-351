'''Tests for simple_imputer.'''
from typing import Optional
import pytest

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import numpy as np
import pandas as pd

from ....wrangler.dataset import Dataset, TableFactory

from .simple_imputer import SimpleImputerModel
# pylint: disable=missing-function-docstring, protected-access,duplicate-code


def test_sunny_day() -> None:
    instance = SimpleImputerModel().instantiate()

    # Simple example dataset from:
    # https://vitalflux.com/imputing-missing-data-sklearn-simpleimputer/#SimpleImputer_Python_Code_Example

    students = [[85, 'M', 'verygood'],
                [95.0, 'F', 'excellent'],
                [75, None, 'good'],
                [np.nan, 'M', 'average'],
                [70, 'M', 'good'],
                [np.nan, None, 'verygood'],
                [92, 'F', 'verygood'],
                [98, 'M', 'excellent']]
    students_df = pd.DataFrame(students, columns=['marks', 'gender', 'result'])

    students_dataset = Dataset()
    students_dataset.dataframe_table = TableFactory(students_df)

    result: Optional[Dataset] = instance.predict(students_dataset)
    assert result is not None
    result_df: pd.DataFrame = result.dataframe_table.as_(pd.DataFrame)

    # we want default strategy to be 'mean' for numerical values (in this case, ~85.83)
    # and 'most_frequent' for categorical values (in this case, 'M')
    assert set(result_df.columns) == set(['marks', 'gender', 'result'])
    assert pytest.approx(85.8333333, 1e-6) == result_df.iat[3, 0]
    assert 'M' == result_df.iat[2, 1]
