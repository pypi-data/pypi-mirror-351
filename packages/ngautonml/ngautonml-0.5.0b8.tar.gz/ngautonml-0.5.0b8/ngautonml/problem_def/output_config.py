'''Output configuration'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path
from typing import Optional, Set, Dict, Any, List

from aenum import Enum as AEnum  # type: ignore[import-untyped]

from ..config_components.impl.config_component import ConfigComponent, ConfigError
from ..wrangler.constants import FileType, Defaults, ProblemDefKeys
from ..executor.executor_kind import ExecutorKind


class OutputConfigError(ConfigError):
    '''Errors during building or validating OutputConfig.'''


class OutputConfig(ConfigComponent):
    '''Output configuration'''

    class Keys(AEnum):
        '''Top-level clauses in output component'''
        OUTPUT_PATH = 'path'
        FILE_TYPE = 'file_type'
        INSTATIATIONS = 'instantiations'

    def __init__(self, clause: Dict[str, Any], parents: Optional[List[str]] = None):
        parents = self._add_parent(parents, ProblemDefKeys.OUTPUT.value)
        super().__init__(clause=clause, parents=parents)

    def validate(self, **kwargs) -> None:
        if self.path is not None:
            if self.path.exists() and not self.path.is_dir():
                raise OutputConfigError(
                    f'Output path {self.path} is not a directory'
                )

            if not self.path.parent.exists():
                raise OutputConfigError(f'Parent of path {self.path} does not exist.')

            if not self.path.parent.is_dir():
                raise OutputConfigError(f'Parent of path {self.path} is not a directory.')

            # Confirm that we have the needed permissions to create this directory.
            self.path.mkdir(exist_ok=True)

        self.file_type  # pylint: disable=pointless-statement

        try:
            # will raise an error if any instantiations are not allowed
            _ = self.instantiations
        except NotImplementedError as err:
            raise OutputConfigError(err) from err

    @property
    def path(self) -> Optional[Path]:
        '''Path to the output folder specified in the problem def'''
        if self._exists(self.Keys.OUTPUT_PATH):
            return Path(self._get(self.Keys.OUTPUT_PATH)).expanduser().resolve()
        return None

    @property
    def instantiations(self) -> Set[ExecutorKind]:
        '''Kinds of instantiations specified in the problem'''
        retval = self._get_with_default(
            self.Keys.INSTATIATIONS, dflt=Defaults.INSTANTIANTIONS)
        return set(ExecutorKind(s) for s in retval)

    @property
    def file_type(self) -> FileType:
        '''Type of file for predictions to be saved in.'''
        retval = self._get_with_default(self.Keys.FILE_TYPE, dflt=Defaults.FILE_TYPE)
        try:
            return FileType[retval.upper()]
        except KeyError as exc:
            raise OutputConfigError(f'{retval} is not a valid file type') from exc
