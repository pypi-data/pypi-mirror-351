'''Makes constructors for DataframeLoaders that wrap sklearn loaders'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List

from ..impl.data_loader_catalog import DataLoaderCatalog
from .sklearn_loader_generator import SklearnLoaderGenerator


LOADERS: List[Dict[str, Any]] = [
    {
        'name': 'sklearn.datasets.make_moons',
        'tags': {
            'input_format': ['sklearn.datasets.make_moons'],
            'loaded_format': ['pandas_dataframe'],
            'source': ['sklearn'],
            'supports_random_seed': ['true'],
            'synthetic': ['true']
        }
    },
    {
        'name': 'sklearn.datasets.load_diabetes',
        'tags': {
            'input_format': ['sklearn.datasets.load_diabetes'],
            'loaded_format': ['pandas_dataframe'],
            'supports_random_seed': ['false'],
            'uses_return_X_y': ['true'],
            'uses_as_frame': ['true']
        }
    },
    {
        'name': 'sklearn.datasets.load_breast_cancer',
        'tags': {
            'input_format': ['sklearn.datasets.load_breast_cancer'],
            'loaded_format': ['pandas_dataframe'],
            'supports_random_seed': ['false'],
            'uses_return_X_y': ['true'],
            'uses_as_frame': ['true']
        }
    }

]


def register(catalog: DataLoaderCatalog):
    '''Register all the algorithms in this file.'''
    for loader_spec in LOADERS:
        catalog.register(SklearnLoaderGenerator(**loader_spec).new_class())
