'''A connector model that changes the names in dictionaries.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, List, Optional, Union

from ..algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog, InputKeyError
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..catalog.catalog import upcast
from ..wrangler.dataset import Dataset


class ConnectorModelInstance(AlgorithmInstance):
    '''Connect one model to another by transforming names.'''
    _transforms: Dict[str, List[str]]

    def __init__(self, parent, **hyperparams: Union[str, List[str]]):
        super().__init__(parent=parent)
        self._transforms = {}
        transforms = self.algorithm.hyperparams(**hyperparams)
        for new_key, old_path in transforms.items():
            if isinstance(old_path, str):
                self._transforms[new_key] = [old_path]
            else:
                self._transforms[new_key] = old_path

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        retval = dataset.output()
        for new_key, old_path in self._transforms.items():
            here = dataset
            for old_key in old_path:
                try:
                    there = here[old_key]
                except KeyError as exc:
                    raise InputKeyError(
                        f'Can not find old path "{".".join(old_path)}"'
                        f' to rename to new key "{new_key}".'
                        f' Looking for "{old_key}".'
                        f' Keys here are [{", ".join(list(here.keys()))}].') from exc
                here = there
            retval[new_key] = here

        return retval


class ConnectorModel(Algorithm):
    '''Connect one model to another by transforming names.
    Usage:
    connector = ConnectorModel()
    instance = connector.instantiate(newkey1='oldkey1', newkey2='oldkey2')
    old_dataset = {'oldkey1':'v1', 'oldkey2':'v2'}
    new_dataset = instance.predict(old_dataset)
    #new_dataset == {'newkey1':'v1', 'newkey2':'v2'}

    If you want to keep a key the same, pass it in as connector.instantiate(samekey='samekey')
    If you want to drop a key and its corresponding value, don't pass it in as a new key.

    You get only the keys that are mentioned in the arguments to instantiate.
    All other key/value pairs are discarded.
    '''
    _name = 'connect'
    _instance_constructor = ConnectorModelInstance
    _tags = {
        'source': ['auton_lab'],
        'preprocessor': ['true'],
    }


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = ConnectorModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
