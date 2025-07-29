'''Constants that are used throughout the module'''
from enum import Enum
from typing import List, FrozenSet, Tuple
from pathlib import Path

# Copyright (c) 2023, 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


# We use this to identify the whole implementation. We use it for
# entry point names, and directories that contain extra configuration
# like ~/.ngautonml/.
PACKAGE_NAME = 'ngautonml'

# We ignore this subdirectory name when autoloading catalogs.
CATALOG_IGNORE = 'impl'


class JSONKeys(Enum):
    '''Standard keys in JSON requests for fit and predict'''
    DATA = 'data'
    DATAFRAME = 'dataframe'
    TARGET = 'target'
    COVARIATES = 'covariates'
    PREDICTIONS = 'predictions'
    PROBABILITIES = 'probabilities'
    HYPERPARAMS = 'hyperparams'
    GROUND_TRUTH = 'ground_truth'
    STATIC_EXOGENOUS = 'static_exogenous'


class ColumnType(Enum):
    '''Data type of a column'''
    NUMERIC = 'numeric'
    INTEGRAL = 'integral'
    CATEGORICAL = 'categorical'
    OTHER = 'other'

    @classmethod
    def list(cls) -> List[str]:
        '''Returns a list of all the valid column types.'''
        def getv(cls_elt: 'ColumnType') -> str:
            return getattr(cls_elt, 'value', '')
        return list(map(getv, cls))

    @classmethod
    def from_str(cls, col_type: str) -> 'ColumnType':
        '''Return a ColumnType from a str, raise a ValueError otherwise.'''
        def getnv(cls_elt: 'ColumnType') -> Tuple[str, str]:
            return (getattr(cls_elt, 'name', ''), getattr(cls_elt, 'value', ''))
        col_type = col_type.lower()
        for name, value in list(map(getnv, cls)):
            if value == col_type:
                return cls[name]
        raise ValueError(f'{col_type} is not a valid {cls.__name__}. '
                         f'Must be one of: {cls.list()}')


class Defaults():
    '''Default values for when not set in JSON problem definition'''
    DATA_TYPE = 'tabular'

    # for the image_dir image classification loader, target name does not need
    #   to  be specified by user, so we set a default.
    IMAGE_CLF_TARGET_NAME = 'class'

    # When we save data files, default to csv.
    FILE_TYPE = 'csv'

    # Frequency of time series for forecasting
    FREQUENCY = 'ME'

    # TODO(piggy): If we introduce an ExecutorCatalog, this should be read
    # from the catalog.
    # TODO(merritt): While we don't have an ExecutorCatalog,
    # the values of INSTANTIANTIONS should be of type Instantiations(Constant)
    INSTANTIANTIONS = ['stub_executor_kind', 'simple']

    # Timeout, in seconds, for listeners
    LISTENER_TIMEOUT = 2.0

    # Default loaded_format when input_format does not have a specifically associated default
    LOADED_FORMAT = 'pandas_dataframe'

    # Random seed
    SEED = 1701

    # How much of the dataset should we use for training?
    SPLIT_FRACTION = 0.8


class Filename(Enum):
    '''Standard output filenames.'''
    TRAIN_PREDICTIONS = 'train'
    TEST_PREDICTIONS = 'test'


class FileType(Enum):
    '''Type of file to save output predictions as.'''
    CSV = 'csv'
    ARFF = 'arff'

    @classmethod
    def list(cls) -> List[str]:
        '''Returns a list of all the valid file extensions.'''
        def getv(cls_elt: 'FileType') -> str:
            return getattr(cls_elt, 'value', '')
        return list(map(getv, cls))


class Matcher(Enum):
    '''Ways that hyperparameter overrides can be matched to pipeline steps'''
    # The Designator for the desired bound pipeline. Defaults to the
    # last queried step if no step is otherwise selected.
    DESIGNATOR = 'designator'

    # The name of the desired step(s).
    NAME = 'name'

    # The name of the algorithm associated with the desired step(s).
    ALGORITHM = 'algorithm'

    # A dict of key/value pairs selecting specific tag values from the
    # algorithm associated with the desired step(s).
    TAGS = 'tags'

    def __str__(self) -> str:
        return f'Matcher.{self.name}'


