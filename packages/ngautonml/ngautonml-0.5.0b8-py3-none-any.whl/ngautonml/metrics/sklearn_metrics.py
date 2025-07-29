'''Wrappers of metrics from sklearn, currently only contains roc_auc_score.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import sklearn.metrics  # type: ignore[import]
from sklearn.metrics import mean_squared_error  # type: ignore[import]

from ..problem_def.task import Task, TaskType
from ..wrangler.dataset import Dataset, DatasetKeyError, DatasetValueError, RoleName, TableFactory
from .impl.metric import MetricInvalidDatasetError, SupervisedMetric
from .impl.metric_catalog import MetricCatalog


class SklearnMetric(SupervisedMetric):
    '''Wrapper for sklean.metrics'''
    _metric: Optional[Callable[..., float]] = None

    def __init__(self,
                 name: str,
                 metric: Optional[Callable[..., float]] = None,
                 tasks: Optional[List[TaskType]] = None,
                 high: bool = True,
                 needs_proba: bool = False,
                 needs_pos_label: bool = False,
                 implements_calculate: bool = True):
        if metric is None:
            metric = getattr(sklearn.metrics, name, None)
        self._metric = metric
        if tasks is None:
            tasks = []
        self._tags = {
            Task.Keys.TASK_TYPE.value: [t.name.lower() for t in tasks],  # type: ignore[attr-defined] # pylint: disable=no-member,line-too-long
        }
        self._tags['needs_pos_label'] = [str(needs_pos_label).lower()]
        self._tags['high'] = [str(high).lower()]
        self._tags['needs_proba'] = [str(needs_proba).lower()]
        self._tags['implements_calculate'] = [str(implements_calculate).lower()]
        super().__init__(name=name)

    def _calculate(self,
                   pred: Dataset,
                   ground_truth: Optional[Dataset] = None) -> Union[
                       float, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        # TODO(Merritt): should be able to accept hyperparams from problem def
        ground_truth = self.validate_input(pred, ground_truth)
        # validate_input is guaranteed to return ground truth Dataset rather than None.
        assert ground_truth.metadata.target is not None
        ground_truth_for_sklearn = list(
            ground_truth.ground_truth_table[ground_truth.metadata.target.name])
        assert pred.metadata.target is not None, (
            'BUG: calculate() called with no target info in metadata'
        )

        if self.needs_proba:
            try:
                if pred.probabilities.shape[1] == 2:
                    # Assume binary classification

                    # requires that binary classification target values are always [0, 1]
                    if set(ground_truth_for_sklearn) != {0, 1}:
                        raise MetricInvalidDatasetError(
                            f'{self._name} requires binary classification '
                            'target values to be [0, 1].  '
                            f'Instead found: {set(ground_truth_for_sklearn)}.')
                    # requires that probabilities gets output with the probabilities for 0 in the
                    # 0th column and 1 in the 1st column
                    #   and the probas for 1 in the 1th column
                    predictions_for_sklearn = pred.probabilities.as_(  # type: ignore[attr-defined]
                        np.ndarray)[:, 1]
                else:
                    predictions_for_sklearn = pred.probabilities.as_(  # type: ignore[attr-defined]
                        np.ndarray)
            except DatasetKeyError:
                # We are not using 'from' because this error will be displayed
                #   alongside metric scores as a explanation for why this score
                #   cannot be calculated, thus we want it to be succint.
                raise MetricInvalidDatasetError(   # pylint: disable=raise-missing-from
                    'No class probabilities output.')
            except DatasetValueError as err:
                raise MetricInvalidDatasetError(
                    'Expected DataFrame for probabilites.') from err
        else:
            pred_table = pred.predictions_table
            predictions_for_sklearn = np.array(
                pred_table[pred.metadata.target.name])

        assert self._metric is not None

        if RoleName.TARGET in pred.metadata.pos_labels and self.needs_pos_label:
            return self._metric(
                ground_truth_for_sklearn,
                predictions_for_sklearn,
                pos_label=pred.metadata.pos_labels[RoleName.TARGET])

        return self._metric(ground_truth_for_sklearn, predictions_for_sklearn)

    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        got = self._calculate(pred, ground_truth)
        if not isinstance(got, float):
            raise NotImplementedError(
                f'Metric {self.name} does not return a float.  Instead found: {got}'
            )
        return got

    def calculate_roc_curve(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> Dataset:
        '''Calculate the ROC Curve.'''
        got = self._calculate(pred, ground_truth)
        if not isinstance(got, tuple) or len(got) != 3:
            raise NotImplementedError(
                f'Metric {self.name} does not return an roc curve of the expected format.  '
                f'Instead found: {got}'
            )
        tpr, fpr, thresholds = got
        retval = pred.output()
        retval.dataframe_table = TableFactory({'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds})
        return retval


def root_mean_squared_error(*args, **kwargs):
    '''Root Mean Squared Error'''
    return np.sqrt(mean_squared_error(*args, **kwargs))


METRICS: List[Dict[str, Any]] = [
    {
        'name': 'roc_auc_score',
        'tasks': [TaskType.BINARY_CLASSIFICATION],
        'needs_proba': True,
    },
    {
        'name': 'roc_curve',
        'tasks': [TaskType.BINARY_CLASSIFICATION],
        'needs_proba': True,
        'needs_pos_label': True,
        'implements_calculate': False
    },
    {
        'name': 'accuracy_score',
        'tasks': [TaskType.BINARY_CLASSIFICATION, TaskType.MULTICLASS_CLASSIFICATION],
    },
    {
        'name': 'f1_score',
        'high': True,
        'tasks': [TaskType.BINARY_CLASSIFICATION],
        'needs_pos_label': True,
    },
    {
        'name': 'mean_squared_error',
        'tasks': [TaskType.FORECASTING, TaskType.REGRESSION],
        'high': False,
    },
    {
        'name': 'root_mean_squared_error',
        'metric': root_mean_squared_error,
        'tasks': [TaskType.FORECASTING, TaskType.REGRESSION],
        'high': False,
    },
    {
        'name': 'mean_absolute_error',
        'tasks': [TaskType.FORECASTING, TaskType.REGRESSION],
        'high': False,
    },
    {
        'name': 'r2_score',
        'high': True,
        'tasks': [TaskType.REGRESSION],
    },
]


def register(catalog: MetricCatalog):
    '''Register all the metrics in this file.'''
    for met in METRICS:
        catalog.register(SklearnMetric(**met))
