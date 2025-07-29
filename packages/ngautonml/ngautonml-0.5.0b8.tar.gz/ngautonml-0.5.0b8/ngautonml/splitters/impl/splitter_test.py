'''tests for splitter.py'''
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=protected-access,duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...problem_def.cross_validation_config import CrossValidationConfig
from ...wrangler.dataset import Dataset
from .splitter import Splitter, SplitDataset


class FakeSplitter(Splitter):
    _name = 'fake'
    _hyperparams = {
        'k1': 'v1',
        'k2': 'v2'
    }

    def split(self,
              dataset: Dataset,
              **unused_kwargs) -> SplitDataset:
        return SplitDataset()


def test_hyperparam_overrides() -> None:
    dut = FakeSplitter(cv_config=CrossValidationConfig({}))
    assert dut._hyperparams == {
        'k1': 'v1',
        'k2': 'v2'
    }
    assert dut.hyperparams(k2='new_val', new_key='new_val2') == {
        'k1': 'v1',
        'k2': 'new_val',
        'new_key': 'new_val2'
    }
