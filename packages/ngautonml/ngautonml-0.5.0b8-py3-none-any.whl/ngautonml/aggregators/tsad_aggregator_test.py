'''Test the TSAD aggregators'''

from typing import Optional

import pytest

from ..generator.bound_pipeline import BoundPipelineStub
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import PipelineResult, PipelineResults
from ..metrics.impl.metric import Metric, MetricStub
from ..ranker.ranker import Ranking, Rankings
from ..wrangler.dataset import Dataset

from .impl.aggregator_auto import AggregatorCatalogAuto

# pylint: disable-msg=R0801,duplicate-code


class MetricSumPred(Metric):
    '''Test metric returning the sum of the predictions (modulo 1000).'''
    _name = 'sum_pred_metric'
    _high = True

    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        return sum(pred.values()) % 1000


class MetricMinVal(Metric):
    '''Test metric returning the minimum of the predictions.'''
    _name = 'min_val_metric'
    _high = True

    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        return min(pred.values())


ranking_123 = ['pipeline_1', 'pipeline_2', 'pipeline_3']
ranking_132 = ['pipeline_1', 'pipeline_3', 'pipeline_2']
ranking_213 = ['pipeline_2', 'pipeline_1', 'pipeline_3']
ranking_231 = ['pipeline_2', 'pipeline_3', 'pipeline_1']
ranking_312 = ['pipeline_3', 'pipeline_1', 'pipeline_2']
ranking_321 = ['pipeline_3', 'pipeline_2', 'pipeline_1']


@pytest.mark.parametrize("aggregator_name,final_ranking", [
    ('tsad.rank_aggregation.borda', ranking_123),
    ('tsad.rank_aggregation.kemeny', ranking_123),
    ('tsad.rank_aggregation.partial_borda', ranking_123),
    ('tsad.rank_aggregation.trimmed_borda', ranking_123),
    ('tsad.rank_aggregation.trimmed_partial_borda', ranking_123),
])
def test_tsad_simple_ranking(aggregator_name, final_ranking) -> None:
    '''Tests the TSAD rank aggregation methods.'''
    catalog = AggregatorCatalogAuto()
    aggregator = catalog.lookup_by_name(aggregator_name)

    results_1 = Dataset({
        '1': 1,
        '2': 2,
        '3': 3,
    })
    results_2 = Dataset({
        '1': 6,
        '2': 4,
        '3': 2,
    })
    results_3 = Dataset({
        '1': 7,
        '2': 5,
        '3': 11,
    })

    pipeline_results = PipelineResults({
        Designator('pipeline_1'): PipelineResult(prediction=results_1,
                                                 bound_pipeline=BoundPipelineStub('pipeline_1')),
        Designator('pipeline_2'): PipelineResult(prediction=results_2,
                                                 bound_pipeline=BoundPipelineStub('pipeline_2')),
        Designator('pipeline_3'): PipelineResult(prediction=results_3,
                                                 bound_pipeline=BoundPipelineStub('pipeline_3')),
    })

    rank_1 = Ranking(metric=MetricSumPred(), results=pipeline_results)
    rank_2 = Ranking(metric=MetricStub(), results=pipeline_results)
    rank_3 = Ranking(metric=MetricMinVal(), results=pipeline_results)

    rankings = Rankings({'rank_1': rank_1, 'rank_2': rank_2, 'rank_3': rank_3})

    aggregate_ranking = aggregator.aggregate(rankings=rankings, all_scores=True)

    assert [s.score for s in aggregate_ranking.scores(all_scores=True)] == [2, 1, 0]
    assert [s.pipeline_des for s in aggregate_ranking.scores(all_scores=True)] == final_ranking
