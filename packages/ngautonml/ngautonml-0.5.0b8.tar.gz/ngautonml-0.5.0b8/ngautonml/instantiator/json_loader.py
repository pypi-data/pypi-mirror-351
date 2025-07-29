'''Load JSON from disk into a pipeline.'''
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .instantiator import InstantiatorError
from .loader import Loader
from ..algorithms.impl.algorithm import AlgorithmCatalog
from ..executor.cucumber import Cucumber
from ..generator.bound_pipeline import BoundPipeline
from ..templates.impl.pipeline_step import PipelineStep


class JsonLoader(Loader):
    '''Load JSON from disk into a pipeline.'''
    _pipeline: BoundPipeline
    _model_folder: Optional[Path]
    _algorithm_catalog: AlgorithmCatalog
    _load_models: bool

    def __init__(self,
                 saver_version: str,
                 algorithm_catalog: AlgorithmCatalog,
                 pipeline_file: Path,
                 model_folder: Optional[Path] = None,
                 load_models: bool = False):
        with pipeline_file.open('rb') as file_pointer:
            pipe = json.load(file_pointer)
        if saver_version != pipe['version']:
            raise InstantiatorError(
                f'This version of ngAutonML only supports {saver_version}, not {pipe["version"]}')

        self._algorithm_catalog = algorithm_catalog
        # TODO(Merritt/Piggy): replace this with a path manager
        self._model_folder = model_folder or (
            Path(pipe['output_dir']) / 'models' / pipe['pipeline_designator'])
        self._load_models = load_models
        pipeline = BoundPipeline(name=pipe['pipeline_template_name'])
        self._pipeline = self._load_pipeline(pipeline=pipeline, steps=pipe['steps'])

    @property
    def pipeline(self) -> BoundPipeline:
        '''Return the underlying pipeline.

        This is the main way of accessing the result of this object.
        '''
        return self._pipeline

    def _load_cucumber(self, step: Dict[str, Any]) -> Cucumber:
        model_path = self._model_folder / (step['model_filename'] + '.pkl')
        with model_path.open('rb') as file_pointer:
            return Cucumber.deserialize(file_pointer.read())

    def _load_step(self, pipeline: BoundPipeline, step: Dict[str, Any]) -> PipelineStep:
        assert self._algorithm_catalog is not None, (
            'BUG: We should not be loading without an algorithm catalog.'
        )
        hyperparams = step.get('hyperparams', {}).copy()
        if self._load_models:
            cucumber = self._load_cucumber(step)
            hyperparams.update(cucumber.hyperparams)
        assert isinstance(step['algorithm_name'], str)
        algorithm = self._algorithm_catalog.lookup_by_name(name=step['algorithm_name'])
        retval = pipeline.step(
            model=algorithm,
            serialized_model=cucumber.serialized_model,
            **hyperparams)
        if 'name' in step:
            retval.set_name(step['name'])
        return retval

    def _load_parallel(self,
                       pipeline: BoundPipeline,
                       pipelines: Dict[str, List[Dict[str, Any]]]) -> PipelineStep:
        subpipes = {}
        for subpipe, substeps in pipelines.items():
            newpipe = pipeline.new(name=subpipe)
            subpipes[subpipe] = self._load_pipeline(pipeline=newpipe, steps=substeps)
        return pipeline.parallel(**subpipes)

    def _load_pipeline(self, pipeline: BoundPipeline, steps: List[Dict[str, Any]]) -> BoundPipeline:
        retval = pipeline
        for step in steps:
            if step['type'] == 'parallel':
                self._load_parallel(pipeline=retval, pipelines=step['subpipelines'])
            elif step['type'] == 'step':
                self._load_step(pipeline=retval, step=step)
        return retval
