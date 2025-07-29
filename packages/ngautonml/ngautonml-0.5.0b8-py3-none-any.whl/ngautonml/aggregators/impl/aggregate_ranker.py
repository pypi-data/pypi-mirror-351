''''Wrap up the primary operations of rank aggregation.'''

from typing import Any, Dict, List

from ...instantiator.executable_pipeline import PipelineResults
from ...ranker.ranker import Ranking, Rankings

from .aggregator import AggregatorRanking, Aggregator


class AggregateRanker():
    '''Wrap up the primary operations of rank aggregation.'''
    _methods: List[Aggregator]
    _rankings: Rankings
    _results: PipelineResults

    def __init__(
            self,
            methods: List[Aggregator],
            rankings: Rankings,
            results: PipelineResults,
            **overrides: Any):
        self._methods = methods
        self._rankings = rankings
        self._results = results
        self._hyperparams = overrides

    def __call__(self) -> Dict[str, Ranking]:
        '''Testable component for rankings.'''
        new_rankings: Dict[str, Ranking] = {}
        for aggregation_method in self._methods:
            try:
                agg_ranking = aggregation_method.aggregate(self._rankings, **self._hyperparams)
            except Exception as err:  # pylint: disable=broad-exception-caught
                agg_ranking = AggregatorRanking(
                    metric=aggregation_method,
                    results=self._results,
                    scores=str(err))
            new_rankings[agg_ranking.metric.name] = agg_ranking
        return new_rankings
