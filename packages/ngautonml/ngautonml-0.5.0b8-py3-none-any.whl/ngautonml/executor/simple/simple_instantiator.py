'''An instantiator for the "simple" executor.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.
from typing import Dict
from pathlib import Path

from ...instantiator.instantiator import Instantiator
from ...generator.bound_pipeline import BoundPipeline
from ...generator.designator import StepDesignator
from .simple_executable_pipeline import SimpleExecutablePipeline


class SimpleInstantiator(Instantiator):
    '''An instantiator for the "simple" executor.'''

    def instantiate(self, pipeline: BoundPipeline) -> SimpleExecutablePipeline:
        retval = SimpleExecutablePipeline(
            pipeline=pipeline)
        return retval

    def save(self, pipeline: BoundPipeline, model_paths: Dict[StepDesignator, Path]) -> Path:
        raise NotImplementedError('Serialization does not make sense for SimpleExecutable.')
        # Fight me.
