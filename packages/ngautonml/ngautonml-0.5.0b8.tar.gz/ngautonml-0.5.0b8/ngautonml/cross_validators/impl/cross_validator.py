'''Base class for objects that perform varieties of cross validation.'''
# pylint: disable=too-many-arguments,duplicate-code
import abc
from typing import Any, Dict

from ...catalog.memory_catalog import MemoryCatalog
from ...catalog.catalog_element_mixin import CatalogElementMixin
from ...executor.executor import Executor
from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import Designator
from ...instantiator.executable_pipeline import PipelineResult
from ...instantiator.instantiator_factory import InstantiatorFactory
from ...splitters.impl.splitter import SplitDataset

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


class CrossValidatorError(Exception):
    '''Base error for cross-validators.'''


class CrossValidator(CatalogElementMixin, metaclass=abc.ABCMeta):
    '''Base class for objects that perform varieties of cross validation.'''

    _hyperparams: Dict[str, Any]

    def __init__(self, *unused_args, **default_hyperparams):
        super().__init__(unused_args, default_hyperparams)
        if not hasattr(self, '_hyperparams'):
            self._hyperparams = {}
        self._hyperparams.update(**default_hyperparams)

    def hyperparams(self, **overrides) -> Dict[str, Any]:
        '''Return cross-validator hyperparams, overridden with overrides'''
        retval = self._hyperparams.copy()
        retval.update(**overrides)
        return retval

    @abc.abstractmethod
    def validate_pipelines(self,
                           split_dataset: SplitDataset,
                           bound_pipelines: Dict[Designator, BoundPipeline],
                           instantiator: InstantiatorFactory,
                           executor: Executor,
                           **overrides
                           ) -> Dict[Designator, PipelineResult]:
        '''Do cross-validation by running pipelines on a split dataset.

        Returns the split dataset and an ExecutorResult for each pipeline.'''


class CrossValidatorCatalog(MemoryCatalog[CrossValidator], metaclass=abc.ABCMeta):
    '''Base class for cross-validator catalog'''
