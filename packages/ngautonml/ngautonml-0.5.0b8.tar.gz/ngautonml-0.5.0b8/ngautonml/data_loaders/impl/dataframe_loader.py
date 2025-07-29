'''Base class for loaders that create pandas dataframes.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
import queue
import time
from typing import Any, Dict, Optional, List, Union

import pandas as pd
from sklearn.model_selection import KFold  # type: ignore[import]

from ...config_components.impl.config_component import (
    ConfigError, ValidationErrors, ParsingErrors)
from ...config_components.distributed_config import DistributedConfig
from ...problem_def.task import TaskType
from ...tables.impl.table import Table
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.constants import JSONKeys
from ...wrangler.dataset import Dataset, Column, ez_dataset, RoleName, TableFactory
from ...config_components.dataset_config import DatasetFileError

from .data_loader import DataLoader
_ = TableCatalogAuto()  # pylint: disable=pointless-statement


class Error(BaseException):
    '''Base class for all errors in this file.'''


class DataframeLoader(DataLoader, metaclass=abc.ABCMeta):
    '''Base class for loaders that create pandas dataframes.'''
    _train_dataset: Dataset
    _que: queue.Queue

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._train_dataset = self._load_train()
        if self._train_dataset is not None:
            self._train_dataset.dataframe_table = self._str_column_names(
                self._train_dataset.dataframe_table)

        self._update_roles()

        self.validate(self._train_dataset, train=True)

        self._que = queue.Queue()
        self._que.put(self._train_dataset)

    def _update_roles(self) -> None:
        '''Give all unassigned columns the Attribute role.'''
        assigned_colnames: List[Union[int, str]] = []
        errors: List[ConfigError] = []

        if self._train_dataset is None:
            return

        for cols in self._metadata.roles.values():
            for col in cols:
                assigned_colnames.append(str(col.name))

        unassigned_colnames = list(
            set(self._train_dataset.dataframe_table.columns) - set(assigned_colnames))
        unassigned_cols = []
        for colname in unassigned_colnames:
            unassigned_cols.append(Column(str(colname)))

        updated_roles = self._metadata.roles
        if RoleName.ATTRIBUTE not in updated_roles:
            updated_roles[RoleName.ATTRIBUTE] = []
        updated_roles[RoleName.ATTRIBUTE].extend(unassigned_cols)

        self._metadata = self._metadata.override_roles(updated_roles)

        # Because train data is already loaded, we need to update its
        # metadata separately.
        self._train_dataset._metadata = self._metadata  # pylint: disable=protected-access

        if len(errors) != 0:
            raise ParsingErrors(errors)

    def _prune_target(self, retval: Dataset) -> Dataset:
        '''remove target col if it is in data

        called by subclasses in load_test() since test data shouldn't have target

        keep target for forecasting problems
        '''
        # TODO(Merritt/Piggy): once we have a forecasting dataloader, we can
        #   do something more elegant than checking the task type here.

        if self._metadata.task != TaskType.FORECASTING:
            target = self._metadata.target
            if target is not None and target.name in retval.dataframe_table.columns:
                retval.dataframe_table = retval.dataframe_table.drop(
                    columns=[target.name])

        return retval

    def _str_column_names(self, table: Table) -> Table:
        table.columns = [str(c) for c in table.columns]
        return table

    def _ensure_cols_present(self, data: Table, role: RoleName) -> List[ConfigError]:
        errors: List[ConfigError] = []
        if role in self._metadata.roles:
            for col in self._metadata.roles[role]:
                if col.name not in data.columns:
                    errors.append(DatasetFileError(
                        f'Column {col.name} specified under role {role}'
                        ' not found among columns in dataset. '
                        f'Found: {data.columns}'))
        return errors

    def validate(self, dataset: Optional[Dataset], train: bool = False) -> None:
        '''Raise a ValidationErrors if something about the dataset is inconsistent.'''
        if dataset is None:
            return  # A None dataset is valid.
        errors: List[ConfigError] = []

        if dataset.has_dataframe:
            errors.extend(self._ensure_cols_present(dataset.dataframe_table, RoleName.INDEX))
            if train:
                errors.extend(
                    self._ensure_cols_present(dataset.dataframe_table, RoleName.ATTRIBUTE))
                errors.extend(
                    self._ensure_cols_present(dataset.dataframe_table, RoleName.TARGET))
        elif dataset.has_ground_truth:
            errors.extend(self._ensure_cols_present(dataset.ground_truth_table, RoleName.INDEX))
            errors.extend(self._ensure_cols_present(dataset.ground_truth_table, RoleName.TARGET))
        else:
            # Raise error?
            pass

        if errors:
            raise ValidationErrors(errors)

    def load_train(self) -> Optional[Dataset]:
        retval = self._train_dataset
        self.validate(retval, train=True)
        return self._conditional_split(retval)

    @abc.abstractmethod
    def _load_train(self) -> Optional[Dataset]:
        ...

    def load_test(self) -> Optional[Dataset]:
        '''Load test data if it exists, otherwise None'''
        retval = self._load_test()
        if retval is None:
            return None

        retval.dataframe_table = self._str_column_names(retval.dataframe_table)

        retval = self._prune_target(retval)
        self.validate(retval)
        # Unlike train data, don't split the test data for a distributed setting.
        return retval

    @abc.abstractmethod
    def _load_test(self) -> Optional[Dataset]:
        ...

    def _load_ground_truth(self) -> Optional[Dataset]:
        '''If the target column exists in the test set, extract it as the ground truth.'''
        test_set = self._load_test()
        if test_set is None:
            print('test set is None')
            return None

        if self._metadata.target is None:
            print('target in metadata is None')

            return None

        target_name = self._metadata.target.name

        if target_name in test_set.dataframe_table.columns:
            retval = Dataset(metadata=self._metadata)
            retval.ground_truth_table = TableFactory(test_set.dataframe_table[[target_name]])
            return retval

        print(f'target name ({target_name}) not in cols ({test_set.dataframe_table.columns}).')
        return None

    def _dataset(self,
                 data: Any,
                 **kwargs) -> Dataset:
        '''Make a Dataset object with minimal boilerplate.

        Args:
            data:
            Object that can be turned into a Table
            target:
            the name of the target column.  A shortcut for speficying metadata
            metadata:
            the full metadata for the dataset.  Cannot be present alongside the target argument.
            key:
            The key for the data in the dataset. Defaults to "dataframe_table".
            cols:
            If set, only selects supplied column(s).
            Will take union with roles if both are specified.
            roles:
            If set, only selects columns with supplied role(s).
            Will take union with cols if both are specified.
        '''

        return ez_dataset(data=data, metadata=self._metadata, **kwargs)

    def _conditional_split(self, data: Dataset) -> Dataset:
        '''Split a dataset if we are in a distributed simulation, otherwise do nothing.

        Requires 1 <= my_id <= num_nodes.
        '''
        problem_def = self._config.metadata.problem_def
        if problem_def is None:
            return data

        distributed = problem_def.get_conf('distributed')
        assert isinstance(distributed, DistributedConfig), (
            f'BUG: Expected distributed to be a DistributedConfig, '
            f'got {type(distributed)} instead.'
        )
        distributed_split = distributed.split
        if distributed_split is None:
            return data

        # split data for a distributed simulation
        kfcv = KFold(
            n_splits=distributed_split.num_nodes,
            shuffle=True,
            random_state=distributed_split.seed  # defaults to default seed
        )

        # 1-based: 1 <= my_id <= num_nodes.
        n = distributed.my_id
        print("DEBUG: distributed.my_id", distributed.my_id)
        # Choose nth split.
        _, indices = next(
            (x for i, x in enumerate(
                kfcv.split(data.dataframe_table.as_(pd.DataFrame)),
                start=1
            ) if i == n), (None, None))
        assert indices is not None, (
            f'BUG: Could not find {n}th split of {distributed_split.num_nodes} '
            f'for node {distributed.my_id}'
        )

        split_df = data.dataframe_table.as_(pd.DataFrame).iloc[indices]
        split_df.reset_index(inplace=True, drop=True)
        retval = data.output()
        # retval.dataframe_table = TableFactory(split_df)
        retval.dataframe_table = TableFactory(split_df)
        return retval

    def poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        next_data = self._poll(timeout=timeout)
        if next_data is None:
            return None
        next_data.dataframe_table = self._str_column_names(next_data.dataframe_table)
        self.validate(next_data)

        return self._conditional_split(data=next_data)

    def _poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        '''Return the latest unsplit dataset.'''
        if timeout is not None:
            time.sleep(timeout)
        try:
            return self._que.get(block=False, timeout=timeout)
        except queue.Empty:
            return None

    def build_dataset_from_json(self, json_data: Dict) -> Dataset:
        '''Build a Dataset object from a JSON object.'''

        data = json_data[JSONKeys.DATA.value]
        if self._metadata.target is None and JSONKeys.TARGET.value in data:

            self._metadata = self._metadata.override_roles(
                {RoleName.TARGET: [Column(name)] for name in data[JSONKeys.TARGET.value].keys()}
            )

        retval = Dataset(metadata=self._metadata)
        if JSONKeys.COVARIATES.value in data:
            retval.covariates_table = TableFactory(data[JSONKeys.COVARIATES.value])
        if JSONKeys.TARGET.value in data:
            retval.target_table = TableFactory(data[JSONKeys.TARGET.value])
        if JSONKeys.DATAFRAME.value in data:
            retval.dataframe_table = TableFactory(data[JSONKeys.DATAFRAME.value])
        if JSONKeys.GROUND_TRUTH.value in data:
            retval.ground_truth_table = TableFactory(data[JSONKeys.GROUND_TRUTH.value])
        return retval
