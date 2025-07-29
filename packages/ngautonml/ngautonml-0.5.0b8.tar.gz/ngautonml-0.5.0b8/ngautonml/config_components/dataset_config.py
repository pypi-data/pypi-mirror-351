'''Specified dataset handling'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring

from typing import Any, Dict, List, Optional

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..problem_def.problem_def_interface import ProblemDefInterface
from ..wrangler.constants import ProblemDefKeys, ProblemDefKeySet, Defaults
from ..wrangler.dataset import Column, Metadata, RoleName
from .impl.config_component import (
    ConfigComponent, ConfigError, InvalidKeyError, InvalidValueError,
    MissingKeyError, ValidationErrors)
from .impl.config_component_catalog import ConfigComponentCatalog


class Error(ConfigError):
    '''Base class for errors in this file.'''


class UnknownConfigClassError(Error):
    '''Problem definition specified a dataset config that is not recognized.'''


class DatasetFileError(Error):
    '''The dataset file does not match information given in the problem definition.'''


class DatasetConfigTypeError(Error, TypeError):
    '''An object in the dataset config was not the right type.'''


DEFAULT_LOADED_FORMATS = {
    'tabular_file': 'pandas_dataframe',
    'pandas_dataframe': 'pandas_dataframe',
    'image_dir': 'tensorflow'
}


class DatasetConfig(ConfigComponent):
    '''Specifies dataset handling.'''
    name = 'dataset'
    tags: Dict[str, Any] = {}

    class Keys(AEnum):
        '''Standard strings used for keys of this clause'''
        CONFIG = 'config'
        COL_ROLES = 'column_roles'
        TRAIN_PATH = 'train_path'
        TEST_PATH = 'test_path'
        TRAIN_DIR = 'train_dir'  # used for ImageDirDataLoader
        TEST_DIR = 'test_dir'  # used for ImageDirDataLoader
        TRAIN_DATA = 'train_data'  # Will eventually be all-purpose (obj, csv, dir, url)
        TEST_DATA = 'test_data'  # Will eventually be all-purpose (obj, csv, dir, url)
        STATIC_EXOGENOUS_PATH = 'static_exogenous_path'  # For forecasting problems only
        INPUT_FORMAT = 'input_format'
        LOADED_FORMAT = 'loaded_format'
        PARAMS = 'params'

    def __init__(self,
                 clause: Dict[str, Any],
                 problem_def: Optional[ProblemDefInterface] = None,
                 **unused_kwargs):
        parents = self._add_parent([], ProblemDefKeys.DATASET.value)
        super().__init__(clause=clause, parents=parents)
        self._roles = self._build_roles()
        self._pos_labels = self._build_pos_labels()
        self._problem_def = problem_def

    def _build_roles(self) -> Dict[RoleName, List[Column]]:
        '''Build dict of column roles'''
        retval: Dict[RoleName, List[Column]] = {}
        for role in self._get_with_default(self.Keys.COL_ROLES, dflt={}):
            # this will throw a parsing error if the key does not match any known role name
            rolename = RoleName[role.upper()]

            col_names = self._get_with_default(self.Keys.COL_ROLES,
                                               role,
                                               ProblemDefKeys.COL_NAME,
                                               dflt=None)
            # TODO(Merritt): don't use ProblemDefKeys here
            if col_names is not None:
                retval[rolename] = [Column(name=col_names)]
            # TODO(Merritt): this assumes one col per role, modify it

        return retval

    def _build_pos_labels(self) -> Dict[RoleName, Any]:
        '''Build dict of pos labels for binary classification.

        In the vast majority of cases, the only key will be RoleName.TARGET'''
        retval: Dict[RoleName, Any] = {}
        for role in self._get_with_default(self.Keys.COL_ROLES, dflt={}):
            rolename = RoleName[role.upper()]
            retval[rolename] = self._get_with_default(
                self.Keys.COL_ROLES, role, ProblemDefKeys.POS_LABEL, dflt=None)
            # TODO(Merritt): don't use ProblemDefKeys here
        return retval

    def validate(self, **kwargs) -> None:
        '''Check the problem definition dataset clause for errors.'''

        # fatal errors

        dataset_keys = set(self._clause.keys())
        if not self.required_keys().issubset(dataset_keys):
            raise ValidationErrors(errors=[MissingKeyError(
                'Required keys missing in dataset clause: '
                f'{self.required_keys().difference(dataset_keys)}')])

        # non-fatal errors

        errors: List[ConfigError] = []

        if not dataset_keys.issubset(self.allowed_keys()):
            errors.append(InvalidKeyError(
                'Invalid key(s) in new dataset clause: '
                f'{dataset_keys.difference(self.allowed_keys())} '
                f'Valid keys are {self.allowed_keys()}'))

        # TODO(piggy/Merritt) Move this to the data loader(s) that require
        # column roles.
        # If no col_roles clause exists, skip this validation.
        for role_name in self._get_with_default(self.Keys.COL_ROLES, dflt=[]):
            role_keys = set(self._get(self.Keys.COL_ROLES, role_name).keys())
            if not ProblemDefKeySet.DATASET.ROLES.REQUIRED.issubset(role_keys):
                errors.append(MissingKeyError(
                    f'Required key(s) missing in role clause for role {role_name}: '
                    f'{ProblemDefKeySet.DATASET.ROLES.REQUIRED.difference(role_keys)}'))

            if not role_keys.issubset(ProblemDefKeySet.DATASET.ROLES.ALLOWED):
                errors.append(InvalidKeyError(
                    f'Invalid key(s) in role clause for role {role_name}: '
                    f'{role_keys.difference(ProblemDefKeySet.DATASET.ROLES.ALLOWED)}'
                ))

        # 'params' subclause must be a dict
        if self._exists(self.Keys.PARAMS):
            params_clause = self._get(self.Keys.PARAMS)
            if not isinstance(params_clause, Dict):
                errors.append(InvalidValueError(
                    f'Expected dict at {ProblemDefKeys.DATASET.value}'  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
                    f'.{self.Keys.PARAMS.value}, instead found '
                    f'{type(params_clause)}.'
                ))

        if len(errors) > 0:
            raise ValidationErrors(errors=errors)

    @property
    def dataloader_tags(self) -> Dict[str, str]:
        '''These tags select the data loader.

        input_format is the format being loaded:
            tabular_file, pandas_dataframe, image directory.

        loaded_format is the format passed to subsequent stages:
            pandas_dataframe or tensorflow tensor
        '''
        input_format = self._get(self.Keys.INPUT_FORMAT)
        if self._exists(self.Keys.LOADED_FORMAT):
            loaded_format = self._get(self.Keys.LOADED_FORMAT)
        else:
            # We deliberately avoid _get_with_default so that we
            # only do this lookup if loaded_format is not specified.
            loaded_format = DEFAULT_LOADED_FORMATS.get(
                input_format, Defaults.LOADED_FORMAT)

        return {
            self.Keys.INPUT_FORMAT.value: input_format,  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
            self.Keys.LOADED_FORMAT.value: loaded_format,  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        }

    @property
    def config(self) -> Optional[str]:
        '''The name of the data loader for this dataset.'''
        return self._get_with_default(self.Keys.CONFIG, dflt=None)

    @property
    def params(self) -> Dict[str, Any]:
        default_params = {}
        # Implement backwards compatability for sytax with params clause.
        if self._exists(self.Keys.TRAIN_PATH):
            default_params[self.Keys.TRAIN_PATH.value] = self._get(self.Keys.TRAIN_PATH)  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        if self._exists(self.Keys.TEST_PATH):
            default_params[self.Keys.TEST_PATH.value] = self._get(self.Keys.TEST_PATH)  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        if self._exists(self.Keys.STATIC_EXOGENOUS_PATH):
            default_params[self.Keys.STATIC_EXOGENOUS_PATH.value] = (  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
                self._get(self.Keys.STATIC_EXOGENOUS_PATH))
        if self._exists(self.Keys.TRAIN_DIR):
            default_params[self.Keys.TRAIN_DIR.value] = self._get(self.Keys.TRAIN_DIR)  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        if self._exists(self.Keys.TEST_DIR):
            default_params[self.Keys.TEST_DIR.value] = self._get(self.Keys.TEST_DIR)  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long

        retval = self._get_with_default(
            self.Keys.PARAMS, dflt=default_params)

        assert isinstance(retval, Dict)
        return retval

    @property
    def metadata(self) -> Metadata:
        '''The metadata needed by models.'''

        return Metadata(problem_def=self._problem_def,
                        roles=self._roles,
                        pos_labels=self._pos_labels)


def register(catalog: ConfigComponentCatalog) -> None:
    '''Register all the objects in this file.'''
    catalog.register(DatasetConfig)
