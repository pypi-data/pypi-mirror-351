'''Base class for sklearn data loaders'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=duplicate-code,too-many-arguments
import abc
from typing import Any, Optional

import pandas as pd

from ..impl.data_loader_catalog import DataLoaderCatalog
from ..impl.dataframe_loader import DataframeLoader


class SklearnLoaderInterface(DataframeLoader, metaclass=abc.ABCMeta):
    '''Generates constructors for SklearnDataLoaders.'''
    _impl: Any
    _test_data: Optional[pd.DataFrame] = None


def register(catalog: DataLoaderCatalog):  # pylint: disable=unused-argument
    '''Nothing to register.

    All subclasses of SklearnAlgorithm are registered in sklearn_algorithms.py
    '''
