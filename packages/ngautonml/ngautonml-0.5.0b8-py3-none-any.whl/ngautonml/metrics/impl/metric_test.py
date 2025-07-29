'''Tests for the Metric Base class implementations'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional

import pytest

from ...catalog.memory_catalog import CatalogNameError
from ...wrangler.dataset import Dataset
from .metric import Metric

# pylint: disable=missing-function-docstring,duplicate-code
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class ExampleMetric(Metric):
    _name = 'TestMetric'
    _high = True

    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        return 0.0


def test_missing_name():

    class BadTestMetric(Metric):
        def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
            return 0.0

    with pytest.raises(CatalogNameError):
        BadTestMetric()


def test_name():
    test_metric = ExampleMetric()
    assert test_metric.name == 'testmetric'
