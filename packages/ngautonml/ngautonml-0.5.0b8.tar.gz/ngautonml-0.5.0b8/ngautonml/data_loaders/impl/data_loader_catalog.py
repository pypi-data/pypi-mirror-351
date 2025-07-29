'''Catalog for objects that load data from one format to another.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Type, Union

from ...catalog.catalog import CatalogLookupError
from ...catalog.memory_catalog import MemoryCatalog
from ...config_components.dataset_config import DatasetConfig

from .data_loader import DataLoader


class DataLoaderCatalog(MemoryCatalog[Type[DataLoader]], metaclass=abc.ABCMeta):
    '''Base class for DataLoader catalogs'''

    def register(self, obj: Type[DataLoader], name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)

    def lookup_by_formats(self,
                          input_format: str,
                          loaded_format: str = 'pandas_dataframe') -> Dict[str, Type[DataLoader]]:
        '''Get a data loader based on input and loaded format.

        Args:

        :input_format: The format of the input data.
        :loaded_format: The format of the loaded data.
        '''
        return self.lookup_by_tag_and(input_format=input_format, loaded_format=loaded_format)

    def construct_instance(self, config: DatasetConfig) -> DataLoader:
        '''Lookup and construct the instance described by config.'''
        if config.config is not None:
            retval = self.lookup_by_name(name=config.config)
            assert isinstance(retval, type(DataLoader))
            return retval(config=config)
        loaders = self.lookup_by_formats(**config.dataloader_tags)
        if len(loaders) != 1:
            raise CatalogLookupError(
                f'Expected exactly one DataLoader for {config.dataloader_tags},'
                f' found {len(loaders)}'
            )
        return next(iter(loaders.values()))(config=config)


class DataLoaderCatalogStub(DataLoaderCatalog):
    '''stub'''
