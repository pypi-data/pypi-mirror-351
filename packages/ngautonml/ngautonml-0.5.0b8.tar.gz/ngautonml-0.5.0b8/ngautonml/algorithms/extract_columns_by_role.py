''' A model that takes a dataset and returns only that columns that have

a specific role (most commonly, attribute and target)'''
from typing import Any, List, Optional, Union

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ..algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..catalog.catalog import upcast
from ..tables.impl.table import TableFactory
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.dataset import Dataset, RoleName
_ = TableCatalogAuto()


class Error(BaseException):
    '''Base class for all errors thrown by this module'''


class InvalidColumnSplitError(Error):
    '''Unable to split columns as specified.'''


class ExtractColumnsByRoleModelInstance(AlgorithmInstance):
    '''Returns only columns with a specific role.'''
    _desired_roles: List[RoleName]

    def __init__(self, parent,
                 desired_roles: Optional[Union[RoleName, List[RoleName]]] = None):
        super().__init__(parent=parent)
        assert desired_roles is not None

        if isinstance(desired_roles, RoleName):
            desired_roles = [desired_roles]

        self._desired_roles = desired_roles

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None

        retval = dataset.output()
        retval_data = {}
        for desired_role in self._desired_roles:
            if desired_role not in dataset.roles.keys():
                continue

            columns_satisfying_role = dataset.roles[desired_role]
            for col in columns_satisfying_role:
                if col.name not in dataset.get_dataframe():
                    continue
                retval_data[col.name] = dataset.get_dataframe()[col.name]

        retval.dataframe_table = TableFactory(retval_data)

        return retval


class ExtractColumnsByRoleModel(Algorithm):
    '''Returns only columns with a specific role.'''
    _name: str = 'Extract Columns by Role'
    _instance_constructor = ExtractColumnsByRoleModelInstance
    _tags = {
        'source': ['auton_lab'],
        'preprocessor': ['true'],
    }

    def _param_from_json(self, hyperparam_name: str, json_value: Any) -> Any:
        if hyperparam_name == 'desired_roles':
            if isinstance(json_value, str):
                return RoleName[json_value]
            assert isinstance(json_value, list)
            return [RoleName[role] for role in json_value]
        return super()._param_from_json(hyperparam_name, json_value)

    def param_to_json(self, hyperparam_name: str, python_value: Any) -> Any:
        if hyperparam_name == 'desired_roles':
            if isinstance(python_value, RoleName):
                return python_value.value
            assert isinstance(python_value, list)
            assert isinstance(python_value[0], RoleName)
            return [role.value for role in python_value]
        return super().param_to_json(hyperparam_name, python_value)


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = ExtractColumnsByRoleModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
