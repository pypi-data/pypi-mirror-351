'''Data structures for hyperparameter manipulation.'''
from typing import Any, Dict, Generator, Iterable, List, NamedTuple, Optional

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..wrangler.constants import Matcher
from .matchers import MatcherFactory
from .param_range import ParamRange


class Selector(Dict[Matcher, Any]):
    '''A single selection clause.  The type of the value depends on the key.
    Matcher.DESIGNATOR: Designator
    Matcher.NAME: str
    Matcher.ALGORITHM: str
    Matcher.TAGS: Dict[str, str]
    '''

    def matches(self, step: Any, pipeline: Any) -> bool:
        '''Does this selector clause match the given step and pipeline?'''

        return all(MatcherFactory().make(matcher, args).matches(step, pipeline)
                   for matcher, args in self.items())

    def __str__(self):
        retval = []
        for matcher, val in self.items():
            retval.append(f'{matcher}={val}')
        return '\n'.join(retval)


class AlwaysSelector(Selector):
    '''This class always selects.'''
    def matches(self, step: Any, pipeline: Any) -> bool:
        return True

    def __str__(self) -> str:
        return 'AlwaysSelector'


class ParamRanges(Dict[str, ParamRange]):
    '''Hold names of hyperparams and how we should bind them.

        Key is a hyperparam name.
    '''
    def __str__(self):
        retval = []
        for name, prange in self.items():
            retval.append(f'{name}={prange}')
        return ','.join(retval)


class Override(NamedTuple):
    '''Holds a Selector and its matching Params.'''
    selector: Selector
    params: ParamRanges
    # This override should not be mentioned in designators.
    no_show: bool = False

    # TODO(Merritt): Consider a classmethod to simplify simpler
    # use cases, e.g. Override.fixed_param(selector, name, value)

    def __str__(self) -> str:
        return f'Override({self.selector}, {self.params})'


class Overrides():
    '''Holds a set of overrides.

    Grow Overrides with append or extend.
    Read Overrides by iterating over it.

    This is a single data structure so that it is easier to do more
    intelligent searches of hyperparameter overrides.
    '''
    _value: List[Override]

    def __init__(self, value: Optional[Iterable[Override]] = None):
        self._value = []
        if value is not None:
            self._value = list(value)

    def __iter__(self) -> Generator[Override, None, None]:
        yield from self._value

    def __len__(self) -> int:
        return len(self._value)

    def copy(self) -> 'Overrides':
        '''Return a shallow copy of this Overrides.'''
        return Overrides(self._value)

    def append(self, value: Override):
        '''Add one Override.'''
        self._value.append(value)

    def extend(self, values: Iterable[Override]):
        '''Add a set of Overrides.'''
        self._value.extend(values)

    def __str__(self) -> str:
        return '[' + ', '.join([str(v) for v in self._value]) + ']'
