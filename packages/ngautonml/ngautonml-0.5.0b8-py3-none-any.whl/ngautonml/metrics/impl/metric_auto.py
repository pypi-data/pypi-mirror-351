'''Autoloader for the metric catalog.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path
from typing import Optional

from ...catalog.plugin_catalog import PluginCatalog
from .metric import Metric
from .metric_catalog import MetricCatalog


class MetricCatalogAuto(PluginCatalog[Metric], MetricCatalog):
    '''Metric catalog that loads from $HOME and from the installation directory.'''
    def __init__(self, default_root: Optional[Path] = None, **kwargs):
        if default_root is None:
            default_root = Path(__file__).parents[2]
        super().__init__(catalog_name='metrics', default_root=default_root, **kwargs)
