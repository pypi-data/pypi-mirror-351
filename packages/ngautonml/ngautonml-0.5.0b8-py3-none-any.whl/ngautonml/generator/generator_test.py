'''Test the generator module.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..algorithms.connect import ConnectorModel
from ..algorithms.impl.algorithm import AlgorithmCatalogStub
from ..algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ..problem_def.problem_def import ProblemDefinition
from ..templates.impl.pipeline_template import PipelineTemplate
from .designator import Designator
from .generator import GeneratorImpl, GeneratorStub

# pylint: disable=missing-function-docstring,duplicate-code,protected-access

TEST_PROBLEM_DEF = '''{
    "_comments" : [
        "A json file fully encapsulating the problem definition",
        "Specifically, an exmaple time series forecasting problem."
    ],
    "dataset": {
        "config": "ignore",
        "column_roles": {}
    },
    "problem_type": {
        "task": "regression"
    },
    "metrics": {
          "MEAN_ABSOLUTE_ERROR": {}
    }
}
'''


def test_init() -> None:
    dut = GeneratorStub(
        name='test_generator',
        algorithm_catalog=AlgorithmCatalogAuto(),
        problem_definition=ProblemDefinition(TEST_PROBLEM_DEF)
    )
    assert dut is not None
    assert dut._algorithm_catalog.__class__.__name__ == "AlgorithmCatalogAuto"


def test_generate_stubbed() -> None:
    dut = GeneratorStub(
        name='stub',
        problem_definition=ProblemDefinition(TEST_PROBLEM_DEF)
    )
    result = dut.generate_all({'stub': PipelineTemplate(name='stub')})
    assert 1 == len(result)
    assert 'stub' == result[Designator('stub')].name


def test_generate_linear() -> None:
    dut = GeneratorImpl(
        algorithm_catalog=AlgorithmCatalogStub(),
        problem_definition=ProblemDefinition(TEST_PROBLEM_DEF)
    )
    pipeline = PipelineTemplate(name='linear_pipeline')
    pipeline.step(ConnectorModel()).set_name('the_step')
    pipeline.step(ConnectorModel())
    pipeline.step(ConnectorModel())
    got = dut.generate(pipeline)
    assert set(got.keys()) == set([Designator('linear_pipeline')])
    assert len(got[Designator('linear_pipeline')].steps) == 3


def test_generate_query() -> None:
    algorithm_catalog = AlgorithmCatalogStub()
    algorithm_catalog.register(ConnectorModel(b='a'), name='atob', tags={'foo': ['bar', 'frob']})
    algorithm_catalog.register(ConnectorModel(d='c'), name='ctod', tags={'foo': ['quux', 'bar']})
    dut = GeneratorImpl(
        algorithm_catalog=algorithm_catalog,
        problem_definition=ProblemDefinition(TEST_PROBLEM_DEF)
    )
    pipeline = PipelineTemplate(name='query_pipeline', algorithm_catalog=algorithm_catalog)
    pipeline.step(ConnectorModel()).set_name('first_step')
    pipeline.query(foo='bar')
    pipeline.step(ConnectorModel()).set_name('last_step')
    got = dut.generate(pipeline)
    key1 = Designator('query_pipeline@atob')
    key2 = Designator('query_pipeline@ctod')
    assert set(got.keys()) == set([key1, key2])
    assert len(got[key1].steps) == 3
    assert got[key2].steps[1].pipeline_designator_component == 'ctod'


def test_generate_parallel() -> None:
    dut = GeneratorImpl(
        algorithm_catalog=AlgorithmCatalogStub(),
        problem_definition=ProblemDefinition(TEST_PROBLEM_DEF)
    )
    pipeline = PipelineTemplate(name='parallel_pipeline', generator=dut)

    pipeline1 = pipeline.new('upper_pipeline')
    pipeline1.step(ConnectorModel()).set_name('upper_step1')
    pipeline1.step(ConnectorModel())
    pipeline2 = pipeline.new('lower_pipeline')
    pipeline2.step(ConnectorModel()).set_name('lower_step')

    pipeline.parallel(upper=pipeline1, lower=pipeline2).set_name('parallel_step')
    pipeline.step(ConnectorModel()).set_name('last_step')

    got = dut.generate(pipeline)

    key = Designator('parallel_pipeline')
    assert set(got.keys()) == set([key])
    assert len(got[key].steps) == 2


def test_generate_all_sunny_day() -> None:
    algorithm_catalog = AlgorithmCatalogStub()
    algorithm_catalog.register(ConnectorModel(b='a'), name='atob', tags={'foo': ['bar', 'frob']})
    algorithm_catalog.register(ConnectorModel(d='c'), name='ctod', tags={'foo': ['quux', 'bar']})

    dut = GeneratorImpl(
        algorithm_catalog=algorithm_catalog,
        problem_definition=ProblemDefinition(TEST_PROBLEM_DEF)
    )

    template1 = PipelineTemplate(name='linear_pipeline')
    template1.step(ConnectorModel()).set_name('the_step')
    template1.step(ConnectorModel())
    template1.step(ConnectorModel())

    template2 = PipelineTemplate(name='query_pipeline', algorithm_catalog=algorithm_catalog)
    template2.step(ConnectorModel()).set_name('first_step')
    template2.query(foo='bar')
    template2.step(ConnectorModel()).set_name('last_step')

    got = dut.generate_all({template1.name: template1, template2.name: template2})

    key1_1 = Designator('linear_pipeline')
    key2_1 = Designator('query_pipeline@atob')
    key2_2 = Designator('query_pipeline@ctod')

    assert set(got.keys()) == set([key1_1, key2_1, key2_2])
