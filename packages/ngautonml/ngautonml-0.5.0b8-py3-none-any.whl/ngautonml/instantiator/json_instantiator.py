'''An instantiator for saving pipelines as JSON.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..executor.executor import ExecutablePipeline
from ..instantiator.instantiator import Instantiator, InstantiatorError
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import StepDesignator
from ..templates.impl.pipeline_step import PipelineStep
from ..templates.impl.parallel_step import ParallelStep
from ..executor.executor_kind import ExecutorKind

from .json_loader import JsonLoader


class JsonInstantiator(Instantiator):
    '''An instantiator for saving pipelines as JSON.'''

    def instantiate(self, pipeline: BoundPipeline) -> ExecutablePipeline:
        raise NotImplementedError(
            'Currently JsonInstantiator is only used to save pipelines to disk.')

    def _serialize_pipeline_steps(
            self,
            pipeline: BoundPipeline,
            model_paths: Dict[StepDesignator, Path]) -> List[Dict[str, Any]]:
        '''Turn all steps in this pipeline into a JSON serializable object for saving.'''
        steps = []
        for step in pipeline.steps:
            steps.append(self._serialize_step(step, model_paths))
        return steps

    def _serialize_step(
            self,
            step: PipelineStep,
            model_paths: Dict[StepDesignator, Path]) -> Dict[str, Any]:
        '''Turn this step into a JSON serializable object for saving.'''

        if isinstance(step, ParallelStep):
            return self._serialize_parallel(step, model_paths)

        retval: Dict[str, Any] = {
            'type': 'step',
        }
        if step.filename is not None:
            retval['model_filename'] = str(step.filename)
        if step.opt_name is not None:
            retval['name'] = step.opt_name

        model_name = step.model_name
        assert model_name is not None, (
            f'BUG: step {step.opt_name} is not parallel but has no model.'
        )
        retval['algorithm_name'] = model_name

        if step.queried:
            retval['queried'] = True

        hyperparams = {
            param: step.model.param_to_json(param, py_value)
            for param, py_value in step.hyperparams().items()
        }
        if hyperparams:
            try:
                _ = json.dumps(hyperparams)
            except (TypeError, OverflowError) as err:
                raise InstantiatorError(
                    f'Something in hyperparams for pipeline step {step.filename}'
                    f'is not JSON serializable:\n{hyperparams}.\n'
                    f'Perhaps {step.model.__class__.__name__}._hyperparam_lookup'
                    ' needs to be extended?') from err
            retval["hyperparams"] = hyperparams
        return retval

    def _serialize_parallel(
            self,
            step: ParallelStep,
            model_paths: Dict[StepDesignator, Path]) -> Dict[str, Any]:
        '''Turn this parallel step, including its subpipelines,
        into a JSON serializable object for saving.'''
        retval = {
            'type': 'parallel',
            'subpipelines': {}
        }
        for sub_name, sub_pipe in step.subpipelines.items():
            assert isinstance(sub_pipe, BoundPipeline), (
                f'BUG: subpipeline {sub_name} recieved by JsonInstantiator is not '
                f'a BoundPipeline, instead found {type(sub_pipe)}. ')
            assert isinstance(retval['subpipelines'], dict)
            retval['subpipelines'][sub_name] = self._serialize_pipeline_steps(
                pipeline=sub_pipe,
                model_paths=model_paths)
        return retval

    def save(self, pipeline: BoundPipeline, model_paths: Dict[StepDesignator, Path]) -> Path:
        '''Save pipeline as a JSON file using self._saver.

        Returns Path to the saved file.
        '''
        if self._saver is None:
            raise InstantiatorError('You must define a Saver to save from an Instantiator.')

        image = {
            'version': self._saver.current_version,
            'pipeline_designator': pipeline.designator,
            'pipeline_template_name': pipeline.name,
            'output_dir': str(self._saver.output_path),
            'steps': self._serialize_pipeline_steps(pipeline=pipeline, model_paths=model_paths)
        }

        body = json.dumps(image, indent=4).encode()

        return self._saver.save_pipeline(
            body,
            des=pipeline.designator,
            kind=ExecutorKind('json'))

    def load(self, pipeline_file: Path, load_models: bool = False,
             model_folder: Optional[Path] = None) -> BoundPipeline:
        '''Load a BoundPipeline from disk.'''
        assert self._algorithm_catalog is not None, (
            'BUG: loading a pipeline requires an algorithm catalog.'
        )
        assert self._saver is not None, (
            'BUG: loading a pipeline requires a saver.'
        )
        return JsonLoader(saver_version=self._saver.current_version,
                          algorithm_catalog=self._algorithm_catalog,
                          load_models=load_models,
                          model_folder=model_folder,
                          pipeline_file=pipeline_file).pipeline
