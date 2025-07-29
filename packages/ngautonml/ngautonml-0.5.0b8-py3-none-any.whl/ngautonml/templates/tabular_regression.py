'''Pipeline template for a tabular regression problem.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=too-many-arguments,duplicate-code
from typing import Dict, List, Optional

from ..algorithms.column_parser import ColumnParser
from ..algorithms.connect import ConnectorModel
from ..algorithms.extract_columns_by_role import ExtractColumnsByRoleModel
from ..algorithms.impl.algorithm import AlgorithmCatalog
from ..algorithms.sklearn.impute.simple_imputer import SimpleImputerModel
from ..algorithms.sklearn.preprocessing.one_hot_encoder import OneHotModel
from ..problem_def.task import DataType, TaskType
from ..templates.impl.pipeline_step import GeneratorInterface
from ..templates.impl.pipeline_template import PipelineTemplate
from ..templates.impl.template import TemplateCatalog
from ..wrangler.dataset import DatasetKeys, RoleName


class TabularRegressionTemplate(PipelineTemplate):
    '''Simple implementation of a template for tabular regression.'''
    _tags: Dict[str, List[str]] = {
        'task': [TaskType.REGRESSION.name],
        'data_type': [DataType.TABULAR.name],
    }
    _name = 'tabular_regression'

    def __init__(self,
                 name: Optional[str] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 generator: Optional[GeneratorInterface] = None):
        super().__init__(name=name or self._name,
                         tags=tags or self._tags,
                         algorithm_catalog=algorithm_catalog, generator=generator)
        self.step(model=ColumnParser())

        attributes = self.new(name='attributes')
        attributes.step(
            model=ExtractColumnsByRoleModel(),
            desired_roles=RoleName.ATTRIBUTE)
        attributes.step(SimpleImputerModel())
        attributes.step(OneHotModel())

        target = self.new(name='target')
        target.step(
            model=ExtractColumnsByRoleModel(),
            desired_roles=RoleName.TARGET)

        self.parallel(target_dataset=target, attributes_dataset=attributes)
        self.step(
            model=ConnectorModel(),
            serialized_model=None,
            **{
                DatasetKeys.TARGET_TABLE.value: [
                    'target_dataset', DatasetKeys.DATAFRAME_TABLE.value],
                DatasetKeys.COVARIATES_TABLE.value: [
                    'attributes_dataset', DatasetKeys.DATAFRAME_TABLE.value]
            }
        )
        self.query(task=TaskType.REGRESSION.name).set_name('regressor')


def register(catalog: TemplateCatalog,
             algorithm_catalog: Optional[AlgorithmCatalog] = None,
             generator: Optional[GeneratorInterface] = None):
    '''Register all the objects in this file.'''
    catalog.register(
        TabularRegressionTemplate(
            algorithm_catalog=algorithm_catalog,
            generator=generator))
