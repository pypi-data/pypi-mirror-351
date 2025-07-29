'''Step object for SimpleExecutor'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Iterable, Optional

from ...algorithms.impl.algorithm import Algorithm
from ...algorithms.impl.algorithm_instance import AlgorithmInstance
from ...algorithms.impl.fittable_algorithm_instance import FittableAlgorithmInstance
from ...generator.designator import Designator
from ...templates.impl.pipeline_step import PipelineStep
from ...wrangler.dataset import Dataset
from ..cucumber import Cucumber, JarOfCucumbers


class Error(Exception):
    '''Base error for SimpleStep'''


class InstantiationError(Error):
    '''Something has gone wrong while attempting to instantiate a model.'''


class SimpleExecutableStep(PipelineStep):
    '''Step representation for the SimpleExecutor

    The constructor 'compiles' a BoundStep (really a PipelineStep)
    into a SimpleStep.
    '''
    _bound_step: PipelineStep
    _model_instance: Optional[AlgorithmInstance]
    _trained = False

    def __init__(self,
                 bound_step: PipelineStep,
                 model: Optional[Algorithm] = None):
        super().__init__(
            model=model or bound_step._model,
            **bound_step.hyperparams())
        model = self._model
        self._bound_step = bound_step
        self._overrides = bound_step._overrides
        self._name = bound_step.opt_name
        self._serial_number = bound_step.serial_number
        self._init_model()

    def _init_model(self):
        '''Provide a customization point for model handling.

        There are some steps such as ParallelStep which need to
        override this because they don't have models.
        '''
        if self._model is None:
            raise InstantiationError(
                f'Can not instantiate {self._bound_step.designator} as model is not set.')
        instance = self._model.instantiate(**self._bound_step.hyperparams())
        if self._bound_step.serialized_model is not None:
            instance = instance.deserialize(self._bound_step.serialized_model)
            self.set_trained()
        self._model_instance = instance

    def set_trained(self):
        '''Force a step to the trained state.'''
        self._trained = True

    @property
    def locked(self) -> bool:
        '''Does this step have a model instance that is currently locked?'''
        return False if self._model_instance is None else self._model_instance.locked

    def converged(self) -> bool:
        '''If this step has a distributed model, has it converged?

        Always returns True for steps with no models or a non-distributed model.

        The threshold is the number of fits since the model changed enough to send to neighbors.
        '''
        return False if self._model_instance is None else self._model_instance.converged

    def fit(self, *args, **kwargs) -> None:
        '''Fit a model based on train data.

        The default fit method does nothing.
        '''
        assert self._model_instance is not None
        if isinstance(self._model_instance, FittableAlgorithmInstance):
            self._model_instance.fit(*args, **kwargs)

    def predict(self, *args, **kwargs) -> Optional[Dataset]:
        '''Apply model to input dataset to create output.

        This may require that the model is fit (self.trained == True) before it is called.
        '''
        assert self._model_instance is not None
        return self._model_instance.predict(*args, **kwargs)

    def cucumberize_all(self, pipeline_designator: Designator) -> JarOfCucumbers:
        '''Make this step into a Cucumber and put it in a JarOfCucumbers.

        Parallel steps will override this, but in the non-parallel case,
            this step only contains one algorithm and thus yields a jar of
            1 cucumber.
        '''
        assert self._model_instance is not None, (
            'BUG: cucumberize() called when model instance is none')
        assert self.filename is not None, (
            'BUG: cucumberize() called when filename is none')
        return JarOfCucumbers({
            self.filename:
            Cucumber(
                impl=self._model_instance,
                filename=self.filename,
                pipeline_designator=pipeline_designator,
                hyperparams=self.hyperparams()
            )}
        )

    @property
    def trained(self) -> bool:
        '''Has this model been trained?'''
        if isinstance(self._model_instance, FittableAlgorithmInstance):
            return self._model_instance.trained
        return True

    def start(self) -> None:
        '''Start the model.'''
        assert self._model_instance is not None
        self._model_instance.start()

    def stop(self) -> None:
        '''Stop the model.'''
        assert self._model_instance is not None
        self._model_instance.stop()

    @property
    def all_instances(self) -> Iterable[AlgorithmInstance]:
        '''Iterate through all algorithm instances.'''
        assert self._model_instance is not None
        yield self._model_instance
