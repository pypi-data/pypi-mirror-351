'''Adds the Borda Rank Aggregator'''

# pylint: disable=too-many-locals

import importlib
from typing import Any
from typing_extensions import Protocol

import numpy as np

from ..instantiator.executable_pipeline import PipelineResults
from ..ranker.ranker import Rankings

from .impl.aggregator import Aggregator, AggregatorInsufficientPipelines, AggregatorRanking
from .impl.aggregator_catalog import AggregatorCatalog


class AggregatorImpl(Protocol):
    '''Type for TSAD aggregator implementations'''
    def __call__(self, ranks: np.ndarray, **kwargs: Any):
        ...


class TSADAggregator(Aggregator):
    '''Generic object for Aggregators from TSAD library.'''
    _aggregator: AggregatorImpl
    _high = False  # The best score is 1, and they get worse as you go up.

    def __init__(self, **params):
        super().__init__(**params)
        self._aggregator = self._load_module(f'.{self._name}')

    def _load_module(self, name: str):
        # Split name into module part (e.g. sklearn.linear_model)
        # and constructor part (e.g. LinearRegression)
        parts = name.split('.')
        constructor_part = parts[-1]
        module = importlib.import_module('.'.join(parts[:-1]), package='ngautonml.aggregators.impl')
        # Load the constructor.
        return getattr(module, constructor_part)

    def aggregate(self,
                  rankings: Rankings,
                  all_scores: bool = False, **overrides) -> AggregatorRanking:
        rankings_list = list(rankings.values())
        first_ranking = rankings_list[0]
        first_scores = first_ranking.scores(all_scores=all_scores)
        num_of_pipelines = len(first_scores)
        num_of_metrics = len(rankings_list)

        assert self._tags is not None, (
            'BUG: self._tags should have been initialized in TSADGenerator.__init__().'
        )
        if 'required_number_of_pipelines' in self._tags:
            num_of_pipelines_required = int(self._tags['required_number_of_pipelines'][0])
            if num_of_pipelines < num_of_pipelines_required:
                raise AggregatorInsufficientPipelines(
                    f'Given {num_of_pipelines} pipelines but '
                    f'require {num_of_pipelines_required} pipelines'
                )

        pipeline_to_index = {}
        index_to_pipeline = {}
        pipeline_results = PipelineResults()
        for i, scored_result in enumerate(first_scores):
            pipeline_des = scored_result.pipeline_des
            pipeline_to_index[pipeline_des] = i
            index_to_pipeline[i] = pipeline_des
            pipeline_results[pipeline_des] = scored_result.result

        # ranks[i, j] = the rank of the jth pipeline under the ith metric
        ranks = np.zeros((num_of_metrics, num_of_pipelines))
        for m, ranking in enumerate(rankings_list):
            for rank, scored_result in enumerate(ranking.scores(all_scores=all_scores)):
                pipeline_des = scored_result.pipeline_des
                n = pipeline_to_index[pipeline_des]
                ranks[m, n] = rank

        _, aggregate_rank = self._aggregator(ranks, **self.hyperparams(**overrides))

        scores = {}
        for i, rank in enumerate(aggregate_rank):
            scores[index_to_pipeline[rank]] = i

        return AggregatorRanking(metric=self, results=pipeline_results, scores=scores)


def register(catalog: AggregatorCatalog):  # pylint: disable=unused-argument
    '''Nothing to register.

    All subclasses of SklearnAlgorithm are registered in sklearn_algorithms.py
    '''
