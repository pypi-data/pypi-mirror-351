'''The "simple" executor'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, Optional
import traceback

from .simple_executable_pipeline import SimpleExecutablePipeline
from ..executor import Executor, ExecutorKind, TrainedPipelineCollection
from ...generator.designator import Designator
from ...instantiator.executable_pipeline import (ExecutablePipeline, PipelineResult,
                                                 FitError, PredictError)
from ...wrangler.dataset import Dataset, DatasetKeys
from ...wrangler.logger import Logger, Level

log = Logger(__file__, level=Level.INFO).logger()


class SimpleExecutor(Executor):
    '''A simple implementation of an Executor'''
    _kind = ExecutorKind('simple')

    def fit(self,
            dataset: Optional[Dataset],
            pipelines: Dict[Designator, ExecutablePipeline]
            ) -> TrainedPipelineCollection:
        '''Train a list of pipelines on a dataset.'''
        retval = TrainedPipelineCollection()
        for des, pipe in pipelines.items():
            assert isinstance(pipe, SimpleExecutablePipeline)
            try:
                retval.set(des, pipe.fit(dataset=dataset))
            except Exception:  # pylint: disable=broad-exception-caught
                trace = traceback.format_exc()
                log.warning(
                    'Encountered error in the %s pipeline during fit:\n%s',
                    des,
                    trace)
                pipe.set_fit_error(FitError(trace))
                retval.set(des, FitError(trace))
        return retval

    def predict(self,
                dataset: Dataset,
                pipelines: Dict[Designator, ExecutablePipeline]
                ) -> Dict[Designator, PipelineResult]:
        '''Use a list of simple pipelines to predict from a dataset.'''
        retval: Dict[Designator, PipelineResult] = {}
        for des, pipe in pipelines.items():
            assert isinstance(pipe, SimpleExecutablePipeline)
            try:
                retval[des] = pipe.predict(dataset=dataset)
            except Exception:  # pylint: disable=broad-exception-caught
                trace = traceback.format_exc()
                log.warning(
                    'Encountered error in the %s pipeline during predict:\n%s',
                    des,
                    trace)
                out_data = dataset.output()
                out_data[DatasetKeys.ERROR.value] = PredictError(trace)
                retval[des] = PipelineResult(
                    prediction=out_data,
                    executable_pipeline=pipe)
        return retval
