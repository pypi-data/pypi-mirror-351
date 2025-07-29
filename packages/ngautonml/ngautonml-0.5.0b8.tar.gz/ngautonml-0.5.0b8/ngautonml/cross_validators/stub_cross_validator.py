'''Stub cross-validator does nothing'''
# pylint: disable=duplicate-code,unused-argument,too-many-arguments
from typing import Dict

from ..catalog.catalog import upcast
from ..executor.executor import Executor
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import PipelineResult
from ..instantiator.instantiator_factory import InstantiatorFactory
from ..splitters.impl.splitter import SplitDataset
from ..wrangler.dataset import Dataset
from .impl.cross_validator import CrossValidator, CrossValidatorCatalog

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


class StubCrossValidator(CrossValidator):
    '''Stub cross-validator does nothing'''

    _name = 'stub_cross_validator'
    _tags = {
        'some_key': ['some_value'],
    }

    def validate_pipelines(self,
                           split_dataset: SplitDataset,
                           bound_pipelines: Dict[Designator, BoundPipeline],
                           instantiator: InstantiatorFactory,
                           executor: Executor,
                           **overrides
                           ) -> Dict[Designator, PipelineResult]:
        '''Stub cross-validator does nothing'''
        retval = {
            des: PipelineResult(
                prediction=Dataset(),
                bound_pipeline=pipe,
                split_dataset=split_dataset)
            for des, pipe in bound_pipelines.items()}
        return retval


def register(catalog: CrossValidatorCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    val = StubCrossValidator()
    catalog.register(val, val.name, upcast(val.tags))
