'''tests for dataset_config.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,duplicate-code


import pytest

from ..wrangler.dataset import Column, RoleName
from ..problem_def.problem_def import ProblemDefinition
from .dataset_config import DatasetConfig
from .impl.config_component import ValidationErrors


ROLE_WITH_NO_COL = {
    'config': 'ignore',
    'column_roles': {
        'target': {}
    }
}


def test_role_with_no_col():
    clause = ROLE_WITH_NO_COL.copy()
    dut = DatasetConfig(clause=clause)

    with pytest.raises(ValidationErrors, match=r'[Nn]ame'):
        dut.validate()


INVALID_KEY = {
    'config': 'ignore',
    'hamster': {
        'gerbil': 'gerbil',
    }
}


def test_dataset_invalid_key() -> None:
    clause = INVALID_KEY.copy()
    dut = DatasetConfig(clause=clause)

    with pytest.raises(ValidationErrors, match='hamster'):
        dut.validate()


POS_LABEL_DATASET = {
    'column_roles': {
        'target': {
            'name': 'a',
            'pos_label': 'good'
        }
    }
}


def test_pos_label_sunny_day() -> None:
    dut = DatasetConfig(POS_LABEL_DATASET)
    assert 'good' == dut.metadata.pos_labels[RoleName.TARGET]


def test_pos_label_missing() -> None:
    clause = {
        'column_roles': {
            'target': {
                'name': 'class'
            }
        }
    }
    dut = DatasetConfig(clause=clause)
    assert dut.metadata.pos_labels[RoleName.TARGET] is None


BINARY_CLASSIFICATION_WITH_POS_LABEL = '''{
    "dataset": {
        "config": "ignore",
        "column_roles": {
            "target": {
                "name": "class",
                "pos_label": "good"
            }
        }
    },
    "problem_type": {
        "task": "binary_classification"
    }
}
'''


def test_metadata_binary_classification_with_pos_label() -> None:
    dut = ProblemDefinition(BINARY_CLASSIFICATION_WITH_POS_LABEL)
    dataset_conf = dut.get_conf(dut.Keys.DATASET)
    assert isinstance(dataset_conf, DatasetConfig)
    metadata = dataset_conf.metadata
    assert metadata.roles[RoleName.TARGET] == [Column('class')]
    assert metadata.pos_labels[RoleName.TARGET] == 'good'
