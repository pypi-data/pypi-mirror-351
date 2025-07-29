'''Base class for Boolean deciders.'''
# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Mapping, Optional

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..algorithms.impl.neighbor_metadata_interface import NeighborMetadataInterface
from ..config_components.distributed_config import DeciderConfig, DecidersConfig
from ..neighbor_manager.node_id import NodeID

from .impl.decider import Decider
from .impl.decider_catalog import DeciderCatalog
from .impl.decider_auto import DeciderCatalogAuto


class BooleanDeciderConfig(DeciderConfig, metaclass=abc.ABCMeta):
    '''Configuration for BooleanDecider.'''

    def __init__(self, name: str, clause: dict) -> None:
        super().__init__(name=name, clause=clause)

    def __str__(self) -> str:
        return f'boolean({",".join([str(c) for c in self._clause])})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BooleanDeciderConfig):
            return False
        return all(self._clause[decider] == other._clause[decider] for decider in self._clause)

    class Keys(AEnum):
        '''Keys for the clause.'''
        ENABLED = 'enabled'

    @property
    def subdeciders(self) -> Dict[str, DeciderConfig]:
        '''Return the subdeciders.'''
        return DecidersConfig(self._clause).decider_configs


class BooleanDecider(Decider, metaclass=abc.ABCMeta):
    '''Decider that decides True if all subdeciders decide True.'''
    name = 'boolean'
    tags = {}
    _config: BooleanDeciderConfig
    _subdeciders: Dict[str, Decider]

    def __init__(self,
                 name: Optional[str] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 config: Optional[DeciderConfig] = None,
                 catalog: Optional[DeciderCatalog] = None
                 ) -> None:
        super().__init__(name=name, tags=tags, config=config)
        if catalog is None:
            catalog = DeciderCatalogAuto()
        self._catalog = catalog
        self._subdeciders = {}
        for decider, clause in self._config.subdeciders.items():
            subdecider = self._catalog.lookup_by_name(decider)(config=clause)
            self._subdeciders[decider] = subdecider

    def _all_decisions(
            self,
            my_meta: NeighborMetadataInterface,
            neighbor_id: NodeID,
            neighbors: Mapping[NodeID, NeighborMetadataInterface]) -> List[bool]:
        '''All the decisions for this operator.'''
        return [decider.decide(my_meta=my_meta, neighbor_id=neighbor_id, neighbors=neighbors)
                for decider in self._subdeciders.values()]


def register(catalog: DeciderCatalog) -> None:
    '''There are no catalog objects in this file.'''
    _ = catalog
