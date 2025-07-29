'''Tests for hyperparam_config.py.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,duplicate-code

import pytest

from ..searcher.param_range import ParamRange
from ..searcher.params import Matcher
from ..wrangler.constants import RangeMethod

from .hyperparam_config import HyperparamConfig, HyperparamTooManyClauses
from .problem_def import remove_comments

TEST_PARAMS = {
    'hyperparams': [
        {
            '_comments': [
                'Apply `max_depth` to all instances of RandomForestClassifier.',
                'Note that algorithm is the name of the algorithm associated with',
                'the step where name is name of the step.'
            ],
            'select': {
                'algorithm': 'sklearn.ensemble.RandomForestClassifier'
            },
            'params': {
                'max_depth': {
                    'fixed': 25
                }
            },
        },
        {
            '_comments': [
                'Apply `strategy` to the algorithm in the "simpleImputer1" step within the',
                'RandomForestClassifier bound pipeline of the tabular_classification template.',
                'This is an unusual special case. You probably want the previous case to set',
                'hyperparams for all instances of the algorithm.'
            ],
            'select': {
                'designator': 'tabular_classifiction::sklearn.ensemble.RandomForestClassifier',
                'name': 'simpleImputer1'
            },
            'params': {
                'strategy': {
                    'fixed': 'median'
                }
            }
        },
        {
            '_comments': [
                'Apply `add_indicator` to all preprocessors of type impute.'
            ],
            'select': {
                'tags': {
                    'preprocess_type': 'impute'
                }
            },
            'params': {
                'add_indicator': {
                    'fixed': 'True'
                }
            }
        },
        {
            '_comments': [
                "Set PRIMITIVE_NAME_1's HYPERPARAM_1 to 1, then 2, then 3",
                "This is how you do grid search. This creates 3 bound pipelines."
            ],
            'select': {
                'algorithm': 'PRIMITIVE_NAME_1'
            },
            'params': {
                'HYPERPARAM_1': {
                    'list': [1, 2, 3]
                }
            }
        },
        {
            '_comments': [
                'Do grid search of values from 0 to 6 in increments of 1 (7 total).',
                'If PRIMITIVE_NAME_1 and PRIMITIVE_NAME_2 are in the same bound',
                'pipeline, we will get 21 bound pipelines.'
            ],
            'select': {
                'algorithm': 'PRIMITIVE_NAME_2'
            },
            'params': {
                'HYPERPARAM_2': {
                    'linear': [0, 1, 6]
                }
            }
        }
    ]
}


def test_hyperparam_sunny_day():
    dut = HyperparamConfig(remove_comments(TEST_PARAMS))
    assert len(dut.overrides) == 5
    overrides = list(dut.overrides)
    assert overrides[0].selector[Matcher.ALGORITHM] == 'sklearn.ensemble.randomforestclassifier'
    assert overrides[0].params['max_depth'] == ParamRange(RangeMethod.FIXED, 25)
    assert overrides[4].params['HYPERPARAM_2'].range == [0, 1, 6]


TOO_MANY_TOP_LEVEL = {
    'hyperparams': [
        {
            'select': {
                'algorithm': 'PRIMITIVE_NAME_1'
            },
            'params': {
                'HYPERPARAM_1': {
                    'list': [1, 2, 3]
                }
            },
            'a_third_thing': {}
        }
    ]
}


def test_hyperparam_extra_clause():
    with pytest.raises(HyperparamTooManyClauses, match='a_third_thing'):
        HyperparamConfig(TOO_MANY_TOP_LEVEL)


TOO_MANY_PARAM_METHODS = {
    'hyperparams': [
        {
            'select': {
                'algorithm': 'PRIMITIVE_NAME_1'
            },
            'params': {
                'HYPERPARAM_1': {
                    'list': [1, 2, 3],
                    'fixed': 25,
                }
            },
        }
    ]
}


def test_hyperparam_extra_method():
    with pytest.raises(HyperparamTooManyClauses, match='fixed'):
        HyperparamConfig(TOO_MANY_PARAM_METHODS)


NO_GRID_PARAMS = {
    'hyperparams': [
        "disable_grid_search",
        {
            'select': {
                'algorithm': 'sklearn.ensemble.RandomForestClassifier'
            },
            'params': {
                'max_depth': {
                    'list': [1, 2, 3],
                    "default": 1,
                }
            },
        },
    ]
}


def test_disable_grid_search() -> None:
    dut = HyperparamConfig(NO_GRID_PARAMS)
    assert dut.disable_grid_search
    assert len(dut.overrides) == 1
