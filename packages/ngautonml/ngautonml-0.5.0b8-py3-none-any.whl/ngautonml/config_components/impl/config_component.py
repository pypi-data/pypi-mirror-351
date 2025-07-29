'''Base class for elements of the Problem Definition file'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
import copy
from typing import Any, Dict, List, Optional, Set, Type, Union

from aenum import Enum as AEnum, extend_enum  # type: ignore[import-untyped]


class ConfigError(BaseException):
    '''All errors thrown by problem definition modules'''


class ConfigDirectoryError(ConfigError, NotADirectoryError):
    '''A path given in the problem doc was not a directory, but should be.'''


class MissingKeyError(ConfigError, KeyError):
    '''We failed to find a given key in the problem doc.'''


class InvalidKeyError(ConfigError, KeyError):
    '''We found an invalid key in the problem doc.'''


class ProblemDefTypeError(ConfigError, TypeError):
    '''A value in the problem definition was the wrong type.'''


class InvalidValueError(ConfigError, ValueError):
    '''A value in the problem definition has the right type but is invalid.'''


class ParsingErrors(ConfigError):
    '''Error(s) thrown when problem definition JSON cannot be parsed'''

    def __init__(self, errors: List[ConfigError]):
        super().__init__(f'At least one parsing error occured: {errors!r}')
        self.errors = errors


class ValidationErrors(ConfigError):
    '''Problem definition JSON can be parsed, but is invalid in some other way.'''

    def __init__(self, errors: List[ConfigError]):
        super().__init__('At least one validation error occured:')
        self.errors = errors

    def __str__(self) -> str:
        retval_list1 = [str(arg) for arg in self.args]
        retval_list2 = [f'\t{repr(error)}' for error in self.errors]
        return '\n'.join(retval_list1 + retval_list2)


class ConfigComponent():
    '''Base class for elements of the Problem Definition file

    This provides _get, _get_with_default, and _exists for
    use by config components.
    '''
    # pylint: disable=too-few-public-methods
    # _parents is a path of ancestor clause names to reach this
    # component, for use in error messages.
    _parents: List[str]
    _clause: Dict[str, Any]
    _sub_component_types: Optional[Dict[str, Type['ConfigComponent']]] = None

    @classmethod
    def register(cls, name: str, config_type: Type['ConfigComponent']) -> None:
        '''Register a new subcomponent.'''
        # Lift the lookup table from the base class to the class receiving the registration.
        if cls._sub_component_types is None:
            cls._sub_component_types = {}
        cls._sub_component_types[name] = config_type  # pylint: disable=unsupported-assignment-operation
        if not hasattr(cls.Keys, name):
            extend_enum(cls.Keys, name, name)

    class Keys(AEnum):
        '''Child classes need to define this class with all their keys.'''

    def __init__(self,
                 clause: Dict[str, Any],
                 parents: Optional[List[str]] = None,
                 **kwargs):
        if parents is None:
            parents = []
        self._parents = parents
        self._clause = clause
        # We need to wait until instantiation time to give all the subcomponents
        # the opportunity to register.
        if self._sub_component_types is not None:
            for name, config_type in self._sub_component_types.items():
                if name in clause:
                    setattr(self,
                            name,
                            config_type(name=name, clause=clause[name], **kwargs))

    def allowed_keys(self) -> Set[str]:
        '''Set of keys that are acceptable for this clause'''
        return {key.value for key in list(self.Keys)}

    # We default to no required keys.
    def required_keys(self) -> Set[str]:
        '''Subset of ALLOWED_KEYS that are required'''
        return set()

    def _add_parent(self,
                    parents: Optional[List[str]],
                    new_parent: str) -> List[str]:
        '''Keep track of where we are in the problem def for error messages.'''
        if parents is None:
            retval = []
        else:
            retval = parents.copy()
        retval.append(new_parent)
        return retval

    def _get(self, *args: Union[int, str, Enum]):
        '''for ex: call _get('metric', 'name') to get metric name'''
        here = self._clause
        so_far = []
        for k in args:
            if isinstance(k, Enum):
                k = k.value
            so_far.append(str(k))
            if isinstance(here, list):
                if not isinstance(k, int):
                    raise ProblemDefTypeError(
                        f'found a list at {".".join(self._parents + so_far[:-1])}, '
                        f'expected an integer at {".".join(self._parents + so_far)}')
                if not -len(here) < k < len(here):
                    raise MissingKeyError(f'Could not find the {k}th element of {here}')
            elif isinstance(here, dict):
                if k not in here:
                    raise MissingKeyError('Could not find '
                                          f'{".".join(so_far)}')
                assert isinstance(k, str), (
                    f'BUG: at _get {".".join(so_far)} we have a non-string key, {k!r} for {here!r}')
            here = here[k]

        return copy.deepcopy(here)

    def _get_with_default(self, *args: Union[int, str, Enum], dflt: Any) -> Any:
        if self._exists(*args):
            return self._get(*args)
        return dflt

    def _exists(self, *args: Union[int, str, Enum]) -> bool:
        '''for ex: call _exists('metric', 'name') to see if metric.name exists'''
        here = self._clause
        so_far = []
        for k in args:
            if isinstance(k, Enum):
                k = k.value
            so_far.append(str(k))
            if isinstance(here, list):
                if not isinstance(k, int):
                    raise ProblemDefTypeError(
                        f'found a list at {".".join(self._parents + so_far[:-1])}, '
                        f'expected an integer at {".".join(self._parents + so_far)}')
                if not -len(here) < k < len(here):
                    raise MissingKeyError(f'Could not find the {k}th element of {here}')
            elif isinstance(here, dict):
                if k not in here:
                    return False
                assert isinstance(k, str), (
                    f'BUG: at _exists {".".join(so_far)} we have a '
                    f'non-string key, {k!r} for {here!r}')
            here = here[k]
        return True

    def validate(self, **kwargs) -> None:
        '''Raise a ConfigError if something about the clause is invalid.

        The base class validate() checks only fotr required and allowed keys.

        For ConfigComponents created by plugins, implementations must not raise an
        error if the clause is an empty dict.
        '''
        _ = kwargs
        errors: List[ConfigError] = []
        if isinstance(self._clause, dict):
            keys = set(self._clause.keys())
            if not self.required_keys().issubset(keys):
                errors.append(MissingKeyError(
                    f'Required keys missing in {".".join(self._parents)} clause: '
                    f'{self.required_keys().difference(keys)}'))

            if not keys.issubset(self.allowed_keys()):
                errors.append(InvalidKeyError(
                    f'Invalid key(s) in {".".join(self._parents)} clause: '
                    f'{keys.difference(self.allowed_keys())}. '
                    f'Valid keys are {self.allowed_keys()}'))

        if len(errors) > 0:
            raise ValidationErrors(errors=errors)


class ConfigComponentStub(ConfigComponent):
    '''Config component for cases where we need a stub.'''
    name = 'stub_config_component'

    def validate(self, **kwargs) -> None:
        pass
