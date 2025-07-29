'''Autoloader for the PipelineLoader catalog.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path
from typing import Optional

from ...catalog.plugin_catalog import PluginCatalog
from .pipeline_loader import PipelineLoader
from .pipeline_loader_catalog import PipelineLoaderCatalog


class PipelineLoaderCatalogAuto(PluginCatalog[PipelineLoader], PipelineLoaderCatalog):
    '''PipelineLoader catalog that loads from $HOME and from the installation directory.'''
    def __init__(self, default_root: Optional[Path] = None, **kwargs):
        if default_root is None:
            default_root = Path(__file__).parents[2]
        super().__init__(catalog_name='pipeline_loaders', default_root=default_root, **kwargs)
