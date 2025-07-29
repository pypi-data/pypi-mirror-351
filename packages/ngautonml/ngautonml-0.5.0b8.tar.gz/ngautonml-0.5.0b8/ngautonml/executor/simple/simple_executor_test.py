'''Tests for the "simple" executor'''
import re
from typing import Dict, Optional, Tuple

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import logging
import pytest
import numpy as np
import pandas as pd
from sklearn import datasets  # type: ignore[import]

from ...algorithms.impl.algorithm import Algorithm
from ...algorithms.impl.fittable_algorithm_instance import FittableAlgorithmInstance
from ...algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import Designator, StepDesignator
from ...instantiator.executable_pipeline import (ExecutablePipeline,
                                                 FitError, PredictError)
from ...algorithms.connect import ConnectorModel
from ...wrangler.dataset import Dataset, Metadata, RoleName
from ...wrangler.dataset import DatasetKeys, Column, TableFactory

from ..cucumber import JarOfCucumbers

from .simple_instantiator import SimpleInstantiator
from .simple_executor import SimpleExecutor
from .simple_executable_pipeline import SimpleExecutablePipeline

# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code,protected-access

REFERENCE_DATASET = Dataset(
    a_key='a_value',
    another_key='another_value',
)


def make_pipeline(instantiator: SimpleInstantiator, name: Designator, **kwargs):
    pipe = BoundPipeline(name=name, tags={})
    connector = ConnectorModel()
    pipe.step(model=connector, new_key='a_key', another_key='another_key').set_name('connector1.1')
    pipe.step(model=connector, **kwargs)

    return instantiator.instantiate(pipeline=pipe)


def load_datasets() -> Tuple[Dataset, Dataset, Dataset]:
    # Load the diabetes dataset
    diabetes_x, diabetes_y = datasets.load_diabetes(return_X_y=True)

    # Use only one feature
    diabetes_x = diabetes_x[:, np.newaxis, 2]

    # Split the data into training/testing sets
    diabetes_x_train = diabetes_x[:-20]
    diabetes_x_test = diabetes_x[-20:]

    # Split the targets into training/testing sets
    diabetes_y_train = diabetes_y[:-20]
    diabetes_y_test = diabetes_y[-20:]

    metadata = Metadata(
        roles={RoleName.TARGET: [Column('target')]}
    )

    dataset_train = Dataset(metadata=metadata)
    dataset_train.covariates_table = TableFactory(
        pd.DataFrame(diabetes_x_train, columns=['attribute']))
    dataset_train.target_table = TableFactory(pd.DataFrame({'target': diabetes_y_train}))

    dataset_test = Dataset(metadata=metadata)
    dataset_test.covariates_table = TableFactory(
        pd.DataFrame(diabetes_x_test, columns=['attribute'])
    )
    ground_truth = Dataset(metadata=metadata)
    ground_truth.ground_truth_table = TableFactory({'target': diabetes_y_test})

    return (dataset_train, dataset_test, ground_truth)


def make_regression_pipeline(instantiator: SimpleInstantiator,
                             name: Designator
                             ) -> SimpleExecutablePipeline:
    catalog = AlgorithmCatalogAuto()
    regression = catalog.lookup_by_name('sklearn.linear_model.LinearRegression')
    connector = ConnectorModel()
    pipe = BoundPipeline(name=name, tags={})
    pipe.step(model=regression).set_name('regression')
    pipe.step(model=connector, result=DatasetKeys.PREDICTIONS_TABLE.value)
    return instantiator.instantiate(pipeline=pipe)


def strip_serial(key: StepDesignator) -> str:
    return re.sub('[0-9]+', 'NUM', key)


def test_fit_sunny_day() -> None:
    instantiator = SimpleInstantiator()
    des1 = Designator('foo')
    des2 = Designator('bar')
    executable1 = make_regression_pipeline(
        instantiator=instantiator,
        name=des1)
    pipe = BoundPipeline(name=des2, tags={})
    pipe.step(model=ConnectorModel(),
              new_key=DatasetKeys.COVARIATES_TABLE.value,
              another_key=DatasetKeys.TARGET_TABLE.value).set_name('connector_special_name')
    executable2 = instantiator.instantiate(pipe)
    pipelines: Dict[Designator, ExecutablePipeline] = {des1: executable1, des2: executable2}

    train, _, _ = load_datasets()

    dut = SimpleExecutor()

    got_training = dut.fit(dataset=train, pipelines=pipelines)
    jar = got_training.models(name=des2)
    assert isinstance(jar, JarOfCucumbers)
    assert set({strip_serial(key) for key in jar.keys()}
               ) == set({'@connect_NUM@connector_special_name'})
    # TODO(Merritt/Piggy): assert more here once this change is more complete


def test_predict_sunny_day() -> None:
    instantiator = SimpleInstantiator()
    des1 = Designator('foo')
    des2 = Designator('bar')
    executable1 = make_pipeline(instantiator=instantiator,
                                name=des1,
                                twice_transformed_key='new_key',
                                another_key='another_key')
    executable2 = make_pipeline(instantiator=instantiator,
                                name=des2,
                                twice_transformed_key2='new_key')

    pipelines: Dict[Designator, ExecutablePipeline] = {des1: executable1, des2: executable2}

    dut = SimpleExecutor()

    dut.fit(dataset=REFERENCE_DATASET, pipelines=pipelines)

    result = dut.predict(dataset=REFERENCE_DATASET, pipelines=pipelines)

    assert [r.prediction for r in result.values()] == [
        {'twice_transformed_key': 'a_value', 'another_key': 'another_value'},
        {'twice_transformed_key2': 'a_value'},
    ]


