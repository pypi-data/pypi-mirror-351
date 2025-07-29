'''Tests for the Saver object'''
# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path
from typing import Optional

import pandas as pd
import pytest

from ..algorithms.connect import ConnectorModel
from ..algorithms.impl.algorithm import Algorithm
from ..algorithms.impl.fittable_algorithm_instance import FittableAlgorithmInstance
from ..executor.cucumber import Cucumber, JarOfCucumbers
from ..generator.designator import Designator, StepDesignator
from ..instantiator.executable_pipeline import ExecutablePipelineStub
from ..instantiator.executable_pipeline import PipelineResult, PipelineResults
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Dataset, TableFactory

from .saver import Saver
from ..problem_def.output_config import OutputConfig
TableCatalogAuto()
# pylint: disable=missing-function-docstring,redefined-outer-name
# pylint: disable=duplicate-code,missing-class-docstring


@pytest.fixture(scope='session')
def output_config(tmp_path_factory: pytest.TempPathFactory) -> OutputConfig:
    tmp_path = tmp_path_factory.mktemp('data')
    tmp_dir = tmp_path / 'sub'
    tmp_dir.mkdir()
    config = OutputConfig(clause={
        'path': str(tmp_dir),
        'instantiations': [
            'stub_executor_kind',
            'simple'
        ],
        'file_type': 'csv'
    })
    return config


def test_save_predictions(output_config: OutputConfig) -> None:
    dut = Saver(output_config=output_config)
    prediction_table = TableFactory({'a': [1, 2, 3]})
    prediction = Dataset()
    prediction.predictions_table = prediction_table

    result = PipelineResult(
        executable_pipeline=ExecutablePipelineStub(),
        prediction=prediction)
    got_path = dut.save(result=result)
    assert output_config.path is not None
    want_path = output_config.path / 'stub_pipeline'
    assert got_path == want_path

    train_pred_path = want_path / 'train_predictions_table.csv'
    assert train_pred_path.exists()

    got_df = pd.read_csv(str(train_pred_path))
    pd.testing.assert_frame_equal(got_df, prediction_table.as_(pd.DataFrame))


class FakeAlgorithm(Algorithm):
    _name = 'fake_algorithm'
    _default_hyperparams = {
        'base_param': 'base_value',
        'param_to_override': 'value_to_override',
    }
    _tags = {}

    def instantiate(self, **hyperparams) -> 'FakeAlgorithmInstance':
        return FakeAlgorithmInstance(parent=self, **hyperparams)


class FakeAlgorithmInstance(FittableAlgorithmInstance):
    def serialize(self) -> bytes:
        return b'fake algorithm instance model\n'

    def fit(self, dataset: Optional[Dataset]) -> None:
        _ = dataset
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        return dataset


DES1 = StepDesignator('a')
DES2 = StepDesignator('b')


class FakeExecutablePipeline(ExecutablePipelineStub):
    '''Fake trained executable pipeline containing 2 models'''

    def __init__(self):
        super().__init__(trained=True)

    def cucumberize_all(self) -> JarOfCucumbers:
        retval = JarOfCucumbers()
        alg1 = ConnectorModel(param='value')
        impl1 = alg1.instantiate()
        alg2 = FakeAlgorithm()
        impl2 = alg2.instantiate()
        retval[DES1] = Cucumber(
            impl=impl1,
            filename=DES1,
            pipeline_designator=Designator('foo'),
            hyperparams=alg1.hyperparams()
        )
        retval[DES2] = Cucumber(
            impl=impl2,
            filename=DES2,
            pipeline_designator=Designator('foo'),
            hyperparams=alg2.hyperparams()
        )
        return retval

    @property
    def locked(self) -> bool:
        return False


def test_save_all_models(output_config: OutputConfig) -> None:
    assert output_config.path is not None
    pipeline = FakeExecutablePipeline()
    results = PipelineResults({
        Designator('foo'): PipelineResult(prediction=Dataset(),
                                          executable_pipeline=pipeline)
    })

    dut = Saver(output_config=output_config)
    got = dut.save_all_models(results)

    assert got == {
        DES1: Path('a.pkl'),
        DES2: Path('b.pkl'),
    }

    file1_contents = (output_config.path / 'models' / 'foo' / got[DES1]).open(mode='rb').read()
    cucumber1 = Cucumber.deserialize(file1_contents)
    assert isinstance(cucumber1, Cucumber)
    assert cucumber1.filename == DES1
    assert cucumber1.hyperparams == {
        'param': 'value',
    }

    file2_contents = (output_config.path / 'models' / 'foo' / got[DES2]).open(mode='rb').read()
    cucumber2 = Cucumber.deserialize(file2_contents)
    assert isinstance(cucumber2, Cucumber)
    assert cucumber2.filename == DES2
    assert cucumber2.hyperparams == {
        'base_param': 'base_value',
        'param_to_override': 'value_to_override',

    }
    assert cucumber2.serialized_model == b'fake algorithm instance model\n'
