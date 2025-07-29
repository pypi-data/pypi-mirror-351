'''Tests for metric_config'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pytest

from .metric_config import MetricConfig, MetricConfigError
# pylint: disable=missing-function-docstring,duplicate-code


def test_metric_config_rainy_day():
    dut = MetricConfig(clause={
        'm1': {'param1': 'value1'},
        'm2': {},
    })
    with pytest.raises(MetricConfigError, match='must have exactly 1'):
        dut.validate()