def test_parallel_sunny_day() -> None:
    instantiator = SimpleInstantiator()
    pipe = BoundPipeline(name=Designator('parallel_pipeline'), tags={})
    subpipe1 = pipe.new('connector_pipeline')
    subpipe1.step(model=ConnectorModel(), new_key='covariates_table').set_name('connector_step')
    subpipe2 = pipe.new('regression_pipeline')
    catalog = AlgorithmCatalogAuto()
    model = catalog.lookup_by_name('sklearn.linear_model.LinearRegression')
    subpipe2.step(model=model).set_name('regression_step')
    subpipe2.step(model=ConnectorModel(), result=DatasetKeys.PREDICTIONS_TABLE.value
                  ).set_name('regression_connect_step')
    pipe.parallel(connector=subpipe1, regression=subpipe2).set_name('parallel_step')
    executable = instantiator.instantiate(pipe)

    train, test, _ = load_datasets()

    dut = SimpleExecutor()

    fake_des = Designator('fake_des')

    dut.fit(dataset=train,
            pipelines={fake_des: executable})

    got_predict = dut.predict(dataset=test,
                              pipelines={fake_des: executable})

    got_result = list(got_predict.values())[0]
    assert got_result.prediction is not None
    got_connector = got_result.prediction['connector']
    got_regression = got_result.prediction['regression']

    assert set(got_connector.keys()) == {'new_key'}
    assert (got_connector['new_key'].as_(pd.DataFrame).iat[0, 0]
            == pytest.approx(0.07786338762689, 1e-6))
    assert set(got_regression.keys()) == {'result'}
    assert got_regression['result'].as_(pd.DataFrame).iat[0, 0] == pytest.approx(225.9732401, 1e-6)


class BrokenAlg(Algorithm):

    def instantiate(self, **hyperparams) -> FittableAlgorithmInstance:
        if hyperparams['kind'] == 'fit':
            del hyperparams['kind']
            return BrokenFitAlgInstance(parent=self, **hyperparams)
        if hyperparams['kind'] == 'predict':
            del hyperparams['kind']
            return BrokenPredictAlgInstance(parent=self, **hyperparams)
        raise NotImplementedError(f'Unimplemented kind: {hyperparams["kind"]}')


class BrokenFitAlgInstance(FittableAlgorithmInstance):
    _name = 'fit is broken'

    def fit(self, dataset: Optional[Dataset]) -> None:
        _ = 1 / 0

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        return dataset


class BrokenPredictAlgInstance(FittableAlgorithmInstance):

    def fit(self, dataset: Optional[Dataset]) -> None:
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        # we need this condition because the model's predict() gets called as part
        #   of the pipeline's fit() call, however we only want to raise an error
        #   on the pipeline's predict() call
        if 'hamster' in (dataset or {}):
            raise NotImplementedError('hamster')
        return dataset


def test_fit_error(caplog: pytest.LogCaptureFixture) -> None:
    pipe = BoundPipeline(name=Designator('broken_fit'))
    pipe.step(model=BrokenAlg(name='fit is broken', kind='fit'))
    executable = SimpleInstantiator().instantiate(pipeline=pipe)

    dut = SimpleExecutor()
    with caplog.at_level(logging.WARNING):
        got = dut.fit(
            dataset=Dataset(),
            pipelines={Designator('broken_fit'): executable})

    got_pipe = got[Designator('broken_fit')]
    assert isinstance(got_pipe, FitError)
    assert 'simple_executor_test.py' in str(got_pipe)
    assert 'ZeroDivisionError' in str(got_pipe)
    assert 'ZeroDivisionError' in caplog.text
    assert 'broken_fit' in caplog.text


def test_predict_error(caplog: pytest.LogCaptureFixture) -> None:
    pipe = BoundPipeline(name=Designator('broken_predict'))
    pipe.step(model=BrokenAlg(name='predict is broken', kind='predict'))
    executable = SimpleInstantiator().instantiate(pipeline=pipe)

    dut = SimpleExecutor()

    des = Designator('broken_predict')
    pipes: Dict[Designator, ExecutablePipeline] = {des: executable}
    dut.fit(dataset=Dataset(), pipelines=pipes)
    with caplog.at_level(logging.WARNING):
        got = dut.predict(
            dataset=Dataset({'hamster': 'something'}),
            pipelines=pipes)
    got_pipe = got[des].prediction
    assert got_pipe is not None
    assert isinstance(got_pipe['error'], PredictError)
    assert 'simple_executor_test.py' in str(got_pipe['error'])
    assert 'NotImplementedError' in str(got_pipe['error'])
    assert 'hamster' in str(got_pipe['error'])
    assert 'hamster' in caplog.text
    assert 'broken_predict' in caplog.text


def test_predict_after_fit_error() -> None:
    '''If we get a fit error, we want pipe.predict() to output that fit error
    inside its prediction dataset.
    '''
    pipe = BoundPipeline(name=Designator('broken_fit'))
    pipe.step(model=BrokenAlg(name='fit is broken', kind='fit'))
    executable = SimpleInstantiator().instantiate(pipeline=pipe)

    des = Designator('broken_fit')
    pipes: Dict[Designator, ExecutablePipeline] = {des: executable}

    dut = SimpleExecutor()
    dut.fit(dataset=Dataset(),
            pipelines=pipes)

    got = dut.predict(dataset=Dataset(),
                      pipelines=pipes)

    got_pipe = got[des].prediction
    assert got_pipe is not None
    assert isinstance(got_pipe['error'], FitError)
    assert 'simple_executor_test.py' in str(got_pipe['error'])
    assert 'ZeroDivisionError' in str(got_pipe['error'])
