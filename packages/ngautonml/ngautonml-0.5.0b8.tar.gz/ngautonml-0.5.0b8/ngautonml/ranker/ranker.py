'''Ranks pipelines by using metrics to evauluate results'''
import abc
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..generator.bound_pipeline import BoundPipelineStub
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import PipelineResult, PipelineResults
from ..metrics.impl.metric import Metric, MetricInvalidDatasetError, MetricStub
from ..splitters.impl.splitter import SplitDataset
from ..wrangler.constants import OutputColName
from ..wrangler.dataset import Dataset, DatasetKeys

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


class RankerError(Exception):
    '''Base class for all errors related to Ranker'''


class ScoredResult():
    '''The results of running a single executable pipeline, with a score from a single metric'''
    _metric: Metric
    _result: PipelineResult
    _score: Optional[float]
    _unscorable_reason: Optional[str]

    def __init__(self,
                 metric: Metric,
                 result: PipelineResult,
                 score: Optional[float] = None,
                 unscorable_reason: Optional[str] = None):
        self._metric = metric
        self._result = result
        self._score = score
        self._unscorable_reason = unscorable_reason

    @property
    def pipeline_des(self) -> Designator:
        '''Designator for the pipeline that produced this ScoredResult'''
        return self._result.bound_pipeline.designator

    @property
    def family_des(self) -> Designator:
        '''Family Designator of the pipeline that produced this ScoredResult'''
        return self._result.bound_pipeline.family_designator

    @property
    def metric(self) -> Metric:
        '''Metric used to evaulate this score'''
        return self._metric

    @property
    def result(self) -> PipelineResult:
        '''PipelineResult used to evaulate this score'''
        return self._result

    @property
    def score(self) -> Optional[Union[float, str]]:
        '''A float representing this result's score,
        or a str explaining why it cannot be scored,
        or None if neither was provided.'''
        if self._score is not None:
            return self._score

        return self._unscorable_reason

    def __lt__(self, other: Any) -> bool:
        # a < b means "a is worse performance than b"
        if not isinstance(other, ScoredResult):
            raise NotImplementedError(
                '__lt__ for ScoredResult requires right-hand side to be a ScoredResult.\n'
                f'found: {other} of type {type(other)}.')

        if other._metric.name != self._metric.name:
            raise RankerError(
                'Cannot compare ScoredResults with differing metrics.\n'
                f'Left-hand side: {self._metric.name}'
                f'Right-hand side: {other._metric.name}')

        if other._score is None and self._score is None:
            # sort alphabetically by unscorable reason
            # (later in the alphabet = worse)
            self_reason = self._unscorable_reason or ""
            other_reason = other._unscorable_reason or ""
            return self_reason > other_reason

        if other._score is None:
            # scorable (self) > unscorable (other)
            return False

        if self._score is None:
            # unscorable (self) < scorable (other)
            return True

        if self._metric.high:
            return self._score < other._score

        return self._score > other._score

    def __str__(self) -> str:

        if self._score is None:
            if self._unscorable_reason is None:
                score_str = 'unscorable'
            else:
                score_str = f'unscorable ({self._unscorable_reason})'
        else:
            score_str = f'{self._score:.4f}'

        return (f'\tpipeline: {self._result.bound_pipeline!s}\n'
                f'\tscore: {score_str}')

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ScoredResult):
            return False
        return self._metric.name == other._metric.name and self._score == other._score


