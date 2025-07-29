'''Logging control object for the project.

Use this like this:
import logging
from ...wranger.logger import Logger

logger = Logger(__file__, level=logging.INFO, to_file=False, to_stdout=True)
logger.debug('message %s', arg)
'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path
import sys
import logging
from typing import List, Optional, Tuple, Union


class Level():
    '''Alternative to log level constants, introduces VERBOSE'''
    CRITICAL: int = logging.CRITICAL
    ERROR: int = logging.ERROR
    WARN: int = logging.WARN
    INFO: int = logging.INFO
    DEBUG: int = logging.DEBUG
    VERBOSE: int = 5


class Logger:
    '''Logging control object for the project.

    Use like this:

    .. code-block:: python

        import logging
        from ...wrangler.logger import Logger

        logger = Logger(__file__, level=logging.INFO, to_file=False, to_stdout=True)
        logger.debug('message %s', arg)
    '''

    @classmethod
    def set_global_level(cls, level: int) -> None:
        '''Override log level for all loggers in this module.'''
        loggers = [logging.getLogger(name)
                   for name in logging.root.manager.loggerDict]  # pylint: disable=no-member,line-too-long
        loggers.append(logging.getLogger())  # Add root logger
        for logger in loggers:
            logger.setLevel(level)

    def __init__(self,
                 from_filename: str,
                 to_filename: str = 'univ',
                 level: int = logging.DEBUG,
                 to_stdout: bool = False,
                 to_file: bool = True,
                 only_if_filepath_contains: Optional[Union[str, List[str]]] = None,
                 only_in_line_range: Optional[Tuple[int, int]] = None):
        pfile = Path(from_filename)
        self._logger = logging.getLogger(pfile.name)
        self._logger.setLevel(level)

        if only_if_filepath_contains:
            self._logger.addFilter(FilepathContains(contains=only_if_filepath_contains))

        if only_in_line_range:
            self._logger.addFilter(OnlyInLineRange(line_range=only_in_line_range))

        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S')
        if to_file:
            fh = logging.FileHandler(f'{to_filename}.log')
            fh.setFormatter(formatter)
            self._logger.addHandler(fh)
        if to_stdout:
            sh = logging.StreamHandler(sys.stdout)
            sh.setFormatter(formatter)
            self._logger.addHandler(sh)

    def logger(self) -> logging.Logger:
        '''Access the logging.Logger associated with this object.'''
        return self._logger


class FilepathContains(logging.Filter):
    '''Logging filter that preserves logs whose filepath contains a given string.

    If multiple strings are provided, will preserve logs whose source file match
    any one of them.
    '''
    _contains: List[str]

    def __init__(self, *args, contains: Union[str, List[str]], **kwargs):
        if isinstance(contains, str):
            contains = [contains]
        self._contains = contains
        super().__init__(*args, **kwargs)

    def filter(self, record: logging.LogRecord) -> bool:
        return any(s in record.pathname for s in self._contains)


class OnlyInLineRange(logging.Filter):
    '''Logging filter that preserves logs who originate from a range of lines.'''
    _line_range: Tuple[int, int]

    def __init__(self, *args, line_range: Tuple[int, int], **kwargs):
        self._line_range = line_range
        super().__init__(*args, **kwargs)

    def filter(self, record: logging.LogRecord) -> bool:
        return self._line_range[0] <= record.lineno <= self._line_range[1]
