'''Base class for distributed alogorithm instances.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
import collections
from copy import deepcopy
from pathlib import Path
import pickle
import queue
import threading
import time
import traceback
from typing import (Any, Callable, Dict, Generic, Iterable, List, Mapping,
                    Optional, Set, Tuple, Type, TypeVar, Union)

import numpy as np
from numpy.random import RandomState  # pylint: disable=no-name-in-module  # This just isn't true.

from ...algorithms.impl.fittable_algorithm_instance import UntrainedError
from ...algorithms.impl.neighbor_metadata import NeighborMetadata
from ...algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ...algorithms.impl.neighbor_state_interface import NeighborStateInterface
from ...config_components.distributed_config import (
    DistributedConfig, DropperConfig, CommunicatorConfig)
from ...deciders.impl.decider import Decider
from ...deciders.impl.decider_auto import DeciderCatalogAuto
from ...neighbor_manager.event import Recv
from ...neighbor_manager.node_id import NodeID
from ...neighbor_manager.neighbor_manager import NeighborManager
from ...neighbor_manager.neighbor_manager_impl import NeighborManagerImpl
from ...wrangler.dataset import Dataset
from ...wrangler.exception_thread import ExceptionThread
from ...wrangler.logger import Logger, Level

from ..impl.algorithm import Algorithm
from ..impl.fittable_algorithm_instance import FittableAlgorithmInstance


log = Logger(__file__, to_stdout=False, level=Level.DEBUG).logger()


NeighborStateSubclass = TypeVar('NeighborStateSubclass', bound='NeighborState')


class NoDataError(Exception):
    '''No data was provided to the algorithm.'''


class ForceFalse(Exception):
    '''Force the decider to return False.'''


class Dropper():
    '''A class that can be used to drop messages.'''
    _config: DropperConfig
    _tried_counter: int = 0
    _dropped_counter: int = 0

    def __init__(self, config: DropperConfig) -> None:
        self._config = config
        self._random = RandomState(seed=config.seed)
        self._first = True
        if config.output_dir is not None:
            log.info('Dropper output dir: %s', config.output_dir)
            config.output_dir.mkdir(parents=True, exist_ok=True)

    def drop(self) -> bool:
        '''Return True if the message should be dropped.'''
        retval = (not self._first) and (1 == self._random.binomial(n=1, p=self._config.drop_rate))

        self._first = False

        self._tried_counter += 1
        if retval:
            self._dropped_counter += 1
        return retval

    @property
    def output_dir(self) -> Optional[Path]:
        '''Return the output directory.'''
        return self._config.output_dir

    @property
    def tried_counter(self) -> int:
        '''Return the number of messages tried.'''
        return self._tried_counter

    @property
    def dropped_counter(self) -> int:
        '''Return the number of messages dropped.'''
        return self._dropped_counter


class NeighborState(
        Generic[NeighborStateSubclass],
        NeighborStateInterface[NeighborStateSubclass]):
    '''A message from a neighbor in the distributed network.'''
    _columns: Optional[List[Union[int, str]]]
    # TODO(Merritt): add a respesentation of total amount of data

    def __init__(self, columns: Optional[List[Union[int, str]]] = None) -> None:
        self._columns = columns

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(columns = {self.columns})'

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, NeighborState):
            return False
        return self.columns == value.columns

    @property
    def columns(self) -> Optional[List[Union[int, str]]]:
        '''The column names.'''
        return self._columns

    @columns.setter
    def columns(self, value: Optional[List[Union[int, str]]]) -> None:
        '''The column names.'''
        self._columns = value

    @abc.abstractmethod
    def encode(self) -> bytes:
        '''Encode a message for distributed neighbors. '''

    @classmethod
    @abc.abstractmethod
    def decode(cls, serialized_model: bytes) -> NeighborStateSubclass:
        '''Decode a message from distributed neighbors.

        This should just redirect to the relevant NeighborState subclass.
        '''

    @property
    def payload_size(self):
        '''Return the size of the payload to send this state.'''
        return self.encode().__sizeof__()

    def state_differs(self,
                      distributed: DistributedConfig,
                      other: Optional[NeighborStateSubclass]) -> bool:
        '''Decide if our state differs meaningfully from another.

        :distributed: contains information from the problem definition, including fit_eps
        :other: is an instance of type(self) or None.
        '''
        if other is None:
            return True

        state_distance = self.distance(other)
        log.log(Level.VERBOSE, 'node %s: state_distance: %s', distributed.my_id, state_distance)

        changed = bool(np.isnan(state_distance) or state_distance > distributed.fit_eps)

        return changed

    @abc.abstractmethod
    def distance(self, other: NeighborStateSubclass) -> float:
        '''A numerical measure of the distance between this state and another.'''

    @classmethod
    def _cast_columns(cls, columns: Any) -> List[str]:
        '''Return columns typed as a list of strings.

        Useful for type safety in subclasses' decode methods.
        '''
        assert isinstance(columns, collections.abc.Iterable), (
            'BUG: expected columns to be iterable, '
            f'instead found {columns} of type {type(columns)}'
        )
        columns = list(columns)
        assert all(isinstance(col_name, (int, str)) for col_name in columns), (
            f'BUG: expected column names to be ints or strings, instead found {columns} '
            f'of types {[type(col_name) for col_name in columns]}.'
        )
        return [str(c) for c in columns]


class DistributedAlgorithmInstance(FittableAlgorithmInstance):  # pylint: disable=too-many-public-methods,line-too-long
    '''Base class for distributed algorithm instances.'''

    _known_neighbors: Set[NodeID]
    _my_id: NodeID
    _neighbor_metadata: Dict[NodeID, NeighborMetadata]
    _my_state_metadata: NeighborMetadata
    _predict_state: Optional[NeighborStateInterface] = None
    _neighbor_constructor: Type[NeighborStateInterface]

    _lock_model: Optional[threading.Lock] = None
    _lock_predict_state: Optional[threading.Lock] = None
    _neighbor_manager: Optional[NeighborManager] = None
    _fit_thread: Optional[ExceptionThread] = None
    _read_thread: Optional[ExceptionThread] = None
    _exception_queue: Optional[queue.Queue[Tuple[Exception, str]]]
    _distributed: DistributedConfig
    _synchronous: bool = False  # Do we run our fit thread or wait to be told to fit?
    _dropper: Optional[Dropper] = None

    _convergence_count: int  # Number of times we considered fitting since the model last changed
    _changed_on_fit: bool  # Set to true if we decided to send last time we fit.
    _convergence_time: Optional[int]  # value of time.monotonic_ns() at start of most recent
    #                                   convergence period (None if we sent on last fit)
    _stop: bool = False
    _pending_message_from_neighbor: bool = False
    _training: bool = False   # True if we are currently training

    _last_dataset: Optional[Dataset] = None
    _columns: Optional[List[Union[int, str]]] = None
    _lambda: np.float64  # How strongly we weight our neighbors' models.
    _omega: np.float64  # How strongly we weight previous states of our own model.

    _fit_counter: int = 0
    _fit_periodic_counter: int = 0
    _predict_counter: int = 0
    _emit_counter: int = 0

    @classmethod
    def instantiate_with_state(
            cls,
            state: bytes,
            parent: Algorithm,
            distributed: DistributedConfig) -> 'DistributedAlgorithmInstance':
        '''Create an instance of this class from a saved state.'''
        instance = cls(parent=parent, distributed=distributed)
        instance._trained = True
        my_state = instance._neighbor_constructor.decode(state)
        instance._my_state_metadata = NeighborMetadata(my_state=my_state)
        instance._predict_state = my_state
        instance._lock_predict_state = threading.Lock()
        return instance

    @property
    def trained(self) -> bool:
        '''Is this algorithm trained?

        Override base class to take the lock.
        '''
        if self._lock_model is None:
            # We are in a deepcopy.
            return self._trained

        with self._lock_model:
            retval = self._trained
        return retval

    def __deepcopy__(self, memo: Dict[int, object]) -> 'DistributedAlgorithmInstance':
        '''Deepcopy implementation.'''
        # We don't want to deepcopy the lock, threads, the neighbor manager, the
        # last dataset, pending message state, the stop flag, or the exception queue.
        alg_name = self._algorithm.name if self._algorithm is not None else 'unknown'
        log.debug('%s: node %d (%x) is deepcopying.', alg_name, self._my_id, id(self))
        assert self._algorithm is not None
        retval = type(self)(parent=self._algorithm,
                            distributed=self._distributed,
                            Lambda=self._lambda,
                            omega=self._omega)
        retval._known_neighbors = deepcopy(self._known_neighbors, memo=memo)
        retval._my_id = self._my_id
        retval._neighbor_metadata = deepcopy(self._neighbor_metadata, memo=memo)
        # retval._my_state = deepcopy(self._my_state, memo=memo)
        retval._my_state_metadata = deepcopy(self._my_state_metadata, memo=memo)
        retval._predict_state = deepcopy(self._predict_state, memo=memo)

        retval._lock_model = None
        retval._lock_predict_state = None
        retval._exception_queue = None
        retval._distributed = deepcopy(self._distributed, memo=memo)

        retval._last_dataset = None
        if self._columns is not None:
            retval._columns = self._columns.copy()

        retval._pending_message_from_neighbor = False
        retval._trained = self._trained

        retval._convergence_time = self._convergence_time
        return retval

    def __init__(self,
                 parent: Algorithm,
                 distributed: DistributedConfig,
                 **kwargs):
        self._lambda = np.float64(kwargs.pop('Lambda'))
        self._omega = np.float64(kwargs.pop('omega'))
        self._tol = np.float64(kwargs.pop('tol'))
        _maxiter = kwargs.pop('maxiter')
        self._maxiter = int(_maxiter) if _maxiter is not None else None
        self._synchronous = bool(kwargs.pop('synchronous', False))
        super().__init__(parent, **kwargs)
        self._distributed = distributed
        self._my_id = distributed.my_id
        self._neighbor_metadata = {}
        self._my_state_metadata = NeighborMetadata()
        self._known_neighbors = set()
        self._lock_model = threading.Lock()
        self._lock_predict_state = threading.Lock()
        self._convergence_count = 0
        self._convergence_time = None
        self._exception_queue = queue.Queue()
        self._changed_on_fit = False
        if self._distributed.dropper is not None:
            self._dropper = Dropper(config=self._distributed.dropper)

    @property
    def _neighbor_models_iter(self) -> Iterable[NeighborState]:
        for _, v in self._neighbor_metadata.items():
            if v.current_state is None:  # This is a neighbor we haven't heard from yet.
                continue
            assert isinstance(v.current_state, NeighborState), (
                'BUG: expected neighbor_models to contain NeighborState, '
                f'instead found {v.current_state} of type {type(v.current_state)}'
            )
            yield v.current_state

    @property  # type: ignore[override]
    def _my_state(self) -> Optional[NeighborStateInterface]:
        '''Get the state of this node.'''
        return self._my_state_metadata.current_state

    @_my_state.setter
    def _my_state(self, value: Optional[NeighborStateInterface]) -> None:
        self._my_state_metadata.current_state = value

    def decide(self,
               neighbor_id: NodeID,
               neighbors: Optional[Mapping[NodeID, NeighborMetadataInterface]] = None) -> bool:
        '''Decide if we should send an update to a specific neighbor.

        :distributed: contains information from the problem definition.
        :neighbor_id: is the ID for the node we want to decide against.
        :neighbors: is an optional mapping of all neighbors. If None, we
            use self._neighbor_metadata. This argument is to simplify testing.
        '''
        results: List[bool] = []
        decider_catalog = DeciderCatalogAuto()
        if neighbors is None:
            neighbors = self._neighbor_metadata
        try:
            for name, config in self._distributed.decider.decider_configs.items():
                if config.enabled:
                    decider: Decider = decider_catalog.lookup_by_name(
                        name)(name=name, config=config)
                    results.append(decider.decide(
                        my_meta=self._my_state_metadata,
                        neighbor_id=neighbor_id,
                        neighbors=neighbors))
        except ForceFalse:
            return False
        return any(results)

    @property
    def locked(self) -> bool:
        '''Check the model locks status'''
        return False if self._lock_model is None else self._lock_model.locked()

    @property
    def converged(self) -> bool:
        '''Check if the model has converged.'''
        if self._lock_model is None:
            # We are in a deepcopy.
            return self._converged()
        with self._lock_model:
            retval = self._converged()
        return retval

    def _converged(self) -> bool:
        '''Check if the model has converged.'''
        if self._convergence_time is None:
            log.debug('node %s (%x) has not converged.', self._my_id, id(self))
            return False
        now = time.monotonic_ns()
        elapsed = now - self._convergence_time
        if elapsed > self._distributed.convergence_time_ns:
            log.info('node %s (%x) has converged.', self._my_id, id(self))
        else:
            log.debug('node %s (%x) has been converging for %s ns.', self._my_id, id(self), elapsed)
        return elapsed > self._distributed.convergence_time_ns

    @property
    def my_id(self) -> NodeID:
        '''Get the ID of this node.'''
        return self._my_id

    @property
    def my_state(self) -> Optional[NeighborStateInterface]:
        '''Get the state of this node.'''
        return self._my_state

    @property
    def predict_state(self) -> Optional[NeighborStateInterface]:
        '''Get the state of this node for prediction.'''
        return self._predict_state

    @property
    def my_state_copy(self) -> Optional[NeighborStateInterface]:
        '''Safely get a copy of the state of this node.'''
        if self._lock_model is None:
            # We are in a deepcopy and can not change.
            return self._my_state

        with self._lock_model:
            retval = deepcopy(self._my_state)
        return retval

    @property
    def dropper(self) -> Optional[Dropper]:
        '''Get the dropper.'''
        return self._dropper

    def start(self) -> None:
        '''Start all supporting threads.'''
        alg_name = self._algorithm.name if self._algorithm is not None else 'unknown'
        log.info('%s: node %s (%x) is starting', alg_name, self._my_id, id(self))
        self._stop = False
        if self._neighbor_manager is None:
            self._neighbor_manager = self._init_neighbor_manager()
            self._neighbor_manager.start()

        if not self._synchronous:
            self._fit_thread = ExceptionThread(target=self._fit_periodically, kwargs={
                'stop': lambda: self._stop
            })
            self._fit_thread.start()
            self._read_thread = ExceptionThread(target=self._read_from_neighbors, kwargs={
                'stop': lambda: self._stop
            })
            self._read_thread.start()

    @property
    def synchronous(self) -> bool:
        '''Return whether we are running synchronously.'''
        return self._synchronous

    def poll_exceptions(self) -> Optional[Tuple[Exception, str]]:
        '''Return most recent exception from inside a thread, if any.'''
        assert self._exception_queue is not None, (
            'BUG: _exception_queue should be set in __init__.  Is this a deepcopy?'
        )
        try:
            return self._exception_queue.get(block=False)
        except queue.Empty:
            return None

    def stop(self) -> None:
        '''Stop all supporting threads.'''
        alg_name = self._algorithm.name if self._algorithm is not None else 'unknown'
        log.info('%s: node %s (%x) is stopping.', alg_name, self._my_id, id(self))
        self._stop = True
        if self._fit_thread is not None:
            self._fit_thread.join()
        if self._read_thread is not None:
            self._read_thread.join()
        if self._neighbor_manager is not None:
            self._neighbor_manager.stop()

    def _init_neighbor_manager(self) -> NeighborManager:
        comm = self.algorithm.communicator_catalog.lookup_by_name(
            self._distributed.communicator.name)
        disc = self.algorithm.discoverer_catalog.lookup_by_name(
            self._distributed.discoverer)
        communicator = comm(distributed=self._distributed,
                            known_neighbors=self._known_neighbors,
                            my_id=self._my_id)
        discoverer = disc(config=self._distributed, communicator=communicator)
        return NeighborManagerImpl(discoverer=discoverer)

    def _read_from_neighbors(self, stop: Callable[[], bool]) -> None:
        '''Read from neighbors and update the neighbor states.'''
        log.debug('node %s (%x) is starting to receive from neighbors.', self._my_id, id(self))
        while not stop():
            self.read_from_neighbors()
            time.sleep(self._distributed.polling_interval)

    def read_from_neighbors(self) -> None:
        '''Read from neighbors and update our local neighbor states.'''
        try:
            if self._neighbor_manager is not None:
                for event in self._neighbor_manager.poll_for_events(
                        timeout=self._distributed.polling_interval):
                    log.log(Level.VERBOSE,
                            'node %s (%x) is reading %s', self._my_id, id(self), event)
                    if isinstance(event, Recv):
                        self._recv(event.neighbor, event.payload)
        except Exception as e:  # pylint: disable=broad-exception-caught
            trace = traceback.format_exc()
            log.error(
                'node %s (%x) error while reading from neighobrs:\n%s',
                self._my_id, id(self), trace)
            assert self._exception_queue is not None, (
                'BUG: _exception_queue should have been set in __init__. Is this a deepcopy?')
            self._exception_queue.put((e, trace))

    @property
    def neighbor_manager(self) -> NeighborManager:
        '''Get the neighbor manager.'''
        assert self._neighbor_manager is not None, (
            'BUG: _neighbor_manager should have been set in __init__. Is this a deepcopy?')
        return self._neighbor_manager

    def _fit_periodically(self, stop: Callable[[], bool]):
        '''Refit if we have seen a message from a neighbor and enough time passed.'''
        log.debug('node %s (%x) is starting to fit periodically.', self._my_id, id(self))
        while not stop():
            assert self._lock_model is not None, (
                'BUG: _lock_model should have been set in __init__. Is this a deepcopy?'
            )

            self.fit_now()
            time.sleep(self._distributed.polling_interval)

    def fit_now(self) -> None:
        '''Fit the model now.

        This is the method that _fit_periodically calls to fit the model.

        If we are running in synchronous mode, we need to call this method to advance the model.
        '''
        assert self._lock_model is not None, (
            'BUG: _lock_model should have been set in __init__. Is this a deepcopy?')
        with self._lock_model:
            did_change = self._changed_on_fit

        if self._pending_message_from_neighbor or did_change:
            log.info(
                'node %s (%x) is spontaneously fitting. '
                'Pending message: %s. changed on last fit: %s.',
                self._my_id,
                id(self),
                self._pending_message_from_neighbor,
                did_change)
            try:
                self._fit_periodic_counter += 1
                self.fit(self._last_dataset)
            except Exception as e:  # pylint: disable=broad-exception-caught
                trace = traceback.format_exc()
                log.error(
                    'node %s (%x) error spontaneously fitting:\n%s',
                    self._my_id, id(self), trace)
                assert self._exception_queue is not None, (
                    'BUG: exception queue should have been set in __init__.  '
                    'Is this a deepcopy?')
                self._exception_queue.put((e, trace))
        if self._my_state is not None:
            with self._lock_model:
                self._emit_fit_complete()
                self._conditionally_send()

    @property
    def fit_counter(self) -> int:
        '''Return the number of times the model has been fit.'''
        return self._fit_counter

    @property
    def fit_periodic_counter(self) -> int:
        '''Return the number of times the model has been fit spontaneously.'''
        return self._fit_periodic_counter

    @property
    def predict_counter(self) -> int:
        '''Return the number of times the model has been predicted.'''
        return self._predict_counter

    def _recv(self, neighbor_id: NodeID, serialized_model: bytes) -> None:
        '''Receive a message from a neighbor.'''
        if self.dropper is not None and self.dropper.drop():
            return
        model = self._decode(serialized_model)
        assert self._lock_model is not None
        with self._lock_model:
            log.info('node %s (%x) received from %s', self._my_id, id(self), neighbor_id)
            log.log(Level.VERBOSE, 'received message: \n %s', model)
            self._pending_message_from_neighbor = True
            if neighbor_id not in self._neighbor_metadata:
                self._neighbor_metadata[neighbor_id] = NeighborMetadata()
            self._neighbor_metadata[neighbor_id].current_state = model

    @abc.abstractmethod
    def _decode(self, serialized_model: bytes) -> NeighborState:
        '''Decode a message from distributed neighbors. '''

    def _send(self) -> None:
        '''Send the model to all neighbors.

        Must be called with the model lock held.
        '''
        log.info('node %s (%x) is sending', self._my_id, id(self))
        assert self._my_state is not None, (
            f'node {self._my_id} ({id(self)})) has no state to send.')
        if self._neighbor_manager is not None:
            log.log(Level.VERBOSE, 'node %s (%x) has a neighbor manager.', self._my_id, id(self))
            self._neighbor_manager.send_all(self._my_state.encode())
        else:
            log.warning('node %s (%x) has no neighbor manager.', self._my_id, id(self))
            return
        # Only reset the last_state_sent if we actually sent a message.
        # We want to catch cumulative drift in self._my_state.v.
        log.debug("node %s (%x) reset last_state_sent.", self._my_id, id(self))
        self._my_state_metadata.sent_current_state()

    def _update_columns(self, dataset: Dataset) -> Dataset:
        '''set self._columns based on the given dataset and cross-check with neighbors.

        If neighbors are reporting a column that we don't see, call
            _resolve_neighbor_column_mismatch.
        '''

        self._columns = self._get_columns(dataset=dataset)

        mismatched_neighbors = {
            node_id: set(neighbor.current_state.columns)
            for node_id, neighbor in self._neighbor_metadata.items()
            if (neighbor.current_state is not None
                and neighbor.current_state.columns is not None
                and not set(neighbor.current_state.columns) == set(self._columns))
        }
        if mismatched_neighbors:
            return self._resolve_neighbor_column_mismatch(dataset, mismatched_neighbors)

        return dataset

    def _resolve_neighbor_column_mismatch(self,
                                          dataset: Dataset,
                                          mismatched_neighbors: Dict[NodeID, Set[Union[int, str]]]
                                          ) -> Dataset:
        '''Handle case where set of columns reported by a neighbor does not match our own.

        Message contains information about
        '''
        _ = dataset
        assert self._columns is not None, (
            'BUG: self._columns should be set before _resolve_neighbor_column_mismatch is called.'
        )
        colset = set(self._columns)
        message = (
            'Found neighbors with mismatched columns: \n'
            + '\n'.join(
                f'node {node_id} lacks columns {colset - cols} '
                f'and has extra columns {cols - colset}.'
                for node_id, cols in mismatched_neighbors.items())
        )
        log.error(message)
        raise NotImplementedError(message)

    def _get_columns(self, dataset: Dataset) -> List[Union[int, str]]:
        '''Get the columns of the dataset.'''
        retval = dataset.dataframe_table.columns
        return [str(c) for c in retval]

    def _is_empty(self, dataset: Dataset) -> bool:
        '''Return True if a dataset cannot be used to fit/predict.'''
        return dataset.dataframe_table.empty

    def _emit_fit_complete(self) -> None:
        '''Emit a message when the model has been fit.'''
        if self._dropper is None:
            return
        self._emit_counter += 1
        record = {
            'my_id': self._my_id,
            'now': time.monotonic_ns(),
            'emit_counter': self._emit_counter,
            'fit_counter': self._fit_counter,
            'fit_periodic_counter': self._fit_periodic_counter,
            'predict_counter': self._predict_counter,
            'dropper_tried_counter': self._dropper.tried_counter,
            'dropper_dropped_counter': self._dropper.dropped_counter,
            'my_state': self._my_state.encode() if self._my_state is not None else None,
        }
        output_dir = self._dropper.output_dir
        if output_dir is not None:
            with open(output_dir
                      / f'id{self._my_id:02d}_{self._emit_counter:010d}_fit_complete.pkl', 'wb'
                      ) as f:
                f.write(pickle.dumps(record))

    def fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Fit the model to the data.

        If dataset is None, we process information from neighbors.
        If dataset is not None but is empty, we ignore it. This allows
        us to work with special data loaders.
        '''
        log.info('node %s (%x) is fitting (%s).',
                 self._my_id,
                 id(self),
                 'no data' if dataset is None else 'with data')

        assert self._lock_model is not None
        with self._lock_model:

            # Set this now so it will be False if an error interrupts the fit.
            self._changed_on_fit = False

            # Clear neighbor message now so we don't refit forever if a messge triggers an error
            self._pending_message_from_neighbor = False

            if dataset is not None:
                if self._is_empty(dataset):
                    log.warning('Node %s encountered empty or malformed dataset on fit: \n%s\n',
                                self._my_id, dataset)
                else:
                    dataset = self._update_columns(dataset.sorted_columns())
                    self._last_dataset = dataset
            self._training = True
            self._fit(dataset, **kwargs)
            self._training = False

            # Set after fit so we are not marked trained if we run into an error
            log.info('node %s (%x) fit complete; state: %s',
                     self._my_id,
                     id(self),
                     self._my_state.__class__.__name__)
            self._trained = True
            self._fit_counter += 1  # TODO(piggy): Move to self._my_state_metadata

            log.debug(
                'node %s (%x) (%s) fit complete; state: %s',
                self._my_id,
                id(self),
                self.__class__.__name__,
                self._my_state
            )
            log.log(
                Level.VERBOSE,
                'full state: %r', self._my_state)

            if self._my_state is not None:
                if not self._distributed.only_send_periodically:
                    self._conditionally_send()
                else:
                    log.info('node %s is not sending.', self._my_id)

            self._update_predict_state()

    def _detect_convergence(self, state_changed: bool) -> None:
        '''Detect if the model has converged.'''
        if self._my_state is None:
            return
        neighbor_distances = [
            self._my_state.distance(n) for n in self._neighbor_models_iter
        ]
        log.info('node %s neighbor distances: %s', self._my_id, neighbor_distances)
        neighbors_differ = [self._my_state.state_differs(self._distributed, n)
                            for n in self._neighbor_models_iter]

        # State changed and not first fit
        state_meaningfully_changed = (
            state_changed
            and self._my_state_metadata.last_state_sent is not None)

        if state_meaningfully_changed and any(neighbors_differ):
            log.debug('node %s is non-converged.', self._my_id)
            # Disable convergence clock
            self._convergence_time = None
        else:
            # State did not change and/or first fit and/or matches all neighbors
            # Start convergence clock
            if self._convergence_time is None:
                log.debug('node %s is starting convergence clock.', self._my_id)
                self._convergence_time = time.monotonic_ns()
            convergence_duration_s = 1e9 * (time.monotonic_ns() - self._convergence_time)
            log.debug('node %s is converged for %s seconds.',
                      self._my_id,
                      convergence_duration_s)

    def _update_predict_state(self):
        '''Update the predict state with the current state.

        The caller must hold the model lock.
        '''
        assert self._lock_predict_state is not None, (
            'BUG: _lock_predict_state should have been set in __init__. Is this a deepcopy?'
        )
        if self._my_state is not None:
            with self._lock_predict_state:
                self._predict_state = deepcopy(self._my_state)

    def _record_current_state_sent(self, positive_decisions: List[NodeID]) -> None:
        for neighbor_id in positive_decisions:
            # We might have not heard from this neighbor yet.
            if neighbor_id not in self._neighbor_metadata:
                self._neighbor_metadata[neighbor_id] = NeighborMetadata()
            self._neighbor_metadata[neighbor_id].last_state_sent = self._my_state

    def _send_broadcast_no_decisions(self, state_changed: bool) -> None:
        if state_changed:
            log.info('node %s (%x) is broadcasting now due to state change.',
                     self._my_id, id(self))
            self._send()

    def _send_unicast_no_decisions(self) -> None:
        assert self._my_state is not None
        assert self._neighbor_manager is not None
        positive_decisions = []
        for neighbor_id in self._neighbor_manager.known_neighbors:
            if neighbor_id in self._neighbor_metadata:
                neighbor = self._neighbor_metadata[neighbor_id]
                if self._my_state.state_differs(
                        distributed=self._distributed, other=neighbor.current_state):
                    positive_decisions.append(neighbor_id)
            else:
                positive_decisions.append(neighbor_id)
        if positive_decisions:
            log.info('node %s (%x) is unicasting now without decisions to %s.',
                     self._my_id, id(self), positive_decisions)
            self._neighbor_manager.send(positive_decisions, self._my_state.encode())
            self._my_state_metadata.sent_current_state()
            self._record_current_state_sent(positive_decisions)

    def _send_broadcast_decisions(self, decisions: List[Tuple[bool, NodeID]]) -> None:
        if any(decision for decision, _ in decisions):
            log.info('node %s (%x) is broadcasting now due to at least 1 decision.',
                     self._my_id, id(self))
            self._send()

    def _send_unicast_decisions(self, decisions: List[Tuple[bool, NodeID]]) -> None:
        assert self._my_state is not None
        assert self._neighbor_manager is not None
        if positive_decisions := [
            neighbor_id for decision, neighbor_id in decisions if decision
        ]:
            log.info('node %s (%x) is unicasting to %s.',
                     self._my_id, id(self), positive_decisions)
            self._neighbor_manager.send(positive_decisions, self._my_state.encode())
            self._my_state_metadata.sent_current_state()
            self._record_current_state_sent(positive_decisions)

    def _conditionally_send(self):  # pylint: disable=too-many-branches
        '''Send the model to neighbors if the deciders say so.

        Must be called with the model lock held.
        '''
        # Bootstrap neighbor discovery.
        state_changed = self._my_state.state_differs(
            distributed=self._distributed,
            other=self._my_state_metadata.last_state_sent)

        if self._my_state_metadata.last_state_sent is None:
            log.info('node %s (%x) is sending for the first time.', self._my_id, id(self))
            self._send()
            return

        self._changed_on_fit = state_changed

        if self._distributed.no_deciders:
            log.info('node %s (%x) is sending without deciders.', self._my_id, id(self))
            if (self._distributed.communicator.strategy
                    == CommunicatorConfig.Strategies.BROADCAST.value):
                log.info('node %s (%x) is broadcasting without decisions.', self._my_id, id(self))
                self._send_broadcast_no_decisions(state_changed=state_changed)
            elif (self._distributed.communicator.strategy
                    == CommunicatorConfig.Strategies.UNICAST.value):
                log.info('node %s (%x) is unicasting without decisions.', self._my_id, id(self))
                self._send_unicast_no_decisions()
            else:
                raise NotImplementedError(
                    f'Unknown strategy: {self._distributed.communicator.strategy}')
        else:
            log.info('node %s (%x) has deciders.', self._my_id, id(self))
            # We have deciders.
            decisions = []
            for neighbor_id in self._neighbor_manager.known_neighbors:
                if neighbor_id not in self._neighbor_metadata:
                    # TODO(piggy): Enhanced deciders should use this information.
                    decisions.append((True, neighbor_id))
                    continue
                decision = self.decide(neighbor_id=neighbor_id)
                decisions.append((decision, neighbor_id))

            log.info('node %s (%x) has decisions: %s', self._my_id, id(self), decisions)
            # Broadcast if any decider says to.
            if (self._distributed.communicator.strategy
                    == CommunicatorConfig.Strategies.BROADCAST.value):
                log.info('node %s (%x) is broadcasting with decisions.', self._my_id, id(self))
                self._send_broadcast_decisions(decisions=decisions)

            # Unicast to neighbors if a decider says to.
            elif (self._distributed.communicator.strategy
                    == CommunicatorConfig.Strategies.UNICAST.value):
                log.info('node %s (%x) is unicasting with decisions.', self._my_id, id(self))
                self._send_unicast_decisions(decisions=decisions)
            else:
                raise NotImplementedError(
                    'Have deciders, but unknown strategy: '
                    f'{self._distributed.communicator.strategy}')
        self._detect_convergence(state_changed=state_changed)

    @abc.abstractmethod
    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Fit the model to the data. This is the actual implementation of fit.'''

    def predict(self, dataset: Optional[Dataset], **kwargs) -> Optional[Dataset]:
        '''Apply model to input dataset to create output.

        This handles lock acquisition and generalized distributed work.
        '''

        log.info('node %s (%x) is predicting (%s).',
                 self._my_id,
                 id(self),
                 'no data' if dataset is None else 'with data')

        if not self._trained and not self._training:
            # As a convenience, wait 2 polling intervals to see if there is a fit
            #   request on the way.  We want to wait just over 1 polling
            #   interval, since that's how long it could take for a pending
            #   fit request to start training.
            time.sleep(self._distributed.polling_interval * 2)

            if not self._trained and not self._training:
                raise UntrainedError(
                    f'Algorithm "{self.catalog_name}" needs to be fit before it can predict')

        assert self._lock_predict_state is not None

        # On the first fit, we spin until we get a predict state.
        ok_to_proceed = False
        timeout = time.monotonic_ns() + self._distributed.predict_wait_for_fit_timeout_ns
        while not ok_to_proceed:
            if time.monotonic_ns() > timeout:
                raise UntrainedError(
                    f'Algorithm "{self.catalog_name}" ran out of time in predict waiting for fit')
            with self._lock_predict_state:
                if self._predict_state is not None:
                    ok_to_proceed = True
            time.sleep(self._distributed.polling_interval)

        with self._lock_predict_state:
            if dataset is not None:
                if self._is_empty(dataset):
                    log.info('Node %s encountered empty or malformed dataset on predict: \n%s\n',
                             self._my_id, dataset)
                else:
                    dataset = dataset.sorted_columns()
            retval = self._predict(dataset=dataset, my_state=self._predict_state, **kwargs)
            self._predict_counter += 1

        log.info('Node %s predictions: \n%s', self._my_id, retval)

        return retval

    @abc.abstractmethod
    def _predict(self, dataset: Optional[Dataset], **kwargs) -> Optional[Dataset]:
        '''Apply model to input dataset to create output.

        This handles model-speific work and does not handle general tasks.q
        '''
