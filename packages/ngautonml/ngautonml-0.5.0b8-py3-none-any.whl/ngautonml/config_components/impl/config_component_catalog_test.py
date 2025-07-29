'''Test the config component catalog'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, List
from .config_component import ConfigComponent
from .config_component_catalog import ConfigComponentCatalogStub
# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code


class TempConfigComponent(ConfigComponent):

    name = "temp_config_component"
    tags: Dict[str, List[str]] = {}

    def validate(self, **kwargs) -> None:
        pass


def test_register() -> None:
    dut = ConfigComponentCatalogStub()
    assert 'temp_config_component' == dut.register(obj=TempConfigComponent)


def test_lookup_by_name() -> None:
    dut = ConfigComponentCatalogStub()
    some_component = TempConfigComponent
    dut.register(obj=some_component)
    got = dut.lookup_by_name('temp_config_component')
    assert isinstance(got, type)
    assert isinstance(got(clause={}), TempConfigComponent)
