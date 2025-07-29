'''Generates a constructor for an SklearnLoader.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=duplicate-code,too-many-arguments
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Type
import importlib
import random

from numpy.random import RandomState  # pylint: disable=no-name-in-module  # This just isn't true.
import pandas as pd

from ...config_components.impl.config_component import InvalidValueError
from ...wrangler.constants import Defaults
from ...wrangler.dataset import Dataset
from ..impl.data_loader_catalog import DataLoaderCatalog
from ..impl.dataframe_loader import DataframeLoader
from .sklearn_loader_interface import SklearnLoaderInterface


def _load_train_impl(self: SklearnLoaderInterface) -> Dataset:
    '''Implementation for _load_train() in the SklearnLoader we generate'''
    # pylint: disable=protected-access
    params = deepcopy(self._config.params)
    if self.tags.get('supports_random_seed', ['false'])[0] == 'true':
        if 'random_seed' in params:
            params['random_state'] = RandomState(params.pop('random_seed'))
        elif params.get('random_state', None) is None:
            params['random_state'] = RandomState(Defaults.SEED)

    if self.tags.get('uses_return_X_y', ['false'])[0] == 'true':
        params['return_X_y'] = True

    if self.tags.get('uses_as_frame', ['false'])[0] == 'true':
        params['as_frame'] = True

    restrict_to_n_features = -1
    if 'restrict_features' in params:
        restrict_to_n_features = params.pop('restrict_features')

    test_size = -1
    if 'test_size' in params:
        test_size = params.pop('test_size')

    (x, y) = self._impl._loader(**params)
    x = pd.DataFrame(x)
    # Make sure all column names are strings
    #   (casting to Index to make mypy happy)
    x.columns = pd.core.indexes.base.Index([str(n) for n in x.columns])

    if restrict_to_n_features >= 0:
        restrict_to_n_features = min(restrict_to_n_features, x.shape[1])
        x = x.iloc[:, :restrict_to_n_features]

    if test_size > x.shape[0]:
        raise InvalidValueError(
            f'test_size is set to {test_size}, but dataset {self.name} '
            f'only has {x.shape[0]} observations.'
        )

    target = self._config.metadata.target
    target_name = target.name if target is not None else 'y'

    if test_size > 0:
        x_test = x.iloc[-test_size:, :]
        y_test = y[-test_size:]
        test_data = x_test
        test_data[target_name] = y_test
        self._test_data = test_data

        x = x.iloc[:-test_size, :]
        y = y[:-test_size]

    train_df = x
    train_df[target_name] = y

    retval = self._dataset(data=train_df)
    return retval


def _load_test_impl(self: SklearnLoaderInterface) -> Optional[Dataset]:
    '''Implementation for _load_test() in the SklearnLoader we generate'''
    # pylint: disable=protected-access
    if self._test_data is not None:
        return self._dataset(data=self._test_data)
    return None


class SklearnLoaderGenerator():
    '''Generates a constructor for an SklearnLoader.'''
    _loader: Callable[..., Any]

    def __init__(self,
                 name: str,
                 loader: Optional[type] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 **hyperparams: Any):
        self.name = name
        if loader is None:
            loader = self._load_module(name)
        self._loader = loader
        if tags is not None:
            self.tags = tags.copy()
        else:
            self.tags = {}
        super().__init__(**hyperparams)

    def _random_name(self) -> str:
        # We don't actually care about collisions as we never look
        # these constructors up by name.
        return f'GeneratedSklearnLoader{random.randint(0, 999999999)}'

    def _load_module(self, name: str):
        # Split name into module part (e.g. sklearn.linear_model)
        # and constructor part (e.g. LinearRegression)
        parts = name.split('.')
        constructor_part = parts[-1]
        module = importlib.import_module('.'.join(parts[:-1]))
        # Load the constructor.
        return getattr(module, constructor_part)

    def new_class(self) -> Type[DataframeLoader]:
        '''Generate a constructor for an SklearnLoader.'''
        return type(self._random_name(), (DataframeLoader, ), {
            "name": self.name,
            "tags": self.tags.copy(),
            "_load_train": _load_train_impl,
            "_load_test": _load_test_impl,
            "_test_data": None,
            "_impl": self,
        })


def register(catalog: DataLoaderCatalog):  # pylint: disable=unused-argument
    '''Nothing to register.

    All subclasses of SklearnAlgorithm are registered in sklearn_algorithms.py
    '''
