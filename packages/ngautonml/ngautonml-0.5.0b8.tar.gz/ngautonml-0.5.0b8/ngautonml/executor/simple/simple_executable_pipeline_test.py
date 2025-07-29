'''Tests for SimpleExecutablePipeline'''
import pickle

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import re
from typing import Dict, Optional

import numpy as np
import pytest

from ...algorithms.connect import ConnectorModel
from ...algorithms.impl.algorithm import Algorithm
from ...algorithms.impl.algorithm_instance import AlgorithmInstance
from ...algorithms.impl.fittable_algorithm_instance import UntrainedError
from ...algorithms.impl.fittable_algorithm_instance import FittableAlgorithmInstance
from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import Designator, StepDesignator
from ...instantiator.executable_pipeline import FitError
from ...wrangler.dataset import Dataset
from ..cucumber import JarOfCucumbers
from .simple_executable_pipeline import SimpleExecutablePipeline

# pylint: disable=missing-function-docstring,missing-class-docstring,protected-access,duplicate-code


class FakeFitter(Algorithm):
    '''Pretend to fit data.'''
    _name = 'fitter_model'

    def instantiate(self, **kwargs) -> AlgorithmInstance:
        return FakeFitterInstance(parent=self, **kwargs)


class FakeFitterInstance(FittableAlgorithmInstance):
    '''Pretend to fit data.'''
    _hyperparams: Dict[str, str]
    _training_data: Dataset

    def __init__(self, parent, serialized_model: Optional[bytes] = None, **kwargs):
        super().__init__(parent=parent)
        self._training_data = Dataset()
        if serialized_model is not None:
            self._training_data = pickle.loads(serialized_model)
        self._hyperparams = kwargs

    def deserialize(self, serialized_model: bytes) -> 'FakeFitterInstance':
        self._training_data = pickle.loads(serialized_model)
        return self

    def serialize(self) -> bytes:
        '''Return a serialized version of a trained model.'''
        return pickle.dumps(self._training_data, pickle.HIGHEST_PROTOCOL)

    def fit(self, dataset: Optional[Dataset]) -> None:
        '''Fit a model based on train data.'''
        if dataset is not None:
            self._training_data = Dataset(dataset.copy())
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        retval = dataset.output()
        retval.update(dataset)
        retval.update(self._hyperparams)
        return retval


REFERENCE_DATASET = Dataset(
    a_key='a_value',
    another_key='another_value',
)


def strip_serial(key: StepDesignator) -> str:
    return re.sub('[0-9]+', 'NUM', key)


def test_fit_sunny_day() -> None:
    pipe = BoundPipeline(name=Designator('foo'), tags={})
    connector = ConnectorModel()
    fitter = FakeFitter()
    pipe.step(
        model=connector,
        a_key_renamed='a_key',
        another_key='another_key').set_name('connector')
    pipe.step(model=fitter).set_name('fitter')

    dut = SimpleExecutablePipeline(pipe)
    got_fit: JarOfCucumbers = dut.fit(dataset=REFERENCE_DATASET)

    got_stripped_jar = {strip_serial(key): val for key, val in got_fit.items()}
    assert set(got_stripped_jar.keys()) == set({
        '@connect_NUM@connector', '@fitter_model_NUM@fitter'})

    got_fitter_cucumber = got_stripped_jar['@fitter_model_NUM@fitter']
    got_fitter_instance = got_fitter_cucumber.deserialize_model(alg=FakeFitter())
    assert isinstance(got_fitter_instance, FakeFitterInstance)

    # connector will transform the data before it gets saved in the fitter
    want_fitter = {
        'a_key_renamed': 'a_value',
        'another_key': 'another_value',
    }
    assert got_fitter_instance._training_data == want_fitter


def test_predict_sunny_day() -> None:
    pipe = BoundPipeline(name=Designator('foo'), tags={})
    connector = ConnectorModel()
    fitter = FakeFitter()
    pipe.step(model=connector,
              a_key_renamed='a_key',
              another_key='another_key').set_name('connector')
    pipe.step(model=fitter, new_key='new_value').set_name('fitter')

    dut = SimpleExecutablePipeline(pipe)
    dut.fit(dataset=REFERENCE_DATASET)

    # Connector will rename a key, FakeFitter will add a new key and value
    got_predict = dut.predict(dataset=REFERENCE_DATASET)
    want_predict = {
        'a_key_renamed': 'a_value',
        'another_key': 'another_value',
        'new_key': 'new_value'
    }
    assert got_predict.prediction is not None
    assert set(got_predict.prediction.keys()) == set(want_predict.keys())
    assert set(got_predict.prediction.values()) == set(want_predict.values())


