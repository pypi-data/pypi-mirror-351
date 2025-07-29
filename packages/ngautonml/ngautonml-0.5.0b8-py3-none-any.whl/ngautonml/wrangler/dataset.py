'''Holds a dataset.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=too-many-branches, too-many-return-statements

from enum import Enum
import copy
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from ngautonml.wrangler.constants import JSONKeys


from ..config_components.impl.config_component import ConfigComponent
from ..problem_def.task import DataType, TaskType
from ..problem_def.problem_def_interface import ProblemDefInterface
from ..tables.impl.table import Table, TableFactory


def df_to_dict_json_friendly(df: pd.DataFrame) -> Dict:
    '''Same as DataFrame.to_dict(orient='list') but converts NaN to None.'''
    return df.replace([np.nan], [None]).to_dict(orient='list')  # type: ignore[list-item]


class Error(BaseException):
    '''Base class for all model-related exceptions.'''
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return self.__class__.__name__ + '(' + ',\n'.join(self.args) + ')'


class DatasetKeyError(Error, KeyError):
    '''Raise when a fit() or predict() method is passed an input dataset
    that is missing required keys.'''


class DatasetValueError(Error, ValueError):
    '''Raise when a dataset has the correct keys but invalid value(s)'''


class MetadataError(Error):
    '''Raise when a dataset is invalid metadata.'''


class ColumnError(Error):
    '''Attempt to select columns in a dataframe that don't exist.'''


class RoleName(Enum):
    '''Possible column roles'''
    INDEX = 'index'
    TARGET = 'target'
    ATTRIBUTE = 'attribute'

    # For testing only
    TEST_ROLE = 'test_role'

    # For time series only
    TIME = 'time'
    TIMESERIES_ID = 'timeseries_id'
    PAST_EXOGENOUS = 'past_exogenous'
    FUTURE_EXOGENOUS = 'future_exogenous'


class Column():
    '''Defines a column in a dataset'''
    _name: str

    def __init__(self,
                 name: str):
        self._name = name

    @property
    def name(self) -> str:
        '''The column's name'''
        return str(self._name)

    def __eq__(self, other: Any):
        if not isinstance(other, Column):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return self._name.__hash__()

    def __str__(self) -> str:
        return f'Column({self.name})'

    def __repr__(self) -> str:
        return f'ngautonml.wrangler.dataset.Column ({self.name})'


class DatasetKeys(Enum):
    '''Standard keys used in the Dataset object passed between models'''
    # Symbols ending with "_" are deprecated and will be removed in the future.
    # They should only appear in dataset.py and dataset_test.py.
    DATAFRAME_ = 'dataframe'
    TARGET_ = 'target'
    COVARIATES_ = 'covariates'
    GROUND_TRUTH_ = 'ground_truth'
    PREDICTIONS_ = 'predictions'
    HYPERPARAMS = 'hyperparams'

    # Indicator of an error during fitting a pipeline
    ERROR = 'error'

    # Temporary keys for migrating to Tables
    DATAFRAME_TABLE = 'dataframe_table'
    TARGET_TABLE = 'target_table'
    COVARIATES_TABLE = 'covariates_table'
    GROUND_TRUTH_TABLE = 'ground_truth_table'
    PROBABILITIES = 'probabilities'
    PREDICTIONS_TABLE = 'predictions_table'

    # for time series forecasting only
    STATIC_EXOGENOUS = 'static_exogenous'

    STATIC_EXOGENOUS_TABLE = 'static_exogenous_table'

    # for keras image processing only
    KERAS_DS = 'keras_ds'
    KERAS_VALIDATE = 'keras_validate'


