'''Load new data from a queue.'''

from queue import Empty, Queue
from typing import Dict, List, Optional

from ..config_components.dataset_config import DatasetConfig
from ..config_components.impl.config_component import InvalidValueError
from ..wrangler.dataset import Dataset

from .impl.data_loader_catalog import DataLoaderCatalog
from .memory_data_loader import MemoryDataLoader


class QueueLoader(MemoryDataLoader):
    '''Load poll data from a queue.'''

    name: str = 'queue'
    tags: Dict[str, List[str]] = {
        'input_format': ['pandas_dataframe'],
        'loaded_format': ['pandas_dataframe'],
    }

    _poll_queue: Optional[Queue] = None
    _timeout: Optional[float] = None

    def __init__(self, config: DatasetConfig):
        '''Create a new QueueLoader.

        Args:
            config: The configuration for the loader.
        '''
        if 'poll_queue' in config.params:
            poll_queue_var_name = config.params['poll_queue']
            self._poll_queue = self._lookup_var(poll_queue_var_name)
            if not isinstance(self._poll_queue, Queue):
                raise InvalidValueError(
                    f'Expecting local variable for poll {poll_queue_var_name} to be '
                    f'a queue.Queue; instead found {type(self._poll_queue)}'
                )
        if 'poll_timeout' in config.params:
            self._timeout = config.params['poll_timeout']
        super().__init__(config=config)

    def _poll(self, timeout: Optional[float] = None) -> Optional[Dataset]:
        '''Poll the queue for data.

        Args:
            timeout: The time to wait for data. If it is None, we
                use the configured timeout for the loader. If that is None,
                we wait forever.

        Returns:
            The data from the queue, or None if the queue times out.
        '''
        if self._poll_queue is None:
            return None
        timeout = timeout if timeout is not None else self._timeout
        try:
            return self._poll_queue.get(timeout=timeout)
        except Empty:
            return None


def register(catalog: DataLoaderCatalog) -> None:
    '''Register all the objects in this file with the catalog.

    Args:
        catalog: The catalog to register the loader with.
    '''
    catalog.register(QueueLoader)
