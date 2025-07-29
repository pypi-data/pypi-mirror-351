'''Tests for params.py'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pytest

from ..wrangler.constants import RangeMethod

from .params import Matcher
from .params import ParamRange, ParamRanges, Selector, Override, Overrides

# pylint: disable=missing-function-docstring,duplicate-code


SAMPLE_OVERRIDE = Override(
    selector=Selector({
        Matcher.ALGORITHM: 'foo_model'
    }),
    params=ParamRanges(
        some_param=ParamRange(
            method=RangeMethod.FIXED,
            prange='some_param_value'
        )
    )
)


def test_overrides():
    dut = Overrides()
    dut.append(SAMPLE_OVERRIDE)

    assert len(dut) == 1
    for override in dut:
        assert override.selector[Matcher('algorithm')] == 'foo_model'
        assert override.params['some_param'].range == 'some_param_value'


def test_override_failures():
    dut = Overrides()

    with pytest.raises(TypeError, match='not subscriptable'):
        dut[0]  # pylint: disable=pointless-statement, unsubscriptable-object

    with pytest.raises(TypeError, match='does not support item assignment'):
        dut[0] = SAMPLE_OVERRIDE  # pylint: disable=unsupported-assignment-operation