class Metadata():
    '''Metadata.'''
    _roles: Dict[RoleName, List[Column]]
    _pos_labels: Dict[RoleName, Any]
    _task: Optional[TaskType]
    _data_type: Optional[DataType]
    _problem_def: Optional[ProblemDefInterface]

    def __init__(self,
                 problem_def: Optional[ProblemDefInterface] = None,
                 roles: Optional[Dict[RoleName, List[Column]]] = None,
                 pos_labels: Optional[Dict[RoleName, Any]] = None,
                 task: Optional[TaskType] = None,
                 data_type: Optional[DataType] = None) -> None:
        self._problem_def = problem_def
        self._roles = roles or {}
        self._pos_labels = pos_labels or {}
        if problem_def is None:
            self._task = task
            self._data_type = data_type
        else:
            self._task = task or problem_def.task.task_type
            self._data_type = data_type or problem_def.task.data_type

    def get_conf(self, config_name: str) -> ConfigComponent:
        '''Get a plugin conf ConfigComponent'''
        assert self._problem_def is not None, 'BUG: _problem_def should be resolved in __init__().'
        return self._problem_def.get_conf(config_name=config_name)

    @property
    def roles(self) -> Dict[RoleName, List[Column]]:
        '''roles maps role names to lists of columns with that role.'''
        return self._roles.copy()

    @property
    def task(self) -> Optional[TaskType]:
        '''Data science task that is being approached with this dataset.'''
        return self._task

    @property
    def data_type(self) -> Optional[DataType]:
        '''Type of data contained in this dataset (image, tabular, etc)'''
        return self._data_type

    @property
    def target(self) -> Optional[Column]:
        '''Get name and index of target column if it exists.'''
        if RoleName.TARGET not in self._roles or len(self._roles[RoleName.TARGET]) == 0:
            return None
        assert len(self._roles[RoleName.TARGET]) <= 1, 'Must have at most 1 target column'
        return self._roles[RoleName.TARGET][0]

    @property
    def pos_labels(self) -> Dict[RoleName, Any]:
        '''maps role names to a positive value for columns with that role'''
        return self._pos_labels.copy()

    def override_roles(self, roles=Dict[RoleName, List[Column]]) -> 'Metadata':
        '''Return a copy of metadata with new roles.'''
        other = copy.deepcopy(self)
        other._roles = roles  # pylint: disable=protected-access
        return other

    @property
    def problem_def(self) -> Optional[ProblemDefInterface]:
        '''Get the problem definition object'''
        return self._problem_def


