'''Autoloader for the Table catalog.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path
from typing import Optional, Type

from ...catalog.plugin_catalog import PluginCatalog
from .table import Table
from .table_catalog import TableCatalog


class TableCatalogAuto(PluginCatalog[Type[Table]], TableCatalog):
    '''Table catalog that loads from $HOME and from the installation directory.'''
    def __init__(self, default_root: Optional[Path] = None, **kwargs):
        if default_root is None:
            default_root = Path(__file__).parents[2]
        super().__init__(catalog_name='tables', default_root=default_root, **kwargs)
