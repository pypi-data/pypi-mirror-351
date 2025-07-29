'''wrapper of sklearn.model_selection.KFold'''
# pylint: disable=duplicate-code,too-many-locals

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pandas as pd
from sklearn.model_selection import KFold  # type: ignore[import]

from ..problem_def.cross_validation_config import CrossValidationConfig
from ..splitters.impl.splitter import Splitter, SplitterCatalog, SplitDataset, Fold
from ..wrangler.dataset import Dataset, TableFactory


class KFoldSplitter(Splitter):
    '''Splitter that splits dataset into k folds'''

    _name = 'sklearn.model_selection.KFold'
    _hyperparams = {
        'n_splits': None,
    }
    _tags = {
        'default': ['true']
    }

    def split(self, dataset: Dataset, **overrides) -> SplitDataset:
        hyperparams = self.hyperparams(**overrides)
        n_splits = hyperparams['n_splits'] or get_num_splits(dataset.dataframe_table.shape[0])

        data_df = dataset.dataframe_table.as_(pd.DataFrame)
        kfcv = KFold(
            n_splits=n_splits,
            shuffle=True,
            random_state=self._cv_config.seed)

        folds = []
        for train_index, test_index in kfcv.split(data_df):
            validate = dataset.output()
            train = dataset.output()
            ground_truth = dataset.output()

            train_df = data_df.iloc[train_index]
            validate_df = data_df.iloc[test_index]

            if dataset.metadata.target is not None:
                validate_df_target = validate_df[[dataset.metadata.target.name]]
                validate_df_no_target = validate_df.drop(dataset.metadata.target.name, axis=1)
            else:
                validate_df_target = None
                validate_df_no_target = validate_df

            train_df.reset_index(inplace=True, drop=True)
            validate_df_no_target.reset_index(inplace=True, drop=True)
            validate_df_target.reset_index(inplace=True, drop=True)

            train.dataframe_table = TableFactory(train_df)
            validate.dataframe_table = TableFactory(validate_df_no_target)
            ground_truth.ground_truth_table = TableFactory(validate_df_target)

            folds.append(Fold(train=train, validate=validate, ground_truth=ground_truth))

        return SplitDataset(folds)


def register(catalog: SplitterCatalog, *args, cv_config: CrossValidationConfig, **kwargs):
    '''Register all the objects in this file.'''
    catalog.register(KFoldSplitter(*args, cv_config=cv_config, **kwargs))


def get_num_splits(length):
    ''' Determine number of splits based on the size of the dataset. '''
    splits = 2

    if length < 10000:
        splits = 5
    elif length < 20000:
        splits = 3

    return splits
