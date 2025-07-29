'''Test the metric catalog'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .metric import MetricStub
from .metric_catalog import MetricCatalogStub

# pylint: disable=missing-function-docstring,duplicate-code


def test_register() -> None:
    dut = MetricCatalogStub()
    dummy_metric = MetricStub()
    assert 'stub_metric' == dut.register(obj=dummy_metric)


def test_register_name() -> None:
    dut = MetricCatalogStub()
    dummy_metric = MetricStub()
    assert 'somenamedmetric' == dut.register(obj=dummy_metric, name='SomeNamedMetric')


def test_lookup_by_name() -> None:
    dut = MetricCatalogStub()
    some_metric = MetricStub()
    dut.register(obj=some_metric, name='SomeNamedMetric')
    assert dut.lookup_by_name('SomeNamedMetric') == some_metric


def test_lookup_one_by_tag() -> None:
    dut = MetricCatalogStub()
    dummy_metric = MetricStub()
    dut.register(obj=dummy_metric, name='NamedDummyMetric', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 1


def test_lookup_by_tag_fail() -> None:
    dut = MetricCatalogStub()
    dummy_metric = MetricStub()
    dut.register(obj=dummy_metric, name='NamedDummyMetric', tags={'k1': ['v1']})
    assert len(dut.lookup_by_tag_and(k1='different_value')) == 0


def test_lookup_multi_by_tag() -> None:
    dut = MetricCatalogStub()
    dummy_metric = MetricStub()
    dut.register(obj=dummy_metric, name="Name1", tags={'k1': ['v1']})
    dummy_metric2 = MetricStub()
    dut.register(obj=dummy_metric2, name="Name2", tags={'k1': ['v1']})
    dummy_metric3 = MetricStub()
    dut.register(obj=dummy_metric3, name="Name3", tags={'k1': ['different_value']})
    assert len(dut.lookup_by_tag_and(k1='v1')) == 2
