'''Interface class for objects that need to use a ProblemDef.*args

Without this we would get circularity.
'''
import abc
from enum import Enum
from typing import Union

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..config_components.impl.config_component import ConfigComponent
from .task import Task


class ProblemDefInterface(ConfigComponent, metaclass=abc.ABCMeta):
    '''Provide an interface for ProblemDef to break circularity.'''

    class Keys(AEnum):
        '''Child classes need to define this class with all their keys.'''
        TASK = 'problem_type'
        DATASET = 'dataset'
        METRICS = 'metrics'
        OUTPUT = 'output'
        HYPERPARAMS = 'hyperparams'
        CROSS_VALIDATION = 'cross_validation'
        AGGREGATION = 'aggregation'
        CONTROL = 'control'

    @abc.abstractmethod
    def get_conf(self, config_name: Union[str, Enum, AEnum]) -> ConfigComponent:
        '''This is needed to make mypy happy.

        Dataset has a ProblemDef that is typed as a ConfigComponent to avoid circularity.
        It needs to use the get_conf method of that ProblemDef
        but mypy complains if ConfigComponent does not have that method.
        '''

    @property
    @abc.abstractmethod
    def task(self) -> Task:
        '''Explains what kind of problem we're solving.

        This affects the selection of pipeline templates and models.
        '''
