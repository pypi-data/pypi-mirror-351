'''Catalog that can be updated by plugins.'''

from typing import Callable, Optional, TypeVar
import os
from pathlib import Path
import sys

from ..wrangler.constants import PACKAGE_NAME
from .catalog import Catalog
from .catalog_shelf import CatalogShelf
from .memory_catalog import MemoryCatalog
from .pathed_catalog import PathedCatalog

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


T = TypeVar("T")


class PluginCatalog(CatalogShelf[T]):
    '''This catalog loads plugins for the given catalog_name.

    default_root is only needed for testing.

    We load the default auto catalog from ../{catalog_name},
    then prepend all the plugins,
    then prepend the home directory.
    '''
    def __init__(self, catalog_name: str, default_root: Optional[Path] = None, **kwargs):

        default_root = default_root or Path(__file__).parent
        super().__init__(PathedCatalog(paths=[default_root / catalog_name], **kwargs), **kwargs)

        group = f'{PACKAGE_NAME}.make_catalog'
        discovered_plugins = entry_points(group=group, name=catalog_name)
        for entrypoint in discovered_plugins:
            make_catalog: Callable[[], Catalog] = entrypoint.load()
            self.prepend(make_catalog(**kwargs))

        home_dir = os.getenv('HOME', '/')
        plugin_dir = Path(home_dir) / f'.{PACKAGE_NAME}' / 'plugins' / catalog_name
        self.prepend(PathedCatalog(paths=[plugin_dir], **kwargs))
        self.validate()
        # Add an empty catalog to take new registrations.
        self.prepend(MemoryCatalog(**kwargs))

    def validate(self):
        '''Apply constraints specific to the catalog type.'''
