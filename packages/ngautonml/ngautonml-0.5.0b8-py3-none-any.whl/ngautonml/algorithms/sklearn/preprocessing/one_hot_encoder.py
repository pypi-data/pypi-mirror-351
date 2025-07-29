'''An AutonML implementation of sklearn.preprocessing.OneHotEncoder.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional
from sklearn import preprocessing  # type: ignore[import]
import pandas as pd


from ....catalog.catalog import upcast
from ....problem_def.task import DataType
from ....wrangler.dataset import Dataset, TableFactory
from ...impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ...impl.algorithm_instance import DatasetError
from ...impl.fittable_algorithm_instance import UntrainedError
from ...impl.sklearn_like_algorithm_instance import SklearnLikeAlgorithmInstance


class OneHotModel(Algorithm):
    '''Wrapper for sklearn.preprocessing.OneHotEncoder

    ===============
    Hyperparameters
    ===============

    :categories: 'auto' or a list of array-like, default='auto'

        Categories (unique values) per feature:
            'auto':
                Determine categories automatically from the training data.
            list:
                categories\\[i\\] holds the categories expected in the ith column.
                The passed categories should not mix strings and numeric values
                within a single feature, and should be sorted in case of numeric values.

            The used categories can be found in the `categories` attribute.

    :drop: {'first', 'if_binary'} or an array-like of shape (n_features,), default=None

        Specifies a methodology to use to drop one of the categories per feature. This is
        useful in situations where perfectly collinear features cause problems, such as when
        feeding the resulting data into an unregularized linear regression model.
        However, dropping one category breaks the symmetry of the original representation and
        can therefore induce a bias in downstream models, for instance for penalized linear
        classification or regression models.

        None: retain all features (the default).
        'first': drop the first category in each feature. If only one category is present, the
        feature will be dropped entirely.
        'if_binary': drop the first category in each feature with two categories. Features with
        1 or more than 2 categories are left intact.
        array: drop[i] is the category in feature X[:, i] that should be dropped.

        When max_categories or min_frequency is configured to group infrequent categories, the
        dropping behavior is handled after the grouping.

    :dtype: number type, default=float

        Desired dtype of output.

    :handle_unknown: {'error', 'ignore', 'infrequent_if_exist'}, default='error'

        Specifies the way unknown categories are handled during transform.

        'error':
            Raise an error if an unknown category is present during transform.
        'ignore':
            When an unknown category is encountered during transform, the resulting one-hot
            encoded columns for this feature will be all zeros. In the inverse transform, an unknown
            category will be denoted as None.
        'infrequent_if_exist':
            When an unknown category is encountered during transform, the
            resulting one-hot encoded columns for this feature will map to the infrequent category
            if it exists. The infrequent category will be mapped to the last position in the
            encoding.

        During inverse transform, an unknown category will be mapped to the category denoted
        'infrequent' if it exists. If the 'infrequent' category does not exist, then transform and
        inverse_transform will handle an unknown category as with handle_unknown='ignore'.
        Infrequent categories exist based on min_frequency and max_categories.

    :min_frequency: int or float, default=None

        Specifies the minimum frequency below which a category will be considered infrequent.
        If int, categories with a smaller cardinality will be considered infrequent.
        If float, categories with a smaller cardinality than min_frequency * n_samples will be
        considered infrequent.

    :max_categories: int, default=None

        Specifies an upper limit to the number of output features for each input feature when
        considering infrequent categories. If there are infrequent categories, max_categories
        includes the category representing the infrequent categories along with the frequent
        categories. If None, there is no limit to the number of output features.
   '''
    _name = 'sklearn.preprocessing.OneHotEncoder'
    _tags = {
        'data_type': [DataType.TABULAR.name],
        'preprocessor': ['true'],
        'source': ['sklearn']
    }
    _default_hyperparams = {
        'categories': 'auto',
        'drop': None,
        'sparse_output': False,
        'dtype': float,
        'handle_unknown': 'ignore',
        'min_frequency': None,
        'max_categories': None,
    }
    _hyperparam_lookup = {
        'dtype': {
            "<float>": float,
            "<int>": int,
        }
    }

    def instantiate(self, **hyperparams) -> 'OneHotModelInstance':
        return OneHotModelInstance(parent=self, **hyperparams)


class OneHotModelInstance(SklearnLikeAlgorithmInstance):
    '''Wrapper for sklearn.preprocessing.OneHotEncoder'''
    _impl: preprocessing.OneHotEncoder
    _constructor = preprocessing.OneHotEncoder

    def __init__(self, parent: Algorithm, **kwargs):
        super().__init__(parent=parent, **kwargs)
        assert hasattr(self, '_impl')
        self._impl.set_output(transform='pandas')

    def fit(self, dataset: Optional[Dataset]) -> None:
        if dataset is None:
            raise DatasetError('attempt to fit with no data for {self.catalog_name}')
        cov_df = dataset.dataframe_table.as_(pd.DataFrame)
        cov_cat_df = cov_df.select_dtypes(include=['bool', 'category', 'object'])
        self._impl.fit(X=cov_cat_df)
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if not self._trained:
            raise UntrainedError(f'attempt to predict before fit for {self.catalog_name}')

        if dataset is None:
            return None

        cov_df = dataset.dataframe_table.as_(pd.DataFrame)
        cov_cat_df = cov_df.select_dtypes(include=['bool', 'category', 'object'])
        cov_rest_df = cov_df.select_dtypes(exclude=['bool', 'category', 'object'])
        output_list = [cov_rest_df]
        if not cov_cat_df.empty:
            encoded_cat_df = self._impl.transform(X=cov_cat_df)
            output_list = [cov_rest_df, encoded_cat_df]
        output_df = pd.concat(output_list, axis=1)

        retval = dataset.output()
        retval.dataframe_table = TableFactory(output_df)

        return retval


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = OneHotModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
