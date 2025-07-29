'''Autoloader for the model catalog.'''
# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path

from ...catalog.memory_catalog import MemoryCatalog
from ...catalog.plugin_catalog import PluginCatalog
from .algorithm import AlgorithmCatalog, Algorithm


class AlgorithmCatalogAuto(PluginCatalog[Algorithm], AlgorithmCatalog):
    '''Model catalog that Automatically loads all models from a directory.

    The models are in ../algorithms.
    '''

    def __init__(self, **kwargs):
        super().__init__(catalog_name='algorithms', default_root=Path(__file__).parents[2])


class FakeAlgorithmCatalogAuto(MemoryCatalog[Algorithm], AlgorithmCatalog):
    '''Algorithm catalog that loads only a subset of algorithms.

    Namely, those that have the {'for_tests': ['true']} tag.
    The goal is to streamline the tests.
    '''

    def __init__(self, **kwargs):
        super().__init__()
        catalog = AlgorithmCatalogAuto(**kwargs)
        for name, algorithm in catalog.lookup_by_tag_and(for_tests="true").items():
            self.register(algorithm, name=name)
