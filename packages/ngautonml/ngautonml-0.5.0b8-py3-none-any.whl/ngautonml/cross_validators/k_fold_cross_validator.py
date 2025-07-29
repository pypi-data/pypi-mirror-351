'''Performs k-fold cross-validation.'''

# Copyright (c) 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=duplicate-code
from typing import Dict, List, Optional

import pandas as pd


from ..catalog.catalog import upcast
from ..executor.executor import Executor
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import (ExecutablePipeline,
                                                PipelineResult,
                                                PredictError)
from ..instantiator.instantiator_factory import InstantiatorFactory
from ..splitters.impl.splitter import SplitDataset
from ..tables.impl.table import TableFactory
from ..wrangler.dataset import Dataset, DatasetKeys
from .impl.cross_validator import CrossValidator, CrossValidatorCatalog


class KFoldCrossValidator(CrossValidator):
    '''Standard k-fold cross-validator.

    Works for single-fold validation as well
    '''

    _name = 'k_fold_cross_validator'

    def _concatenate_predictions(self,
                                 datasets: List[Optional[Dataset]]) -> Optional[Dataset]:
        '''Concatenate a list of fold prediction Datasets into a single Dataset
        that covers the entire train set.'''
        assert len(datasets) > 0, 'BUG: _concatenate() called when length of dataset list is 0'

        if any(dset is None for dset in datasets):
            return None

        assert datasets[0] is not None
        retval = datasets[0].output()

        errors: List[PredictError] = []
        for dset in datasets:
            assert dset is not None
            if DatasetKeys.ERROR.value in dset:
                errors.append(dset[DatasetKeys.ERROR.value])

        if len(errors) > 0:
            # handle errors
            error_text = 'Pipeline errors occurred during cross-validation: \n' + '\n'.join([
                str(error) for error in errors
            ])
            retval[DatasetKeys.ERROR.value] = PredictError(error_text)
            return retval

        retval.predictions_table = datasets[0].predictions_table
        for dset in datasets[1:]:
            assert dset is not None
            retval.predictions_table = TableFactory(
                pd.concat([retval.predictions_table.as_(pd.DataFrame),
                           dset.predictions_table.as_(pd.DataFrame)], axis=0, ignore_index=True))

        if DatasetKeys.PROBABILITIES.value in datasets[0]:
            dsets: List[pd.DataFrame] = []
            for dset in datasets:
                assert dset is not None
                dsets.append(dset.probabilities.as_(pd.DataFrame))  # type: ignore[attr-defined]
            probabilities_df = pd.concat(dsets, axis=0, ignore_index=True)
            retval.probabilities = TableFactory(probabilities_df)

        return retval

    def _concatenate_all(
            self,
            predictions: Dict[Designator,
                              List[Optional[Dataset]]]) -> Dict[Designator, Optional[Dataset]]:
        '''Concatenate each list of fold prediction Datasets into a single Dataset
        that covers the entire train set.'''
        retval: Dict[Designator, Optional[Dataset]] = {
            des: self._concatenate_predictions(data) for des, data in predictions.items()}
        return retval

    def validate_pipelines(self,
                           split_dataset: SplitDataset,
                           bound_pipelines: Dict[Designator, BoundPipeline],
                           instantiator: InstantiatorFactory,
                           executor: Executor,
                           **overrides
                           ) -> Dict[Designator, PipelineResult]:
        '''Do cross-validation by running pipelines on a split dataset.

        Returns the split dataset and an ExecutorResult for each pipeline.'''
        # For each fold, we will append that fold's predictions to the list of datasets for the
        # corresponding pipeline
        train_predictions: Dict[Designator, List[Optional[Dataset]]] = {
            des: [] for des in bound_pipelines}

        executable_pipelines: Dict[Designator, ExecutablePipeline] = {}

        for fold in split_dataset.folds:
            # Instantiate new executable pipelines for each bound pipeline
            # TODO(Piggy/Merritt): run this cross validator in parallel to take advantage of
            #       separate executable pipelines existing for each fold
            executable_pipelines = instantiator.instantiate_all(kind=executor.kind,
                                                                pipelines=bound_pipelines)
            # Fit all executable pipelines on this fold's train set
            executor.fit(dataset=fold.train, pipelines=executable_pipelines)
            # Predict with all executable pipelines on this fold's validate set
            fold_predictions = executor.predict(dataset=fold.validate,
                                                pipelines=executable_pipelines)

            # For each fold and pipeline, append that fold's predictions to that pipeline's
            # train_predictions
            for des, datasets in train_predictions.items():
                datasets.append(fold_predictions[des].prediction)

        # For each pipeline, concatenate its train predictions from a list of datsets into one
        # dataset
        train_predictions_concat = self._concatenate_all(predictions=train_predictions)

        retval: Dict[Designator, PipelineResult] = {
            des: PipelineResult(
                prediction=train_predictions_concat[des],
                bound_pipeline=bound_pipelines[des],
                split_dataset=split_dataset)
            for des in bound_pipelines}
        return retval


def register(catalog: CrossValidatorCatalog, *unused_args, **unused_kwargs) -> None:
    '''Register the cross-validator in the catalog.'''
    val = KFoldCrossValidator()
    catalog.register(val, val.name, upcast(val.tags))
