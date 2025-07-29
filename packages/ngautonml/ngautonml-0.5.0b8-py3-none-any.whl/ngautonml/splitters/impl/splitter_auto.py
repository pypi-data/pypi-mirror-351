'''Autoloader for the splitter catalog.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path

from ...catalog.plugin_catalog import PluginCatalog

from .splitter import SplitterCatalog, Splitter


class SplitterCatalogAuto(PluginCatalog[Splitter], SplitterCatalog):
    '''Splitter catalog that automatically loads all splitters from a directory.

    Data splitters are in ../splitters.
    '''

    def __init__(self, **kwargs):
        super().__init__(catalog_name='splitters', default_root=Path(__file__).parents[2], **kwargs)
