'''tests for cross_validator_auto.py'''
# pylint: disable=missing-function-docstring,duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..stub_cross_validator import StubCrossValidator
from .cross_validator_auto import CrossValidatorCatalogAuto


def test_sunny_day() -> None:
    dut = CrossValidatorCatalogAuto()
    stub = dut.lookup_by_name('stub_cross_validator')
    assert isinstance(stub, StubCrossValidator)
