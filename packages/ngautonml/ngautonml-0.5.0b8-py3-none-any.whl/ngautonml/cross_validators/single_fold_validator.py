'''Uses a single train/test split and only produces predictions for test split.

Does not do true cross-validation.
'''
# pylint: disable=too-many-arguments,unused-argument

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict

from ..catalog.catalog import upcast
from ..executor.executor import ExecutablePipeline, Executor
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import PipelineResult
from ..instantiator.instantiator_factory import InstantiatorFactory
from ..splitters.impl.splitter import SplitDataset
from .impl.cross_validator import CrossValidator, CrossValidatorCatalog


class SingleFoldValidator(CrossValidator):
    '''Uses a single train/test split and only produces predictions for test split.'''

    _name = 'single_fold_validator'
    _tags = None

    def validate_pipelines(self,
                           split_dataset: SplitDataset,
                           bound_pipelines: Dict[Designator, BoundPipeline],
                           instantiator: InstantiatorFactory,
                           executor: Executor,
                           **overrides
                           ) -> Dict[Designator, PipelineResult]:
        '''Uses a single train/test split and only produces predictions for test split.'''

        assert len(split_dataset.folds) == 1, (
            f'BUG: SingleFoldValidator got split dataset with {len(split_dataset)} folds.  '
            'Exactly one fold required.'
        )

        executable_pipelines: Dict[Designator, ExecutablePipeline] = {}
        for designation, pipe in bound_pipelines.items():
            instance = instantiator.instantiate(
                kind=executor.kind,
                pipeline=pipe)
            executable_pipelines[designation] = instance

        executor.fit(split_dataset.folds[0].train, executable_pipelines)
        print('Fit all pipelines.')

        train_predictions = executor.predict(
            dataset=split_dataset.folds[0].validate,
            pipelines=executable_pipelines)
        print(f'Got predictions for {len(train_predictions)} pipelines.')

        retval = {
            des: PipelineResult(
                prediction=train_predictions[des].prediction,
                bound_pipeline=pipe,
                split_dataset=split_dataset)
            for des, pipe in bound_pipelines.items()}
        return retval


def register(catalog: CrossValidatorCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    val = SingleFoldValidator()
    catalog.register(val, val.name, upcast(val.tags))
