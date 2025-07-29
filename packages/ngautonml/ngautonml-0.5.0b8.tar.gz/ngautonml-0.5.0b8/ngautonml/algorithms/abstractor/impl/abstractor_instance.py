'''Base class for abstractor instances.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, Optional, TypeVar

from ....algorithms.impl.fittable_algorithm_instance import UntrainedError
from ....neighbor_manager.node_id import NodeID
from ....wrangler.logger import Logger, Level
from ....wrangler.dataset import Dataset

from ...impl.distributed_algorithm_instance import DistributedAlgorithmInstance, NeighborState

log = Logger(__file__, to_stdout=False, level=Level.INFO).logger()


NeighborStateSubclass = TypeVar('NeighborStateSubclass', bound='AbstractorNeighborState')


class NoDataError(Exception):
    '''No data was provided to the abstractor.'''


class PredictCalledError(Exception):
    '''Predict was called on an abstractor.'''


class AbstractorNeighborState(NeighborState[NeighborStateSubclass]):
    '''A message from a neighbor in the abstractor network.'''

    @abc.abstractmethod
    def synthesize(self) -> Dataset:
        '''Synthesize a training dataset typical of the state.
        '''


class AbstractorInstance(DistributedAlgorithmInstance):
    '''Base class for abstractor instances.'''
    _neighbors: Dict[NodeID, AbstractorNeighborState]

    @property  # type: ignore[override]
    def _my_state(self) -> Optional[AbstractorNeighborState]:
        retval = DistributedAlgorithmInstance._my_state.fget(self)  # type: ignore[attr-defined] # pylint: disable=assignment-from-no-return,line-too-long
        assert retval is None or isinstance(retval, AbstractorNeighborState), (
            'BUG: expected _my_state to be None or an AbstractorNeighborState.')
        return retval

    @_my_state.setter
    def _my_state(self, value: Optional[AbstractorNeighborState]) -> None:
        assert value is None or isinstance(value, AbstractorNeighborState), (
            'BUG: expected value to be None or an AbstractorNeighborState.')
        DistributedAlgorithmInstance._my_state.fset(self, value)  # type: ignore[attr-defined]

    @property
    def my_state(self) -> Optional[AbstractorNeighborState]:
        '''Return the state of the Abstractor.'''
        return self._my_state

    def predict_passthrough(self, *args, **kwargs) -> Optional[Dataset]:
        '''Passthrough to the predict method of DistributedAlgorithm.'''
        return super().predict(*args, **kwargs)

    def predict(self, *args, **kwargs) -> Optional[Dataset]:
        '''Predict the output of the model.'''
        raise PredictCalledError('predict is not normally implemented in an Abstractor.')

    def _predict(self, *args, **kwargs) -> Optional[Dataset]:
        '''Predict the output of the model.'''
        raise PredictCalledError('predict is not normally implemented in an Abstractor.')

    @abc.abstractmethod
    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Fit the model to the data. This is the actual implementation of fit.'''

    def synthesize(self) -> Dataset:
        '''Synthesize a training dataset typical of the state.'''
        my_state = self.my_state
        if my_state is None:
            raise UntrainedError('Cannot synthesize without a state.')
        return my_state.synthesize()
