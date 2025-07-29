'''Tests for plugin_catalog.py.'''

import os
from pathlib import Path
import subprocess

import pytest

from .catalog import Catalog
from .plugin_catalog import PluginCatalog
from .widgets.impl.widget_catalog import NamedWidget

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code

EXTRA_WIDGET_SOURCE = '''
from typing import Any, Optional
from ngautonml.catalog.widgets.impl.widget_catalog import NamedWidget, WidgetCatalog

class ExtraWidget(NamedWidget):
    _name = 'Gizmo'
    _tags = {
        'some_tag': ['home_directory']
    }


def register(catalog: WidgetCatalog):
    catalog.register(ExtraWidget())
'''


@pytest.fixture(scope="session")
def home_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    retval = tmp_path_factory.mktemp("data")
    source_path = retval / '.ngautonml' / 'plugins' / 'widgets' / 'extra_widget.py'
    source_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open('wt') as file:
        file.write(EXTRA_WIDGET_SOURCE)
    return retval


def test_home_directory_auto(home_path) -> None:
    os.environ['HOME'] = str(home_path)
    dut: Catalog = PluginCatalog('widgets', default_root=Path(__file__).parent)
    got1 = dut.lookup_by_name('Gizmo')
    assert isinstance(got1, NamedWidget)
    # if this were using the Gizmo in ./widgets/some_subfolder/gizmo.py,
    #   the value of 'some_tag' would be 'test_dir'
    assert got1.tags['some_tag'] == ['home_directory']

    got2 = dut.lookup_by_name('DooDad')
    assert isinstance(got2, NamedWidget)
    # we are using the DooDad in ./widgets/doodad.py, so the
    #   value of 'some_tag_ is 'test_dir'
    assert got2.tags['some_tag'] == ['test_dir']
    assert hasattr(got2, 'quux')


def test_with_plugin() -> None:
    if 'PYTEST_XDIST_WORKER' in os.environ:
        # This test flakes a LOT under xdist. Run it without -n to get a result.
        return
    pluginpath = (Path(__file__).parents[2] / 'plugins' / 'testplugin'
                  / 'dist' / 'testplugin-0.0.1-py3-none-any.whl')
    subprocess.run(['python', '-m', 'build'], cwd=pluginpath.parents[1], check=True)
    subprocess.run(['pip', 'install', pluginpath], check=False)
    try:
        dut: Catalog = PluginCatalog('widgets', default_root=Path(__file__).parent)
        got = dut.lookup_by_name('DooDad')
        assert isinstance(got, NamedWidget)
        # because testplugin is installed, DooDad will be overridden by the one
        #   in testplugin, where the value of 'some_tag' is 'plugin_dir'
        assert got.tags['some_tag'] == ['plugin_dir']
        assert hasattr(got, 'quux')
    finally:
        subprocess.run(['pip', 'uninstall', '-y', 'testplugin'], check=False)


def test_register_to_plugin_catalog(home_path) -> None:
    os.environ['HOME'] = str(home_path)
    dut: PluginCatalog = PluginCatalog('widgets', default_root=Path(__file__).parent)

    new_doodad = NamedWidget(name='DooDad', tags={'some_tag': ['hand_registered']})

    dut.register(new_doodad)

    got = dut.lookup_by_name('DooDad')
    assert isinstance(got, NamedWidget)
    assert got.tags['some_tag'] == ['hand_registered']
