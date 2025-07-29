'''Load data from a given format to a given format.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
import inspect
from typing import Any, Dict, List, Optional

from ...config_components.dataset_config import DatasetConfig
from ...wrangler.dataset import Dataset, Metadata


class DataLoader(metaclass=abc.ABCMeta):
    '''Base class for things that load data from a given format to a given format.'''
    name: str = 'data_loader_base_class'
    tags: Dict[str, List[str]] = {
        'input_format': [],
        'loaded_format': [],
    }
    _config: DatasetConfig
    _metadata: Metadata

    def __init__(self, config: DatasetConfig):
        self._config = config
        self._metadata = config.metadata

    @abc.abstractmethod
    def validate(self, dataset: Optional[Dataset]) -> None:
        '''Raise a ValidationErrors if something about the dataset is inconsistent.'''

    @abc.abstractmethod
    def _load_train(self) -> Optional[Dataset]:
        ...

    def load_train(self) -> Optional[Dataset]:
        '''Load a Dataset from the information in the problem description'''
        retval = self._load_train()
        self.validate(retval)
        return retval

    @abc.abstractmethod
    def _load_test(self) -> Optional[Dataset]:
        ...

    def load_test(self) -> Optional[Dataset]:
        '''Load test data if it exists, otherwise None'''
        retval = self._load_test()
        if retval is not None:
            self.validate(retval)
        return retval

    @abc.abstractmethod
    def _load_ground_truth(self) -> Optional[Dataset]:
        '''If the target column exists in the test set, extract it as the ground truth.'''

    def load_ground_truth(self) -> Optional[Dataset]:
        '''If the target column exists in the test set, extract it as the ground truth.'''
        retval = self._load_ground_truth()
        if retval is not None:
            self.validate(retval)
        return retval

    @abc.abstractmethod
    def _dataset(self, data: Any, **kwargs) -> Dataset:
        ...

    @abc.abstractmethod
    def build_dataset_from_json(self, json_data: Dict) -> Dataset:
        '''Build a Dataset object from a JSON object.'''

    def ez_dataset(self, data: Any, **kwargs) -> Dataset:
        '''Make a Dataset object with minimal boilerplate.

        Args:
            data:
            Object that can be turned into a Table
            target:
            the name of the target column.  A shortcut for speficying metadata
            metadata:
            the full metadata for the dataset.  Cannot be present alongside the target argument.
            key:
            The key for the data in the dataset. Defaults to "dataframe_table".
            cols:
            If set, only selects supplied column(s).
            Will take union with roles if both are specified.
            roles:
            If set, only selects columns with supplied role(s).
            Will take union with cols if both are specified.
        '''
        retval = self._dataset(data=data, **kwargs)
        self.validate(retval)
        return retval

    @abc.abstractmethod
    def poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        '''Poll for new training data.

        We'll wait up to timeout seconds for new data to arrive.
        If it times out we'll return None.

        A timeout of None waits forever.

        In a distributed simulation, the data is split based on node ID.
        '''

    def _lookup_var(self, var, default=None) -> Any:
        '''Look up a variable in the call stack.'''
        for frameinfo in inspect.stack(0)[:]:
            if var in frameinfo.frame.f_locals:
                return frameinfo.frame.f_locals[var]
        return default
