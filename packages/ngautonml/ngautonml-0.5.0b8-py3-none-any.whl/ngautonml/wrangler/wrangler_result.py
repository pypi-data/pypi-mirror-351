'''
This module defines the WranglerResult class, which represents
the results of the Wrangler.fit_predict_rank function.

The WranglerResult class contains information about the
split dataset, pipeline results, rankings, and executable pipelines.
'''

from typing import Dict, Optional

from ..generator.designator import Designator
from ..instantiator.executable_pipeline import ExecutablePipeline, PipelineResults
from ..ranker.ranker import Rankings
from ..splitters.impl.splitter import SplitDataset


class WranglerResult():
    '''The results of Wrangler.fit_predict_rank()'''

    _split_dataset: SplitDataset
    _train_results: PipelineResults
    _test_results: Optional[PipelineResults]
    _rankings: Rankings

    def __init__(self,
                 split_dataset: SplitDataset,
                 train_results: PipelineResults,
                 test_results: Optional[PipelineResults],
                 rankings: Rankings):
        '''
        Initialize a WranglerResult object.

        Args:
        :split_dataset: The ground truth and folds used to rank the pipelines.
        :train_results: Predictions on train data, acquired using cross-validation.
        :test_results: Predictions on test data, if supplied in the problem definition.
        :rankings: The rankings of all bound pipelines.
        '''
        self._split_dataset = split_dataset
        self._train_results = train_results
        self._test_results = test_results
        self._rankings = rankings

    @property
    def split_dataset(self) -> SplitDataset:
        '''The ground truth and folds used to rank the pipelines.'''
        return self._split_dataset

    @property
    def train_results(self) -> PipelineResults:
        '''Predictions on train data, acquired using cross-validation.'''
        return self._train_results

    @property
    def test_results(self) -> Optional[PipelineResults]:
        '''Predictions on test data, if supplied in the problem definition.'''
        return self._test_results

    @property
    def rankings(self) -> Rankings:
        '''The rankings of all bound pipelines.'''
        return self._rankings

    @property
    def executable_pipelines(self) -> Dict[Designator, ExecutablePipeline]:
        '''Get all the executable pipelines.'''
        return self._train_results.executable_pipelines
