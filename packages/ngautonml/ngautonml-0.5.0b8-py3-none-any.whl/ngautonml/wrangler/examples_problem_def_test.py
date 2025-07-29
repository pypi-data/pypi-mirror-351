'''Tests ensuring that the problem definition JSON in the examples folder is valid.'''
import os
from pathlib import Path

from ..problem_def.problem_def import ProblemDefinition

# pylint: disable=missing-function-docstring,duplicate-code


def module_path() -> Path:
    current_path = str(os.getenv('PYTEST_CURRENT_TEST')).split('::', maxsplit=1)[0]
    pathobj = Path(current_path).resolve()
    module_parent = pathobj.parents[2]
    return module_parent


def test_example_tabular_regression(tmp_path: Path) -> None:
    path = module_path() / 'examples' / 'regression' / 'diabetes.json'
    csv_path = module_path() / 'examples' / 'regression' / 'diabetes-train.csv'
    test_csv_path = module_path() / 'examples' / 'regression' / 'diabetes-test.csv'
    with path.open() as file:
        pd_str = file.read()
    pd_paths_fixed = pd_str.replace(
        'ngautonml/examples/regression/diabetes-train.csv',
        str(csv_path)
    )
    pd_paths_fixed = pd_paths_fixed.replace(
        'ngautonml/examples/regression/diabetes-test.csv',
        str(test_csv_path)
    )
    pd_paths_fixed = pd_paths_fixed.replace(
        'ngautonml/examples/regression/diabetes-output',
        str(tmp_path / 'output_dir')
    )
    ProblemDefinition(pd_paths_fixed)  # fails if example json is not valid


def test_example_tabular_classification(tmp_path: Path):
    pd_path = module_path() / 'examples' / 'classification' / 'credit.json'
    csv_path = module_path() / 'examples' / 'classification' / 'credit-train.csv'
    test_csv_path = module_path() / 'examples' / 'classification' / 'credit-test.csv'
    with pd_path.open() as file:
        pd_str = file.read()
    pd_paths_fixed = pd_str.replace(
        'ngautonml/examples/classification/credit-train.csv',
        str(csv_path)
    )
    pd_paths_fixed = pd_paths_fixed.replace(
        'ngautonml/examples/classification/credit-test.csv',
        str(test_csv_path)
    )
    pd_paths_fixed = pd_paths_fixed.replace(
        'ngautonml/examples/classification/credit-output',
        str(tmp_path / 'output_dir')
    )
    ProblemDefinition(pd_paths_fixed)  # fails if example json is not valid


def test_example_tabular_classification_arff(tmp_path: Path):
    pd_path = module_path() / 'examples' / 'classification' / 'credit-arff.json'
    arff_path = module_path() / 'examples' / 'classification' / 'dataset_31_credit-g.arff'
    with pd_path.open() as file:
        pd_str = file.read()
    pd_paths_fixed = pd_str.replace(
        'ngautonml/examples/classification/dataset_31_credit-g.arff',
        str(arff_path)
    )
    pd_paths_fixed = pd_paths_fixed.replace(
        'ngautonml/examples/classification/credit-output',
        str(tmp_path / 'output_dir')
    )
    ProblemDefinition(pd_paths_fixed)  # fails if example json is not valid
