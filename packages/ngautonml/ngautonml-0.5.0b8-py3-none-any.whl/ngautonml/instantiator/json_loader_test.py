'''Tests for json_loader.py'''
import json
from pathlib import Path
import pytest

from ..algorithms.impl.algorithm import AlgorithmCatalog, AlgorithmCatalogStub
from ..algorithms.impl.fake_algorithm import FakeAlgorithm, FakeInstance, FAKE_SERIALIZED
from ..algorithms.connect import ConnectorModel, ConnectorModelInstance
from ..executor.cucumber import Cucumber
from ..executor.simple.simple_executable_step import SimpleExecutableStep
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator, StepDesignator
from ..templates.impl.parallel_step import ParallelStep
from ..wrangler.dataset import Dataset
from .json_loader import JsonLoader


# pylint: disable = missing-function-docstring,protected-access,redefined-outer-name,duplicate-code


@pytest.fixture(scope='session')
def algorithm_catalog() -> AlgorithmCatalog:
    retval = AlgorithmCatalogStub()
    retval.register(FakeAlgorithm())
    retval.register(ConnectorModel())
    return retval


@pytest.fixture(scope='session')
def pipeline_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output_path = tmp_path_factory.mktemp('output')
    contents = {
        'version': '1.0',
        'pipeline_designator': 'fake_bound',
        'pipeline_template_name': 'fake_bound',
        'output_dir': str(output_path),
        'steps': [
            {
                'type': 'parallel',
                'subpipelines': {
                    'left': [
                        {
                            'algorithm_name': 'fake_algorithm',
                            'model_filename': '@fake_algorithm_1@',
                            'type': 'step',
                            'queried': True
                        },
                    ],
                    'right': [
                        {
                            'algorithm_name': 'fake_algorithm',
                            'model_filename': '@fake_algorithm_3@named_step',
                            'type': 'step',
                            'name': 'named_step'
                        },
                    ]
                },
            },
            {
                'type': 'step',
                'algorithm_name': 'connect',
                'hyperparams': {
                    'newkey': ['left', 'oldkey'],
                    'othernewkey': ['right', 'oldkey']
                },
                'model_filename': '@connect_5@',
            }
        ],
    }
    pipeline_output_path = output_path / 'pipelines' / 'fake_bound.json'
    pipeline_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pipeline_output_path, 'w', encoding='utf-8') as filepointer:
        json.dump(contents, filepointer)

    fake_inst = FakeInstance(parent=FakeAlgorithm())
    fake_inst.fit(dataset=Dataset())
    fake_pickle = Cucumber(
        impl=fake_inst,
        filename=StepDesignator('fake_step_des'),
        pipeline_designator=Designator('fake_bound'),
        hyperparams={}
    ).serialize()
    connector_pickle = Cucumber(
        impl=ConnectorModelInstance(parent=ConnectorModel()),
        filename=StepDesignator('@connect_5@'),
        pipeline_designator=Designator('fake_bound'),
        hyperparams={
            'newkey': ['left', 'oldkey'],
            'othernewkey': ['right', 'oldkey']
        }
    ).serialize()

    model_dir = output_path / 'models' / 'fake_bound'
    model_dir.mkdir(parents=True, exist_ok=True)

    with open(model_dir / '@fake_algorithm_1@.pkl', 'wb') as filepointer:
        filepointer.write(fake_pickle)

    with open(model_dir / '@fake_algorithm_3@named_step.pkl', 'wb') as filepointer:
        filepointer.write(fake_pickle)

    with open(model_dir / '@connect_5@.pkl', 'wb') as filepointer:
        filepointer.write(connector_pickle)

    # save a model to disk at output_folder/models/fake_bound/@connect_5@.pkl

    return pipeline_output_path


def test_load_pipeline_sunny_day(algorithm_catalog: AlgorithmCatalog, pipeline_file: Path) -> None:
    dut = JsonLoader(
        saver_version='1.0',
        algorithm_catalog=algorithm_catalog,
        pipeline_file=pipeline_file,
        load_models=True)

    got = dut.pipeline

    assert len(got.steps) == 2
    parallel_step = got.steps[0]
    connector_step = got.steps[1]
    assert isinstance(parallel_step, ParallelStep)
    assert connector_step.hyperparams() == {
        'newkey': ['left', 'oldkey'],
        'othernewkey': ['right', 'oldkey'],
    }
    left_pipeline = parallel_step.subpipelines['left']
    assert isinstance(left_pipeline, BoundPipeline)
    left_step = left_pipeline.steps[0]
    # Instantiate left_step as kind 'simple'.
    left_executable = SimpleExecutableStep(left_step)
    left_instance = left_executable._model_instance
    assert isinstance(left_instance, FakeInstance)
    assert left_instance.evidence_of_deserialize == FAKE_SERIALIZED
