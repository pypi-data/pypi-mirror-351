'''Test the pipeline template catalog module.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=duplicate-code

import pytest

from .pipeline_template import PipelineTemplate
from .template import TemplateCatalog, TemplateRegisterError


def test_register() -> None:
    '''Test registering a template'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        name='TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    assert dut.register(test_template) == 'testtemplate'


def test_register_with_strings() -> None:
    '''Test registering a template with strings instead of lists in tags'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        'TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    assert dut.register(test_template) == 'testtemplate'
    assert dut.lookup_by_task(task='some task') == {'testtemplate': test_template}


def test_register_no_task() -> None:
    '''Attempt to register template without task'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        'TestTemplate',
        tags={'data_type': ['Some Type'], 'task': []})
    dut.register(test_template)
    with pytest.raises(TemplateRegisterError,
                       match=r"[Tt]ask"):
        dut.validate()


def test_register_no_datatype() -> None:
    '''Attempt to register template without datatype'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        'TestTemplate',
        tags={'data_type': [], 'task': ['Some Task']})
    dut.register(test_template)
    with pytest.raises(TemplateRegisterError,
                       match=r"[Dd]ata"):
        dut.validate()


def test_register_fails() -> None:
    '''Attempt to register template without datatype.

    Expected behavior: a TemplateRegisterError will be thrown.
    (The template may still register)
    '''
    dut = TemplateCatalog()
    test_template_bad = PipelineTemplate(
        'TestTemplateBad',
        tags={'data_type': [], 'task': ['Another Task']})
    dut.register(test_template_bad)
    with pytest.raises(TemplateRegisterError,
                       match=r"[Dd]ata"):
        dut.validate()


def test_lookup_by_task() -> None:
    '''Test finding a template by task'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        'TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    assert 1 == len(dut.lookup_by_task(['Some Task']))


def test_lookup_by_task_fail() -> None:
    '''Test looking up a nonexistent task'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        'TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    assert 0 == len(dut.lookup_by_task('Nonexistent'))


def test_lookup_by_task_multi() -> None:
    '''Test finding multiple templates by task'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        'TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    test_second = PipelineTemplate(
        'TestSecond',
        tags={'data_type': ['Another Type'], 'task': ['Some Task']})
    dut.register(test_second)
    assert 2 == len(dut.lookup_by_task('Some Task'))


def test_lookup_by_datatype() -> None:
    '''Test finding a template by datatype'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        'TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    assert 1 == len(dut.lookup_by_datatype('Some Type'))


def test_lookup_by_datatype_fail() -> None:
    '''Test looking up a nonexistent datatype'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        name='TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    assert 0 == len(dut.lookup_by_datatype('Nonexistent'))


def test_lookup_by_datatype_multi() -> None:
    '''Test finding multiple templates by datatype'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        name='TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    test_second = PipelineTemplate(
        name='TestSecond',
        tags={'data_type': ['Some Type'], 'task': ['Another Task']})
    dut.register(test_second)
    assert 2 == len(dut.lookup_by_datatype('Some Type'))


def test_lookup_by_task_and_type() -> None:
    '''Test finding a template by task and datatype'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        name='TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    assert 1 == len(dut.lookup_by_both(task='Some Task',
                                       data_type='Some Type'))


def test_lookup_by_task_and_type_fail() -> None:
    '''Test looking up a nonexistent task and datatype'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        name='TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    assert 0 == len(dut.lookup_by_both(task='Nonexistent',
                                       data_type='Nonexistent'))


def test_lookup_by_task_and_type_mismatch() -> None:
    '''Test looking up a task but datatype does not match'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        name='TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    assert 0 == len(dut.lookup_by_both(task='Some Task',
                                       data_type='Nonexistent'))


def test_lookup_by_task_and_type_multi() -> None:
    '''Test finding multiple templates by task and datatype'''
    dut = TemplateCatalog()
    test_template = PipelineTemplate(
        name='TestTemplate',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_template)
    test_second = PipelineTemplate(
        name='TestSecond',
        tags={'data_type': ['Some Type'], 'task': ['Some Task']})
    dut.register(test_second)
    test_third = PipelineTemplate(
        name='TestThird',
        tags={'data_type': ['Some Type'], 'task': ['Different Task']})
    dut.register(test_third)
    assert 2 == len(dut.lookup_by_both(task='Some Task',
                                       data_type='Some Type'))
