'''Test object to register in a Widget catalog.'''
from typing import Optional

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ngautonml.catalog.catalog import upcast
from ngautonml.catalog.widgets.impl.widget_catalog import WidgetCatalog, NamedWidget
# pylint: disable=duplicate-code


class DooDad(NamedWidget):
    '''Test object to register in a Widget catalog.'''
    tags = {
        'some_tag': ['test_dir'],
    }
    frob: Optional[str]
    quux: Optional[str]

    def __init__(self, frob: Optional[str] = None, quux: Optional[str] = None):
        super().__init__('DooDad')
        self.frob = frob
        self.quux = quux


def register(catalog: WidgetCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    doodad = DooDad(*args, **kwargs)
    catalog.register(doodad, doodad.name, upcast(doodad.tags))
