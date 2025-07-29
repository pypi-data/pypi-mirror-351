'''Class representing problem type, which is a combination of data type and task.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..config_components.impl.config_component import (
    ConfigComponent, ConfigError, ValidationErrors,
    InvalidValueError, ProblemDefTypeError)
from ..wrangler.constants import ProblemDefKeys, Defaults


class DataType(Enum):
    '''Possible input data types'''
    TABULAR = auto()
    IMAGE = auto()
    TIMESERIES = auto()
    TEXT = auto()

    @staticmethod
    def validate(name: str) -> List[str]:
        '''Return an error message if data type is not in the list'''
        errors: List[str] = []
        names = [member.name for member in DataType]
        if name.upper() not in names:
            errors.append(f'"{name}" not among valid data types: f{names}')
        return errors


class TaskType(Enum):
    '''Possible ML tasks'''
    BINARY_CLASSIFICATION = auto()
    MULTICLASS_CLASSIFICATION = auto()
    REGRESSION = auto()
    FORECASTING = auto()
    DENSITY_ESTIMATION = auto()
    OTHER = auto()
    TEST_TASK = auto()  # Only used in testing

    @staticmethod
    def validate(name: str) -> List[str]:
        '''Return an error message if task type is not in the list'''

        # TODO(Merritt/Piggy): figure out how to deal with this without using forecasting
        errors: List[str] = []
        names = [member.name for member in TaskType]
        if name.upper() not in names:
            errors.append(f'"{name}" not among valid task types: f{names}')
        return errors


class Task(ConfigComponent):
    '''Parsed form of the problem_type.'''

    class Keys(AEnum):
        '''Top-level keys in Task component'''
        DATA_TYPE = 'data_type'
        TASK_TYPE = 'task'

    def required_keys(self) -> Set[str]:
        '''Subset of ALLOWED_KEYS that are required'''
        return {self.Keys.TASK_TYPE.value}  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long

    def __init__(self, clause: Dict[str, Any], parents: Optional[List[str]] = None):
        parents = self._add_parent(parents, ProblemDefKeys.TASK.value)
        super().__init__(clause=clause, parents=parents)

    @property
    def data_type(self) -> DataType:
        '''Data type'''
        return DataType[self._get_with_default(
            self.Keys.DATA_TYPE,
            dflt=Defaults.DATA_TYPE).upper()]

    @property
    def task_type(self) -> TaskType:
        '''ML task'''
        field = self._get(self.Keys.TASK_TYPE)
        try:
            return TaskType[field.upper()]
        except KeyError as err:
            raise InvalidValueError(
                f'task type {field} is not recognized.') from err

    def __str__(self) -> str:
        data_type_name = "None"
        if self.data_type is not None:
            data_type_name = self.data_type.name
        task_name = "None"
        if self.task_type is not None:
            task_name = self.task_type.name
        return (f'{{Data type: {data_type_name}'
                f', Task: {task_name} }}')

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Task):
            if __value.data_type == self.data_type and __value.task_type == self.task_type:
                return True
        return False

    def validate(self, **kwargs) -> None:
        # test that problem_type maps to a dictionary containing exactly data_type and task_type
        super().validate(**kwargs)
        errors: List[ConfigError] = []

        if isinstance(self._clause, dict):

            if self.Keys.DATA_TYPE.value in self._clause:  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
                errmessages = DataType.validate(self._clause[self.Keys.DATA_TYPE.value])  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
                errors = errors + [InvalidValueError(err) for err in errmessages]

            if self.Keys.TASK_TYPE.value in self._clause:  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
                errmessages = TaskType.validate(self._clause[self.Keys.TASK_TYPE.value])  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
                errors = errors + [InvalidValueError(err) for err in errmessages]
        else:
            errors.append(ProblemDefTypeError(
                f'{ProblemDefKeys.TASK.value} must be a dict, '
                f'instead found {type(self._clause)}'))

        if len(errors) > 0:
            raise ValidationErrors(errors=errors)
