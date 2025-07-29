'''These are the kinds of executable pipelines for different executors.'''
from typing import Set

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


# TODO(piggy): If we introduce an ExecutorCatalog, the constructor for
# ExecutorKind should confirm that the kind exists in the catalog.
class ExecutorKind(str):
    '''The class for the Executor Kind identifying the type of Executor'''
    _ALLOWED = {'json', 'stub_executor_kind', 'simple'}

    @staticmethod
    def __new__(cls, content):
        if content.lower() not in cls._ALLOWED:
            raise NotImplementedError(
                f'Executor kind {content} is not recognized. '
                f'Existing executor kinds: {cls._ALLOWED}'
            )
        return str.__new__(cls, content.lower())

    @classmethod
    def allowed(cls) -> Set[str]:
        '''Currently supported executor kinds'''
        return cls._ALLOWED

    @property
    def suffix(self) -> str:
        '''Filename suffix used for saving pipelines to disk'''
        if self == 'json':
            return '.json'
        if self == 'stub_executor_kind':
            return '.stub'
        raise NotImplementedError(
            f'No file suffix available for ExecutorKind "{self}".')
