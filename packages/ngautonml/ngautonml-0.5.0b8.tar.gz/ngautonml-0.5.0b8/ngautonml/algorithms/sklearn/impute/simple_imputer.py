'''Wrapper for sklearn.impute.SimpleImputer'''
import pickle
from typing import Dict, Any, List, Optional

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from sklearn import impute  # type: ignore[import]
import pandas as pd
import numpy as np

from ....algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ....algorithms.impl.algorithm_instance import AlgorithmInstance, DatasetError
from ....algorithms.impl.fittable_algorithm_instance import (FittableAlgorithmInstance,
                                                             UntrainedError)
from ....catalog.catalog import upcast
from ....problem_def.task import DataType
from ....wrangler.dataset import Dataset, TableFactory
from ....wrangler.constants import ColumnType


class SimpleImputerModel(Algorithm):
    '''Wrapper for sklearn.impute.SimpleImputer

    Different imputers are used for different column types (numeric, integral, categorical).
    Each hyperparam is a dict of subhyperparams, which map 1:1 onto the sklearn imputers.

    ===========
    hyperparams
    ===========

    :numeric: Dict[str, Any]

        Hyperparams for the sklearn.impute.SimpleImputer applied to continuous or
        real-valued numeric columns.

        Default\\:

        .. code-block:: Python

            {
                'missing_values': np.nan,
                'strategy': 'mean',
                'fill_value': None,
                'copy': True,
                'add_indicator': False,
                'keep_empty_features': False
            }

    :integral: Dict[str, Any]

        Hyperparams for the sklearn.impute.SimpleImputer applied to discrete or integer columns.

        Default\\:

        .. code-block:: Python

            {
                'missing_values': np.nan,
                'strategy': 'median',
                'fill_value': None,
                'copy': True,
                'add_indicator': False,
                'keep_empty_features': False
            }

    :categorical: Dict[str, Any]

        Hyperparams for the sklearn.impute.SimpleImputer applied to categorical columns.

        Default\\:

        .. code-block:: Python

            {
                'missing_values': None,
                'strategy': 'most_frequent',
                'fill_value': None,
                'copy': True,
                'add_indicator': False,
                'keep_empty_features': False
            }

    ==============
    subhyperparams
    ==============

    :missing_values: int, float, str, np.nan, None or pandas.NA, default=np.nan

        The placeholder for the missing values.
        All occurrences of missing_values will be imputed. For pandas dataframes
        with nullable integer dtypes with missing values, missing_values can
        be set to either np.nan or pd.NA.

    :strategy: str, default='mean'

        The imputation strategy.

        If “mean”, then replace missing values using the mean along each
        column. Can only be used with numeric data.

        If “median”, then replace missing values using the median along each
        column. Can only be used with numeric data.

        If “most_frequent”, then replace missing using the most frequent
        value along each column. Can be used with strings or numeric data.
        If there is more than one such value, only the smallest is returned.

        If “constant”, then replace missing values with fill_value.
        Can be used with strings or numeric data.

    :fill_value: str or numerical value, default=None

        When strategy == “constant”, fill_value is used to replace all
        occurrences of missing_values. For string or object data types,
        fill_value must be a string. If None, fill_value will be 0 when imputing
        numerical data and “missing_value” for strings or object data types.

    :copy: bool, default=True

        If True, a copy of X will be created. If False, imputation will be
        done in-place whenever possible.

    :add_indicator: bool, default=False

        If True, a MissingIndicator transform will stack onto output of the
        imputer's transform. This allows a predictive estimator to account for
        missingness despite imputation. If a feature has no missing values at
        fit/train time, the feature won't appear on the missing indicator even
        if there are missing values at transform/test time.

    :keep_empty_features: bool, default=False

        If True, features that consist exclusively of missing values when fit is
        called are returned in results when transform is called. The imputed
        value is always 0 except when strategy="constant" in which case
        fill_value will be used instead.
    '''
    _name = 'sklearn.impute.SimpleImputer'
    _tags = {
        'source': ['sklearn'],
        'preprocessor': ['true'],
        'data_type': [DataType.TABULAR.name]
    }
    _default_hyperparams = {
        ColumnType.NUMERIC.value: {
            'missing_values': np.nan,
            'strategy': 'mean',
            'fill_value': None,
            'copy': True,
            'add_indicator': False,
            'keep_empty_features': False
        },
        ColumnType.INTEGRAL.value: {
            'missing_values': np.nan,
            'strategy': 'median',
            'fill_value': None,
            'copy': True,
            'add_indicator': False,
            'keep_empty_features': False
        },
        ColumnType.CATEGORICAL.value: {
            'missing_values': None,
            'strategy': 'most_frequent',
            'fill_value': None,
            'copy': True,
            'add_indicator': False,
            'keep_empty_features': False
        }
    }

    def instantiate(self, **hyperparams) -> AlgorithmInstance:
        return SimpleImputerModelInstance(parent=self, **hyperparams)


