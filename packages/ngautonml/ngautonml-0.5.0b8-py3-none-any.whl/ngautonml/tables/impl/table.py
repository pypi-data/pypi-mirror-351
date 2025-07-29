'''A table of data, supporting multiple formats.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.
import abc
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, Union
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)


class Error(BaseException):
    '''Base class for all table-related errors.'''
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        comma_newline = ',\n'
        return f'{self.__class__.__name__}({comma_newline.join(self.args)})'


class CanNotInstantiate(Error):
    '''The implementaiton does not understand how to use the type of value.'''


class TableValueError(Error, ValueError):
    '''Raised when a table has the correct keys but invalid values.'''


class TableWarehouse():
    '''A place to store raw materials for building Table objects.
    '''
    _exporters: Dict[type, Dict[type, Callable[['Table'], Any]]] = defaultdict(dict)
    _constructors: Dict[type, Callable[[Any], 'Table']] = {}
    # Ordered by issubclass() order, most general to most specific.
    _ordered_types: List[type] = []

    def __init__(self):
        raise NotImplementedError('TableWarehouse is a static class')

    @classmethod
    def construct(cls, value: Any) -> 'Table':
        '''Return the constructor for the given type.'''
        my_type = type(value)
        if my_type in cls._constructors:
            return cls._constructors[my_type](value)
        for my_type in cls._ordered_types:
            if isinstance(value, my_type):
                return cls._constructors[my_type](value)
        for my_type in cls._ordered_types:
            if issubclass(my_type, value.__class__):
                return cls._constructors[my_type](value)
        raise CanNotInstantiate(
            f'Can not instantiate a Table from this {type(value)} value: {str(value)[:255]}')

    @classmethod
    def export(cls, from_type: type, to_type: type) -> Callable[['Table'], Any]:
        '''Return the exporter for the given types.'''
        try:
            return cls._exporters[from_type][to_type]
        except KeyError:
            raise TableValueError(f'Can not export {from_type} table to a {to_type}')  # pylint: disable=line-too-long,raise-missing-from

    @classmethod
    def register_constructor(
            cls, my_type: type, constructor: Callable[[Any], 'Table']) -> None:
        '''Register a new table type.

        Enables tables to be created with syntax like (e.g. using ``pd.DataFrame``
        and ``DataFrameTable``):

        .. code-block:: python

            my_df = pd.DataFrame()
            foo = TableFactory(my_df)

        And the type of ``foo`` will be ``DataFrameTable``.

        '''
        cls._constructors[my_type] = constructor
        cls._ordered_types.append(my_type)

    @classmethod
    def register_exporter(
            cls,
            from_type: type, to_type: type,
            exporter: Callable[['Table'], Any]) -> None:
        '''Register a new exporter pair.

        Enables the as_() function:

        .. code-block: python

            foo = my_table.as_(pd.DataFrame).iloc[0, 2]

            my_np = my_table.as_(np.ndarray)
        '''
        cls._exporters[from_type][to_type] = exporter


class Table(metaclass=abc.ABCMeta):
    '''The interface for Table for one variety of Table.'''
    name: str
    tags: Dict[str, List[str]]
    my_type: Type  # This is the type of the value we are wrapping.
    _value: Any  # Has type my_type.

    # All subclasses must implement this __init__ signature.
    # When we get something from a catalog we don't otherwise know what
    # arguments it needs.
    def __init__(self, value: Any):
        if not isinstance(value, self.my_type):
            raise CanNotInstantiate()
        self._value = value

    def value(self):
        '''Get the native representation of the table.

        This is special because the return object is generally mutable.
        '''
        return self._value

    def __eq__(self, other: Any) -> bool:
        '''Test two objects for equality.'''
        if not isinstance(other, Table):
            return False
        if self.my_type != other.my_type:
            return all(self._value == other.as_(self.my_type))  # type: ignore[attr-defined]
        return self._value == other._value

    def __getitem__(self, key: Any) -> Any:
        '''Select a subitem of the table by key.'''
        return self._value[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        '''Set a subitem of the table by key.'''
        self._value[key] = value

    def __len__(self) -> int:
        '''Return the length of this table.'''
        return len(self._value)

    def __str__(self) -> str:
        '''Return a string representation of the table.'''
        return f'Table({self._value})'

    def __repr__(self) -> str:
        '''Return a source representation of the table.'''
        return f'Table({self._value!r})'

    def __add__(self, other: Any) -> 'Table':
        '''Add a table and another thing together.'''
        if not isinstance(other, Table):
            try:
                return TableFactory(self._value + other)
            except TypeError:
                other_as_self = TableFactory(other).as_(self.my_type)
        else:
            other_as_self = other.as_(self.my_type)
        return TableFactory(self._value + other_as_self)

    def as_(self, to_type: type) -> Any:
        '''Return the table as the requested type.'''
        return TableWarehouse.export(self.my_type, to_type)(self)

    def copy(self) -> 'Table':
        '''Make a copy of the table.'''
        return self.__class__(self._value.copy())

    @property
    def size(self) -> int:
        '''Return the size of the table in elements.'''
        return self._value.size

    def equals(self, other: Any) -> bool:
        '''Test two objects for equality.'''
        if not isinstance(other, Table):
            return False
        other_as_self = other.as_(self.my_type)
        value_ordered = self.sort_columns()
        return value_ordered._value.equals(other_as_self)  # pylint: disable=protected-access,line-too-long

    @property
    def shape(self) -> tuple:
        '''Get the shape of the table.'''
        return self._value.shape

    @abc.abstractmethod
    def drop(self, columns: List[Union[int, str]]) -> 'Table':
        '''Return a copy of this table with selected columns dropped.'''

    @abc.abstractmethod
    def drop_duplicates(self) -> 'Table':
        '''Drop the duplicates from the table.'''

    def compare(self, other: 'Table') -> 'Table':
        '''Compare two tables.'''
        return TableFactory(self._value.compare(other.value()))

    @property
    @abc.abstractmethod
    def columns(self) -> List[Union[int, str]]:
        '''Return the column names of the table.

        The can be passed to drop().
        '''

    @columns.setter
    @abc.abstractmethod
    def columns(self, value: List[Union[int, str]]) -> None:
        '''Set the column names of the table.'''

    @property
    @abc.abstractmethod
    def empty(self) -> bool:
        '''Return True if the table is empty.'''

    @abc.abstractmethod
    def head(self, n: int) -> 'Table':
        '''Return the first n rows of the table.'''

    @abc.abstractmethod
    def to_csv(self, *args, **kwargs) -> str:
        '''Output the table as a CSV string to a file and return its path.'''

    @abc.abstractmethod
    def as_dict(self, *args, **kwargs) -> Dict[Union[str, int], Any]:
        '''Convert table to a dictionary.'''

    def mean(self, *args, **kwargs) -> 'Table':
        '''Return a table containing the column-wise means of this table.'''
        return TableFactory(self._value.mean(*args, **kwargs))

    def sum(self, *args, **kwargs) -> 'Table':
        '''Return a table containing the column-wise sums of this table.'''
        return TableFactory(self._value.sum(*args, **kwargs))

    def std(self, *args, **kwargs) -> 'Table':
        '''Return the standard deviation of the table.'''
        return TableFactory(self._value.std(*args, **kwargs))

    def sort_columns(self) -> 'Table':
        '''Return a copy of the table with columns sorted.'''
        # By default, we assume columns are numbered and thus always sorted.
        return self.copy()


def TableFactory(value: Any) -> 'Table':  # pylint: disable=invalid-name
    '''A table of data, supporting multiple formats.

    We only convert the data when a specific format is requested.

    Usage:

    TableFactory(foo) returns a FooTable

    e.g., if foo is a pandas dataframe, TableFactory(foo) returns a DataFrameTable containing foo.
    '''
    return TableWarehouse.construct(value)
