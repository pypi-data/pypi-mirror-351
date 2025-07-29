'''Metric object class for configurable and user-made metrics.'''
import abc

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Optional

from ...catalog.catalog_element_mixin import CatalogElementMixin
from ...wrangler.dataset import Dataset
from ...wrangler.dataset import DatasetKeys


class MetricError(Exception):
    '''Base error class for metrics'''


class MetricNameError(MetricError):
    '''Metric lacks a proper indexing name.'''


class MetricAttributeError(MetricError):
    '''Metric is missing a required attribute.'''


class MetricInvalidDatasetError(MetricError):
    '''Metric was passed a dataset it cannot use.'''


class Metric(CatalogElementMixin, metaclass=abc.ABCMeta):
    '''Base class wrapper for accessing metric objects.

    **Standard tags\\:**

    high
        values in 'true', 'false'.
        'true' means a higher score is better.

        If not specified, 'high' is assumed to be 'true' by the Ranker.

    needs_pos_label
        values in 'true', 'false'.
        'true' means there must be a pos_label specified in the Metadata
        in order for the metric to be used.

    needs_proba
        values in 'true', 'false'

        True means metric uses class probabilites instead of class predictions.
        For ex., ROC AUC.
        Should only be True for classification metrics.

    task
        values in 'binary_classification', 'multiclass_classification',
        'regression', and any other existing task types

        task(s) that the metric can be used for.
    '''
    _name: Optional[str] = None

    def __str__(self):
        return self.name

    @property
    def high(self) -> bool:
        '''Interprets 'high' tag as a boolean.

        True means a higher score is better.
        Defaults to True if tag is not set.
        '''
        return self._tag_to_bool('high', default=True)

    @property
    def needs_pos_label(self) -> bool:
        '''Interprets the 'needs_pos_label' tag as a boolean.

        False means there must be a pos_label specified in the Metadata
        in order for the metric to be used.

        Defaults to True if tag not set.
        '''
        return self._tag_to_bool('needs_pos_label', default=False)

    @property
    def needs_proba(self) -> bool:
        '''Interprets needs_proba tag as a boolean.

        True means metric uses class probabilites instead of class predictions.
        Defaults to False if tag not set
        '''
        return self._tag_to_bool('needs_proba', default=False)

    @abc.abstractmethod
    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        '''Calculates the metric results.'''

    def calculate_roc_curve(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> Dataset:
        '''Calculate the ROC Curve.'''
        _, _ = pred, ground_truth  # Convince pylint that this function is not abstract.
        raise NotImplementedError(
            f'calculate_roc_curve is not implemented for metric {self.name}.')


class SupervisedMetric(Metric):
    '''Subclass for supervised Metrics'''

    def validate_input(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> Dataset:
        '''Validates the Dataset and GroundTruth given. Useful for derived classes.'''
        if ground_truth is None:
            raise MetricInvalidDatasetError(
                'No Ground Truth Provided!')

        if pred is None:
            raise MetricInvalidDatasetError(
                'No Predictions Provided!')

        if not pred.has_predictions():
            raise MetricInvalidDatasetError(
                f'Predictions has no "{DatasetKeys.PREDICTIONS_TABLE.value}" key.')

        # Attempt to infer the GROUND_TRUTH.
        _ = ground_truth.ground_truth_table

        if ground_truth.metadata.target is None:
            raise MetricInvalidDatasetError(
                'Ground truth has no target column in metadata.')

        # We take a Optional[Dataset] and turn it into a Dataset. Type checkers are happy.
        return ground_truth

    @abc.abstractmethod
    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        '''
        Calculates the metric results.

        Most Supervised Metrics will require a ground truth. The implementation
        of the calculate should check if the ground truth exists.
        '''


class MetricStub(Metric):
    '''This is a stub'''
    _name = 'stub_metric'
    _high = True

    def calculate(self, pred: Dataset, ground_truth: Optional[Dataset] = None) -> float:
        return 0.0