class Dataset(Dict[str, Any]):
    '''Holds a dataset.
    Allows for arbitrary keys and values as long as the keys are strings.

    Standard keys: covariates, target, dataframe
    '''
    _metadata: Metadata

    def __init__(self,
                 *args,
                 metadata: Optional[Metadata] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if metadata is None:
            metadata = Metadata(roles={}, pos_labels={})
        self._metadata = metadata

    def __str__(self) -> str:
        retval = 'Dataset({'
        for key, val in self.items():
            retval = f'{retval}\'{key}\': {self._str_value(val)}\n'
        retval = retval + '})'
        return retval

    def _str_value(self, value: Any) -> str:
        '''String representation of Dataset values.'''
        if isinstance(value, pd.DataFrame):
            return f'pandas.DataFrame(shape = {value.shape}, head = \n{value.head(5)})'
        return str(value)

    SPECIAL_KEYS = {
        DatasetKeys.DATAFRAME_.value,
        DatasetKeys.COVARIATES_.value,
        DatasetKeys.TARGET_.value,
        DatasetKeys.GROUND_TRUTH_.value,
        DatasetKeys.DATAFRAME_TABLE.value,
        DatasetKeys.COVARIATES_TABLE.value,
        DatasetKeys.TARGET_TABLE.value,
        DatasetKeys.GROUND_TRUTH_TABLE.value,
        DatasetKeys.PREDICTIONS_.value,
        DatasetKeys.PREDICTIONS_TABLE.value,
        DatasetKeys.STATIC_EXOGENOUS.value,
        DatasetKeys.STATIC_EXOGENOUS_TABLE.value,
    }

    JSON_NAME = {
        DatasetKeys.DATAFRAME_TABLE.value: JSONKeys.DATAFRAME.value,
        DatasetKeys.COVARIATES_TABLE.value: JSONKeys.COVARIATES.value,
        DatasetKeys.TARGET_TABLE.value: JSONKeys.TARGET.value,
        DatasetKeys.GROUND_TRUTH_TABLE.value: JSONKeys.GROUND_TRUTH.value,
        DatasetKeys.PREDICTIONS_TABLE.value: JSONKeys.PREDICTIONS.value,
        DatasetKeys.PROBABILITIES.value: JSONKeys.PROBABILITIES.value,
        DatasetKeys.STATIC_EXOGENOUS_TABLE.value: JSONKeys.STATIC_EXOGENOUS.value,
    }

    def __getitem__(self, key):
        '''Get a value from the dataset.'''
        if self.SPECIAL_KEYS.intersection(super().keys()):
            if key == DatasetKeys.DATAFRAME_.value:
                return self.dataframe_table.as_(pd.DataFrame)
            if key == DatasetKeys.COVARIATES_TABLE.value:
                return self.covariates_table
            if key == DatasetKeys.TARGET_TABLE.value:
                return self.target_table
            if key == DatasetKeys.COVARIATES_.value:
                return self.covariates_table.as_(pd.DataFrame)
            if key == DatasetKeys.TARGET_.value:
                return self.target_table.as_(pd.DataFrame)
            if key == DatasetKeys.GROUND_TRUTH_.value:
                return self.ground_truth_table.as_(pd.DataFrame)
            if key == DatasetKeys.GROUND_TRUTH_TABLE.value:
                return self.ground_truth_table
            if key == DatasetKeys.PREDICTIONS_.value:
                return self.predictions_table.as_(pd.DataFrame)
            if key == DatasetKeys.PREDICTIONS_TABLE.value:
                return self.predictions_table
            if key == DatasetKeys.STATIC_EXOGENOUS.value:
                return self.static_exogenous_table.as_(pd.DataFrame)
            if key == DatasetKeys.STATIC_EXOGENOUS_TABLE.value:
                return self.static_exogenous_table
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        '''Set a value in the dataset.'''
        if key == DatasetKeys.DATAFRAME_.value:
            self.dataframe_table = TableFactory(value)
        elif key == DatasetKeys.COVARIATES_TABLE.value:
            super().__setitem__(DatasetKeys.COVARIATES_TABLE.value, value)
        elif key == DatasetKeys.TARGET_TABLE.value:
            super().__setitem__(DatasetKeys.TARGET_TABLE.value, value)
        elif key == DatasetKeys.GROUND_TRUTH_.value:
            self.ground_truth_table = TableFactory(value)
        elif key == DatasetKeys.GROUND_TRUTH_TABLE.value:
            super().__setitem__(DatasetKeys.GROUND_TRUTH_TABLE.value, value)
        elif key == DatasetKeys.PREDICTIONS_.value:
            super().__setitem__(DatasetKeys.PREDICTIONS_TABLE.value, TableFactory(value))
        elif key == DatasetKeys.PREDICTIONS_TABLE.value:
            super().__setitem__(DatasetKeys.PREDICTIONS_TABLE.value, value)
        elif key == DatasetKeys.STATIC_EXOGENOUS_TABLE.value:
            super().__setitem__(DatasetKeys.STATIC_EXOGENOUS_TABLE.value, value)
        else:
            if isinstance(value, Table):
                if key == DatasetKeys.COVARIATES_.value:
                    super().__setitem__(DatasetKeys.COVARIATES_TABLE.value, value)
                    return
                if key == DatasetKeys.TARGET_.value:
                    super().__setitem__(DatasetKeys.TARGET_TABLE.value, value)
                    return

            super().__setitem__(key, value)

    def copy(self) -> 'Dataset':
        '''Return a copy of the dataset.'''
        retval = self.output()
        retval.update(self)
        return retval

    def to_prejson(self) -> Dict[str, Any]:
        '''Represent self as a dict that can be transformed to json.'''
        retval: Dict[str, Any] = {}
        for key, val in self.items():
            if key in self.JSON_NAME:
                key = self.JSON_NAME[key]
            retval[key] = self._json_value(val)
        return retval

    def _json_value(self, value: Any) -> Any:
        '''Represent a value as something that can be converted to JSON.'''
        if isinstance(value, pd.DataFrame):
            return df_to_dict_json_friendly(value)
        if isinstance(value, Table):
            return df_to_dict_json_friendly(value.as_(pd.DataFrame))
        # TODO(Merritt): raise an error?
        return value

    @property
    def roles(self) -> Dict[RoleName, List[Column]]:
        '''Information about column roles in the dataset'''
        return self._metadata.roles

    @property
    def metadata(self) -> Metadata:
        '''Config metadata for use by models'''
        return self._metadata

    @property
    def dataframe_table(self) -> Table:
        '''Return the dataframe at DatasetKeys.DATAFRAME as a Table.'''
        if not self.keys():
            return TableFactory(pd.DataFrame())
        if DatasetKeys.DATAFRAME_TABLE.value in super().keys():
            return super().__getitem__(DatasetKeys.DATAFRAME_TABLE.value)
        if DatasetKeys.DATAFRAME_.value in super().keys():
            return TableFactory(super().__getitem__(DatasetKeys.DATAFRAME_.value))
        if DatasetKeys.COVARIATES_.value in super().keys():
            if DatasetKeys.TARGET_.value in super().keys():
                return TableFactory(pd.concat([
                    super().__getitem__(DatasetKeys.COVARIATES_.value),
                    super().__getitem__(DatasetKeys.TARGET_.value)],
                    axis=1, join='inner'))
            return TableFactory(super().__getitem__(DatasetKeys.COVARIATES_.value))
        if DatasetKeys.COVARIATES_TABLE.value in super().keys():
            if DatasetKeys.TARGET_TABLE.value in super().keys():
                return TableFactory(pd.concat([
                    super().__getitem__(DatasetKeys.COVARIATES_TABLE.value).as_(pd.DataFrame),
                    super().__getitem__(DatasetKeys.TARGET_TABLE.value).as_(pd.Series)],
                    axis=1, join='inner'))
            return super().__getitem__(DatasetKeys.COVARIATES_TABLE.value)
        raise DatasetKeyError(
            f'Attempting to extract key "{DatasetKeys.DATAFRAME_TABLE.value}" '
            f'as input, instead found keys {list(self.keys())}.')
        # This method will be modified once Table migration is complete

    @dataframe_table.setter
    def dataframe_table(self, data: Table) -> None:
        '''Set the dataframe at DatasetKeys.DATAFRAME_TABLE.'''
        self[DatasetKeys.DATAFRAME_TABLE.value] = data

    @property
    def has_target(self) -> bool:
        '''Return True if the dataset has a target.'''
        return (DatasetKeys.TARGET_.value in self
                or DatasetKeys.TARGET_TABLE.value in self
                or (self.metadata.target is not None
                    and self.has_dataframe))

    @property
    def target_table(self) -> Table:
        '''Return the dataframe at DatasetKeys.TARGET as a Table.'''
        if DatasetKeys.TARGET_TABLE.value in super().keys():
            return super().__getitem__(DatasetKeys.TARGET_TABLE.value)

        # The following 2 lines will be deleted once Table migration is complete.
        if DatasetKeys.TARGET_.value in super().keys():
            return TableFactory(super().__getitem__(DatasetKeys.TARGET_.value))

        if self.metadata.target is not None:
            return TableFactory(self.dataframe_table[self.metadata.target.name])

        # This is for algorithms that do not require a target.
        return TableFactory(None)

    @target_table.setter
    def target_table(self, data: Table) -> None:
        '''Set the dataframe at DatasetKeys.TARGET_TABLE.'''
        self[DatasetKeys.TARGET_TABLE.value] = data

    @property
    def covariates_table(self) -> Table:
        '''Return the dataframe at DatasetKeys.COVARIATES as a Table.'''
        if DatasetKeys.COVARIATES_TABLE.value in super().keys():
            return super().__getitem__(DatasetKeys.COVARIATES_TABLE.value)

        # The following 2 lines will be deleted once Table migration is complete.
        if DatasetKeys.COVARIATES_.value in super().keys():
            return TableFactory(super().__getitem__(DatasetKeys.COVARIATES_.value))

        if (self.metadata.target is not None
                and self.metadata.target.name in self.dataframe_table.columns):
            return self.dataframe_table.drop(columns=[self.metadata.target.name])

        return self.dataframe_table

    @covariates_table.setter
    def covariates_table(self, data: Table) -> None:
        '''Set the dataframe at DatasetKeys.COVARIATES_TABLE.'''
        self[DatasetKeys.COVARIATES_TABLE.value] = data

    @property
    def ground_truth_table(self) -> Table:
        '''Return the dataframe at DatasetKeys.GROUND_TRUTH as a Table.'''
        if DatasetKeys.GROUND_TRUTH_TABLE.value in super().keys():
            return super().__getitem__(DatasetKeys.GROUND_TRUTH_TABLE.value)

        if DatasetKeys.GROUND_TRUTH_.value in super().keys():
            return TableFactory(super().__getitem__(DatasetKeys.GROUND_TRUTH_.value))

        if DatasetKeys.PREDICTIONS_TABLE.value in super().keys():
            return super().__getitem__(DatasetKeys.PREDICTIONS_TABLE.value)

        if DatasetKeys.PREDICTIONS_.value in super().keys():
            return TableFactory(super().__getitem__(DatasetKeys.PREDICTIONS_.value))

        if self.metadata.target is not None:
            return TableFactory(self.dataframe_table[self.metadata.target.name])

        raise DatasetKeyError(
            f'Attempting to extract key "{DatasetKeys.GROUND_TRUTH_TABLE.value}" '
            f'as input, instead found keys {list(self.keys())}.')

    @ground_truth_table.setter
    def ground_truth_table(self, data: Table) -> None:
        '''Set the dataframe at DatasetKeys.GROUND_TRUTH_TABLE.'''
        self[DatasetKeys.GROUND_TRUTH_TABLE.value] = data

    @property
    def has_ground_truth(self) -> bool:
        '''Return True if the dataset has a ground truth.'''
        return (DatasetKeys.GROUND_TRUTH_.value in self
                or DatasetKeys.GROUND_TRUTH_TABLE.value in self
                or (self.metadata.target is not None
                    and self.has_dataframe))

    @property
    def predictions_table(self) -> Table:
        '''Return the dataframe at DatasetKeys.PREDICTIONS_TABLE
        or raise an error if it doesn't exist.'''

        if DatasetKeys.PREDICTIONS_TABLE.value in super().keys():
            return super().__getitem__(DatasetKeys.PREDICTIONS_TABLE.value)
        if DatasetKeys.PREDICTIONS_.value in super().keys():
            return TableFactory(super().__getitem__(DatasetKeys.PREDICTIONS_.value))

        if DatasetKeys.ERROR.value in self:
            raise DatasetKeyError(
                f'Attempting to extract key "{DatasetKeys.PREDICTIONS_TABLE.value}" '
                f'as input, instead found keys {list(self.keys())}. '
                f'Error: {self[DatasetKeys.ERROR.value]}')
        raise DatasetKeyError(
            f'Attempting to extract key "{DatasetKeys.PREDICTIONS_TABLE.value}" '
            f'as input, instead found keys {list(self.keys())}.')

    @predictions_table.setter
    def predictions_table(self, data: Table) -> None:
        self[DatasetKeys.PREDICTIONS_TABLE.value] = data

    def has_predictions(self) -> bool:
        '''Return True if the dataset has predictions.'''
        return DatasetKeys.PREDICTIONS_.value in self or DatasetKeys.PREDICTIONS_TABLE.value in self

    @property
    def static_exogenous_table(self) -> Optional[Table]:
        '''Return the dataframe at DatasetKeys.STATIC_EXOGENOUS_TABLE
        or raise an error if it doesn't exist.'''

        if DatasetKeys.STATIC_EXOGENOUS_TABLE.value in super().keys():
            return super().__getitem__(DatasetKeys.STATIC_EXOGENOUS_TABLE.value)
        if DatasetKeys.STATIC_EXOGENOUS.value in super().keys():
            return TableFactory(super().__getitem__(DatasetKeys.STATIC_EXOGENOUS.value))

        raise DatasetKeyError(
            f'Attempting to extract key "{DatasetKeys.STATIC_EXOGENOUS_TABLE.value}" '
            f'as input, instead found keys {list(self.keys())}.')

    @static_exogenous_table.setter
    def static_exogenous_table(self, data: Optional[Table]) -> None:
        self[DatasetKeys.STATIC_EXOGENOUS_TABLE.value] = data

    def has_static_exogenous(self) -> bool:
        '''Return True if the dataset has static exogenous data.'''
        return ((DatasetKeys.STATIC_EXOGENOUS.value in self
                 or DatasetKeys.STATIC_EXOGENOUS_TABLE.value in self)
                and self.static_exogenous_table is not None)

    # TODO(Piggy): There are 20 references to this that lack the name of the target column.
    # This is arguably a bug, but it doesn't matter until we have multiple target columns.
    # The format should be something like this:
    # {
    #    'probabilities': {
    #       'target_column_name_1': [
    #           {value1: 0.6, value2: 0.4, value3: 0.0},
    #           {value1: 0.2, value2: 0.6, value3: 0.2},
    #           {value1: 0.1, value2: 0.2, value3: 0.7},
    #       },
    #       'target_column_name_2': [
    #           {4: 0.6, 5: 0.4, 6: 0.0},
    #           {4: 0.1, 5: 0.8, 6: 0.1},
    #           {4: 0.1, 5: 0.2, 6: 0.7},
    #       },
    #    },
    #    'predictions': {'target_column_name_1': [value1, value2, value3],
    #                    'target_column_name_2': [4, 5, 6]}

    def _check_for_error(self, key: DatasetKeys) -> None:
        '''Check for an error key and raise an error if it exists.'''

        if key.value not in self:
            if DatasetKeys.ERROR.value in self:
                raise DatasetKeyError(
                    f'Attempting to extract key "{key.value}" '
                    f'as input, instead found keys {list(self.keys())}. '
                    f'Error: {self[DatasetKeys.ERROR.value]}')
            raise DatasetKeyError(
                f'Attempting to extract key "{key.value}" '
                f'as input, instead found keys {list(self.keys())}.')

    @property
    def probabilities(self) -> Table:
        '''
        Return the table at `DatasetKeys.PROBABILITIES`
        or raise an error if it doesn't exist.
        '''
        self._check_for_error(DatasetKeys.PROBABILITIES)

        table = self[DatasetKeys.PROBABILITIES.value]

        if not isinstance(table, Table):
            raise DatasetValueError(
                f'Input key key {DatasetKeys.PROBABILITIES.value} must point to '
                f'a Table, instead found a {type(table)}: '
                f'{table}'
            )

        return table

    @probabilities.setter
    def probabilities(self, data: Table) -> None:
        self[DatasetKeys.PROBABILITIES.value] = data

    def output(self, override_metadata: Optional[Metadata] = None) -> 'Dataset':
        '''Return a new dataset containing same metadata and nothing else.

        Metadata can also be overriden, all preexisting metadata will be lost.
        Generally called to create a new dataset to fill with a model's output.
        '''
        return self.__class__(metadata=override_metadata or self._metadata)

    def get_dataframe(self) -> pd.DataFrame:
        '''Return the dataframe at DatasetKeys.DATAFRAME, or raise an error if it doesn't exist.'''

        return self.dataframe_table.as_(pd.DataFrame)

    @property
    def has_dataframe(self) -> bool:
        '''Return True if the dataset has a dataframe.'''
        return DatasetKeys.DATAFRAME_.value in self or DatasetKeys.DATAFRAME_TABLE.value in self

    def sorted_columns(self) -> 'Dataset':
        '''Sort columns of a dataset.

        This sorts DATAFRAME and COVARIATES by column name.

        This is needed so that the distributed algorithms operate
        on the same columns in the same order.
        '''
        # TODO(Piggy/Dan): If this becomes a performance problem
        #   we can cache the column order and only sort if the
        #   columns change.
        retval = self.output()

        for key in super().keys():
            if isinstance(super().__getitem__(key), Table):
                retval[key] = super().__getitem__(key).sort_columns()
            else:
                retval[key] = super().__getitem__(key)

        return retval


# These keys have been converted to Table.
TABLE_KEYS = {
    DatasetKeys.DATAFRAME_TABLE.value,
    DatasetKeys.PROBABILITIES.value,
    DatasetKeys.COVARIATES_TABLE.value,
    DatasetKeys.TARGET_TABLE.value,
    DatasetKeys.GROUND_TRUTH_TABLE.value,
}


def ez_dataset(data: Any,
               target: Optional[str] = None,
               metadata: Optional[Metadata] = None,
               key: Union[str, DatasetKeys] = DatasetKeys.DATAFRAME_TABLE,
               cols: Optional[List[str]] = None,
               roles: Optional[List[Union[RoleName, str]]] = None,
               ) -> Dataset:
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

    assert target is None or metadata is None, (
        'Cannot specify target and metadata'
    )
    if target is not None and metadata is None:
        metadata = Metadata(roles={RoleName.TARGET: [Column(target)]})

    retval = Dataset(metadata=metadata)

    if isinstance(data, Table):
        data_table = data
    else:
        data_table = TableFactory(data)

    # Trim to selected columns if either cols or roles is set.
    cols_to_select = set()
    if cols is not None:
        cols_to_select.update(cols)
    if roles is not None and metadata is not None:
        for role in roles:
            if isinstance(role, str):
                role = RoleName[role.upper()]
            cols_to_select.update(
                c.name for c in metadata.roles[role])
    if cols_to_select:
        if cols_to_select.issubset(data_table.columns):
            data_table = TableFactory(data_table[sorted(cols_to_select)])
        else:
            raise ColumnError(
                f'selecting columns {cols_to_select} from '
                f'dataframe with columns {data_table.columns};'
                'not all requested columns are present.'
            )

    if not isinstance(key, str):
        key = key.value

    if key in TABLE_KEYS:
        # keys thatcan currently hold Tables
        retval[key] = data_table
    else:
        retval[key] = data_table.as_(pd.DataFrame)
    return retval
