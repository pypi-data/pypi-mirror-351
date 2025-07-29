'''Convert two-valued fields into binary fields.'''
import logging
from typing import Any, Dict, Optional

# Copyright (c) 2023, 2025 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pandas as pd

from ..algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ..algorithms.impl.algorithm_instance import AlgorithmInstance
from ..catalog.catalog import upcast
from ..tables.impl.table import TableFactory
from ..wrangler.dataset import Dataset, RoleName
from ..wrangler.logger import Logger

logger = Logger(__file__, level=logging.INFO, to_file=False, to_stdout=False).logger()


class BinarizerModelInstance(AlgorithmInstance):
    '''Connect one model to another by transforming names.'''
    _pos_labels: Dict[RoleName, Any]

    def __init__(self, parent, **hyperparams: Any):
        super().__init__(parent=parent)

        self._pos_labels = {
            RoleName[n.upper()]: v
            for n, v in self.algorithm.hyperparams(**hyperparams).items()
        }

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if dataset is None:
            return None
        retval = dataset.output()

        pos_labels = self._pos_labels.copy()  # take care not to update the base values.
        pos_labels.update(dataset.metadata.pos_labels)

        retval_data = dataset.dataframe_table.as_(pd.DataFrame)
        for role in pos_labels:
            if role not in dataset.roles.keys():
                continue

            columns_satisfying_role = dataset.roles[role]

            positive = pos_labels[role]
            for col in columns_satisfying_role:
                # json lacks a bytes representation. We use str.
                first = retval_data[col.name].iloc[0]
                if isinstance(first, bytes) and isinstance(positive, str):
                    positive = positive.encode()
                logger.debug('positive: %r', positive)
                retval_data[col.name] = (
                    retval_data[col.name].apply(lambda x, pos=positive: x == pos))

        retval.dataframe_table = TableFactory(retval_data)

        return retval


class BinarizerModel(Algorithm):
    '''Convert two-valued fields into binary fields.

    Takes a DatasetKeys.DATAFRAME.
    Yields a DatasetKeys.DATAFRAME.

    A column needs to have a pos_label property in the
    problem definition to be converted.

    If the field is already boolean, no change is made.

    If the field is bytes, the pos_label will be converted
    to bytes for the default encoding with str.encode().
    '''
    _name = 'binarize'
    _tags = {
        'source': ['auton_lab'],
        'preprocessor': ['true'],
    }
    _instance_constructor = BinarizerModelInstance


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = BinarizerModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
