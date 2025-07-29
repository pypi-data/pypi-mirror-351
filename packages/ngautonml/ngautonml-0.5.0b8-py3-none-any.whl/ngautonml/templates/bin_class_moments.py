'''Pipeline template for the method of moments applied to binary classification.
'''
# pylint: disable=too-many-arguments,duplicate-code
from typing import Dict, List, Optional


# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..algorithms.column_parser import ColumnParser
from ..algorithms.connect import ConnectorModel
from ..algorithms.domain_adaptation.auton_moment_matcher import AutonMomentMatcher
from ..algorithms.extract_columns_by_role import ExtractColumnsByRoleModel
from ..algorithms.identity import IdentityModel
from ..algorithms.impl.algorithm import AlgorithmCatalog
from ..algorithms.moments import Moments
from ..algorithms.sklearn.impute.simple_imputer import SimpleImputerModel
from ..algorithms.sklearn.preprocessing.one_hot_encoder import OneHotModel
from ..problem_def.task import DataType, TaskType
from ..templates.impl.pipeline_step import GeneratorInterface
from ..templates.impl.pipeline_template import PipelineTemplate
from ..templates.impl.template import TemplateCatalog
from ..wrangler.dataset import DatasetKeys, RoleName


class BinClassMomentsTemplate(PipelineTemplate):
    '''Implementation of a template for binary tabular classification.'''
    _tags: Dict[str, List[str]] = {
        'task': [TaskType.BINARY_CLASSIFICATION.name],
        'data_type': [DataType.TABULAR.name],
    }
    _name = 'method_of_moments'

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
        data = attributes.new(name='data')
        data.step(model=IdentityModel())

        moments = attributes.new(name='moments')
        moments.step(model=Moments())

        attributes.parallel(data=data, moments=moments)
        attributes.step(
            model=ConnectorModel(),
            serialized_model=None,
            **{
                DatasetKeys.HYPERPARAMS.value: ['moments', DatasetKeys.HYPERPARAMS.value],
                DatasetKeys.DATAFRAME_TABLE.value: ['data', DatasetKeys.DATAFRAME_TABLE.value]
            }
        )
        attributes.step(
            model=AutonMomentMatcher()
        )
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
        self.query(task=TaskType.BINARY_CLASSIFICATION.name,
                   data_type=DataType.TABULAR.name).set_name('classifier')


def register(catalog: TemplateCatalog,
             algorithm_catalog: Optional[AlgorithmCatalog] = None,
             generator: Optional[GeneratorInterface] = None):
    '''Register all the objects in this file.'''
    catalog.register(
        BinClassMomentsTemplate(
            algorithm_catalog=algorithm_catalog,
            generator=generator))
