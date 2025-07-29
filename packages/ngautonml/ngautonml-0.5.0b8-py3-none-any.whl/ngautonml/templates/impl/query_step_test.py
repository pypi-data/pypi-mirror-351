'''Tests for ParallelStep'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any

from ...algorithms.impl.algorithm import Algorithm, AlgorithmCatalogStub

from .query_step import QueryStep
from .pipeline_template import PipelineTemplate

# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code,protected-access


class ModelStub(Algorithm):
    def instantiate(self, **unused_kwargs) -> Any:
        return None


def test_query() -> None:
    model = ModelStub()
    algorithm_catalog = AlgorithmCatalogStub()
    algorithm_catalog.register(model, name='Some_Model', tags={'some_tag': ['some_value']})

    dut = PipelineTemplate(name='Fake_Template', algorithm_catalog=algorithm_catalog)
    query_step = dut.query(some_tag='some_value')
    assert len(dut._steps) == 1
    assert isinstance(query_step, QueryStep)
