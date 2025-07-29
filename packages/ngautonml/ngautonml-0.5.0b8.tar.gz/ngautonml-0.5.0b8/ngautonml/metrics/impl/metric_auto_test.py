'''Tests for metric_auto.py.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os
from pathlib import Path

import pytest

from ...wrangler.constants import PACKAGE_NAME
from ..sklearn_metrics import SklearnMetric
from .metric import Metric
from .metric_auto import MetricCatalogAuto

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code


FAKE_METRIC_SOURCE = '''
from typing import Any, Optional
from ngautonml.metrics.impl.metric import Metric
from ngautonml.metrics.impl.metric_catalog import MetricCatalog

class FakeMetric(Metric):
    _name = 'fake_metric'
    _tags = {
        'some_tag': ['some_value']
    }

    def calculate(self, pred: Any, ground_truth: Optional[Any] = None) -> float:
        return 1.0


def register(catalog: MetricCatalog):
    catalog.register(FakeMetric())
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = retval / f'.{PACKAGE_NAME}' / 'plugins' / 'metrics' / 'fake_metric.py'
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(FAKE_METRIC_SOURCE)
    return retval


def test_metric_catalog_auto() -> None:
    dut = MetricCatalogAuto()
    assert isinstance(dut.lookup_by_name('ROC_AUC_score'), SklearnMetric)
    assert len(dut.lookup_by_tag_and(task='binary_classification')) >= 2


def test_home_directory_auto(tmp_path) -> None:
    os.environ['HOME'] = str(tmp_path)
    dut = MetricCatalogAuto()
    got = dut.lookup_by_name('fake_metric')
    assert isinstance(got, Metric)
    assert got.tags['some_tag'] == ['some_value']
