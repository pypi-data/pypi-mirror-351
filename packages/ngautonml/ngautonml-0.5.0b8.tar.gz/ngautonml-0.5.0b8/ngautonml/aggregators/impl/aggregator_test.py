'''Tests for the Aggregator Base class implementations'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...instantiator.executable_pipeline import PipelineResults
from ...metrics.impl.metric import MetricStub
from ...ranker.ranker import Ranking, Rankings, RankingStub
from .aggregator import Aggregator

# pylint: disable=missing-function-docstring,duplicate-code
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class ExampleAggregator(Aggregator):
    _name = 'TestAggregator'

    def aggregate(self, rankings: Rankings, all_scores: bool = False) -> Ranking:
        return RankingStub(MetricStub(), PipelineResults())


def test_name():
    dut = ExampleAggregator()
    assert dut.name == 'testaggregator'
    got = dut.aggregate({})
    assert got.metric.name == 'stub_metric'
