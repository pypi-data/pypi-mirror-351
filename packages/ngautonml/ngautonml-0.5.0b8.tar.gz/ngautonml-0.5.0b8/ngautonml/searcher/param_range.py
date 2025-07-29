'''Holds values for unbound hyperparams.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Optional

from ..wrangler.constants import RangeMethod


class ParamRange():
    '''How to pick value(s) for a hyperparam.

    :method: specifies the method for picking values (FIXED, LIST, LINEAR).
    :range: specifies value(s) for the hyperparamter.

    The typing of range depends on the value of method, and the
    type T of the hyperparameter associated with this ParamRange.

    * RangeMethod.FIXED: T
    * RangeMethod.LIST: List[T]
    * RangeMethod.LINEAR: List[T]*
        * 3 elements: [start, increment, end]
        * T must be a NumberLikeObject (supports +, < operations)
    '''
    _method: RangeMethod
    _range: Any
    _default: Any = None

    def __init__(self, method: RangeMethod, prange: Any, default: Optional[Any] = None):
        self._method = method
        self._range = prange
        self._default = default

    @property
    def method(self) -> RangeMethod:
        '''Specifies the method for picking values (FIXED, LIST, LINEAR).'''
        return self._method

    @property
    def range(self) -> Any:
        '''This is the value(s) assigned to the hyperparam.

        The typing of range depends on the value of method, and the
        type T of the hyperparameter associated with this ParamRange.

        * RangeMethod.FIXED: T
        * RangeMethod.LIST: List[T]
        * RangeMethod.LINEAR: List[T]*

            * 3 elements: [start, increment, end]
            * T must be a NumberLikeObject (supports +, < operations)
        '''
        return self._range

    @property
    def default(self) -> Any:
        '''Extract the default defaults.'''
        if self.method == RangeMethod.FIXED:
            return self._default or self.range
        return self._default

    def __str__(self) -> str:
        return f'ParamRange({self.method}: {self.range})'

    def __eq__(self, other) -> bool:
        if not isinstance(other, ParamRange):
            return False
        return (self._method == other._method
                and self._range == other._range
                and self._default == other._default)
