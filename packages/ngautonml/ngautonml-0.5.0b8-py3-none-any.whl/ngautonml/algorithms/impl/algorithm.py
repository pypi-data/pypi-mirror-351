'''Catalog for models'''
import abc
from typing import Any, Dict, Optional

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .binder import BinderFactory
from ...catalog.catalog import Catalog
from ...catalog.memory_catalog import MemoryCatalog
from ...catalog.catalog_element_mixin import CatalogElementMixin
from ...communicators.impl.communicator_auto import CommunicatorCatalogAuto
from ...communicators.impl.communicator_catalog import CommunicatorCatalog
from ...discoverers.impl.discoverer_auto import DiscovererCatalogAuto
from ...discoverers.impl.discoverer_catalog import DiscovererCatalog
from ...searcher.param_range import ParamRange

# Things that go in catalogs (like Models) typically have a name and a
# dictionary of tags. Consider extracting this pattern as a mixin.
# We could then remove the following pylint disable.
# pylint: disable=duplicate-code


class Error(BaseException):
    '''Base class for all model-related exceptions.'''


class HyperparamError(Error):
    '''A hyperparam has an unknown name or incorrect value'''


class InputKeyError(Error, KeyError):
    '''Raise when a fit() or predict() method is passed an input dataset
    that is missing required keys.'''


class InputValueError(Error, ValueError):
    '''Raise when a fit() or predict() method is passed an input dataset
    with the correct keys but invalid value(s).'''


