'''Tests for auton_simple_domain_confusion.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pandas as pd
import numpy as np
import pytest

from ...tables.impl.table_auto import TableCatalogAuto
from ...wrangler.dataset import Dataset

from .auton_moment_matcher import AutonMomentMatcher
from ..moments import Moments

# pylint: disable=missing-function-docstring,duplicate-code
_ = TableCatalogAuto()


def test_identity():

    source = Dataset(
        dataframe=pd.DataFrame({
            'a': [1.5, 2.5, 3.5],
            'b': [4.0, 5.0, 6.0]
        }),
    )
    preprocessor = Moments().instantiate()
    preprocessor.fit(source)
    source_params = preprocessor.predict(None)

    train_population = Dataset(
        dataframe=pd.DataFrame({
            'a': [1.5, 2.5, 3.5],
            'b': [4.0, 5.0, 6.0]
        }),
        hyperparams=source_params['hyperparams']
    )

    test_population = Dataset(
        dataframe=pd.DataFrame({
            'a': [1.5, 2.5, 3.5],
            'b': [4.0, 5.0, 6.0]
        }),
        hyperparams=source_params['hyperparams']
    )

    model = AutonMomentMatcher()
    dut = model.instantiate()

    dut.fit(train_population)

    got = dut.predict(test_population)

    np.testing.assert_allclose(got.dataframe_table.as_(np.ndarray),
                               test_population.dataframe_table.as_(np.ndarray), atol=.001)


def test_mean_shifted():

    source = Dataset(
        dataframe=pd.DataFrame({
            'a': [3.5, 1.5, 7.5],
            'b': [4.0, 5.0, 6.0]
        }),
    )
    preprocessor = Moments().instantiate()
    preprocessor.fit(source)
    source_params = preprocessor.predict(None)

    train_population = Dataset(
        dataframe=pd.DataFrame({
            'a': np.array([3.5, 1.5, 7.5]) + 10,
            'b': np.array([4.0, 5.0, 6.0]) + 10

        }),
        hyperparams=source_params['hyperparams']
    )

    model = AutonMomentMatcher()
    dut = model.instantiate()

    dut.fit(train_population)

    got = dut.predict(train_population)

    np.testing.assert_allclose(got.dataframe_table.mean(axis=0).as_(np.ndarray),
                               np.array([np.mean([3.5, 1.5, 7.5]), 5]), atol=.001)


def test_sunny_day():

    source_cov = np.array([[1, 2], [-3, 9]])
    source_mu = np.array([-6, 3])
    target_cov = np.array([[8, -1], [1, 4]])
    target_mu = np.array([0.2, 7.3])

    # Ensure covariances are PSD
    source_cov = source_cov.T @ source_cov
    target_cov = target_cov.T @ target_cov

    np.random.seed(1)
    source_df = pd.DataFrame(
        data=np.random.multivariate_normal(source_mu, source_cov, size=10000),
        columns=['a', 'b'])
    target_train_df = pd.DataFrame(
        data=np.random.multivariate_normal(target_mu, target_cov, size=10000),
        columns=['a', 'b'])
    target_test_df = pd.DataFrame(
        data=np.random.multivariate_normal(target_mu, target_cov, size=10000),
        columns=['a', 'b'])

    source = Dataset(dataframe=source_df)
    preprocessor = Moments().instantiate()
    preprocessor.fit(source)
    source_params = preprocessor.predict(None)

    train_population = Dataset(
        dataframe=target_train_df,
        hyperparams=source_params['hyperparams']
    )

    test_population = Dataset(
        dataframe=target_test_df
    )

    model = AutonMomentMatcher()
    dut = model.instantiate()

    dut.fit(train_population)

    got = dut.predict(test_population)

    np.testing.assert_allclose(got.dataframe_table.mean(axis=0), source_mu, rtol=.05)
    np.testing.assert_allclose(np.cov(got.dataframe_table.as_(np.ndarray).T), source_cov, rtol=.05)


def test_hyperparams_required():
    model = AutonMomentMatcher()
    dut = model.instantiate()

    with pytest.raises(ValueError,
                       match=r'mean.*required.*confusion.*\n.*covariance.*required.*confusion'):
        dut.hyperparams()


def test_hyperparams_set_in_constructor():
    model = AutonMomentMatcher()
    dut = model.instantiate(mean=np.array([1, 2]), covariance=np.array([[1, 2], [3, 4]]))

    assert np.all(dut.hyperparams()['mean'] == np.array([1, 2]))
    assert np.all(dut.hyperparams()['covariance'] == np.array([[1, 2], [3, 4]]))


def test_hyperparams_override():
    model = AutonMomentMatcher()
    base_mean = np.array([3, 4])
    base_covariance = np.array([[3, 4], [5, 6]])
    override_covariance = np.array([[1, 2], [3, 4]])
    dut = model.instantiate(mean=base_mean, covariance=base_covariance)

    got = dut.hyperparams(covariance=override_covariance)
    assert np.all(got['mean'] == base_mean)
    assert np.all(got['covariance'] == override_covariance)