class Ranking:
    '''Holds the result of applying a single metric to multiple ExecutorResult.'''
    _metric: Metric
    _results: PipelineResults
    _scores: List[ScoredResult]
    _matriarch_scores: List[ScoredResult]
    _ground_truth: Optional[Dataset] = None

    def __init__(self,
                 metric: Metric,
                 results: PipelineResults,
                 ground_truth: Optional[Dataset] = None):
        self._metric = metric
        self._results = results
        self._scores = []  # List of ScoredResults, ordered from best to worst
        self._matriarch_scores = []
        self._ground_truth = ground_truth
        self.score()

    def __str__(self):
        retval = f'--{self._metric}--\n'
        for i, score in enumerate(self.scores()):
            retval = f'{retval}{i+1}:\n{score}\n'
        return retval

    @property
    def str_all_scores(self) -> str:
        '''Create a string representation of all scores.'''
        retval = f'--{self._metric}--\n'
        for i, score in enumerate(self.scores(all_scores=True)):
            retval = f'{retval}{i+1}:\n{score}\n'
        return retval

    def score(self) -> None:
        '''Calculate the scores of all results.'''
        self._scores = []
        family_designators = set()
        for res in self._results.values():
            family_designators.add(res.family_designator)
            if DatasetKeys.ERROR.value in (res.prediction or {}):
                assert res.prediction is not None, (
                    'BUG: prediction is None but error is somehow present.')
                self._scores.append(ScoredResult(
                    metric=self._metric,
                    result=res,
                    unscorable_reason=str(res.prediction[DatasetKeys.ERROR.value])
                ))
                continue
            try:
                if res.prediction is None:
                    raise MetricInvalidDatasetError('Prediction is None')
                score = self._metric.calculate(
                    pred=res.prediction,
                    ground_truth=self._ground_truth)
                scored_result = ScoredResult(
                    metric=self._metric,
                    result=res,
                    score=score)
            except MetricInvalidDatasetError as err:
                scored_result = ScoredResult(
                    metric=self._metric,
                    result=res,
                    unscorable_reason=str(err))
            self._scores.append(scored_result)

        # We want the best scores first
        # __lt__ on a ScoredResult is defined so that higher=better
        # Thus we always reverse (sort from high to low)
        self._scores.sort(reverse=True)

        # Pick out the highest scoring pipelines in each family,
        # the "matriarchs".
        for a_score in self._scores:
            if a_score.family_des in family_designators:
                self._matriarch_scores.append(a_score)
                family_designators.remove(a_score.family_des)

    @property
    def metric(self) -> Metric:
        '''The metric used to evaulate this Ranking'''
        return self._metric

    def scores(self, all_scores: bool = False) -> List[ScoredResult]:
        '''All ScoredResults, sorted from best to worst.'''
        if len(self._scores) != len(self._results):
            self.score()
        if all_scores:
            return self._scores
        return self._matriarch_scores

    def scores_as_dict(self, all_scores: bool = False) -> Dict[Designator, ScoredResult]:
        '''All ScoredResults, in a dict keyed by their pipeline's Designator.'''
        return {s.pipeline_des: s for s in self.scores(all_scores)}

    def as_dataframe(self, all_scores: bool = False) -> pd.DataFrame:
        '''Return ranking as a dataframe with 2 columns, pipeline designator and score.'''
        scores = self.scores(all_scores)
        retval = pd.DataFrame()
        retval[OutputColName.DESIGNATOR.value] = [str(s.pipeline_des) for s in scores]
        retval[self.metric.name] = [s.score for s in scores]
        return retval

    def best(self, num: int, all_scores: bool = False) -> List[ScoredResult]:
        '''Return best [num] ScoredResults, in order.'''
        if num < 0 or num > len(self.scores(all_scores=all_scores)):
            raise IndexError(
                f'Cannot get best {num} scores.  '
                f'Choose a number between 0 and {len(self.scores(all_scores=all_scores))}.')
        return self.scores(all_scores=all_scores)[:num]


class RankingStub(Ranking):
    '''stub'''

    def best(self, num: int, all_scores: bool = False) -> List[ScoredResult]:
        return [ScoredResult(
            metric=self._metric,
            result=PipelineResult(
                prediction=Dataset(),
                bound_pipeline=BoundPipelineStub(name='stub'),
                split_dataset=SplitDataset()),
            score=0.0)]


class Rankings(Dict[str, Ranking]):
    '''Dictionary of Rankings keyed by metric name.'''

    def __str__(self):
        summary = ['The rankings are:']
        for metric in sorted(self.keys()):
            summary.append(f'{self[metric]}')
        return '\n'.join(summary)

    def as_dataframe(self, order_metric: Optional[str] = None) -> pd.DataFrame:
        '''Return Rankings as a dataframe with columns for pipe designator and each metric.

        order_metric determines the order of pipelines in the output.
        If not provided, the first metric alphabetically will be used.
        '''
        metrics = sorted(self.keys())
        if order_metric is None:
            order_metric = metrics[0]
        retval = self[order_metric].as_dataframe().set_index(OutputColName.DESIGNATOR.value)
        for m in sorted(set(self.keys()) - {order_metric}):
            m_df = pd.DataFrame(self[m].as_dataframe())
            # Join additional metrics using designator as index, so that
            #   scores correspond to pipelines correctly.
            retval = retval.join(m_df.set_index(OutputColName.DESIGNATOR.value))
        # Change designator from index back to normal col
        retval.reset_index(inplace=True)
        return retval


class Ranker(metaclass=abc.ABCMeta):
    '''Base class for pipeline rankers'''

    def rank(self,
             results: PipelineResults,
             metrics: Dict[str, Metric],
             ground_truth: Optional[Dataset] = None) -> Rankings:
        '''Rank the results of a run of the executor using one or multiple metrics'''
        return Rankings({k: Ranking(v, results, ground_truth) for k, v in metrics.items()})


class RankerStub(Ranker):
    '''stub'''

    def rank(self,
             results: PipelineResults,
             metrics: Dict[str, Metric],
             ground_truth: Optional[Dataset] = None) -> Rankings:
        return Rankings({'stub metric': Ranking(
            metric=MetricStub(),
            results=PipelineResults({
                Designator('stub_designator'): PipelineResult(
                    prediction=Dataset(),
                    bound_pipeline=BoundPipelineStub(name='stub'),
                    split_dataset=SplitDataset()
                )
            })
        )})
