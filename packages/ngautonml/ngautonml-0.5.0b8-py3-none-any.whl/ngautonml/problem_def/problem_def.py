'''Contains ProblemDefinition'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import json
import textwrap
from typing import Any, Dict, List, Optional, Set, Union

from aenum import Enum  # type: ignore[import-untyped]

from ..config_components.impl.config_component import (
    ConfigComponent, ConfigError, InvalidKeyError,
    MissingKeyError, ParsingErrors, ValidationErrors)
from ..config_components.impl.config_component_catalog import ConfigComponentCatalog
from ..config_components.impl.config_component_auto import ConfigComponentAuto
from ..wrangler.constants import ProblemDefKeys
from .aggregation_config import AggregationConfig, AggregationError
from .cross_validation_config import CrossValidationConfig
from .hyperparam_config import HyperparamConfig, HyperparamError
from .metric_config import MetricConfig, MetricConfigError
from .output_config import OutputConfig
from .problem_def_interface import ProblemDefInterface
from .task import Task

# pylint: disable=too-many-branches,too-many-statements


class ProblemDefinition(ProblemDefInterface):
    '''Represents information needed to define an AutoML run'''
    _catalog: Optional[ConfigComponentCatalog] = None
    _plugin_components: Dict[str, ConfigComponent]
    _task: Optional[Task] = None
    _aggregation_config: Optional[AggregationConfig] = None
    _cross_validation_config: Optional[CrossValidationConfig] = None
    _metric_configs: Optional[Dict[str, MetricConfig]] = None
    _hyperparam_config: Optional[HyperparamConfig] = None
    _output_config: Optional[OutputConfig] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_catalog']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._catalog = ConfigComponentAuto()

    def allowed_keys(self) -> Set[str]:
        '''Set of keys that are acceptable for this clause'''
        allowed = super().allowed_keys()
        allowed.update(self._plugin_components.keys())
        return allowed

    def required_keys(self) -> Set[str]:
        '''Subset of ALLOWED_KEYS that are required'''
        return {self.Keys.TASK.value, self.Keys.DATASET.value}   # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long

    def __init__(self,
                 clause: Union[str, Dict[str, Any]]):

        if self._catalog is None:
            self._catalog = ConfigComponentAuto()

        if isinstance(clause, str):
            clause = self._parse_json(pdef=clause)
        super().__init__(clause=remove_comments(clause))

        errors: List[ConfigError] = []

        self._plugin_components = {}

        for plugin_name, constructor in self._catalog.items():
            try:
                plugin_clause = self._get(plugin_name)
            except MissingKeyError:
                # We do not require all plugin clauses to be present.
                plugin_clause = {}

            try:
                # But we still want to instantiate the plugin so that we can use its validator.
                self._plugin_components[plugin_name] = (
                    constructor(clause=plugin_clause, problem_def=self))
            except ParsingErrors as err:
                errors.extend(err.errors)

        try:
            self._task = Task(self._get(
                ProblemDefKeys.TASK))
        except KeyError as err:
            errors.append(InvalidKeyError(err))

        try:
            self._cross_validation_config = CrossValidationConfig(self._get_with_default(
                ProblemDefKeys.CROSS_VALIDATION, dflt={}))
        except KeyError as err:
            errors.append(InvalidKeyError(err))

        try:
            metrics_clause = self._get_with_default(ProblemDefKeys.METRICS, dflt={})
            self._metric_configs = {name: MetricConfig(clause={name: info})
                                    for name, info in metrics_clause.items()}
        except MetricConfigError as err:
            errors.append(err)

        try:
            hyperparam_clause = self._get_with_default(ProblemDefKeys.HYPERPARAMS, dflt=[])
            self._hyperparam_config = HyperparamConfig(
                clause={ProblemDefKeys.HYPERPARAMS.value: hyperparam_clause})
        except HyperparamError as err:
            errors.extend(err.errors)

        try:
            output_clause = self._get_with_default(ProblemDefKeys.OUTPUT, dflt={})
            self._output_config = OutputConfig(output_clause)
            # TODO(piggy): Confirm that OutputConfig calls its own validate()
            # and drop this call.
            self._output_config.validate()
        except ValidationErrors as err:
            errors.extend(err.errors)

        try:
            aggregation_clause = self._get_with_default(ProblemDefKeys.AGGREGATION, dflt={})
            self._aggregation_config = AggregationConfig(aggregation_clause)
        except AggregationError as err:
            errors.extend(err.errors)

        try:
            # This is where we do validation between sections.
            self.validate()
        except ValidationErrors as err:
            errors.extend(err.errors)

        if len(errors) > 0:
            raise ValidationErrors(errors)

    def _parse_json(self, pdef: str) -> Dict[str, Any]:
        '''Attempts to interpret pdef as a JSON string or path to JSON file.

        If neither succeeds, raises ParsingErrors.
        '''
        errors: List[ConfigError] = []

        try:
            retval = json.loads(pdef)
            return retval
        except json.decoder.JSONDecodeError as err:
            errors.append(ConfigError(err))

        try:
            with open(pdef, 'r', encoding='utf8') as f:
                retval = json.load(f)
            return retval
        except FileNotFoundError as err:
            errors.append(ConfigError(err))
        except OSError as err:
            errors.append(ConfigError(err))
        except json.decoder.JSONDecodeError as err:
            errors.append(ConfigError(err))

        errors.insert(0, ConfigError(
            'String provided could not be parsed as JSON or path to JSON file.'))
        raise ParsingErrors(errors=errors)

    def __str__(self):
        return textwrap.dedent(f'''
            problem_type={self.task}
        ''')

    def validate(self, **kwargs) -> None:
        super().validate(**kwargs)  # all errors thrown by base class are fatal

        errors: List[ConfigError] = []

        try:
            self.task.validate()
        except ValidationErrors as err:
            # If task type is not provided, we cannot continue with validation
            raise err

        if self._metric_configs is not None:
            for metric_config in self._metric_configs.values():
                try:
                    metric_config.validate()
                except MetricConfigError as err:
                    errors.append(err)

        for component in self._plugin_components.values():
            try:
                component.validate(problem_def=self)
            except ValidationErrors as errs:
                errors.extend(errs.errors)

        if len(errors) > 0:
            raise ValidationErrors(errors)

    @property
    def task(self) -> Task:
        '''Explains what kind of problem we're solving.

        This affects the selection of pipeline templates and models.
        '''
        assert self._task is not None, (
            'BUG: attempt to access problem_type but it is None.')
        return self._task

    @property
    def metric_configs(self) -> Dict[str, MetricConfig]:
        '''Names and other information, if applicable, about all the metrics for this problem.

        If there are no metrics specified, will return an empty list, in which case the wrangler is
        responsible for using a default metric based on the problem type.
        '''
        assert self._metric_configs is not None, (
            'BUG: attempt to access metric_config but it is None.')
        return self._metric_configs

    @property
    def cross_validation_config(self) -> CrossValidationConfig:
        '''
        Get configuration information for cross-validation.
        '''
        assert self._cross_validation_config is not None, (
            'BUG: attempt to access cross_validation_config but it is None.'
        )

        return self._cross_validation_config

    @property
    def output(self) -> OutputConfig:
        '''All the configuration about things to output.'''
        assert self._output_config is not None, (
            'BUG: empty output session should be handled in constructor.'
        )
        return self._output_config

    @property
    def hyperparams(self) -> HyperparamConfig:
        '''Configuration for all hyperparam overrides.'''
        assert self._hyperparam_config is not None, (
            'BUG: self._hyperparam_config is supposed to be set in __init__().')
        return self._hyperparam_config

    @property
    def aggregation(self) -> AggregationConfig:
        '''Configuration for rank aggregation.

        The only valid entry is "method" which gives
        the catalog name of a rank aggregation method.
        See the top level "aggregators" directory.
        '''
        assert self._aggregation_config is not None, (
            'BUG: self._aggregation_config is supposed to be set in __init__().')
        return self._aggregation_config

    def get_conf(self, config_name: Union[str, Enum]) -> ConfigComponent:
        '''Get the plugin ConfigComponent for the config_name.'''
        if isinstance(config_name, Enum):
            config_name = config_name.value
        assert isinstance(config_name, str)
        return self._plugin_components[config_name]


def remove_comments(entry: Any) -> Any:
    '''Remove '_comments' fields from every dict inside an anonymous object.'''
    if isinstance(entry, dict):
        retval = {
            k: remove_comments(v)
            for k, v in entry.items()
            if k != '_comments'
        }
        return retval
    if isinstance(entry, list):
        return [remove_comments(v) for v in entry]
    return entry
