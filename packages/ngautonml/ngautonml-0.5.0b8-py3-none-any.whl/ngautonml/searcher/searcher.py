'''Searcher object.

This object sits between the Generator and the Instantiator.
It implements static searching algoritms (like grid search)
and does hyperparameter overriding (a trivial special case
of search).
'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
import logging
from typing import Any, Dict, List, Optional, Set

from frozendict import frozendict

from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..problem_def.hyperparam_config import HyperparamConfig
from ..templates.impl.pipeline_step import PipelineStep
from ..wrangler.constants import RangeMethod

from .frozen_overrides import FrozenOverrides
from .params import Overrides, ParamRanges
from .param_range import ParamRange


class Searcher(metaclass=abc.ABCMeta):
    '''Generate new BoundPipelines based on hyperparam search spaces.'''
    _overrides: Overrides
    _disable_grid_search: bool
    _inject: Optional[Dict[str, Any]]

    def __init__(
        self,
        hyperparams: HyperparamConfig,
        inject: Optional[Overrides] = None
    ):
        self._overrides = hyperparams.overrides.copy()
        self._overrides.extend(inject or [])
        self._disable_grid_search = hyperparams.disable_grid_search

    @abc.abstractmethod
    def bind_hyperparams(self, pipeline: BoundPipeline) -> Dict[Designator, BoundPipeline]:
        '''Bind new BoundPipelines with revised hyperparameters.'''

    def bind_all(self,
                 pipelines: Dict[Designator, BoundPipeline]) -> Dict[Designator, BoundPipeline]:
        '''Bind all the hyperparams for a set of BoundPipelines.'''
        retval: Dict[Designator, BoundPipeline] = {}
        for pipe in pipelines.values():
            retval.update(self.bind_hyperparams(pipe))
        return retval


class TrivialSearcher(Searcher):
    '''Just return the pipeline passed to us. Not really a searcher.'''
    def bind_hyperparams(self, pipeline: BoundPipeline) -> Dict[Designator, BoundPipeline]:
        return {
            pipeline.designator: pipeline
        }


class StepSet():
    '''Turn a step into a set of steps for all hyperparam bindings.'''

    # The key of _steps is optional because at initialization we
    # need to use None as a key.
    _steps: Dict[Optional[frozendict[str, str]], PipelineStep]
    _algorithm: Any  # Breaking circularity; really an Algorithm
    _pipeline_designator_component: str

    def __init__(self, step: PipelineStep):
        self._steps = {None: step}
        assert step.has_model(), (
            'BUG: attempt to bind hyperparams for step '
            f'({step.pipeline_designator_component}) with no algorithm')
        self._algorithm = step.model
        self._pipeline_designator_component = step.pipeline_designator_component

    def multiply(self,
                 hyperparam_name: str,
                 param_range: ParamRange,
                 no_show: Set[str]) -> 'StepSet':
        '''Expand the set of steps by the number of values in param.'''
        new_steps: Dict[Optional[frozendict[str, str]], PipelineStep] = {}
        for old_bindings, old_step in self._steps.items():
            bindings: Dict[str, Any] = self._algorithm.bind(
                hyperparam_name=hyperparam_name, param_range=param_range)
            for new_value_str, new_value in bindings.items():

                new_step = old_step.clone(**{hyperparam_name: new_value})
                assert new_step.filename is not None

                new_bindings: Optional[frozendict[str, str]] = frozendict()
                if hyperparam_name in no_show:
                    if old_bindings is not None:
                        new_bindings = old_bindings
                    else:
                        new_bindings = None
                else:
                    if old_bindings is None:
                        # step does not have any pre-existing overrides
                        new_bindings = frozendict({hyperparam_name: new_value_str})
                    else:
                        # step has preexisting overrides
                        new_bindings = old_bindings.set(hyperparam_name, new_value_str)  # type: ignore[attr-defined]  # pylint: disable=line-too-long

                new_steps[new_bindings] = new_step
        self._steps = new_steps
        return self

    @property
    def steps(self) -> Dict[Optional[FrozenOverrides], PipelineStep]:
        '''Render self as a dict of PipelineSteps.'''
        retval: Dict[Optional[FrozenOverrides], PipelineStep] = {}
        for bind, step in self._steps.items():
            if bind is None:
                retval[None] = step
                continue
            retval[FrozenOverrides({
                self._pipeline_designator_component: bind
            })] = step
        return retval


class PipelineBuilder():
    '''Build a set of pipelines by repeatedly adding a single Step or a StepSet.'''
    _pipename: str
    _steps: Optional[Dict[Optional[FrozenOverrides], List[PipelineStep]]]

    def __init__(self, pipename: str):
        self._pipename = pipename
        self._steps = None

    def append(self, step_set: StepSet) -> 'PipelineBuilder':
        '''Expand self._steps, adding each step from step_set to the end of each step list.

        If len(self._steps) is n, and len(step_set) is m, len(self._steps) will become m*n.
        '''
        if self._steps is None:
            self._steps = {key: [step] for key, step in step_set.steps.items()}
            return self
        new_steps: Dict[Optional[FrozenOverrides], List[PipelineStep]] = {}
        for old_frozen_overrides, old_steps in self._steps.items():
            for new_frozen_overrides, new_step in step_set.steps.items():

                if new_frozen_overrides is not None and old_frozen_overrides is not None:
                    updated_frozen_overrides = old_frozen_overrides.update(
                        new_frozen_overrides.thaw())
                elif new_frozen_overrides is not None:
                    updated_frozen_overrides = new_frozen_overrides
                elif old_frozen_overrides is not None:
                    updated_frozen_overrides = old_frozen_overrides
                else:
                    # Case: both None
                    updated_frozen_overrides = FrozenOverrides()

                new_steps[updated_frozen_overrides] = old_steps + [new_step]

        self._steps = new_steps
        return self

    def append_step(self, step: PipelineStep) -> 'PipelineBuilder':
        '''Add a single step to every step list in self._steps.

        (used for steps that don't match any selectors because they have no hyperparam overrides)
        '''
        if self._steps is None:
            self._steps = {None: [step]}
            return self
        for key in self._steps:
            self._steps[key].append(step)
        return self

    def build(self) -> Dict[Designator, BoundPipeline]:
        '''Render the final BoundPipelines from lists of steps.'''
        retval: Dict[Designator, BoundPipeline] = {}
        if self._steps is None:
            return retval
        for frozen_overrides, rev_steps in self._steps.items():
            new_pipeline = BoundPipeline.build(
                steps=list(reversed(rev_steps)),
                template_name=self._pipename,
                frozen_overrides=frozen_overrides)
            retval[new_pipeline.designator] = new_pipeline
        return retval


class SearcherImpl(Searcher):
    '''This is the default searcher.'''

    def bind_hyperparams(self, pipeline: BoundPipeline) -> Dict[Designator, BoundPipeline]:
        '''Bind this Searcher's hyperparam range(s) to the pipeline'''
        builder = PipelineBuilder(pipeline.name)
        for step in reversed(pipeline.steps):
            default_alg_ranges = ParamRanges(
                {k: p for k, p in step.hyperparams().items() if isinstance(p, ParamRange)}
            )
            overrides = Overrides(self._overrides)

            no_show: Set[str] = set()  # These are overrides that should not be used in names.
            params = default_alg_ranges.copy()
            for override in overrides:
                if override.selector.matches(step, pipeline):
                    logging.info('Matched: %s\n\tto step: %s\n\tin pipeline: %s\n',
                                 override,
                                 step.pipeline_designator_component,
                                 pipeline.designator)
                    params.update(override.params)
                if override.no_show:
                    no_show.update(override.params.keys())

            if len(params) > 0:
                step_set = StepSet(step)
                for hyperparam_name, param_range in params.items():
                    range_to_multiply = param_range
                    if self._disable_grid_search:
                        # Replace existing range with fixed range at default
                        range_to_multiply = ParamRange(
                            method=RangeMethod.FIXED,
                            prange=param_range.default)
                    step_set.multiply(hyperparam_name=hyperparam_name,
                                      param_range=range_to_multiply,
                                      no_show=no_show)

                builder.append(step_set)
            else:
                builder.append_step(step)

        return builder.build()
