'''Metric configuration'''
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..config_components.impl.config_component import ConfigComponent, ConfigError


class MetricConfigError(ConfigError):
    '''Base error for MetricConfig.'''


class MetricConfig(ConfigComponent):
    '''Configured metrics'''
    _catalog_name: Optional[str] = None

    class Constants(Enum):
        '''Constants below and above top level.'''
        CATALOG_NAME = 'catalog_name'
        METRICS = 'metrics'

    def __init__(self, clause: Dict[str, Any], parents: Optional[List[str]] = None):
        parents = self._add_parent(parents, self.Constants.METRICS.value)
        super().__init__(clause=clause, parents=parents)

    def validate(self, **kwargs) -> None:
        '''Throw a MetricConfigError if the metric clause is invalid'''
        errors: List[MetricConfigError] = []

        if len(self._clause.keys()) != 1:
            errors.append(MetricConfigError(
                'Metric clause must have exactly 1 key;'
                f'found {len(self._clause.keys())} ({self._clause.keys()})'
            ))

        try:
            # These are all run to make sure they generate no errors.
            self.name  # pylint: disable=pointless-statement
            self.hyperparams  # pylint: disable=pointless-statement
            self.catalog_name  # pylint: disable=pointless-statement
        except AssertionError as err:
            errors.append(MetricConfigError(str(err)))

        if len(errors) > 0:
            raise MetricConfigError(errors)

    def allowed_keys(self) -> Set[str]:
        return set(self._clause.keys())

    @property
    def name(self) -> str:
        '''The instance name for this metric.'''
        return list(self._clause.keys())[0]

    @property
    def hyperparams(self) -> Dict[str, Any]:
        '''The hyperparams for this metric.

        If you want more than one instance of a single metric
        with different hyperparams, define each with its own
        name and use the 'catalog_name' to specify the metric
        in the catalog to use.
        '''
        retval = dict(list(self._clause.values())[0])
        if self.Constants.CATALOG_NAME.value in retval:
            del retval[self.Constants.CATALOG_NAME.value]
        return retval

    @property
    def catalog_name(self) -> str:
        '''The metric catalog name for this metric.

        We can have different metric entries with the same catalog_name,
        but different hyperparams.

        Defaults to self.name.
        '''
        metric_info: Dict[str, Any] = list(self._clause.values())[0]
        retval = metric_info.get(self.Constants.CATALOG_NAME.value, self.name)
        assert isinstance(retval, str), f'catalog_name must be a str, not a {type(retval)}'
        return retval
