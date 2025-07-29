'''Deal with hyperparam bindings.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from numbers import Number
from typing import Any, Callable, Dict, Iterable, List, Type

from ...wrangler.constants import RangeMethod


class Error(Exception):
    '''Base class for all errors thrown by this module'''


class RangeError(Error):
    '''Binder was passed inappropriate range of values.'''


class Binder(metaclass=abc.ABCMeta):
    '''Create a dict naming all hyperparameter values for a step.

    parse_value is an algorithm-specific function that parses JSON values of a
            parameter into python values.
    '''

    _parse_value: Callable[[str, Any], Any]

    def __init__(self, parse_value: Callable[[str, Any], Any]):
        self._parse_value = parse_value

    @abc.abstractmethod
    def bind(self, hyperparam_name: str, prange: Any) -> Dict[str, Any]:
        '''Create a dict naming all hyperparameter values for a step.

        The typing of prange depends on the value of method, and the
        type T (as parsed from JSON) of the hyperparameter
        associated with this type of Binder\\:

        * FIXED: T
        * LIST: List[T]
        * LINEAR: List[T]
            * 3 elements: [start, increment, end]
            * T must be a NumberLikeObject (supports +, < operations)
            * If any of these values are complex, we will use their
              absolute values for comparison.

        Keys of retval are hyperparam values parsed to str
        Values of retval are corresponding hyperparam values parsed into python
        '''


class FixedBinder(Binder):
    '''Bind FIXED ParamRange.'''

    def bind(self, hyperparam_name: str, prange: Any) -> Dict[str, Any]:
        '''Bind FIXED ParamRange.

        prange: Any
            single json hyperparam value

        Keys of retval are hyperparam values unparsed to str.
        Values of retval are corresponding hyperparam values parsed into python.

        retval will always have 1 element in it.
        '''
        return {str(prange): self._parse_value(hyperparam_name, prange)}


class ListBinder(Binder):
    '''Bind LIST ParamRange.'''

    def bind(self, hyperparam_name: str, prange: Any) -> Dict[str, Any]:
        '''Bind LIST ParamRange.

        prange: List[Any]
            List of json hyperparam values

        Keys of retval are hyperparam values unparsed to str.
        Values of retval are corresponding hyperparam values parsed into python.

        retval will contain a number of elements equal to the length of the list in
            the problem definition.
        '''
        if not isinstance(prange, Iterable):
            raise RangeError('ListBinder requires an iterable param range, '
                             f'instead found {prange} of type {type(prange)}.')
        retval: Dict[str, Any] = {}
        value_list = [
            self._parse_value(
                hyperparam_name,
                value) for value in prange]
        value_strings = [str(p) for p in prange]
        for i, value_str in enumerate(value_strings):
            retval[value_str] = value_list[i]
        return retval


def abs_if_complex(num: Number):
    '''Take abs of complex numbers only.'''
    if isinstance(num, complex):
        return abs(num)
    return num


class LinearBinder(Binder):
    '''Bind LINEAR ParamRange.'''

    def bind(self, hyperparam_name: str, prange: Any) -> Dict[str, Any]:
        '''Bind LINEAR ParamRange.

        prange: List[Any]
            a list of 3 values, [start, increment, max],
            which are all parsable into subclasses of Number.
            If any of these values are complex, we will use their absolute values for comparison.

        Keys of retval are hyperparam values unparsed to str.
        Values of retval are corresponding hyperparam values parsed into python.
        '''
        if not isinstance(prange, Iterable):
            raise RangeError('LinearBinder requires an iterable param range, '
                             f'instead found {prange} of type {type(prange)}.')
        prange = list(prange)
        if len(prange) != 3:
            raise RangeError('LinearBinder requires a param range of length 3, '
                             f'instead found {prange} of length {len(prange)}')
        retval: Dict[str, Any] = {}

        start, increment, end = [
            self._parse_value(
                hyperparam_name, value) for value in prange]
        values: List[Number] = []
        current = start
        # We conditionally use abs() so this works for complex numbers.
        while abs_if_complex(current) <= abs_if_complex(end):
            values.append(current)
            current += increment
        for value in values:
            retval[str(value)] = value
        # These assertions must come after the basic operations so that
        # mypy does not complain about Number not supporting +.
        if not isinstance(start, Number):
            raise RangeError('LinearBinder start must parse to a Number. '
                             f'Instead found {start} of type {type(start)}')
        if not isinstance(increment, Number):
            raise RangeError('LinearBinder increment must parse to a Number. '
                             f'Instead found {increment} of type {type(increment)}')
        if not isinstance(end, Number):
            raise RangeError('LinearBinder end must parse to a Number. '
                             f'Instead found {end} of type {type(start)}')
        return retval


BIND: Dict[RangeMethod, Type[Binder]] = {
    RangeMethod.FIXED: FixedBinder,
    RangeMethod.LINEAR: LinearBinder,
    RangeMethod.LIST: ListBinder,
}


class BinderFactory():
    '''Make a Binder instance for the given method.'''

    def build(self,
              range_method: RangeMethod,
              parse_value: Callable[[str, Any], Any]
              ) -> Binder:
        '''Build a Binder object for the given range_method.

        Pass in the Algorithm-specific value parser.
        '''
        if range_method not in BIND:
            raise NotImplementedError(
                f'BUG: method {range_method} not implemented.')

        return BIND[range_method](parse_value=parse_value)
