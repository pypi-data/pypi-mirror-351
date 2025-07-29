'''Autoloader for the template catalog.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path

from ...catalog.plugin_catalog import PluginCatalog
from .pipeline_template import PipelineTemplate
from .template import TemplateCatalog


class TemplateCatalogAuto(PluginCatalog[PipelineTemplate], TemplateCatalog):
    '''Template catalog that automatically loads all templates from a directory.

    Templates are in ../templates.
    '''

    def __init__(self, **kwargs):
        super().__init__('templates', default_root=Path(__file__).parents[2], **kwargs)
