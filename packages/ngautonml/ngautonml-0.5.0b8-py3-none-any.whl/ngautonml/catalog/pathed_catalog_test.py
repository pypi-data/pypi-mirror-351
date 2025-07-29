'''Tests for pathed_catalog.py.'''

from pathlib import Path

import pytest

from .catalog import Catalog
from .pathed_catalog import PathedCatalog
from .widgets.impl.widget_catalog import NamedWidget

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code


EXTRA_WIDGET_SOURCE = '''
from typing import Any, Optional
from ngautonml.catalog.widgets.impl.widget_catalog import NamedWidget, WidgetCatalog

class ExtraWidget(NamedWidget):
    _name = 'extra_widget'
    _tags = {
        'some_tag': ['extra_dir']
    }


def register(catalog: WidgetCatalog):
    catalog.register(ExtraWidget())
'''


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = retval / 'extra_widget.py'
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(EXTRA_WIDGET_SOURCE)
    return retval


def test_home_directory_auto(tmp_path) -> None:
    dut: Catalog = PathedCatalog(paths=[tmp_path, Path(__file__).parent / 'widgets'])
    got1 = dut.lookup_by_name('extra_widget')
    assert isinstance(got1, NamedWidget)
    assert got1.tags['some_tag'] == ['extra_dir']
    got2 = dut.lookup_by_name('Gizmo')
    assert isinstance(got2, NamedWidget)
    assert got2.tags['some_tag'] == ['test_dir']
    assert hasattr(got2, 'quux')