def test_fit_must_precede_predict() -> None:
    pipe = BoundPipeline(name=Designator('foo'), tags={})
    fitter = FakeFitter()
    pipe.step(model=fitter).set_name('fitter')
    dut = SimpleExecutablePipeline(pipeline=pipe)

    # the only model in this pipeline is the FakeFitter, which notably
    #   does *not* raise an UntrainedError if predict() is called
    #   before fit.  Thus, we test that SimpleExecutablePipeline does so
    #   natively.
    with pytest.raises(UntrainedError):
        dut.predict(dataset=Dataset())


def test_subpipeline_designator_propagation() -> None:
    '''Test that subpipelines in a parallel step are saved with the same
            designator as their parent pipeline.
    '''
    pipe = BoundPipeline(name=Designator('foo'), tags={})
    par1 = pipe.new(name='par1')
    par1.step(model=ConnectorModel(), new_k1='a_key')
    par2 = pipe.new(name='par2')
    par2.step(model=ConnectorModel(), new_k2='another_key')
    pipe.parallel(par1=par1, par2=par2)
    pipe.step(model=ConnectorModel(),
              from_par1=['par1', 'new_k1'],
              from_par2=['par2', 'new_k2'])

    dut = SimpleExecutablePipeline(pipeline=pipe)
    assert dut.designator == Designator('foo')
    got_fit: JarOfCucumbers = dut.fit(dataset=REFERENCE_DATASET)
    for cucumber in got_fit.values():
        assert cucumber.pipeline_designator == Designator('foo')


class RandomAlgorithmInstance(AlgorithmInstance):

    def __init__(self, parent: Algorithm, **hyperparams):
        super().__init__(parent)
        if 'random_seed' in hyperparams:
            # TODO(piggy): use generator instead of setting globally to avoid flakiness
            np.random.seed([hyperparams['random_seed']])

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        retval = dataset.output()
        retval['result'] = np.random.randint(0, 10, 5)
        return retval


class RandomAlgorithm(Algorithm):
    def instantiate(self, **hyperparams) -> RandomAlgorithmInstance:
        return RandomAlgorithmInstance(parent=self, **self.hyperparams(**hyperparams))


def test_set_seed() -> None:
    pipe = BoundPipeline(name=Designator('foo'), tags={})
    pipe.step(model=RandomAlgorithm(random_seed=1234))
    dut = SimpleExecutablePipeline(pipeline=pipe)

    dut.fit(Dataset())
    got = dut.predict(Dataset())

    # For seed == 1234
    assert got.prediction is not None
    assert (got.prediction['result'] == [2, 1, 9, 4, 2]).all()


class BrokenAlg(Algorithm):

    def instantiate(self, **hyperparams) -> FittableAlgorithmInstance:
        return BrokenAlgInstance(parent=self, **hyperparams)


class BrokenAlgInstance(FittableAlgorithmInstance):
    _name = 'fit is broken'

    def fit(self, dataset: Optional[Dataset]) -> None:
        if dataset is None or 'better_data' not in dataset:
            _ = 1 / 0
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        return dataset


def test_fit_error_reset() -> None:
    '''If we get an error while fitting, the results of predict() will always
    be a FitError.

    If we refit on data that works correctly, we want this error to go away.
    '''
    pipe = BoundPipeline(name=Designator('conditionally_broken_fit'))
    pipe.step(model=BrokenAlg(name='conditionally_broken_alg'))
    dut = SimpleExecutablePipeline(pipeline=pipe)
    dut.set_fit_error(FitError())

    test_data = Dataset({'hamster': 'gerbil'})

    dut.fit(dataset=Dataset({'better_data': 'good data goes here'}))

    got_fixed = dut.predict(dataset=test_data)
    assert got_fixed.prediction == test_data
