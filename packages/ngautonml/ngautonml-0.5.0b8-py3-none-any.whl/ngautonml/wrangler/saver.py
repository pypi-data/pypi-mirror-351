'''Save results.'''
from pathlib import Path

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.
from typing import Dict, Optional
import pandas as pd

from ngautonml.tables.impl.table import Table

from ..executor.executor_kind import ExecutorKind
from ..generator.designator import Designator, StepDesignator
from ..instantiator.executable_pipeline import ExecutablePipeline
from ..instantiator.executable_pipeline import PipelineResult, PipelineResults
from ..problem_def.output_config import OutputConfig

from .constants import Filename, FileType, OutputFolder
from .dataset import Dataset


def save_csv(path: Path, filename: Filename, dataset: Optional[Dataset]) -> None:
    '''Save the dataset as a csv at the specified path'''
    if dataset is None:
        raise NotImplementedError('Cannot save a None dataset.')
    for key, val in dataset.items():
        outfile = path / (f'{filename.value}_{key}.{FileType.CSV.value}')
        if not isinstance(val, pd.DataFrame) and not isinstance(val, Table):
            raise NotImplementedError(f'Cannot save a {type(val)}.')
        val.to_csv(outfile, index=False)


def save_arff(path: Path, filename: Filename, dataset: Optional[Dataset]) -> None:
    '''Save dataset as an arff file.'''
    raise NotImplementedError()


Savers = {
    FileType.CSV: save_csv,
    FileType.ARFF: save_arff
}


class Saver():
    '''Save results from the wrangler.'''
    _output_config: OutputConfig
    _current_ver: str

    def __init__(self, output_config: OutputConfig):
        self._output_config = output_config
        self._current_ver = '1.0'

    @property
    def current_version(self) -> str:
        '''Current version of directory system for saving pipelines and models.

        Needed for backward compatibility of saved files.
        '''
        return self._current_ver

    @property
    def output_path(self) -> Path:
        '''The root of the output hierarchy.'''
        assert self._output_config.path is not None, (
            'BUG: Saver is only built if there is an output path.'
        )
        return self._output_config.path

    def save(self, result: PipelineResult) -> Path:
        '''Save train predictions, and optionally test predictions, for a single PipelineResult.

        Operates according to this saver's output config.
        Returns the Path to the folder containing the predictions.
        '''

        foldername = result.bound_pipeline.designator
        folderpath = self.output_path / foldername
        folderpath.mkdir(exist_ok=True)

        Savers[self._output_config.file_type](
            path=folderpath,
            filename=Filename.TRAIN_PREDICTIONS,
            dataset=result.prediction
        )

        return folderpath

    def save_all_models(self, results: PipelineResults) -> Dict[StepDesignator, Path]:
        '''Save all the models in a PipelineResults.

        Returns a Path object for each saved step relative to the output root.
        '''
        return self.save_models(results.executable_pipelines)

    def model_path(self, des: Designator, model_filename: str) -> Path:
        '''The absolute path to a saved model, given its filename and pipeline designator.'''
        if self.current_version == '1.0':
            return self.output_path / OutputFolder.MODELS / des / model_filename
        raise NotImplementedError('model_path only knows version 1.0')

    def save_models(self,
                    pipelines: Dict[Designator, ExecutablePipeline]) -> Dict[StepDesignator, Path]:
        '''Save all the models in every executable pipeline.

        Returns a Path object for each saved step relative to the output root.
        '''
        retval = {}
        for pipedesignator, pipeline in pipelines.items():
            for stepdesignator, cucumber in pipeline.cucumberize_all().items():
                filename = cucumber.filename + '.pkl'
                model_path = self.model_path(des=pipedesignator, model_filename=filename)
                model_path.parent.mkdir(parents=True, exist_ok=True)
                with open(model_path, 'wb') as file_pointer:
                    file_pointer.write(cucumber.serialize())
                retval[stepdesignator] = Path(filename)
        return retval

    def save_pipeline(self, pipeline: bytes, des: Designator, kind: ExecutorKind) -> Path:
        '''Save a serialized pipeline in a file based on its designator and kind.'''
        pipepath = self.output_path / OutputFolder.PIPELINES
        pipepath.mkdir(exist_ok=True)
        filename = f'{des}{kind.suffix}'
        with open(pipepath / filename, 'wb') as file_pointer:
            file_pointer.write(pipeline)
        return pipepath / filename
