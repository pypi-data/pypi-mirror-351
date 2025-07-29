'''Tests for splitter_auto.py'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...problem_def.cross_validation_config import CrossValidationConfig
from ..k_fold_splitter import KFoldSplitter

from .splitter_auto import SplitterCatalogAuto

# pylint: disable=missing-function-docstring,duplicate-code


def test_sunny_day() -> None:
    dut = SplitterCatalogAuto(cv_config=CrossValidationConfig({}))
    single_fold = dut.lookup_by_name('sklearn.model_selection.KFold')
    assert isinstance(single_fold, KFoldSplitter)


def test_lookup_by_task_defaults_properly() -> None:
    dut = SplitterCatalogAuto(cv_config=CrossValidationConfig({}))
    single_fold = dut.lookup_by_task('unknown')
    assert isinstance(single_fold, KFoldSplitter)
