'''Tests for identity model.'''
from .identity import IdentityModel
from ..wrangler.dataset import Dataset
# pylint: disable=missing-function-docstring,duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


def test_sunny_day() -> None:
    model = IdentityModel().instantiate()

    dataset = Dataset(
        a=[1, 2, 3],
        b='something else'
    )

    got = model.predict(dataset=dataset)
    assert got == dataset
