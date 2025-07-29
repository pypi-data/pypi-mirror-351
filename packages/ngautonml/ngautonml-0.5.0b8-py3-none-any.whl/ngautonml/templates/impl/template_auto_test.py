'''Test the autoloading template catalog.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .parallel_step import ParallelStep
from .query_step import QueryStep
from .template_auto import TemplateCatalogAuto

# pylint: disable=missing-function-docstring,duplicate-code


def test_sunny_day() -> None:
    dut = TemplateCatalogAuto()
    demo_template = dut.lookup_by_name('tabular_classification')
    assert isinstance(demo_template.steps[1], ParallelStep)
    subpipe_keys = sorted(list(demo_template.steps[1].subpipeline_keys))
    assert ['attributes_dataset', 'target_dataset'] == subpipe_keys
    assert isinstance(demo_template.steps[3], QueryStep)


def test_lookup_by_datatype() -> None:
    dut = TemplateCatalogAuto()
    templates = dut.lookup_by_datatype(data_type='tabular')
    assert 'tabular_classification' in templates


def test_lookup_by_task() -> None:
    dut = TemplateCatalogAuto()
    templates = dut.lookup_by_task(task='binary_classification')
    assert 'tabular_classification' in templates


def test_lookup_by_both() -> None:
    dut = TemplateCatalogAuto()
    templates = dut.lookup_by_both(
        data_type='tabular',
        task='binary_classification')
    assert 'tabular_classification' in templates
