'''Loads a local file as a pandas DataFrame.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from scipy.io.arff import loadarff  # type: ignore[import]

from ..config_components.dataset_config import DatasetConfig
from ..wrangler.constants import FileType
from ..wrangler.dataset import Dataset, DatasetKeys, RoleName, TaskType, TableFactory
from ..wrangler.logger import Level, Logger
from .impl.dataframe_loader import DataframeLoader, DatasetFileError
from .impl.data_loader_catalog import DataLoaderCatalog

logger = Logger(__file__, level=Level.DEBUG).logger()


class LocalDataLoader(DataframeLoader):
    '''Loads a local file as a pandas DataFrame.'''

    name: str = 'local'
    tags: Dict[str, List[str]] = {
        'input_format': ['csv', 'arff', 'tabular_file'],
        'loaded_format': ['pandas_dataframe'],
    }

    _train_path: Path
    _test_path: Optional[Path] = None
    _ext: str

    def __init__(self, config: DatasetConfig):
        train_path: Path = Path(config.params[config.Keys.TRAIN_PATH.value])  # type: ignore[attr-defined] # pylint: disable=line-too-long
        self._train_path = train_path.expanduser().resolve()
        ext: str = train_path.suffix[1:]

        if ext not in FileType.list():
            raise DatasetFileError(
                f'Train path from the problem definition ({train_path})'
                f' does not point to a file with one of these extensions: {FileType.list()}'
            )

        self._ext = ext

        if config.Keys.TEST_PATH.value in config.params:  # type: ignore[attr-defined]
            test_path = Path(config.params[config.Keys.TEST_PATH.value])  # type: ignore[attr-defined] # pylint: disable=line-too-long
            test_path = test_path.expanduser().resolve()
            test_ext = test_path.suffix[1:]
            if test_ext != ext:
                raise DatasetFileError(
                    f'test data: "{test_path}" is not same file type as train data'
                    f'(Expected: .{ext})')

            self._test_path = test_path

        self._static_path = None
        if config.Keys.STATIC_EXOGENOUS_PATH.value in config.params:  # type: ignore[attr-defined]
            static_path = Path(
                config.params[config.Keys.STATIC_EXOGENOUS_PATH.value]).expanduser().resolve()  # type: ignore[attr-defined] # pylint: disable=line-too-long
            static_ext = static_path.suffix[1:]
            if static_ext != ext:
                raise DatasetFileError(
                    f'static data: "{static_path}" is not same file type as train data'
                    f'(Expected: .{ext})')

            self._static_path = static_path

        super().__init__(config=config)

    def _drop_unnamed_cols(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        '''Deal with pandas CSV loader loading the index as an unnamed column.

        There are a few potential ways to do this.
        We choose to drop all cols called 'Unnamed: [int of any length]',
        as those were likely unnamed in the actual csv.'''
        # TODO(Merritt): warn user if we encounter this under certain circumstances
        # (for ex: not in first column
        # or the col is literally named 'Unnamed: [num]' in the csv)
        drop_cols = dataframe.filter(regex=r'^Unnamed: \d+$').columns
        retval = dataframe.drop(labels=drop_cols, axis=1)
        return retval

    def _load_dataframe(self, path: Path) -> pd.DataFrame:
        '''Load the file at path based on self._ext'''
        retval = None

        try:
            if self._ext == FileType.CSV.value:
                retval = pd.read_csv(path)
            elif self._ext == FileType.ARFF.value:
                raw_data = loadarff(path)
                retval = pd.DataFrame(raw_data[0])
        except FileNotFoundError as exc:
            raise DatasetFileError(f'Unable to load file from "{path}".') from exc

        if retval is None:
            raise DatasetFileError(f'Unsupported file type: {path}')

        return self._drop_unnamed_cols(retval)

    def _load_dataset(self, path: Path) -> Dataset:
        '''Load a Dataset into a DataFrame from the provided Path'''
        retval = Dataset(metadata=self._metadata)

        data = self._load_dataframe(path=path)

        retval.dataframe_table = TableFactory(data)

        # if this is a forecasting problem, load static exogenous data or create an empty key for it
        # TODO(Piggy/Merritt): replace this with something that can be used by both memory and local
        # to load additional data requested by a plugin
        if self._metadata.task == TaskType.FORECASTING:
            if self._static_path is None:
                retval.static_exogenous_table = None
                logger.debug('Forecasting problem has no static exogenous table.')
            else:
                static = self._load_dataframe(self._static_path)
                retval.static_exogenous_table = TableFactory(static)

        return retval

    def _load_train(self) -> Dataset:
        return self._load_dataset(
            path=self._train_path)

    def _load_test(self) -> Optional[Dataset]:
        if self._test_path is None:
            return None

        retval = self._load_dataset(
            path=self._test_path)

        return retval

    def ez_dataset(self,
                   data: Any,
                   key: Union[DatasetKeys, str] = DatasetKeys.DATAFRAME_TABLE,
                   cols: Optional[List[str]] = None,
                   roles: Optional[List[Union[RoleName, str]]] = None,
                   **kwargs) -> Dataset:
        '''Load a Dataset object, by placing data at the supplied key.

        As of 2023-12-04 we only know how to handle things we can turn into a pandas DataFrame.

        Args:
          :data: Dataframe or object that can be turned into one.
            If data is a Path or a str, will attempt
            to load the file it points to as a dataframe and put that in the dataset.
          :key: The key for the data in the dataset. Defaults to "dataframe".
          :cols: If set, only selects supplied column(s).
            Will take union with roles if both are specified.
          :roles: If set, only selects columns with supplied role(s).
            Will take union with cols if both are specified.
        '''

        if isinstance(data, (Path, str)):
            path = Path(data)
            data = self._load_dataframe(path=path)

        return super().ez_dataset(data, key=key, cols=cols, roles=roles, **kwargs)


def register(catalog: DataLoaderCatalog):
    '''Register all the objects in this file.'''
    catalog.register(LocalDataLoader)
