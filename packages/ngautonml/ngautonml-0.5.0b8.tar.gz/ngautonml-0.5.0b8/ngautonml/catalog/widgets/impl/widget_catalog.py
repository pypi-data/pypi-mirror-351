'''Widgets for testing.'''

from ...memory_catalog import MemoryCatalog
from ...catalog_element_mixin import CatalogElementMixin


class Widget():
    '''This is the thing that is stored in WidgetCatalog.'''


class NamedWidget(Widget, CatalogElementMixin):
    '''Widget that properly inherits from CatalogElementMixin and thus has a name'''


class WidgetCatalog(MemoryCatalog[Widget]):
    '''This is the class we will exercise.'''
