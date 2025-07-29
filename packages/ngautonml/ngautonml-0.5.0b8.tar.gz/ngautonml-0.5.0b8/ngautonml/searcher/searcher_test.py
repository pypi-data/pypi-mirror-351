'''Tests for searcher.py'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, List, Optional

from ..algorithms.connect import ConnectorModel
from ..algorithms.impl.algorithm import Algorithm
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..problem_def.hyperparam_config import HyperparamConfig
from ..problem_def.task import TaskType
from ..templates.impl.pipeline_step import PipelineStep
from ..wrangler.constants import RangeMethod
from ..wrangler.dataset import Dataset
from .param_range import ParamRange
from .searcher import SearcherImpl, StepSet
from .frozen_overrides import FrozenOverrides

# pylint: disable=missing-docstring, duplicate-code


def test_step_set_fixed_sunny_day():
    # We use ConnectorModel just because its hyperparameters are easy to work with.
    step = PipelineStep(name='some_step',
                        model=ConnectorModel(overridable_param='overridable_value'))
    dut = StepSet(step=step)

    # 'multiply' binds all steps in the set.
    # it may increase the number of steps for RangeMethods other than FIXED,
    #   but that is not the case here.
    dut.multiply('some_param', ParamRange(RangeMethod.FIXED, prange='some_value'),
                 no_show=set())
    assert len(dut.steps) == 1
    new_step = list(dut.steps.values())[0]
    assert new_step.filename.endswith('@some_step:some_param=some_value')
    assert "connect_" in new_step.filename
    want_key = FrozenOverrides.freeze({
        new_step.pipeline_designator_component: {'some_param': 'some_value'}})
    assert dut.steps[want_key].hyperparams() == {
        'overridable_param': 'overridable_value',
        'some_param': 'some_value',
    }

    # Try another multiply and see that we get a new step.
    dut.multiply('another_param', ParamRange(RangeMethod.FIXED, 'another_value'),
                 no_show=set())
    assert len(dut.steps) == 1
    new_step = list(dut.steps.values())[0]
    assert new_step.filename.endswith(
        '@some_step:another_param=another_value,some_param=some_value')
    assert "connect_" in new_step.filename
    want_key = FrozenOverrides.freeze({new_step.pipeline_designator_component: {
        'some_param': 'some_value',
        'another_param': 'another_value'}})
    print(dut.steps)
    assert dut.steps[want_key].hyperparams() == {
        'overridable_param': 'overridable_value',
        'some_param': 'some_value',
        'another_param': 'another_value',
    }


def test_step_set_filenames():
    PipelineStep.reset_serial_number()
    step = PipelineStep(name='some_step',
                        model=ConnectorModel(overridable_param='overridable_value'))
    dut = StepSet(step=step)

    dut.multiply('some_param', ParamRange(RangeMethod.FIXED, prange='some_value'),
                 no_show=set())
    key1 = FrozenOverrides.freeze({'some_step': {'some_param': 'some_value'}})
    assert dut.steps[key1].pipeline_designator_component == 'some_step'
    assert dut.steps[key1].filename == '@connect_1@some_step:some_param=some_value'

    dut.multiply('overridable_param', ParamRange(RangeMethod.FIXED, prange='new_value'),
                 no_show=set())

    key2 = FrozenOverrides.freeze({'some_step': {
        'some_param': 'some_value',
        'overridable_param': 'new_value'}})
    assert dut.steps[key2].pipeline_designator_component == 'some_step'
    assert (
        dut.steps[key2].filename
        == '@connect_2@some_step:overridable_param=new_value,some_param=some_value')


def test_step_set_filenames_unnamed_step():
    PipelineStep.reset_serial_number()
    step = PipelineStep(model=ConnectorModel(overridable_param='overridable_value'))
    dut = StepSet(step=step)

    dut.multiply('some_param', ParamRange(RangeMethod.FIXED, prange='some_value'),
                 no_show=set())

    key1 = FrozenOverrides.freeze({
        'connect': {'some_param': 'some_value'}
    })
    assert dut.steps[key1].filename == '@connect_1@:some_param=some_value'


def test_step_set_list_sunny_day():
    step = PipelineStep(model=ConnectorModel(overridable_param='overridable_value'),
                        name='some_step')
    dut = StepSet(step=step)

    # This is the test.
    dut.multiply('some_param', ParamRange(RangeMethod.LIST, prange=['list_value1', 'list_value2']),
                 no_show=set())

    key1 = FrozenOverrides.freeze({'some_step': {'some_param': 'list_value1'}})
    key2 = FrozenOverrides.freeze({'some_step': {'some_param': 'list_value2'}})
    assert set(dut.steps.keys()) == {key1, key2}
    assert dut.steps[key1].hyperparams() == {
        'overridable_param': 'overridable_value',
        'some_param': 'list_value1',
    }
    # Can we append a FIXED value to each of those?
    dut.multiply('another_param', ParamRange(RangeMethod.FIXED, 'another_value'),
                 no_show=set())
    key3 = FrozenOverrides.freeze({'some_step': {
        'some_param': 'list_value2',
        'another_param': 'another_value'}})
    assert dut.steps[key3].hyperparams() == {
        'overridable_param': 'overridable_value',
        'some_param': 'list_value2',
        'another_param': 'another_value',
    }


def test_step_set_linear_sunny_day():
    step = PipelineStep(model=ConnectorModel(overridable_param='overridable_value'),
                        name='some_step')
    dut = StepSet(step=step)

    # This is the test.
    dut.multiply('some_param', ParamRange(RangeMethod.LINEAR, prange=[1, 1, 3]),
                 no_show=set())

    key1 = FrozenOverrides.freeze({'some_step': {'some_param': '1'}})
    key2 = FrozenOverrides.freeze({'some_step': {'some_param': '2'}})
    key3 = FrozenOverrides.freeze({'some_step': {'some_param': '3'}})
    assert set(dut.steps.keys()) == {key1, key2, key3}
    assert dut.steps[key3].hyperparams() == {
        'overridable_param': 'overridable_value',
        'some_param': 3,
    }
    # Can we append a FIXED value to each of those?
    dut.multiply('another_param', ParamRange(RangeMethod.FIXED, 'another_value'),
                 no_show=set())
    key4 = FrozenOverrides.freeze({'some_step': {
        'some_param': '2',
        'another_param': 'another_value'}})
    assert dut.steps[key4].hyperparams() == {
        'overridable_param': 'overridable_value',
        'some_param': 2,
        'another_param': 'another_value',
    }


def test_step_set_linear_complex():
    '''The elements of range for LINEAR hyperparams must be a subclass of Number.

    However, there is a special case of complex numbers where the < operation does not work.
    As this could potentially cause problems, ensure it is properly handled.
    '''
    step = PipelineStep(model=ConnectorModel(overridable_param='overridable_value'),
                        name='some_step')
    dut = StepSet(step=step)

    # This is the test.
    dut.multiply('some_param',
                 ParamRange(method=RangeMethod.LINEAR,
                            prange=[complex(1, 1), complex(1, 1), complex(3, 3)]),
                 no_show=set())

    key1 = FrozenOverrides.freeze({'some_step': {'some_param': '(1+1j)'}})
    key2 = FrozenOverrides.freeze({'some_step': {'some_param': '(2+2j)'}})
    key3 = FrozenOverrides.freeze({'some_step': {'some_param': '(3+3j)'}})
    assert set(dut.steps.keys()) == {key1, key2, key3}
    assert dut.steps[key3].hyperparams() == {
        'overridable_param': 'overridable_value',
        'some_param': complex(3, 3),
    }


FIXED_HYPERPARM_CONFIG = HyperparamConfig(clause={
    'hyperparams': [
        {
            'select': {
                'name': 'step2',
            },
            'params': {
                'added_param': {
                    'fixed': 8,
                },
                'new_param': {
                    'fixed': 16,
                }
            },
        },
    ],
})


def test_searcher_impl_fixed() -> None:
    pipeline = BoundPipeline(name='some_template')
    pipeline.step(model=ConnectorModel()).set_name('step1')
    step2 = pipeline.step(model=ConnectorModel(base_param=1),
                          added_param=2).set_name('step2')

    dut = SearcherImpl(FIXED_HYPERPARM_CONFIG)

    # This is the actual test.
    got: Dict[Designator, BoundPipeline] = dut.bind_hyperparams(pipeline=pipeline)

    # Confirm that we only got 1 pipeline back, because the parameters that we bound are FIXED.
    assert len(got) == 1
    new_pipeline = got[Designator('some_template@step2:added_param=8,new_param=16')]
    new_steps: List[PipelineStep] = new_pipeline.steps
    # Make sure the original step did not get modified.
    assert step2.hyperparams() == {
        'base_param': 1,
        'added_param': 2,
    }
    # Confirm that only the matched step got modified.
    assert new_steps[0].hyperparams() == {}
    assert new_steps[1].hyperparams() == {
        'base_param': 1,
        'added_param': 8,
        'new_param': 16,
    }


EMPTY_HYPERPARM_CONFIG = HyperparamConfig(clause={
    'hyperparams': []
})


def test_null_search() -> None:
    '''Test that Searcher behaves correctly when there are no matching overrides.'''
    pipeline = BoundPipeline(name='some_template')
    pipeline.step(model=ConnectorModel()).set_name('step1').mark_queried()
    pipeline.step(model=ConnectorModel(base_param=1)).set_name('step2')

    dut = SearcherImpl(EMPTY_HYPERPARM_CONFIG)
    got: Dict[Designator, BoundPipeline] = dut.bind_hyperparams(pipeline=pipeline)

    want_des = Designator('some_template@step1')
    assert len(got) == 1
    assert want_des in got
    assert got[want_des].designator == want_des


class FakeAlgorithmInstance(AlgorithmInstance):
    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        return Dataset(dataset.copy())


class FakeAlgorithm(Algorithm):
    _name = 'fake_algorithm'
    _default_hyperparams = {
        'base_param': ParamRange(RangeMethod.LIST, ['a', 'b']),
        'param_to_override': 'value_to_override',
    }
    _tags = {
        'task': [
            TaskType.REGRESSION.name,
            TaskType.BINARY_CLASSIFICATION.name,
        ]
    }

    def instantiate(self, **hyperparams) -> FakeAlgorithmInstance:
        return FakeAlgorithmInstance(parent=self, **hyperparams)


def test_default_grid_search() -> None:
    pipeline = BoundPipeline('bound_pipeline')
    step = pipeline.step(model=FakeAlgorithm(param_to_override='overridden_value'))
    step.set_name('some_step')
    dut = SearcherImpl(EMPTY_HYPERPARM_CONFIG)

    # This is the test.
    got = dut.bind_hyperparams(pipeline)

    assert set(got.keys()) == {
        'bound_pipeline@some_step:base_param=a',
        'bound_pipeline@some_step:base_param=b'
    }
    assert got[Designator('bound_pipeline@some_step:base_param=a')].steps[0].hyperparams() == {
        'base_param': 'a',
        'param_to_override': 'overridden_value'
    }
    assert got[Designator('bound_pipeline@some_step:base_param=b')].steps[0].hyperparams() == {
        'base_param': 'b',
        'param_to_override': 'overridden_value'
    }


def test_non_matching_overrides() -> None:
    '''When a searcher is created with only Override(s) whose Selector(s) do not match any steps
        of the pipeline, we want it to return a single pipeline that is a copy of what we
        started with.
    '''
    pipeline = BoundPipeline('bound_pipeline')
    step = pipeline.step(model=ConnectorModel(some_param='some_value'))
    step.set_name('some_step')
    dut = SearcherImpl(HyperparamConfig({
        'hyperparams': [
            {
                'select': {
                    'algorithm': 'does not match'
                },
                'params': {
                    'some_param': {
                        'fixed': 'a_value_we_wont_see'
                    }
                }
            },
            {
                'select': {
                    'algorithm': 'also_does_not_match',
                },
                'params': {
                    'some_param': {
                        'fixed': 'another_value_we_wont_see',
                    }
                },
            },
        ]
    }))

    # This is the test.
    got = dut.bind_hyperparams(pipeline)

    assert set(got.keys()) == {
        'bound_pipeline'
    }
    assert len(got[Designator('bound_pipeline')].steps) == 1
