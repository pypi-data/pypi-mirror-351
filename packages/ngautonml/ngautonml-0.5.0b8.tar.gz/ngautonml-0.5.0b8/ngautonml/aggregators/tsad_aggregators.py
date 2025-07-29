'''Wraps TSAD aggregators with TSADAggregator and registers them.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


from typing import Any, Dict, List
from .impl.aggregator_catalog import AggregatorCatalog
from .tsad_aggregator import TSADAggregator


AGGREGATORS: List[Dict[str, Any]] = [
    {
        'name': 'tsad.rank_aggregation.borda',
        'tags': {'for_tests': ['true']},
    },
    {
        'name': 'tsad.rank_aggregation.kemeny',
        'tags': {'required_number_of_pipelines': ['3']},
    },
    {
        'name': 'tsad.rank_aggregation.partial_borda',
        'weights': None,
        'top_k': 5,
    },
    {
        'name': 'tsad.rank_aggregation.trimmed_borda',
        'weights': None,
        'top_k': 5,
        'top_kr': None,
        'aggregation_type': 'kemeny',
        'metric': 'influence',
        'n_neighbors': 6,
    },
    {
        'name': 'tsad.rank_aggregation.trimmed_partial_borda',
        'tags': {'for_tests': ['true']},
        'weights': None,
        'top_k': 5,
        'top_kr': None,
        'aggregation_type': 'kemeny',
        'metric': 'influence',
        'n_neighbors': 6,
    },
]


def register(catalog: AggregatorCatalog, *unused_args, **unused_kwargs) -> None:
    '''Register all the objects in this file.'''
    for agg in AGGREGATORS:
        catalog.register(TSADAggregator(**agg))
