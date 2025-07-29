'''Tests for the OutputConfig object'''
from pathlib import Path

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pytest

from ..wrangler.constants import FileType
from ..executor.executor_kind import ExecutorKind

from .output_config import OutputConfig, OutputConfigError
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name,duplicate-code


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("data")


def test_output_config_sunny_day(tmp_path: Path) -> None:
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir()
    dut = OutputConfig(clause={
        'path': str(tmp_dir),
        'instantiations': [
            'stub_executor_kind',
            'simple'
        ],
        'file_type': 'csv'
    })
    dut.validate()
    assert dut.path == tmp_dir
    assert dut.instantiations == set([ExecutorKind('simple'), ExecutorKind('stub_executor_kind')])
    assert dut.file_type == FileType.CSV


def test_illegal_instantiation(tmp_path: Path) -> None:
    tmp_dir = tmp_path / "sub"
    dut = OutputConfig(clause={
        'path': str(tmp_dir),
        'instantiations': [
            'stub_executor_kind',
            'fake_instantiation'
        ],
        'file_type': 'csv'
    })
    with pytest.raises(OutputConfigError, match=r'fake_instantiation'):
        dut.validate()


def test_illegal_file_type(tmp_path: Path) -> None:
    tmp_dir = tmp_path / "sub"
    dut = OutputConfig(clause={
        'path': str(tmp_dir),
        'file_type': 'fake_file_type'
    })
    with pytest.raises(OutputConfigError, match=r'fake_file_type'):
        dut.validate()
