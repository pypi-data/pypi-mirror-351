'''Configuration for the hyperparam clause.

 We use a single data structure, HyperparamConfig, for all hyperparam clauses
 instead of separate structures for each clause so that it is easier to do
 intelligent searches of hyperparameter overrides.
'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
from typing import Dict, Any, List, Union

from ..config_components.impl.config_component import ConfigComponent, ConfigError
from ..searcher.params import Overrides, Override, Selector, ParamRanges, ParamRange
from ..wrangler.constants import (ProblemDefControl,
                                  RangeMethod, Matcher, MATCHERS_TO_LOWERCASE)


class HyperparamError(ConfigError):
    '''Accummulating error for hyperparam parsing.'''

    errors: List[ConfigError]

    def __init__(self, errors: List[ConfigError]):
        super().__init__(f'At least one validation error occured: {errors!r}')
        self.errors = errors


class HyperparamTooManyClauses(ConfigError):
    '''A subclause had unexpected keys.'''


class ControlError(ConfigError):
    '''The control strings for hyperparam config are incorrect.'''


class HyperparamConfig(ConfigComponent):
    '''Configuration for the hyperparam clause.

    We use a single data structure, HyperparamConfig, for all hyperparam clauses
    instead of separate structures for each clause so that it is easier to do
    intelligent searches of hyperparameter overrides.
    '''
    _control: List[str]
    _disable_grid_search = False

    class Constants(Enum):
        '''Keys below the top level.'''
        HYPERPARAMS = 'hyperparams'
        SELECT = 'select'
        PARAMS = 'params'
        DEFAULT = 'default'

    def __init__(self, clause: Dict[str, Any]):
        super().__init__(clause=clause)
        self._overrides = Overrides()

        (overrides, control) = self._split_overrides_control(
            self._get(self.Constants.HYPERPARAMS))
        for override_clause in overrides:
            self._overrides.append(self._parse_override(override_clause))
        self._control = control
        self._parse_control()

        self.validate()

    def _parse_control(self):
        for s in self._control:
            if s == ProblemDefControl.DISABLE_GRID_SEARCH.value:
                self._disable_grid_search = True
            else:
                raise ControlError(f'Invalid control {s}')

    def _split_overrides_control(self, clauses: List[Union[str, Dict[str, Any]]]):
        retval_str = []
        retval_overrides = []
        for val in clauses:
            if isinstance(val, str):
                retval_str.append(val)
            elif isinstance(val, dict):
                retval_overrides.append(val)
            else:
                raise ControlError(f'Unexpected hyperparam type, {val}:{type(val)}')
        return (retval_overrides, retval_str)

    def _parse_override(self, subclause: Dict[str, Dict[str, Any]]) -> Override:
        select_clause = subclause.pop(self.Constants.SELECT.value)
        params_clause = subclause.pop(self.Constants.PARAMS.value)
        if subclause:
            raise HyperparamTooManyClauses(f'Unexpected extra clauses: {subclause!r}')
        select = Selector()
        for matcher, arg in select_clause.items():
            matcher_enum = Matcher[matcher.upper()]
            if matcher_enum in MATCHERS_TO_LOWERCASE:
                arg = arg.lower()
            select[matcher_enum] = arg
        params = ParamRanges()
        for name, hyperparam_param in params_clause.items():
            params[name] = self._parse_param(hyperparam_param)

        return Override(selector=select, params=params)

    def _parse_param(self, param: Dict[str, Any]) -> ParamRange:
        default = param.pop(self.Constants.DEFAULT.value, None)
        if len(param) != 1:
            raise HyperparamTooManyClauses(f'expecting 1 key, got {param!r}')

        for method, range_value in param.items():
            return ParamRange(method=RangeMethod[method.upper()],
                              prange=range_value,
                              default=default)
        assert False, 'BUG: Unreachable code'

    @property
    def disable_grid_search(self) -> bool:
        """Should we disable grid search?

        If true, we skip the Searcher.
        """
        return self._disable_grid_search

    @property
    def overrides(self) -> Overrides:
        '''Return the hyperparam overrides described by the config.'''
        return self._overrides

    def validate(self, **kwargs) -> None:
        '''Make sure the hyperparam object makes sense.'''
        allowed = {x.value for x in ProblemDefControl}
        if not set(self._control).issubset(allowed):
            not_recognized = set(self._control) - allowed
            raise ControlError(
                f'Unrecognized control options: {not_recognized}'
                f'Must be among {allowed}'
            )