MATCHERS_TO_LOWERCASE = {Matcher.ALGORITHM, Matcher.DESIGNATOR, Matcher.NAME}


class OutputColName(Enum):
    '''Standard column names for output dataframes'''
    GROUND_TRUTH = 'ground truth'
    DESIGNATOR = 'pipeline'


class OutputFolder():
    '''Names of folders created to store output'''
    TRAIN_PREDICTIONS = Path('train_predictions')
    TEST_PREDICTIONS = Path('test_predictions')
    MODELS = Path('models')
    PIPELINES = Path('pipelines')


class ProblemDefControl(Enum):
    '''Standard values used in the JSON problem definition'''
    DISABLE_GRID_SEARCH = 'disable_grid_search'


class ProblemDefKeys(Enum):
    '''Standard top-level keys used in the JSON problem definition.'''
    # Top-level keys
    # TODO(piggy): Long term, we want these to be in ProblemDef or a closely
    #   related file.  They are still here for now until we can solve the problem
    #   of top-level ConfigComponents being able to know their own name without
    #   circular imports.
    # pylint: disable=duplicate-code
    TASK = 'problem_type'
    DATASET = 'dataset'
    METRICS = 'metrics'
    OUTPUT = 'output'
    HYPERPARAMS = 'hyperparams'
    CROSS_VALIDATION = 'cross_validation'
    AGGREGATION = 'aggregation'
    CONTROL = 'control'

    # Dataset keys
    CONFIG = 'config'
    COL_ROLES = 'column_roles'
    TRAIN_PATH = 'train_path'
    TEST_PATH = 'test_path'
    # pylint: disable=duplicate-code
    TRAIN_DIR = 'train_dir'  # used for ImageDirDataLoader
    TEST_DIR = 'test_dir'  # used for ImageDirDataLoader
    # pylint: enable=duplicate-code
    STATIC_EXOGENOUS_PATH = 'static_exogenous_path'  # For forecasting problems only

    # Column roles keys
    POS_LABEL = 'pos_label'
    COL_NAME = 'name'


# TODO(Merritt): this is deprecated, replace with REQUIRED_KEYS and
#   ALLOWED_KEYS classmethod in ConfigComponent
class ProblemDefKeySet():
    '''Standard sets of problem def keys'''

    class DATASET():
        '''Standard sets of keys for the dataset config clause.'''
        REQUIRED: FrozenSet[str] = frozenset([
            ProblemDefKeys.CONFIG.value])
        ALLOWED: FrozenSet[str] = REQUIRED.union(frozenset([
            ProblemDefKeys.COL_ROLES.value,
            ProblemDefKeys.TEST_PATH.value,
            ProblemDefKeys.TRAIN_PATH.value,
            ProblemDefKeys.TRAIN_DIR.value,
            ProblemDefKeys.TEST_DIR.value,
            ProblemDefKeys.STATIC_EXOGENOUS_PATH.value]))

        class ROLES():
            '''Metadata for roles'''
            REQUIRED: FrozenSet[str] = frozenset([
                ProblemDefKeys.COL_NAME.value])
            ALLOWED: FrozenSet[str] = REQUIRED.union(frozenset([
                ProblemDefKeys.POS_LABEL.value
            ]))


class RangeMethod(Enum):
    '''Methods of specifying the range of a hyperparameter for tuning'''
    # We provide exactly the one fixed value in range.
    FIXED = 'fixed'
    # Search each of the values in range.
    LIST = 'list'
    # Search a linear range of values in range: [start, increment, end]
    LINEAR = 'linear'

    def __str__(self) -> str:
        return f'RangeMethod.{self.name}'
