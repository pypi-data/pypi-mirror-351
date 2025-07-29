'''
Catalog for pipeline templates

pipeline templates are DAGs of "slots" that can contain either a specific algorithm,
or a query to the AlgorithmCatalog for the Generator to fill in.
'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, List, Union

from ...catalog.catalog import CatalogError
from ...catalog.memory_catalog import MemoryCatalog
from ...problem_def.task import Task
from .pipeline_template import PipelineTemplate


class TemplateRegisterError(CatalogError):
    '''Template missing required keys for registration.'''


class TemplateCatalog(MemoryCatalog[PipelineTemplate]):
    '''Mixin class for pipeline template catalogs'''
    def validate(self):
        '''Validate the catalog is capable of generating a pipeline.'''
        errors = []

        for obj in self.all_objects():
            final_tags = obj.tags
            # Check that at least one task and data type exists
            tasks = final_tags[Task.Keys.TASK_TYPE.value]  # pylint: disable=no-member,line-too-long
            data_types = final_tags[Task.Keys.DATA_TYPE.value]  # pylint: disable=no-member,line-too-long

            if 0 == len(tasks):
                errors.append(TemplateRegisterError(
                    f'No task defined in Template Register for {obj.name}'))

            if 0 == len(data_types):
                errors.append(TemplateRegisterError(
                    f'No data type defined in Template Register for {obj.name}'))

        if 0 < len(errors):
            raise TemplateRegisterError(errors)

    # TODO(piggy): Rewrite this in terms of Task.
    def lookup_by_task(self, task: Union[str, List[str]]) -> Dict[str, PipelineTemplate]:
        '''Returns list of all templates that match at least one given task'''
        results: Dict[str, PipelineTemplate] = {}

        tasks = task

        if isinstance(task, str):
            tasks = [task]

        for tas in tasks:
            results.update(
                self.lookup_by_tag_and(**{Task.Keys.TASK_TYPE.value: tas}))  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        return results

    # TODO(piggy): Rewrite this in terms of DataType.
    def lookup_by_datatype(self, data_type: Union[str, List[str]]) -> Dict[str, PipelineTemplate]:
        '''Returns list of all templates that match at least one given task'''
        results: Dict[str, PipelineTemplate] = {}

        data_types = data_type

        if isinstance(data_type, str):
            data_types = [data_type]

        for dts in data_types:
            results.update(
                self.lookup_by_tag_and(**{Task.Keys.DATA_TYPE.value: dts}))  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long

        return results

    # TODO(piggy): Rewrite this in terms of ProblemType.
    def lookup_by_both(self,
                       data_type: Union[str, List[str]],
                       task: Union[str, List[str]]
                       ) -> Dict[str, PipelineTemplate]:
        '''Returns all templates that match any combination of a data_type and task'''
        by_datatype = self.lookup_by_datatype(data_type)
        by_task = self.lookup_by_task(task)

        return dict(by_datatype.items() & by_task.items())


class TemplateCatalogStub(TemplateCatalog):
    '''stub'''
