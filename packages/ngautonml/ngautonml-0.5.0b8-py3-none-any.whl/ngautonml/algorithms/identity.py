'''A model that returns output identical to input.

Used for parallel subpipelines where one of them has no operations in it.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional
from ..algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..catalog.catalog import upcast
from ..wrangler.dataset import Dataset


class IdentityModelInstance(AlgorithmInstance):
    '''A model that returns output identical to input.'''

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        new_dataset = dataset.output()
        new_dataset.update(dataset)
        return new_dataset


class IdentityModel(Algorithm):
    '''A model that returns output identical to input.'''
    _name = 'identity'
    _instance_constructor = IdentityModelInstance
    _tags = {
        'source': ['auton_lab'],
        'preprocessor': ['true'],
    }


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = IdentityModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
