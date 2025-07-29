'''Build a shelf of catalogs based just on paths.'''

from pathlib import Path
from typing import List, TypeVar

from .memory_catalog import MemoryCatalog
from .catalog_shelf import CatalogShelf


T = TypeVar("T")


class PathedCatalog(CatalogShelf[T]):
    '''Make a shelf of memory-based catalogs based on a path.'''

    def __init__(self, paths: List[Path], **kwargs):
        results: List[MemoryCatalog[T]] = []
        for path in paths:
            catalog = MemoryCatalog[T](**kwargs)
            catalog.load(module_directory=path)
            results.append(catalog)
        super().__init__(*results)
