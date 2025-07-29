'''Aggregator object class for configurable and user-made aggregators.'''
import abc

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Optional, Union

from ...catalog.catalog_element_mixin import CatalogElementMixin
from ...generator.designator import Designator
from ...instantiator.executable_pipeline import PipelineResults
from ...metrics.impl.metric import Metric, MetricStub
from ...ranker.ranker import Ranking, Rankings, RankingStub, ScoredResult
from ...wrangler.dataset import Dataset


class AggregatorError(Exception):
    '''Base error class for aggregators'''


class AggregatorNameError(AggregatorError):
    '''Aggregator lacks a proper indexing name.'''


class AggregatorAttributeError(AggregatorError):
    '''Aggregator is missing a required attribute.'''


class AggregatorInvalidDatasetError(AggregatorError):
    '''Aggregator was passed a dataset it cannot use.'''


class AggregatorInsufficientPipelines(AggregatorError):
    '''Aggregator requires more pipelines.'''


class Aggregator(Metric, CatalogElementMixin, metaclass=abc.ABCMeta):
    '''Base class wrapper for accessing Aggregator objects.'''
    _hyperparams: Optional[Dict[str, Any]] = None

    def __init__(self,
                 name: Optional[str] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 **overrides):
        super().__init__(name=name, tags=tags)
        if self._hyperparams is None:
            self._hyperparams = {}
        params = self._hyperparams.copy()
        params.update(overrides)
        self._hyperparams = params

    def __str__(self):
        return self.name

    @abc.abstractmethod
    def aggregate(self, rankings: Rankings, all_scores: bool = False) -> Ranking:
        '''Calculates the Aggregator results.'''

    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        '''Calculates the metric results.'''
        raise AggregatorError('calculate is not implemented for Aggregators')

    def hyperparams(self, **overrides) -> Dict[str, Any]:
        '''Get the hyperparameters for this aggregator.

        Arguments passed to this function override defaults for the aggregator.
        '''
        assert self._hyperparams is not None, (
            'BUG: Aggregator._hyperparams should be resolved in __init__.')
        hyperparams = self._hyperparams.copy()
        hyperparams.update(**overrides)
        return hyperparams


class AggregatorStub(Aggregator):
    '''This is a stub'''
    _name = 'stub_aggregator'
    _high = True

    def aggregate(self, rankings: Rankings, all_scores: bool = False) -> Ranking:
        return RankingStub(metric=MetricStub(self._name), results=PipelineResults())


class AggregatorRanking(Ranking):
    '''This is the Aggregator version of a Ranking.

    We pass the scores in at init time.
    '''

    def __init__(self, metric: Aggregator, results: PipelineResults,
                 scores: Union[Dict[Designator, int], str]):
        super().__init__(metric=metric, results=results)
        self._scores = []
        if isinstance(scores, str):
            self._scores = [ScoredResult(metric=metric, result=result, unscorable_reason=scores)
                            for result in results.values()]
        else:
            for des, ranking in scores.items():
                scored_result = ScoredResult(metric=metric, result=results[des], score=ranking)
                self._scores.append(scored_result)
            self._scores.sort(reverse=metric.high)

    def score(self) -> None:
        '''Scores are precalculated (do nothing).'''
