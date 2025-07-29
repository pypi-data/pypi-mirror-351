'''Base class for objects that split datasets.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Any, Dict, List, NamedTuple, Optional

import pandas as pd


from ...catalog.memory_catalog import MemoryCatalog
from ...catalog.catalog_element_mixin import CatalogElementMixin
from ...problem_def.cross_validation_config import CrossValidationConfig
from ...wrangler.dataset import Dataset, TableFactory


class SplitterError(Exception):
    '''Base error for splitters.'''


class Fold(NamedTuple):
    '''A fold for cross-validation'''
    train: Dataset
    validate: Dataset
    ground_truth: Optional[Dataset] = None


class SplitDataset(List[Fold]):
    '''A split dataset for cross-validation'''

    @property
    def folds(self) -> List[Fold]:
        '''List of folds

        Exists as a property for backwards compatibility.
        '''
        return self

    @property
    def ground_truth(self) -> Optional[Dataset]:
        '''Return ground truth if it exists and can be automatically extracted.'''
        if len(self) == 0:
            return None
        reference_dataset = self[0].train
        if not reference_dataset.has_dataframe:
            # Not a pandas dataset.
            return None

        if all(f.ground_truth is None for f in self):
            # Unsupervised
            return None

        dfs: List[pd.DataFrame] = []
        for f in self:
            assert f.ground_truth is not None
            dfs.append(f.ground_truth.ground_truth_table.as_(pd.DataFrame))

        retval = reference_dataset.output()
        retval.ground_truth_table = TableFactory(pd.concat(dfs).reset_index(drop=True))
        return retval


class Splitter(CatalogElementMixin, metaclass=abc.ABCMeta):
    '''Base class for objects that split datasets.'''

    _hyperparams: Dict[str, Any]
    _cv_config: CrossValidationConfig

    def __init__(self,
                 *args,
                 cv_config: CrossValidationConfig,
                 **default_hyperparams):
        super().__init__(*args, **default_hyperparams)
        self._cv_config = cv_config
        if not hasattr(self, '_hyperparams'):
            self._hyperparams = {}
        self._hyperparams.update(**default_hyperparams)

    def hyperparams(self, **overrides) -> Dict[str, Any]:
        '''Return splitter hyperparams, overridden with overrides'''
        retval = self._hyperparams.copy()
        retval.update(**overrides)
        return retval

    @abc.abstractmethod
    def split(self,
              dataset: Dataset,
              **overrides) -> SplitDataset:
        '''Divide dataset into multiple datasets according to the DatasetConfig.'''


class SplitterCatalog(MemoryCatalog[Splitter], metaclass=abc.ABCMeta):
    '''Base class for splitter catalog'''

    def lookup_by_task(self, task: str) -> Splitter:
        '''Get the right splitter for the task.'''
        splitters = self.lookup_by_tag_and(task=task)
        assert len(splitters) <= 1, f'BUG: Somehow we got too many splitters for task "{task}".'
        if len(splitters) == 0:
            splitters = self.lookup_by_tag_and(default='true')
            assert len(splitters) == 1, (
                'BUG: There should be exactly one default splitter (task "{task}").')
        return list(splitters.values())[0]
