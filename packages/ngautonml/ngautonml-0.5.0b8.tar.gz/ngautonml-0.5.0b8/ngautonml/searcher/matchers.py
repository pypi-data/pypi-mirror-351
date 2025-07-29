'''Matcher functions'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Any, Dict, List

from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..templates.impl.pipeline_step import PipelineStep
from ..wrangler.constants import Matcher


class MatcherClass(metaclass=abc.ABCMeta):
    '''Matches a step or pipeline.

    args defines what this class matches
    matches(step, pipeline) returns True iff that step and pipeline match with args
    '''
    args: Any

    def __init__(self, args):
        self._args = args

    @abc.abstractmethod
    def matches(self, step: PipelineStep, pipeline: BoundPipeline) -> bool:
        '''Returns True iff step and pipeline match with this class's args'''


class AlgorithmMatcher(MatcherClass):
    '''Match by algorithm name.

    args is the algorithm name to match. This is the name of the algorithm
    associated with the step.
    '''
    _args: str

    def matches(self, step: PipelineStep, pipeline: BoundPipeline) -> bool:
        return step.has_model() and step.model_name == self._args


class DesignatorMatcher(MatcherClass):
    '''Match by designator.

    args is the designator to match.'''
    _args: Designator

    def matches(self, step: PipelineStep, pipeline: BoundPipeline) -> bool:
        designator = Designator(f'{pipeline.designator}')
        return designator == self._args


class NameMatcher(MatcherClass):
    '''Match by step name.

    args is the step name to match.'''
    _args: str

    def matches(self, step: PipelineStep, pipeline: BoundPipeline) -> bool:
        return step.pipeline_designator_component == self._args


class TagsMatcher(MatcherClass):
    '''Match by tags.

    args is the tag(s) to match

    matches() returns True iff at least one tag-value in args matches one of the
    corresponding tag-values on the algorithm in the pipeline step.
    '''

    _args: Dict[str, str]

    def matches(self, step: PipelineStep, pipeline: BoundPipeline) -> bool:
        tags = self._args
        if step.tags is None:
            # If the step has no model, it can not have tags and so can not match.
            return False
        submatches: List[bool] = []
        for tag_type, tag_value in tags.items():
            submatches.append(tag_type in step.tags and tag_value in step.tags[tag_type])
        return all(submatches)


_MATCHER_TABLE = {
    Matcher.ALGORITHM: AlgorithmMatcher,
    Matcher.DESIGNATOR: DesignatorMatcher,
    Matcher.NAME: NameMatcher,
    Matcher.TAGS: TagsMatcher,
}


class MatcherFactory:
    '''Select a matcher by Matcher'''
    def make(self, matcher: Matcher, args: Any) -> MatcherClass:
        '''Create a matcher class instance for the given matcher and args.'''
        # All of the classes in _MATCHER_TABLE define matches().
        return _MATCHER_TABLE[matcher](args)  # type: ignore[abstract]
