'''Available instantiators'''
from typing import Dict, Optional

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..executor.executor_kind import ExecutorKind
from ..executor.simple.simple_instantiator import SimpleInstantiator
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..wrangler.saver import Saver
from .executable_pipeline import ExecutablePipeline
from .instantiator import InstantiatorStub, Instantiator
from .json_instantiator import JsonInstantiator

# TODO(piggy): Maybe replace this with a catalog?
INSTANTIATORS = {
    ExecutorKind('json'): JsonInstantiator,
    ExecutorKind('stub_executor_kind'): InstantiatorStub,
    ExecutorKind('simple'): SimpleInstantiator,
}


class InstantiatorFactory():
    '''Factory class for pipeline instantiators'''
    _kind = None
    _saver: Optional[Saver]

    def __init__(self, saver: Optional[Saver] = None):
        self._saver = saver

    def build(self, kind: ExecutorKind) -> Instantiator:
        '''Build an instantiator of the requested kind.'''
        return INSTANTIATORS[kind](saver=self._saver)

    def instantiate(
        self,
        kind: ExecutorKind,
        pipeline: BoundPipeline
    ) -> ExecutablePipeline:
        '''Instantiate a single bound pipeline into a single kind of executable pipeline.

        Optionally instantiate the pipeline with the given trained models.
        '''
        return INSTANTIATORS[kind](saver=self._saver).instantiate(
            pipeline=pipeline)

    def instantiate_all(
        self,
        kind: ExecutorKind,
        pipelines: Dict[Designator, BoundPipeline]
    ) -> Dict[Designator, ExecutablePipeline]:
        '''Instantiate a dict of bound pipelines into a dict of executable pipelines,

        all of kind 'kind'.'''
        return INSTANTIATORS[kind](saver=self._saver).instantiate_all(
            pipelines=pipelines)
