'''tests for cross_validator.py'''
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=protected-access,duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..stub_cross_validator import StubCrossValidator


class FakeCV(StubCrossValidator):
    _name = 'fake_cv_default_hyperparams'
    _hyperparams = {
        'k1': 'v1',
        'k2': 'v2'
    }


def test_hyperparam_overrides() -> None:
    dut = FakeCV()
    assert dut._hyperparams == {
        'k1': 'v1',
        'k2': 'v2'
    }
    assert dut.hyperparams(k2='new_val', new_key='new_val2') == {
        'k1': 'v1',
        'k2': 'new_val',
        'new_key': 'new_val2'
    }


class FakeCVNoDefaults(StubCrossValidator):
    _name = 'fake_cv_no_default_hyperparams'


def test_no_default_hyperparams() -> None:
    dut = FakeCVNoDefaults()
    assert not dut._hyperparams
