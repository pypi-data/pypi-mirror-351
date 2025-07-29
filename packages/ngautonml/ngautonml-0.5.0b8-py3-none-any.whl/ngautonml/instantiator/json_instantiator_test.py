'''Tests for json_instantiator.py'''
import json
from typing import Any
import re

import pytest

from ..algorithms.connect import ConnectorModel
from ..algorithms.impl.fake_algorithm import FakeAlgorithm
from ..executor.cucumber import Cucumber, JarOfCucumbers
from ..generator.bound_pipeline import BoundPipelineStub
from ..generator.designator import Designator, StepDesignator
from ..problem_def.output_config import OutputConfig
from ..wrangler.saver import Saver
from .instantiator import InstantiatorStub
from .json_instantiator import JsonInstantiator

# pylint: disable=missing-class-docstring, missing-function-docstring, redefined-outer-name, duplicate-code


@pytest.fixture(scope='session')
def output_config(tmp_path_factory: pytest.TempPathFactory) -> OutputConfig:
    tmp_path = tmp_path_factory.mktemp('data')
    tmp_dir = tmp_path / 'sub'
    tmp_dir.mkdir()
    config = OutputConfig(clause={
        'path': str(tmp_dir),
        'instantiations': [
            'json'
        ]
    })
    return config


@pytest.fixture(scope='session')
def json_instantiator(tmp_path_factory: pytest.TempPathFactory) -> JsonInstantiator:
    return JsonInstantiator(saver=Saver(output_config=output_config(tmp_path_factory)))


KEYS_TO_TRANSFORM = {'model_filename'}


def strip_serial(top: Any) -> Any:
    '''For a parsed JSON representation of a pipeline, replace all serial
    numbers in model filenames with "NUM" (since we cannot otherwise predict them)'''
    retval = top
    if isinstance(top, dict):
        retval = {}
        for key, value in top.items():
            if key in KEYS_TO_TRANSFORM:
                retval[key] = re.sub('[0-9]+', 'NUM', value)
                continue
            retval[key] = strip_serial(value)
        return retval
    if isinstance(top, list):
        retval = []
        for item in top:
            retval.append(strip_serial(item))
        return retval
    return retval


def test_json_instantiator_sunny_day(output_config: OutputConfig) -> None:
    pipeline = BoundPipelineStub(name='Fake_Bound')
    pipe1 = pipeline.new(name='at')
    pipe1.step(FakeAlgorithm(name='A')).mark_queried()
    pipe1.step(FakeAlgorithm(name='T'))
    pipe2 = pipeline.new(name='dt')
    pipe2.step(FakeAlgorithm(name='D')).set_name('named_step')
    pipe2.step(FakeAlgorithm(name='T'))
    pipeline.parallel(left=pipe1, right=pipe2)
    pipeline.step(ConnectorModel(
        name='ring',
        newkey=['left', 'oldkey'],
        othernewkey=['right', 'oldkey']))
    pipeline.validate()

    # Create a fake JarOfCucumbers for the saver to save.
    cucumbers = JarOfCucumbers({
        StepDesignator('a'): Cucumber(
            impl=FakeAlgorithm().instantiate(),
            filename=StepDesignator('a'),
            pipeline_designator=pipeline.designator,
            hyperparams={}
        )
    })

    # Create a fake executable pipeline, storing that fake jar of cucumbers.
    compiler = InstantiatorStub(cucumbers)
    pipelines = {
        Designator('Fake_Bound'): compiler.instantiate(pipeline=pipeline),
    }

    # Make a saver and save the models in our fake executable pipeline,
    #   writing the pickled fake cucumbers to disk.
    saver = Saver(output_config=output_config)
    model_paths = saver.save_models(pipelines=pipelines)

    # Use the JsonInstantiator to save our fake executable pipeline as json
    #   Uses the paths to the fake saved models provided by the saver
    dut = JsonInstantiator(saver=saver)
    dut.save(pipeline, model_paths=model_paths)

    assert output_config.path is not None
    with open(output_config.path / 'pipelines' / 'fake_bound.json', 'rb') as file_pointer:
        got = json.load(file_pointer)

    assert strip_serial(got) == {
        'version': '1.0',
        'pipeline_designator': 'fake_bound',
        'pipeline_template_name': 'fake_bound',
        'output_dir': str(output_config.path),
        'steps': [
            {
                'type': 'parallel',
                'subpipelines': {
                    'left': [
                        {
                            'algorithm_name': 'a',
                            'model_filename': '@a_NUM@',
                            'type': 'step',
                            'queried': True
                        },
                        {
                            'algorithm_name': 't',
                            'model_filename': '@t_NUM@',
                            'type': 'step'
                        }
                    ],
                    'right': [
                        {
                            'algorithm_name': 'd',
                            'model_filename': '@d_NUM@named_step',
                            'type': 'step',
                            'name': 'named_step'
                        },
                        {
                            'algorithm_name': 't',
                            'model_filename': '@t_NUM@',
                            'type': 'step'
                        }
                    ]
                },
            },
            {
                'type': 'step',
                'algorithm_name': 'ring',
                'hyperparams': {
                    'newkey': ['left', 'oldkey'],
                    'othernewkey': ['right', 'oldkey']
                },
                'model_filename': '@ring_NUM@',
            }
        ],
    }
