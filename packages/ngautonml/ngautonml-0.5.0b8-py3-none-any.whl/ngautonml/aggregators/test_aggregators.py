'''Wraps test aggregators with TSADAggregator and registers them.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


from typing import Any, Dict, List
from .impl.aggregator_catalog import AggregatorCatalog
from .tsad_aggregator import TSADAggregator


AGGREGATORS: List[Dict[str, Any]] = [
    {
        'name': 'test_aggregators.identity',
        'tags': {'for_tests': ['true']},
    },
]


def register(catalog: AggregatorCatalog, *unused_args, **unused_kwargs) -> None:
    '''Register all the objects in this file.'''
    for agg in AGGREGATORS:
        catalog.register(TSADAggregator(**agg))