class Algorithm(CatalogElementMixin, metaclass=abc.ABCMeta):
    '''This object holds an algorithm.

    This can be an algorithm for training a model, a preprocessing
    algorithm, or a complete trained model.

    .. rubric:: Parameters:

    * ``communincator_catalog``: ``Optional[CommunicatorCatalog]``.
      Catalog that holds communicators for distributed algorithms,
      unused otherwise.
    * ``discoverer_catalog``: ``Optional[DiscovererCatalog]``.
      Catalog that holds discoverers for distributed algorithms,
      unused otherwise.
    * ``**hyperparams``: ``Any``.
      Arbitrary hyperparams that are interpreted by each individual algorithm.

    '''
    _instance_constructor: type  # This is really Type[AlgorithmInstance]
    _name: str = "unnamed"
    _default_hyperparams: Optional[Dict[str, Any]] = None
    _basename: str = ''

    # These two catalogs are only used by distributed algorithms
    _communicator_catalog: CommunicatorCatalog
    _discoverer_catalog: DiscovererCatalog

    # Map from json representation to python representation for specifically named hyperparams.
    # Both json and python elements need to be comparable with ==.
    # Format: {hyperparam_name: {json_value: python_value}}
    _hyperparam_lookup: Dict[str, Dict[Any, Any]]

    def __init__(self,
                 name: Optional[str] = None,
                 communicator_catalog: Optional[CommunicatorCatalog] = None,
                 discoverer_catalog: Optional[DiscovererCatalog] = None,
                 **hyperparams):
        self._name = name or self._name
        self._communicator_catalog = (communicator_catalog or CommunicatorCatalogAuto())
        self._discoverer_catalog = (discoverer_catalog or DiscovererCatalogAuto())
        super().__init__()

        # Convert class _default_hyperparams to an instance-specific
        # data structure.
        if self._default_hyperparams is None:
            self._default_hyperparams = {}
        params = self._default_hyperparams.copy()
        params.update(hyperparams)
        self._default_hyperparams = params
        if not hasattr(self, '_hyperparam_lookup'):
            self._hyperparam_lookup = {}

    @property
    def basename(self):
        '''Return the base name of the model.

        This should be the name used by nf.NeuralForecast to
        label the output column.
        '''
        return self._basename

    @property
    def communicator_catalog(self) -> CommunicatorCatalog:
        '''The communicator catalog'''
        return self._communicator_catalog

    @property
    def discoverer_catalog(self) -> DiscovererCatalog:
        '''The discoverer catalog'''
        return self._discoverer_catalog

    def instantiate(self, **hyperparams) -> Any:
        '''Create an instance of an algorithm that can hold training data.

        Args:
          serialized_model is a saved form of a trained model that instantiate
          can restore.
          hyperparams includes hyperparameters and other parameters needed
          when setting up an instance of the algorithm.

        Returns:
          AlgorithmInstance (marked as Any to break circularity)
        '''
        return self._instance_constructor(
            parent=self,
            **self._default_param_ranges(**self.hyperparams(**hyperparams)))

    def _default_param_ranges(self, **hyperparams) -> Dict[str, Any]:
        '''If any hyperparams are of type ParamRange, replace them with their default values.'''
        return {
            k: (v.default if isinstance(v, ParamRange) else v)
            for k, v in hyperparams.items()
        }

    def hyperparams(self, **overrides) -> Dict[str, Any]:
        '''Get the hyperparameters for this algorithm.

        Arguments passed to this function override defaults for the algorithm.
        '''
        assert self._default_hyperparams is not None, (
            'BUG: Algorithm._default_hyperparams should be resolved in __init__.')
        default_hyperparams = self._default_hyperparams.copy()
        default_hyperparams.update(**overrides)
        return default_hyperparams

    def _param_from_json(self, hyperparam_name: str, json_value: Any) -> Any:
        '''Parse the value for the given hyperparameter from the problem definition JSON.

        The default parser simply returns the value we parsed from JSON. Not all
        hyperparameter values are strings, numbers, lists, or dictionaries. Some
        are full python objects.
        '''
        # We really want to change the text of the KeyError.
        # pylint: disable=raise-missing-from
        if hyperparam_name in self._hyperparam_lookup:
            try:
                return self._hyperparam_lookup[hyperparam_name][json_value]
            except KeyError:
                raise KeyError(f'for {hyperparam_name}, could not find a parsed python value for'
                               f' json value {json_value} in hyperparam lookup table.  Only'
                               f' found {self._hyperparam_lookup[hyperparam_name].keys()}.')
        return json_value

    def param_to_json(self, hyperparam_name: str, python_value: Any) -> Any:
        '''Represent a hyperparam as a JSON serializabe structure.'''
        if hyperparam_name in self._hyperparam_lookup:
            for json_value, table_python_value in self._hyperparam_lookup[hyperparam_name].items():
                if python_value == table_python_value:
                    return json_value
            raise KeyError(f'for {hyperparam_name}, could not find a json value for '
                           f'python value {python_value} in hyperparam lookup table. '
                           f'Only found {self._hyperparam_lookup[hyperparam_name].values()}.')
        return python_value

    def bind(self, hyperparam_name: str, param_range: ParamRange) -> Dict[str, Any]:
        '''Bind names to final values for params.

        Returns: {'valuestr': value}
        '''
        return BinderFactory().build(
            param_range.method, parse_value=self._param_from_json).bind(
                hyperparam_name=hyperparam_name, prange=param_range.range)


class AlgorithmStub(Algorithm):
    '''Stub algorithm'''

    def instantiate(self, **hyperparams) -> Any:
        return None


class AlgorithmCatalog(Catalog[Algorithm], metaclass=abc.ABCMeta):
    '''Base class for algorithm catalogs'''
    # pylint: disable=unused-argument
    # These unused arguments are to make signatures match. quack.
    def __init__(self, communicator_catalog: Optional[CommunicatorCatalog] = None,
                 discoverer_catalog: Optional[DiscovererCatalog] = None, **kwargs):
        # This makes mypy happy. We make the signature compatable with MemoryAlgorithmCatalog.
        super().__init__(**kwargs)


class MemoryAlgorithmCatalog(MemoryCatalog[Algorithm], AlgorithmCatalog):
    '''An Algorithm catalog that has load and register.'''


class AlgorithmCatalogStub(MemoryCatalog[Algorithm], AlgorithmCatalog):
    '''stub'''
