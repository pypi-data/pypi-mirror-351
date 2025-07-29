'''Test the catalog shelf module.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, Iterable, Set, Tuple, Union
import pytest

from .catalog import Catalog, CatalogLookupError
from .memory_catalog import MemoryCatalog
from .catalog_shelf import CatalogShelf
from .catalog_element_mixin import CatalogElementMixin

# pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code


class Widget():
    '''This is the thing that is stored in WidgetCatalog.'''


class NamedWidget(Widget, CatalogElementMixin):
    '''Widget that properly inherits from CatalogElementMixin and thus has a name'''


class WidgetCatalog(MemoryCatalog[Widget]):
    '''This is the class we will exercise.'''


class WidgetNonMemoryCatalog(Catalog[Widget]):
    '''This is a non-memory catalog.'''

    @property
    def tagtypes(self) -> Set[str]:
        return set()

    def all_objects(self) -> Iterable[Widget]:
        return []

    def items(self) -> Iterable[Tuple[str, Widget]]:
        return []

    def tagvals(self, tagtype: str) -> Set[str]:
        return set()

    def lookup_by_name(self, name: str) -> Widget:
        raise CatalogLookupError()

    def lookup_by_tag_and(self, **tags: Union[str, Iterable[str]]) -> Dict[str, Widget]:
        return {}


def test_items():
    '''Register a widget into a shelf with an empty catalog at the start.'''
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1 = NamedWidget(name='widget1')
    catalog2.register(widget1)
    widget2 = NamedWidget(name='widget2')
    dut = CatalogShelf(catalog1, catalog2)
    dut.register(widget2)
    assert dict(dut.items()) == {
        'widget1': widget1,
        'widget2': widget2,
    }


def test_one_catalog():
    '''Load a catalog into the Shelf'''
    catalog1 = WidgetCatalog()
    widget1 = NamedWidget(name='widget1')
    catalog1.register(widget1)
    dut = CatalogShelf(catalog1)
    assert dut.lookup_by_name('widget1') == widget1


def test_lookup_by_name():
    '''Load two catalogs into the shelf and call an algorithm from the second'''
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1 = NamedWidget(name='widget1')
    catalog1.register(widget1)
    widget2 = NamedWidget(name='widget2')
    catalog2.register(widget2)
    dut = CatalogShelf(catalog1, catalog2)
    assert dut.lookup_by_name('widget1') == widget1
    assert dut.lookup_by_name('widget2') == widget2


def test_lookup_by_name_conflict():
    '''Load two catalogs into the shelf and call an algorithm that is in both'''
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1 = NamedWidget(name='conflicting_widget', tags={'version': ['one']})
    catalog1.register(widget1)
    widget2 = NamedWidget(name='conflicting_widget', tags={'version': ['two']})
    catalog2.register(widget2)
    dut = CatalogShelf(catalog1, catalog2)
    assert dut.lookup_by_name('conflicting_widget').tags['version'][0] == 'one'


def test_lookup_by_tags_conflicting_names() -> None:
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1 = NamedWidget(name='conflicting_widget', tags={'version': ['one']})
    catalog1.register(widget1)
    widget2 = NamedWidget(name='conflicting_widget', tags={'version': ['one'],
                                                           'label': ['another']})
    catalog2.register(widget2)
    dut = CatalogShelf(catalog1, catalog2)
    res = dut.lookup_by_tag_and(version='one')
    assert len(res) == 1
    got = res['conflicting_widget']
    assert isinstance(got, NamedWidget)
    assert 'label' not in got.tags


def test_tagvals() -> None:
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1 = NamedWidget(name='widget1', tags={'version': ['one']})
    catalog1.register(widget1)
    widget2 = NamedWidget(name='widget2', tags={'version': ['two'],
                                                'label': ['another']})
    catalog2.register(widget2)
    dut = CatalogShelf(catalog1, catalog2)
    res = dut.tagvals('version')
    assert res == {'one', 'two'}


def test_tagtypes() -> None:
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1 = NamedWidget(name='widget1', tags={'version': ['one']})
    catalog1.register(widget1)
    widget2 = NamedWidget(name='widget2', tags={'version': ['two'],
                                                'label': ['another']})
    catalog2.register(widget2)
    dut = CatalogShelf(catalog1, catalog2)
    res = dut.tagtypes
    assert res == {'label', 'version'}


def test_prepend() -> None:
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1 = NamedWidget(name='conflict', tags={'version': ['one']})
    catalog1.register(widget1)
    widget2 = NamedWidget(name='conflict', tags={'version': ['two']})
    catalog2.register(widget2)
    dut = CatalogShelf(catalog1, catalog2)

    got1 = dut.lookup_by_name('conflict')
    assert got1.tags == {'version': ['one']}

    dut.prepend(catalog2)
    got2 = dut.lookup_by_name('conflict')
    assert got2.tags == {'version': ['two']}


def test_register():
    '''Register a widget into a shelf with an empty catalog at the start.'''
    catalog1 = WidgetCatalog()
    catalog2 = WidgetCatalog()
    widget1_1 = NamedWidget(name='widget1', tags={'version': ['one']})
    catalog2.register(widget1_1)
    widget1_2 = NamedWidget(name='widget1', tags={'version': ['two']})
    dut = CatalogShelf(catalog1, catalog2)
    dut.register(widget1_2)
    assert dut.lookup_by_name('widget1').tags['version'][0] == 'two'


def test_register_fail():
    '''Running register() on a shelf should fail if the first catalog is not a MemoryCatalog.'''
    catalog1 = WidgetNonMemoryCatalog()
    catalog2 = WidgetCatalog()
    widget1_1 = NamedWidget(name='widget1', tags={'version': ['one']})
    catalog2.register(widget1_1)
    widget1_2 = NamedWidget(name='widget1', tags={'version': ['two']})
    dut = CatalogShelf(catalog1, catalog2)
    with pytest.raises(AssertionError, match='first catalog'):
        dut.register(widget1_2)
    looked_up = dut.lookup_by_name('widget1')
    assert isinstance(looked_up, NamedWidget)
    assert looked_up.tags['version'][0] == 'one'
