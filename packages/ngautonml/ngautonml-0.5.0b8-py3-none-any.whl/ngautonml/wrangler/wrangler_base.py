'''Base class for Wranglers that can fit, predict and rank sets of pipelines.

The Wrangler does the automl pieces, this base class does the rest.
'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=too-many-instance-attributes,too-many-arguments

import abc
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Type, Union

from ..aggregators.impl.aggregator_auto import AggregatorCatalogAuto
from ..aggregators.impl.aggregator_catalog import AggregatorCatalog
from ..algorithms.impl.algorithm import AlgorithmCatalog
from ..algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ..catalog.catalog import Catalog
from ..communicators.impl.communicator_auto import CommunicatorCatalogAuto
from ..communicators.impl.communicator_catalog import CommunicatorCatalog
from ..config_components.dataset_config import DatasetConfig
from ..cross_validators.impl.cross_validator import CrossValidatorCatalog
from ..cross_validators.impl.cross_validator_auto import \
    CrossValidatorCatalogAuto
from ..data_loaders.impl.data_loader import DataLoader
from ..data_loaders.impl.data_loader_auto import DataLoaderCatalogAuto
from ..data_loaders.impl.data_loader_catalog import DataLoaderCatalog
from ..discoverers.impl.discoverer_auto import DiscovererCatalogAuto
from ..discoverers.impl.discoverer_catalog import DiscovererCatalog
from ..executor.executor import Executor
from ..executor.simple.simple_executor import SimpleExecutor
from ..generator.bound_pipeline import BoundPipeline
from ..generator.designator import Designator
from ..generator.generator import Generator, GeneratorImpl
from ..instantiator.executable_pipeline import (ExecutablePipeline,
                                                PipelineResults)
from ..instantiator.instantiator_factory import InstantiatorFactory
from ..metrics.impl.metric import Metric, MetricInvalidDatasetError
from ..metrics.impl.metric_catalog import MetricCatalog
from ..metrics.impl.metric_auto import MetricCatalogAuto
from ..pipeline_loaders.impl.pipeline_loader_auto import PipelineLoaderCatalogAuto
from ..pipeline_loaders.impl.pipeline_loader_catalog import PipelineLoaderCatalog
from ..problem_def.problem_def import ProblemDefinition
from ..ranker.ranker import Ranker, Rankings
from ..ranker.ranker_impl import RankerImpl
from ..searcher.searcher import Searcher, SearcherImpl
from ..splitters.impl.splitter import SplitterCatalog
from ..splitters.impl.splitter_auto import SplitterCatalogAuto
from ..templates.impl.pipeline_template import PipelineTemplate
from ..templates.impl.template import TemplateCatalog
from ..templates.impl.template_auto import TemplateCatalogAuto

from .dataset import Dataset
from .logger import Level, Logger
from .saver import Saver

log = Logger(__file__, level=Level.WARN, to_stdout=True).logger()


class Error(Exception):
    '''Base error for Wrangler.'''


class WranglerFailure(Error):
    '''Wrangler can not procede.'''


class ReassignmentError(Error):
    '''An attempt was made to assign a value more than once.'''


class WranglerBase(metaclass=abc.ABCMeta):  # pylint: disable=too-many-public-methods
    '''Base class for Wranglers that can fit, predict and rank sets of pipelines.

    The Wrangler does the automl pieces, this base class does the rest.
    '''
    _bound_pipelines: Optional[Dict[Designator, BoundPipeline]] = None
    # These are all pipelines identified during the first run.
    _all_executable_pipelines: Optional[Dict[Designator, ExecutablePipeline]] = None
    # This is a subset of _all_pipelines which will be the default
    # for subsequent fit, predict, and rank methods.
    _current_executable_pipelines: Optional[Dict[Designator, ExecutablePipeline]] = None

    def __init__(
        self,
        problem_definition: ProblemDefinition,
        aggregator_catalog: Optional[Type[AggregatorCatalog]] = None,
        algorithm_catalog: Optional[Type[AlgorithmCatalog]] = None,
        communicator_catalog: Optional[Type[CommunicatorCatalog]] = None,
        dataloader_catalog: Optional[Type[DataLoaderCatalog]] = None,
        discoverer_catalog: Optional[Type[DiscovererCatalog]] = None,
        executor: Optional[Type[Executor]] = None,
        generator: Optional[Type[Generator]] = None,
        instantiator_factory: Optional[Type[InstantiatorFactory]] = None,
        metric_catalog: Optional[Type[MetricCatalog]] = None,
        pipeline_loader_catalog: Optional[Type[PipelineLoaderCatalog]] = None,
        ranker: Optional[Type[Ranker]] = None,
        saver: Optional[Type[Saver]] = None,
        searcher: Optional[Type[Searcher]] = None,
        splitter_catalog: Optional[Type[SplitterCatalog]] = None,
        template_catalog: Optional[Type[TemplateCatalog]] = None,
        validator_catalog: Optional[Type[CrossValidatorCatalog]] = None
    ):
        # TODO(Merritt): initialize the logger
        # instantiate default components only if input is None
        self._pd = problem_definition

        self._metric_catalog = (metric_catalog or MetricCatalogAuto)()
        self._communicator_catalog = (communicator_catalog or CommunicatorCatalogAuto)()
        self._discoverer_catalog = (discoverer_catalog or DiscovererCatalogAuto)()
        self._algorithm_catalog = (algorithm_catalog or AlgorithmCatalogAuto)(
            communicator_catalog=self._communicator_catalog,
            discoverer_catalog=self._discoverer_catalog
        )
        self._generator = (generator or GeneratorImpl)(
            algorithm_catalog=self._algorithm_catalog,
            problem_definition=self._pd)
        self._template_catalog = (template_catalog or TemplateCatalogAuto)(
            algorithm_catalog=self._algorithm_catalog,
            generator=self._generator
        )
        self._pipeline_loader_catalog = (pipeline_loader_catalog or PipelineLoaderCatalogAuto)(
            algorithm_catalog=self._algorithm_catalog,
            template_catalog=self._template_catalog)
        self._searcher = (searcher or SearcherImpl)(hyperparams=self._pd.hyperparams)
        self._executor = (executor or SimpleExecutor)()
        self._ranker = (ranker or RankerImpl)()
        self._splitter_catalog = (splitter_catalog or SplitterCatalogAuto)(
            cv_config=self._pd.cross_validation_config)
        self._dataloader_catalog = (dataloader_catalog or DataLoaderCatalogAuto)()
        self._dataloader: Optional[DataLoader] = None
        self._validator_catalog = (validator_catalog or CrossValidatorCatalogAuto)()
        self._aggregator_catalog = (aggregator_catalog or AggregatorCatalogAuto)()
        self._saver = None
        # If there is no output path, we'll output no files.
        if self._pd.output.path is not None:
            self._saver = (saver or Saver)(self._pd.output)
        self._instantiator_factory = (
            instantiator_factory or InstantiatorFactory)(
                saver=self._saver)

    @property
    def aggregator_catalog(self) -> AggregatorCatalog:
        '''Query and register aggregators'''
        return self._aggregator_catalog

    @property
    def algorithm_catalog(self) -> AlgorithmCatalog:
        '''Query and register algorithms'''
        return self._algorithm_catalog

    @property
    def bound_pipelines(self) -> Dict[Designator, BoundPipeline]:
        '''The set of pipelines that have been bound.'''
        assert self._bound_pipelines is not None, (
            'BUG: bound_pipelines accessed before it is set.'
        )
        return self._bound_pipelines

    @property
    def communicator_catalog(self) -> CommunicatorCatalog:
        '''Query and register communicators'''
        return self._communicator_catalog

    @property
    def dataloader_catalog(self) -> DataLoaderCatalog:
        '''Load data based on input and loaded types.'''
        return self._dataloader_catalog

    @property
    def discoverer_catalog(self) -> DiscovererCatalog:
        '''Query and register discoverers.'''
        return self._discoverer_catalog

    @property
    def metric_catalog(self) -> Catalog[Metric]:
        '''Query and register metrics.'''
        return self._metric_catalog

    @property
    def metrics(self) -> Dict[str, Metric]:
        '''The metrics specified in the problem definition.'''
        return self._metric_catalog.lookup_metrics(self._pd)

    @property
    def pipeline_loader_catalog(self) -> PipelineLoaderCatalog:
        '''Query and register pipeline loaders.'''
        return self._pipeline_loader_catalog

    @property
    def splitter_catalog(self) -> SplitterCatalog:
        '''Query and register splitters.'''
        return self._splitter_catalog

    @property
    def template_catalog(self) -> TemplateCatalog:
        '''Query and register templates.'''
        return self._template_catalog

    @property
    def validator_catalog(self) -> CrossValidatorCatalog:
        '''Query and register cross validators.'''
        return self._validator_catalog

    @property
    def generator(self) -> Generator:
        '''Generates bound pipelines from templates.'''
        return self._generator

    @property
    def ranker(self) -> Ranker:
        '''Ranks the results of running pipelines.'''
        return self._ranker

    @property
    def all_trained(self) -> bool:
        '''Are all the current pipelines trained?'''
        if self._current_executable_pipelines is None:
            return True
        return all(pipeline.trained
                   for pipeline in self._current_executable_pipelines.values())

    @property
    def locked(self) -> bool:
        '''Does any current pipeline contain a model that is currently locked?'''
        if self._current_executable_pipelines is None:
            return False
        return any(pipe.locked
                   for pipe in self._current_executable_pipelines.values())

    def converged(self) -> bool:
        '''Are all the models in all the current pipelines converged?'''

        if self._current_executable_pipelines is None:
            return False
        return all(pipe.converged()
                   for pipe in self._current_executable_pipelines.values())

    def _find_data_loader(self) -> DataLoader:
        if self._dataloader is not None:
            return self._dataloader
        dataset_config = self._pd.get_conf(self._pd.Keys.DATASET.value)  # type: ignore[attr-defined] # pylint: disable=line-too-long
        assert isinstance(dataset_config, DatasetConfig)
        self._dataloader = self._dataloader_catalog.construct_instance(dataset_config)
        return self._dataloader

    def load_train_dataset(self) -> Optional[Dataset]:
        '''Load this wrangler's train data.'''
        return self._find_data_loader().load_train()

    def load_test_dataset(self) -> Optional[Dataset]:
        '''Load this wrangler's test data, without the target column.'''
        return self._find_data_loader().load_test()

    def load_ground_truth_dataset(self) -> Optional[Dataset]:
        '''Load the target column for this wrangler's test data.'''
        return self._find_data_loader().load_ground_truth()

    def ez_dataset(self, data: Any, **kwargs) -> Dataset:
        '''Load in-memory data into a Dataset object, stored at key 'key'.'''
        return self._find_data_loader().ez_dataset(data=data, **kwargs)

    def save(self, train_results: PipelineResults) -> Dict[Designator, Path]:
        '''Save all the models and all the pipelines.'''
        assert self._saver is not None, 'BUG: Only call save if there is a saver.'
        retval: Dict[Designator, Path] = {}
        model_paths = self._saver.save_models(train_results.executable_pipelines)
        for kind in self._pd.output.instantiations:
            instantiatior = self._instantiator_factory.build(kind)
            for des, result in train_results.items():
                retval[des] = instantiatior.save(result.bound_pipeline, model_paths)
        return retval

    def _build_pipelines(self) -> Dict[Designator, BoundPipeline]:
        '''Build a set of pipelines to use for machine learning'''
        templates = self.lookup_templates()
        if len(templates) == 0:
            raise WranglerFailure(f'found no templates for {self._pd.task}')
        log.info('Found %d templates', len(templates))
        print(f'Found {len(templates)} templates')

        gen_result = self._generator.generate_all(templates)
        log.info("Generated %d bound pipelines", len(gen_result))
        print(f"Generated {len(gen_result)} bound pipelines")

        retval = self._searcher.bind_all(gen_result)
        log.info('Hyperparam searcher produced %d bound pipelines', len(retval))
        print(f'Hyperparam searcher produced {len(retval)} bound pipelines')

        return retval

    def fit(self,
            dataset: Optional[Dataset],
            pipelines: Optional[Dict[Designator, ExecutablePipeline]] = None
            ) -> Dict[Designator, ExecutablePipeline]:
        '''Fit the given pipelines with a new dataset.

        If no pipelines are specified, use the current set.
        '''
        if pipelines is None:
            pipelines = self._current_executable_pipelines

        assert pipelines is not None
        self._executor.fit(
            dataset=dataset,
            pipelines=pipelines)

        return pipelines

    def predict(self,
                new_data: Optional[Dataset] = None,
                trained_pipelines: Optional[
                    Dict[Designator, ExecutablePipeline]] = None) -> PipelineResults:
        '''Predict on new test data that was not supplied in the problem definition.'''
        if trained_pipelines is None:
            trained_pipelines = self._current_executable_pipelines
        assert trained_pipelines is not None, (
            'BUG: predict called with None current pipelines.'
        )
        pipeline_errors: List[str] = []
        for des, pipe in trained_pipelines.items():
            if pipe.kind != self._executor.kind:
                pipeline_errors.append(
                    f'Pipeline {des} has incorrect ExecutorKind {pipe.kind}; '
                    f'expected {self._executor.kind}. \n')
            elif not pipe.trained:
                pipeline_errors.append(
                    f'Pipeline {des} is untrained. \n')

        if len(pipeline_errors) > 0:
            raise WranglerFailure(
                'Bad pipeline(s) provided to predict(): \n'
                f'{"".join(pipeline_errors)}')

        if new_data is None:
            new_data = self.load_test_dataset()
        if new_data is None:
            raise WranglerFailure('No data provided to predict() and no test data specified '
                                  'in the problem definition.  Nothing to predict.')
        results = self._executor.predict(dataset=new_data, pipelines=trained_pipelines)
        return PipelineResults(results)

    def set_current(self, *args: str) -> None:
        '''Set the current set of pipelines to work with by name.

        If no arguments are given, reset to the full set of pipelines
        identified in the last fit_predict_rank.
        '''
        if len(args) == 0:
            self._current_executable_pipelines = self._all_executable_pipelines
            return
        if self._all_executable_pipelines is None:
            self._current_executable_pipelines = None
            return
        self._current_executable_pipelines: Dict[Designator, ExecutablePipeline] = {
            Designator(des): self._all_executable_pipelines[Designator(des)]
            for des in args
        }

    def roc_curve(self,
                  results: Union[PipelineResults, Dict[Designator, Optional[Dataset]]],
                  ground_truth: Dataset,
                  metric: Union[str, Metric] = 'roc_curve') -> Dict[
                      Designator, Union[Dataset, Exception, None]]:
        '''Compute the ROC curve for a set of pipeline results.

        Returns:
            A dictionary of results, where the key is the designator of the pipeline
            and the value is the ROC curve. Eash Dataset contains a DataFrame with
            columns 'fpr', 'tpr', and 'thresholds'.

            The value will be None if the input dataset is None.

            If an expected type of Exception is raised while calculating,
            it will return it in the place of a Dataset.
        '''
        if isinstance(results, PipelineResults):
            results = results.predictions

        if isinstance(metric, str):
            metric = self._metric_catalog.lookup_by_name(metric)

        retval: Dict[Designator, Union[Dataset, Exception, None]] = {}

        for des, pred in results.items():
            if pred is None:
                retval[des] = pred
            else:
                try:
                    retval[des] = metric.calculate_roc_curve(pred=pred, ground_truth=ground_truth)
                except (NotImplementedError, MetricInvalidDatasetError) as err:
                    retval[des] = err

        return retval

    def rank(self,
             results: PipelineResults,
             metrics: Optional[Iterable[Union[str, Metric]]] = None,
             ground_truth: Optional[Dataset] = None) -> Rankings:
        '''Rank a set of pipeline results.

        If no metrics are provided, uses the ones from the problem definition

        If no ground truth is provided, attempts to infer it using the SplitDataset
        associated with an arbitrary PipelineResult.
        '''
        metrics_for_ranker: Dict[str, Metric] = {}
        if metrics is None:
            metrics_for_ranker = self._metric_catalog.lookup_metrics(self._pd)
        else:
            for m in metrics:
                if isinstance(m, Metric):
                    metrics_for_ranker[m.name] = m
                    continue

                if isinstance(m, str):
                    metrics_for_ranker[m] = self._metric_catalog.lookup_by_name(m)
                    continue

                raise ValueError(
                    'Element of metrics dict is neither Metric nor str.  '
                    f'Instead found {m} of type {type(m)}.'
                )
        if ground_truth is None:
            ground_truth = self._find_data_loader().load_ground_truth()
        if ground_truth is None:
            ground_truth = results.infer_ground_truth()

        return self.ranker.rank(results=results,
                                metrics=metrics_for_ranker,
                                ground_truth=ground_truth)

    @abc.abstractmethod
    def lookup_templates(self) -> Dict[str, PipelineTemplate]:
        '''Look up the templates that match the problem definition.'''
