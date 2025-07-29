"""The wrangler is the central control object for all of AutonML."""

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=too-many-instance-attributes,too-many-arguments

from typing import Dict, Optional

from ..aggregators.impl.aggregate_ranker import AggregateRanker
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import (ExecutablePipeline,
                                                PipelineResult,
                                                PipelineResults)
from ..templates.impl.pipeline_template import PipelineTemplate

from .dataset import Dataset
from .logger import Level, Logger
from .wrangler_base import WranglerBase
from .wrangler_result import WranglerResult

log = Logger(__file__, level=Level.ERROR).logger()


class Wrangler(WranglerBase):
    '''The wrangler is the central control object for all of AutonML.'''

    def lookup_templates(self) -> Dict[str, PipelineTemplate]:
        '''Look up the templates that match the problem definition.'''
        task = self._pd.task
        data_type = "None"
        if task.data_type is not None:
            data_type = task.data_type.name
        task_type = "None"
        if task.task_type is not None:
            task_type = task.task_type.name

        return self._template_catalog.lookup_by_both(
            data_type=[data_type], task=[task_type])

    def train_all_results(self,
                          results: PipelineResults,
                          dataset: Dataset) -> PipelineResults:
        '''Instantiate and train all pipelines in results.

        Note that we do NOT calculate new predictions.
        '''
        retval = PipelineResults()
        pipelines: Dict[Designator, ExecutablePipeline] = {}

        for des, result in results.items():
            pipelines[des] = self._instantiator_factory.instantiate(
                kind=self._executor.kind,
                pipeline=result.bound_pipeline)

        self._executor.fit(
            dataset=dataset,
            pipelines=pipelines)

        for des, pipe in pipelines.items():
            retval[des] = PipelineResult(
                prediction=results[des].prediction,
                split_dataset=results[des].split_dataset,
                executable_pipeline=pipe)

        return retval

    def _predict_test_data(self,
                           executable_pipelines: Dict[Designator, ExecutablePipeline]
                           ) -> Optional[PipelineResults]:
        '''Run the executor again on test data to get test predictions,
            if test data is supplied in the problem definition.

        (Currently runs all pipelines, may eventually run x best ones)'''
        assert self._bound_pipelines is not None, (
            'BUG: wrangle_test() called with no bound pipelines.')

        test_dataset = self.load_test_dataset()

        if test_dataset is None:
            return None

        test_predictions = self._executor.predict(
            dataset=test_dataset,
            pipelines=executable_pipelines)
        return PipelineResults(test_predictions)

    def fit_predict_rank(self) -> WranglerResult:
        '''Do all the autoML things.'''
        train_dataset = self.load_train_dataset()

        self._bound_pipelines = self._build_pipelines()

        task = self._pd.task
        assert task.task_type is not None, (
            'BUG: missing task should have been caught in validation.')
        splitters = self._splitter_catalog.lookup_by_tag_and(**{
            'task': task.task_type.name,
            'data_type': task.data_type.name,
        })
        if not splitters:
            splitters = self._splitter_catalog.lookup_by_tag_and(**{
                'default': 'true'
            })
        assert len(splitters) == 1, f'BUG: More than one splitter returned for {task}: {splitters}'
        splitter = list(splitters.values())[0]

        assert train_dataset is not None
        split_data = splitter.split(
            dataset=train_dataset,
            **self._pd.cross_validation_config.splitter_hyperparams
        )
        log.info('Split dataset into %d folds.', len(split_data.folds))
        print(f'Split dataset into {len(split_data.folds)} folds.')

        cross_validator = self._validator_catalog.lookup_by_name('k_fold_cross_validator')
        cross_validator_results = PipelineResults(cross_validator.validate_pipelines(
            split_dataset=split_data,
            bound_pipelines=self._bound_pipelines,
            instantiator=self._instantiator_factory,
            executor=self._executor))

        metrics = self._metric_catalog.lookup_metrics(self._pd)
        print(f'Got {len(metrics)} metrics.')
        rankings = self._ranker.rank(
            results=cross_validator_results,
            metrics=metrics,
            ground_truth=split_data.ground_truth)
        log.info('Rankings: %s', [str(rank) for rank in rankings])

        methods = [self._aggregator_catalog.lookup_by_name(method)
                   for method in self._pd.aggregation.method]
        new_rankings = AggregateRanker(methods=methods,
                                       rankings=rankings,
                                       results=cross_validator_results)()
        rankings.update(new_rankings)
        print(f'Added {len(new_rankings)} aggregate rankings.')

        train_results = self.train_all_results(
            results=cross_validator_results,
            dataset=train_dataset)

        if self._all_executable_pipelines is None:
            self._all_executable_pipelines = train_results.executable_pipelines
            self._current_executable_pipelines = self._all_executable_pipelines

        if self._saver is not None:
            self.save(train_results)

        test_results = self._predict_test_data(train_results.executable_pipelines)

        return WranglerResult(
            split_dataset=split_data,
            train_results=train_results,
            test_results=test_results,
            rankings=rankings)