class SimpleImputerModelInstance(FittableAlgorithmInstance):
    '''Wrapper for sklearn.impute.SimpleImputer'''
    _imputers: Dict[ColumnType, impute.SimpleImputer]

    def __init__(self,
                 parent: SimpleImputerModel,
                 **hyperparams: Dict[str, Any]):
        super().__init__(parent=parent)
        self._imputers = self._make_imputers(**self.algorithm.hyperparams(**hyperparams))

    @classmethod
    def _make_imputers(cls, **hyperparams: Dict[str, Any]
                       ) -> Dict[ColumnType, impute.SimpleImputer]:
        retval: Dict[ColumnType, impute.SimpleImputer] = {}
        for col_type, params in hyperparams.items():
            imputer = impute.SimpleImputer(**params)
            imputer.set_output(transform='pandas')
            retval[ColumnType.from_str(col_type)] = imputer
        return retval

    @classmethod
    def _split_df_by_col_type(cls,
                              data_df: pd.DataFrame
                              ) -> Dict[ColumnType, pd.DataFrame]:
        # Sort columns by name to ensure stable order.
        cols = data_df.columns.to_list()
        data_df = data_df[sorted(cols)]

        numeric_df = data_df.select_dtypes(include=['float'])
        integral_df = data_df.select_dtypes(include=['int'])
        categorical_df = data_df.select_dtypes(include=['object', 'bool'])
        other_df = data_df.select_dtypes(exclude=['float', 'object', 'bool', 'int'])

        return {
            ColumnType.NUMERIC: numeric_df,
            ColumnType.INTEGRAL: integral_df,
            ColumnType.CATEGORICAL: categorical_df,
            ColumnType.OTHER: other_df
        }

    def _fit_imputers(self, data_split: Dict[ColumnType, pd.DataFrame]):
        # This may throw an error if re-fitting the same model on data with different column types
        for col_type in [ColumnType.NUMERIC, ColumnType.INTEGRAL, ColumnType.CATEGORICAL]:
            if not data_split[col_type].empty:
                self._imputers[col_type].fit(X=data_split[col_type])
            elif col_type in self._imputers:
                del self._imputers[col_type]

        # ignore ColumnType.OTHER
        self._trained = True

    def fit(self, dataset: Optional[Dataset]) -> None:
        '''Imputers can be fit, but they don't need to.'''
        if dataset is None:
            raise DatasetError(f'attempt to fit {self.catalog_name} with no data')
        data_df = dataset.dataframe_table.as_(pd.DataFrame)
        data_split = self._split_df_by_col_type(data_df=data_df)
        self._fit_imputers(data_split=data_split)

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None

        data_df = dataset.dataframe_table.as_(pd.DataFrame)
        data_split = self._split_df_by_col_type(data_df=data_df)

        if not self._trained:
            self._fit_imputers(data_split=data_split)

        output_list: List[pd.DataFrame] = [data_split[ColumnType.OTHER]]
        # do not transform cols with type OTHER
        for ctype, imp in self._imputers.items():
            if not data_split[ctype].empty:
                output_list.append(imp.transform(X=data_split[ctype]))

        output_df: pd.DataFrame = pd.concat(output_list, axis=1)
        retval = dataset.output()
        retval.dataframe_table = TableFactory(output_df)
        return retval

    def deserialize(self, serialized_model: bytes) -> 'SimpleImputerModelInstance':
        self._imputers = pickle.loads(serialized_model)
        self._trained = True
        return self

    def serialize(self) -> bytes:
        '''Return a serialized version of a trained model.'''
        if not self._trained:
            raise UntrainedError(
                f'attempt to serialize model before fit for {self.algorithm.name}')
        return pickle.dumps(self._imputers, pickle.HIGHEST_PROTOCOL)


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = SimpleImputerModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
