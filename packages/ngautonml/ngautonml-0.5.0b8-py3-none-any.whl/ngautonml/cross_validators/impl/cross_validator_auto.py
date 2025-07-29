'''Autoloader for the cross-validator catalog.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path

from ...catalog.plugin_catalog import PluginCatalog
from .cross_validator import CrossValidatorCatalog, CrossValidator


class CrossValidatorCatalogAuto(PluginCatalog[CrossValidator], CrossValidatorCatalog):
    '''CrossValidator catalog that automatically loads all cross-validators from a directory.

    Pipeline cross-validators are in ../cross_validators.
    '''

    def __init__(self, **kwargs):
        super().__init__(catalog_name='cross_validators',
                         default_root=Path(__file__).parents[2],
                         **kwargs)
