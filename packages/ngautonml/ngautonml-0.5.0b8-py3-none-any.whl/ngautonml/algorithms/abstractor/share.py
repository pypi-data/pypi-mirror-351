'''The simplest abstractor algorithm that just shares data.'''

from typing import Dict, Iterable, List, Optional

import pickle

import pandas as pd

from ...catalog.catalog import upcast
from ...tables.impl.table import TableFactory
from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.dataset import Dataset
from ...wrangler.logger import Logger, Level

from ..impl.algorithm import MemoryAlgorithmCatalog

from .impl.abstractor import Abstractor
from .impl.abstractor_instance import (
    AbstractorInstance, AbstractorNeighborState)

log = Logger(__file__, to_stdout=False, level=Level.DEBUG).logger()
_ = TableCatalogAuto()

# pylint: disable=protected-access


class ShareAbstractor(Abstractor):
    '''An abstractor that just copies data.'''
    _name = 'share_abstractor'
    _default_hyperparams = {  # pylint: disable=duplicate-code
        'Lambda': 1.0,
        'omega': 0.667,
        'tol': 0.000000001,
        'maxiter': None,
    }
    _tags: Dict[str, List[str]] = {
        'source': ['autonlab'],
        'distributed': ['true'],
        'abstractor': ['true'],
    }

    def instantiate(self, **hyperparams) -> 'ShareAbstractorInstance':
        return ShareAbstractorInstance(parent=self, **hyperparams)


class ShareAbstractorNeighborState(AbstractorNeighborState):
    '''A abstractor neighbor state that just holds data.'''
    _data: Dataset

    def __init__(self, columns: list, data: Dataset):
        # Remove duplicate rows to avoid exponential growth.
        unique_data = data.dataframe_table.drop_duplicates()
        self._data = data.output()
        self._data.dataframe_table = unique_data
        super().__init__(columns=columns)
        # TODO(piggy): A much more network-efficient way to do this would be to
        # keep track of our net dataset separately, and only communicate the
        # diff between our dataset and the union of all our neighbors' datasets.
        # We are converged when the diff is empty.

    def encode(self) -> bytes:
        '''Encode a message for distributed neighbors. '''
        return pickle.dumps((self._columns, self._data))

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'ShareAbstractorNeighborState':
        '''Decode a message from distributed neighbors.'''
        columns, data = pickle.loads(serialized_model)
        return cls(columns=columns, data=data)

    def distance(self, other: Optional['ShareAbstractorNeighborState']) -> float:
        '''Return the distance to another state.'''
        if other is None or self._data is None or other._data is None:
            return 1.0
        if set(self._data.dataframe_table.columns) != set(other._data.dataframe_table.columns):
            return 1.0
        if len(self._data.dataframe_table) != len(other._data.dataframe_table):
            return 1.0
        comparison = self._data.dataframe_table.compare(other._data.dataframe_table)
        return 1.0 * comparison.size

    def synthesize(self) -> Dataset:
        '''Return the data we have.'''
        return self._data


class ShareAbstractorInstance(AbstractorInstance):
    '''An instance of AbstractorInstance that just shares data.'''
    _neighbor_constructor = ShareAbstractorNeighborState

    @property
    def _neighbor_models_iter(self) -> Iterable[ShareAbstractorNeighborState]:
        for v in super()._neighbor_models_iter:
            assert isinstance(v, ShareAbstractorNeighborState), (
                'BUG: expected neighbor_models to contain ShareAbstractorNeighborState, '
                f'instead found {v} of type {type(v)}'
            )
            yield v

    def __init__(self, parent, distributed, **kwargs):
        self.hyperparams = parent.hyperparams(**kwargs)
        super().__init__(parent=parent, distributed=distributed, **parent.hyperparams(**kwargs))

    def _decode(self, serialized_model: bytes) -> ShareAbstractorNeighborState:
        '''Decode a message from distributed neighbors. '''
        return ShareAbstractorNeighborState.decode(serialized_model)

    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Concatenate, sort, and uniquify.
        '''
        if dataset is None and not self._neighbor_metadata:
            return
        new_data: Dataset
        new_df = pd.DataFrame()
        if self._neighbor_metadata:
            for neighbor in self._neighbor_models_iter:
                new_df = pd.concat([new_df, neighbor._data.dataframe_table.as_(pd.DataFrame)])
            new_data = next(self._neighbor_models_iter)._data.output()  # type: ignore
        if dataset is not None:
            new_df = pd.concat([new_df, dataset.dataframe_table.as_(pd.DataFrame)])
            new_data = dataset.output()

        new_df = new_df.sort_values(by=list(new_df.columns))
        new_df = new_df.drop_duplicates()

        new_df.reset_index(drop=True, inplace=True)

        new_data.dataframe_table = TableFactory(new_df)

        self._my_state = ShareAbstractorNeighborState(columns=list(new_df.columns), data=new_data)

    @property
    def my_state(self) -> Optional[ShareAbstractorNeighborState]:
        '''Accessor so that tests can see the state'''
        retval = self._my_state
        if retval is not None:
            assert isinstance(retval, ShareAbstractorNeighborState)
        return retval


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = ShareAbstractor(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
