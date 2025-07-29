'''Specifies  a distributed AI setting.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..neighbor_manager.node_id import NodeID
from ..wrangler.constants import Defaults

from .impl.config_component import (
    ConfigComponent, ConfigError, InvalidValueError, ValidationErrors)
from .impl.config_component_catalog import ConfigComponentCatalog


class SplitConfig(ConfigComponent):
    '''Specifies how to split data for simulations.'''

    @property
    def seed(self) -> int:
        '''Seed for random number generation.'''
        return self._get_with_default('seed', dflt=Defaults.SEED)

    @property
    def num_nodes(self) -> int:
        '''The number of nodes in the system.'''
        return self._get('num_nodes')


class DeciderConfig(ConfigComponent):
    '''Specifies configuration for a single decider.'''
    _name = 'decider'
    tags: Dict[str, Any] = {}

    def __init__(self, name: str, clause: Dict[str, Any]) -> None:
        self._name = name
        super().__init__(clause)

    class Keys(AEnum):
        '''Valid keys for the top level or DeciderConfig.'''
        ENABLED = 'enabled'

    def required_keys(self) -> Set[str]:
        return set()

    @property
    def name(self) -> str:
        '''Name of the decider.'''
        return self._name

    @property
    def enabled(self) -> bool:
        '''Is the decider enabled?'''
        return self._get_with_default('enabled', dflt=True)


class DecidersConfig(ConfigComponent):
    '''Specifies configuration for all deciders.'''

    def __init__(self, clause: Dict[str, Any]) -> None:
        super().__init__(clause)

    @property
    def decider_configs(self) -> Dict[str, DeciderConfig]:
        '''Get all decider configurations.'''
        return {name: getattr(self, name) for name in self._clause.keys()}

    def required_keys(self) -> Set[str]:
        return set()


class CommunicatorConfig(ConfigComponent):
    '''Specifies configuration for a communicator.'''
    _my_id: NodeID

    def __init__(self, clause: Dict[str, Any], my_id: NodeID, **kwargs) -> None:
        super().__init__(clause=clause, my_id=my_id, **kwargs)
        self._my_id = my_id

    class Constants(Enum):
        '''Keys below the top level.'''
        NAME = 'name'
        STRATEGY = 'strategy'

    class Strategies(Enum):
        '''Strategies for the communicator.'''
        BROADCAST = 'broadcast'  # All messages go to all neighbors.
        UNICAST = 'unicast'  # Messages only go to qualifying neighbors.

    class Defaults(Enum):
        '''Default values'''
        COMMUNICATOR = 'memory'
        STRATEGY = 'broadcast'

    @property
    def name(self) -> str:
        '''Name of the communicator.

        Options include 'memory', 'sockets', and 'kafka'.
        '''
        return self._get_with_default(self.Constants.NAME, dflt=self.Defaults.COMMUNICATOR.value)

    @property
    def strategy(self) -> str:
        '''Strategy for the communicator.'''
        return self._get_with_default(self.Constants.STRATEGY, dflt=self.Defaults.STRATEGY.value)


class DropperConfig(ConfigComponent):
    '''Specifies configuration for packet dropper.'''
    name = 'dropper'
    tags: Dict[str, Any] = {}

    class Constants(Enum):
        '''Keys below the top level.'''

    class Keys(AEnum):
        '''Valid keys for the top level of DropperConfig.'''
        DROP_RATE = 'drop_rate'
        OUTPUT_DIR = 'output_dir'
        SEED = 'seed'

    def required_keys(self) -> Set[str]:
        return {
            self.Keys.DROP_RATE.value,  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        }

    @property
    def drop_rate(self) -> float:
        '''Probability of dropping a packet.'''
        return float(self._get_with_default(self.Keys.DROP_RATE, dflt=0.0))

    @property
    def seed(self) -> int:
        '''Seed for random number generation.'''
        return self._get_with_default('seed', dflt=Defaults.SEED)

    @property
    def output_dir(self) -> Optional[Path]:
        '''The number of nodes in the system.'''
        retval = self._get_with_default(self.Keys.OUTPUT_DIR, dflt=None)
        return Path(retval) if retval is not None else None


class DistributedConfig(ConfigComponent):
    '''Specifies distributed configration in a distributed AI setting.'''
    name = 'distributed'
    tags: Dict[str, Any] = {}

    class Constants(Enum):
        '''Keys below the top level.'''
        NAME = 'name'
        # Discoverers
        STATIC = 'static'  # Static neighbor configuration
        ADJACENCY = 'adjacency'
        EDGES = 'edges'
        DYNAMIC = 'dynamic'  # Simple dynamic neighbor configuration
        # Subitems
        NODES_AND_ENDPOINTS = 'nodes_and_endpoints'
        # Regularization
        WEIGHT_MATRIX = 'weight_matrix'

    class Defaults(Enum):
        '''Default values'''
        DISCOVERER = 'dynamic'
        POLLING_INTERVAL = '0.1'
        FIT_EPS = '0.0000001'
        REGULARIZATION = 'function_space'
        PWFF_TIMEOUT = '60.000000000'  # seconds
        ONLY_SEND_PERIODICALLY = False
        CONVERGENCE_TIME_NS = 1000000000  # 1 second

    class Keys(AEnum):
        '''Valid keys for the top level DistributedConfig.'''
        COMMUNICATOR = 'communicator'  # Config for the communicator to use
        DISCOVERER = 'discoverer'  # Config for the discoverer to use
        DECIDER = 'decider'  # Config for the decider to use
        DROPPER = 'dropper'  # Configuration for packet dropper
        FIT_EPS = 'fit_eps'  # Minimum change in model before sending to neighbors
        MY_ID = 'my_id'  # ID of the current node
        PIPELINES = 'pipelines'  # Clause of pipeline loaders
        POLLING_INTERVAL = 'polling_interval'  # Time for models to wait between refitting
        PWFF_TIMEOUT = 'predict_wait_for_fit_timeout'  # TO predict() to wait for fit() to complete
        REGULARIZATION = 'regularization'  # Info about nieghbor regularization
        SPLIT = 'split'  # Info about splitting of the data for simulations
        ONLY_SEND_PERIODICALLY = 'only_send_periodically'
        CONVERGENCE_TIME_NS = 'convergence_time_ns'

    def required_keys(self) -> Set[str]:
        return {
            self.Keys.DISCOVERER.value,  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
            self.Keys.COMMUNICATOR.value  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        }

    def get_static_adjacency(self, my_id: NodeID) -> Optional[List[NodeID]]:
        '''If we have a static config, get the list of my_id's neighbors.

        Returns None if there is no static config.
        '''
        if not self._exists(self.Keys.DISCOVERER, self.Constants.STATIC):
            return None
        if self._get(self.Keys.DISCOVERER, self.Constants.NAME) != self.Constants.STATIC.value:
            return None
        if self._exists(self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.ADJACENCY):
            my_neighbors: List[int] = self._get(
                self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.ADJACENCY, str(my_id))
            return [NodeID(n) for n in sorted(my_neighbors)]
        if self._exists(self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.EDGES):
            retval = set()
            for edge in self._get(
                self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.EDGES
            ):
                if edge[0] == int(my_id):
                    retval.add(edge[1])
                if edge[1] == int(my_id):
                    retval.add(edge[0])
            return [NodeID(n) for n in sorted(retval)]
        raise NotImplementedError(
            f'unrecognized static clause(s): '
            f'{self._get(self.Keys.DISCOVERER, self.Constants.STATIC).keys()}')

    def get_adjacency(self) -> Optional[Dict[NodeID, List[NodeID]]]:
        '''If we have a static config, get full adjacency of the network.

        Returns None if there is no static config.
        '''
        if not self._exists(self.Keys.DISCOVERER, self.Constants.STATIC):
            return None
        if self._get(self.Keys.DISCOVERER, self.Constants.NAME) != self.Constants.STATIC.value:
            return None
        if self._exists(self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.ADJACENCY):
            adjacency = self._get(
                self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.ADJACENCY)
            return {NodeID(int(k)): [NodeID(n) for n in v] for k, v in adjacency.items()}
        if self._exists(self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.EDGES):
            edges = self._get(
                self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.EDGES)
            retval: Dict[NodeID, List[NodeID]] = {}
            for edge in edges:
                if edge[0] not in retval:
                    retval[edge[0]] = []
                if edge[1] not in retval:
                    retval[edge[1]] = []
                retval[edge[0]].append(edge[1])
                retval[edge[1]].append(edge[0])
            return {NodeID(int(k)): [NodeID(n) for n in v] for k, v in retval.items()}
        raise NotImplementedError(
            f'unrecognized static clause(s): '
            f'{self._get(self.Keys.DISCOVERER, self.Constants.STATIC).keys()}')

    def validate(self, **kwargs: Any) -> None:
        errors: List[ConfigError] = []

        if self._exists(self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.EDGES):
            edges = self._get(
                self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.EDGES)
            if not isinstance(edges, list):
                raise ValidationErrors([InvalidValueError(
                    f'edges must be a list, instead found {edges} of type {type(edges)}')])
            for edge in self._get(
                self.Keys.DISCOVERER, self.Constants.STATIC, self.Constants.EDGES
            ):
                if len(edge) != 2:
                    errors.append(InvalidValueError(
                        f'Edge {edge} does not have exactly two elements.'))

        if len(errors) > 0:
            raise ValidationErrors(errors=errors)

    @property
    def fit_eps(self) -> float:
        '''Minimum change in model before sending to neighbors.'''
        return float(self._get_with_default(
            self.Keys.FIT_EPS, dflt=self.Defaults.FIT_EPS.value))

    @property
    def polling_interval(self) -> float:
        '''Time for models to wait between refitting in seconds, float.'''
        return float(self._get_with_default(
            self.Keys.POLLING_INTERVAL, dflt=self.Defaults.POLLING_INTERVAL.value))

    @property
    def decider(self) -> DecidersConfig:
        '''Configuration for the deciders.'''
        return DecidersConfig(clause=self._get_with_default(
            self.Keys.DECIDER, dflt={}))

    @property
    def no_deciders(self) -> bool:
        '''Are there no enabled deciders?'''
        for decider in self.decider.decider_configs.values():
            if decider.enabled:
                return False
        return True

    @property
    def discoverer(self) -> str:
        '''Which discoverer should we use?

        Options include 'static' and 'dynamic'.
        '''
        return self._get_with_default(
            self.Keys.DISCOVERER, self.Constants.NAME, dflt=self.Defaults.DISCOVERER.value)

    @property
    def communicator(self) -> CommunicatorConfig:
        '''Configuration for the communicator.'''
        return CommunicatorConfig(clause=self._get_with_default(self.Keys.COMMUNICATOR, dflt={}),
                                  my_id=self.my_id)

    @property
    def dropper(self) -> Optional[DropperConfig]:
        '''Configuration for packet dropper.'''
        clause = self._get_with_default(self.Keys.DROPPER, dflt=None)
        return DropperConfig(clause) if clause is not None else None

    @property
    def split(self) -> Optional[SplitConfig]:
        '''Info about splitting of the data for simulations.'''
        clause = self._get_with_default(self.Keys.SPLIT, dflt=None)
        if clause is None:
            return None
        assert isinstance(clause, dict), (
            f'BUG: expected a dict at {self.Keys.SPLIT}, instead found {type(clause)}'
        )

        return SplitConfig(clause)

    @property
    def my_id(self) -> NodeID:
        '''Node ID for the current node.'''
        # TODO(Piggy): rewrite this, injecting my_id from the command line.
        return self._get_with_default(self.Keys.MY_ID, dflt=NodeID(1))

    @my_id.setter
    def my_id(self, value: NodeID) -> None:
        '''Set the node ID for the current node.'''
        self._clause[self.Keys.MY_ID.value] = value  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long

    @property
    def only_send_periodically(self) -> bool:
        '''If true, we do not consider sending on every fit.'''
        return self._get_with_default(
            self.Keys.ONLY_SEND_PERIODICALLY, dflt=self.Defaults.ONLY_SEND_PERIODICALLY.value)

    @property
    def pipelines(self) -> Dict[str, List[Any]]:
        '''List of pipeline loaders to use.'''
        return self._get_with_default(self.Keys.PIPELINES, dflt={})

    @property
    def regularization_type(self) -> str:
        '''Type of neighbor regularization'''
        return self._get_with_default(self.Keys.REGULARIZATION, self.Constants.NAME,
                                      dflt=self.Defaults.REGULARIZATION)

    @property
    def neighbor_weights(self) -> Dict[NodeID, float]:
        '''Weights for neighbors, if used in regularization.'''
        # TODO(merritt): relies on node IDs starting at 0
        matrix = self._get_with_default(self.Keys.REGULARIZATION, self.Constants.WEIGHT_MATRIX,
                                        dflt=None)
        if matrix is None:
            return {}

        row = matrix[int(self.my_id)]
        return {NodeID(i): weight for i, weight in enumerate(row)}

    @property
    def predict_wait_for_fit_timeout_ns(self) -> int:
        '''How long should predict() wait for fit() to complete?  (In nanoseconds)'''
        pwff_s = float(self._get_with_default(self.Keys.PWFF_TIMEOUT,
                                              dflt=self.Defaults.PWFF_TIMEOUT.value))
        return int(1000000000 * pwff_s)

    @property
    def convergence_time_ns(self) -> int:
        '''How long should we wait for convergence?  (In nanoseconds)'''
        return int(self._get_with_default(self.Keys.CONVERGENCE_TIME_NS,
                                          dflt=self.Defaults.CONVERGENCE_TIME_NS.value))


def register(catalog: ConfigComponentCatalog) -> None:
    '''Register all the objects in this file.'''
    catalog.register(DistributedConfig)
