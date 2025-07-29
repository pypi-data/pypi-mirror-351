'''Tests for the StubDecider class.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..config_components.distributed_config import DecidersConfig, DistributedConfig
from .impl.decider_auto import DeciderCatalogAuto
from .stub_decider import DeciderStub


def test_sunny_day():
    '''Test the StubDecider class.'''
    _ = DeciderCatalogAuto()
    distributed = DistributedConfig(clause={
        'decider': {
            'stub_decider': {}
        }
    })
    decider = DeciderStub(config=distributed.decider.stub_decider)  # pylint: disable=no-member
    assert decider.decide(None, None, None) is True


def test_catalog():
    '''Test the decider_stub in the DeciderCatalog class.'''
    distributed = DistributedConfig(
        clause={
            'decider': {
                'stub_decider': {}
            },
        }
    )
    catalog = DeciderCatalogAuto()
    decider = catalog.lookup_by_name('stub_decider')(config=distributed.decider.stub_decider)  # pylint: disable=no-member
    assert decider.decide(None, None, None) is True

    assert 'stub_decider' in [k.value for k in DecidersConfig.Keys]
