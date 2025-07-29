'''A fake distributed algorithm used for tests.'''

from typing import Any, Optional

import pickle

from ...config_components.distributed_config import DistributedConfig
from ...wrangler.dataset import Dataset
from ...wrangler.logger import Logger, Level

from .algorithm import Algorithm
from .distributed_algorithm_instance import (
    DistributedAlgorithmInstance, NeighborState)

log = Logger(__file__, to_stdout=False, level=Level.DEBUG).logger()


class FakeDistributedAlgorithm(Algorithm):
    '''A fake distributed algorithm used for tests.'''
    _name = 'fake_distributed_algorithm'
    _default_hyperparams = {  # pylint: disable=duplicate-code
        'Lambda': 1.0,
        'omega': 0.667,
        'tol': 0.000000001,
        'maxiter': None,
    }

    def instantiate(self, **hyperparams) -> 'FakeDistributedInstance':
        return FakeDistributedInstance(parent=self, **hyperparams)


class FakeDistributedAlgorithmNeighbor(NeighborState):
    '''A fake distributed algorithm neighbor state.'''
    def encode(self) -> bytes:
        '''Encode a message for distributed neighbors. '''
        return pickle.dumps(self._columns)

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'FakeDistributedAlgorithmNeighbor':
        '''Decode a message from distributed neighbors.'''
        columns = pickle.loads(serialized_model)
        return cls(columns=columns)

    def state_differs(self,
                      distributed: DistributedConfig,
                      other: Optional[Any]) -> bool:
        '''Decide whether to send a message to neighbors.

        last_state_sent is an instance of type(self) or None.
        '''
        _ = distributed
        return other is None  # Only send once

    def distance(self, other: 'FakeDistributedAlgorithmNeighbor') -> float:
        return 0.0


FAKE_SERIALIZED = b'fake serialized algorithm'


class FakeDistributedInstance(DistributedAlgorithmInstance):
    '''An instance of FakeAlgorithm for tests.'''
    evidence_of_deserialize = None
    _neighbor_constructor = FakeDistributedAlgorithmNeighbor

    def __init__(self, parent, distributed, **kwargs):
        self.hyperparams = parent.hyperparams(**kwargs)
        super().__init__(parent=parent, distributed=distributed, **parent.hyperparams(**kwargs))

    def deserialize(self, serialized_model: bytes) -> 'FakeDistributedInstance':
        self.evidence_of_deserialize = serialized_model
        return self

    def serialize(self) -> bytes:
        return FAKE_SERIALIZED

    def _decode(self, serialized_model: bytes) -> FakeDistributedAlgorithmNeighbor:
        '''Decode a message from distributed neighbors. '''
        return FakeDistributedAlgorithmNeighbor.decode(serialized_model)

    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''If we get data, update our state to match its columns.

        If we get no data but have seen a neighbor, update our state to match the
            neighbor's columns.
        '''
        if dataset is not None:
            self._my_state = FakeDistributedAlgorithmNeighbor(
                columns=dataset.dataframe_table.columns)
        elif self._neighbor_metadata:
            self._my_state = FakeDistributedAlgorithmNeighbor(
                columns=next(self._neighbor_models_iter).columns)  # type: ignore
            # not sure why mypy complains about using next() as above,
            #   we use it identically in other places.

    def _predict(self, dataset: Optional[Dataset], **kwargs) -> Optional[Dataset]:
        '''Apply model to input dataset to create output.

        This handles model-speific work and does not handle general tasks.
        '''
        return dataset

    @property
    def my_state(self) -> Optional[FakeDistributedAlgorithmNeighbor]:
        '''Accessor so that tests can see the state'''
        retval = self._my_state
        if retval is not None:
            assert isinstance(retval, FakeDistributedAlgorithmNeighbor)
        return retval


class FitCountDistributedAlgorithm(Algorithm):
    '''A fake distributed algorithm that counts the number of times it has been fit'''
    _name = 'fit_count_distributed_algorithm'
    _default_hyperparams = {
        'Lambda': 1.0,
        'omega': 0.667,
        'tol': 0.000000001,
        'maxiter': None,
    }

    def instantiate(self, **hyperparams) -> 'FitCountDistributedInstance':
        return FitCountDistributedInstance(parent=self, **hyperparams)


class FitCountDistributedAlgorithmNeighbor(FakeDistributedAlgorithmNeighbor):
    '''A fake distributed algorithm neighbor state that counts the number of fits.'''
    fit_count: int

    def __init__(self, fit_count: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.fit_count = fit_count

    def encode(self) -> bytes:
        '''Encode a message for distributed neighbors. '''
        return pickle.dumps(self.fit_count)

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'FitCountDistributedAlgorithmNeighbor':
        '''Decode a message from distributed neighbors.'''
        fit_count = pickle.loads(serialized_model)
        return cls(fit_count=fit_count)

    def state_differs(self,
                      distributed: DistributedConfig,
                      other: Optional[Any]) -> bool:
        '''Always report that our state has changed until we've been fit 3 times'''
        log.debug('Checking if state changed, fit count: %s', self.fit_count)
        _ = distributed
        _ = other
        return self.fit_count < 3


class FitCountDistributedInstance(FakeDistributedInstance):
    '''An instance of FakeAlgorithm for tests that counts fits.'''

    def _decode(self, serialized_model: bytes) -> FitCountDistributedAlgorithmNeighbor:
        '''Decode a message from distributed neighbors. '''
        return FitCountDistributedAlgorithmNeighbor.decode(serialized_model)

    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Fit the model to the data. This is the actual implementation of fit.'''
        _ = dataset
        if self._my_state is None:
            self._my_state = FitCountDistributedAlgorithmNeighbor(fit_count=0)
        assert isinstance(self._my_state, FitCountDistributedAlgorithmNeighbor)
        self._my_state.fit_count += 1
        log.debug('Fit count incrementing to %s', self._my_state.fit_count)
