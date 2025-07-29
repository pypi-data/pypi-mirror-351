'''An object that glues together a sequence of catalogs.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, TypeVar, Union

from .catalog import Catalog, CatalogLookupError
from .memory_catalog import MemoryCatalog

T = TypeVar('T')


class CatalogShelf(Catalog[T]):
    '''Catalog object that holds a stack of other Catalog objects.'''
    _catalogs: List[Catalog[T]]
    _kwargs: Dict[str, Any]

    # pylint: disable=super-init-not-called
    def __init__(self, *catalogs: Catalog[T], **kwargs):
        self._catalogs = list(catalogs)
        self._kwargs = kwargs

    @property
    def tagtypes(self) -> Set[str]:
        '''Retrieve list of all tag types present in catalog'''
        retval = set()
        for catalog in self._catalogs:
            retval.update(catalog.tagtypes)
        return retval

    def all_objects(self) -> Iterable[T]:
        '''Retrieve all objects in all catalogs.

        Note that some objects may be returned which are otherwise
        masked during lookups.
        '''
        for catalog in self._catalogs:
            yield from catalog.all_objects()

    def items(self) -> Iterable[Tuple[str, T]]:
        for catalog in self._catalogs:
            for key, obj in catalog.items():
                yield (key, obj)

    def tagvals(self, tagtype: str) -> Set[str]:
        '''Retrieve all tag values present for a given tag type'''
        retval = set()
        for catalog in self._catalogs:
            retval.update(catalog.tagvals(tagtype=tagtype))
        return retval

    def lookup_by_name(self, name: str) -> Any:
        '''Find an object registered under name.

        The object comes from the first catalog with the name.
        '''
        for catalog in self._catalogs:
            try:
                return catalog.lookup_by_name(name=name)
            except CatalogLookupError:
                pass
        raise CatalogLookupError(name)

    def lookup_by_tag_and(self, **tags: Union[str, Iterable[str]]) -> Dict[str, T]:
        '''Find objects with a certain tag type and tag.'''
        result: Dict[str, T] = {}
        for catalog in reversed(self._catalogs):
            result.update(catalog.lookup_by_tag_and(**tags))
        return result

    def prepend(self, catalog: Catalog[T]) -> None:
        '''Add catalog to the front of the list of catalogs.'''
        catalogs = [catalog] + self._catalogs
        self._catalogs = catalogs

    def register(self, obj: T, name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        '''Register a new object with the first catalog.'''
        assert isinstance(self._catalogs[0], MemoryCatalog), (
            'You can not register on a shelf unless the first catalog is a MemoryCatalog.')
        first: MemoryCatalog = self._catalogs[0]
        return first.register(obj=obj, name=name, tags=tags)
