'''Test the TSAD aggregators'''

# pylint: disable=duplicate-code

from typing import Optional

from ..generator.bound_pipeline import BoundPipelineStub
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import PipelineResult, PipelineResults
from ..metrics.impl.metric import Metric
from ..ranker.ranker import Ranking, Rankings
from ..wrangler.dataset import Dataset

from .impl.aggregate_ranker import AggregateRanker
from .impl.aggregator_auto import AggregatorCatalogAuto
from .tsad_aggregator import TSADAggregator


class MetricMinVal(Metric):
    '''Test metric returning the minimum of the predictions.'''
    _name = 'min_val_metric'
    _high = True

    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        return min(pred.values())


def test_tsad_simple_ranking() -> None:
    '''Tests the overriding of hyperparameters works for aggregators.'''
    catalog = AggregatorCatalogAuto()
    aggregator = catalog.lookup_by_name('test_aggregators.identity')

    results_1 = Dataset({
        '1': 1,
    })
    results_2 = Dataset({
        '1': 2,
    })
    results_3 = Dataset({
        '1': 3,
    })

    pipeline_results = PipelineResults({
        Designator('pipeline_1'): PipelineResult(prediction=results_1,
                                                 bound_pipeline=BoundPipelineStub('pipeline_1')),
        Designator('pipeline_2'): PipelineResult(prediction=results_2,
                                                 bound_pipeline=BoundPipelineStub('pipeline_2')),
        Designator('pipeline_3'): PipelineResult(prediction=results_3,
                                                 bound_pipeline=BoundPipelineStub('pipeline_3')),
    })

    rankings = Rankings({'MinRanking': Ranking(metric=MetricMinVal(), results=pipeline_results)})

    identity_ranking = aggregator.aggregate(rankings=rankings)
    reverse_ranking = aggregator.aggregate(rankings=rankings, reverse=True)

    assert [s.pipeline_des for s in identity_ranking.scores(all_scores=True)] \
        == ['pipeline_1', 'pipeline_2', 'pipeline_3']
    assert [s.pipeline_des for s in reverse_ranking.scores(all_scores=True)] \
        == ['pipeline_3', 'pipeline_2', 'pipeline_1']


def test_fail_aggregator():
    '''Tests aggregators which raise exceptions.'''
    catalog = AggregatorCatalogAuto()
    catalog.register(TSADAggregator(
        name='test_aggregators.identity',
        tags={'for_tests': ['true']},
        fail=True,
    ))
    aggregator = catalog.lookup_by_name('test_aggregators.identity')

    results_1 = Dataset({
        '1': 1,
    })
    results_2 = Dataset({
        '1': 2,
    })
    results_3 = Dataset({
        '1': 3,
    })

    pipeline_results = PipelineResults({
        Designator('pipeline_1'): PipelineResult(prediction=results_1,
                                                 bound_pipeline=BoundPipelineStub('pipeline_1')),
        Designator('pipeline_2'): PipelineResult(prediction=results_2,
                                                 bound_pipeline=BoundPipelineStub('pipeline_2')),
        Designator('pipeline_3'): PipelineResult(prediction=results_3,
                                                 bound_pipeline=BoundPipelineStub('pipeline_3')),
    })

    rankings = Rankings({'MinRanking': Ranking(metric=MetricMinVal(), results=pipeline_results)})

    new_rankings = AggregateRanker(methods=[aggregator],
                                   rankings=rankings,
                                   results=pipeline_results,
                                   )()
    new_scores = new_rankings['test_aggregators.identity'].scores(all_scores=True)

    assert new_scores[0].score == 'intentional failure'
    assert new_scores[1].score == 'intentional failure'
    assert new_scores[2].score == 'intentional failure'
