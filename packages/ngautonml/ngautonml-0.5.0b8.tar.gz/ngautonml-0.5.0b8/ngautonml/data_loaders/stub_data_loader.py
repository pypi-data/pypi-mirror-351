'''Stub Data Loader for testing purposes.'''

from typing import Any, Dict, List, Optional

from ..wrangler.dataset import Dataset

from .impl.data_loader import DataLoader
from .impl.data_loader_catalog import DataLoaderCatalog


class DataLoaderStub(DataLoader):
    '''Stub Data Loader'''
    name: str = 'stub'
    tags: Dict[str, List[str]] = {
        'input_format': ['stub_input_format'],
        'loaded_format': ['stub_loaded_format'],
    }

    def _load_train(self) -> Optional[Dataset]:
        return Dataset(metadata=self._metadata)

    def _load_test(self) -> Optional[Dataset]:
        return Dataset(metadata=self._metadata)

    def _load_ground_truth(self) -> Optional[Dataset]:
        return Dataset(metadata=self._metadata)

    def _dataset(self, data: Any, **kwargs) -> Dataset:
        return Dataset(metadata=self._metadata)

    def validate(self, dataset: Optional[Dataset]) -> None:
        pass

    def poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        pass

    def build_dataset_from_json(self, json_data: Dict) -> Dataset:
        return Dataset(metadata=self._metadata)


def register(catalog: DataLoaderCatalog):
    '''Register all the objects in this file.'''
    catalog.register(DataLoaderStub)
