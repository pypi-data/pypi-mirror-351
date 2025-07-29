'''This file handles integration for all the steps in distributed algorithms.'''
import json
import logging
from queue import Queue
import threading
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Type

from flask import Flask, request

from ..algorithms.impl.distributed_algorithm_instance import DistributedAlgorithmInstance
from ..config_components.distributed_config import DistributedConfig
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import ExecutablePipeline
from ..metrics.impl.metric import Metric
from ..neighbor_manager.node_id import NodeID
from ..searcher.params import Override, Overrides, ParamRange, ParamRanges, Selector
from ..searcher.searcher import Searcher, SearcherImpl
from ..splitters.impl.splitter import Splitter
from ..templates.impl.pipeline_template import PipelineTemplate
from ..wrangler.dataset import Dataset, DatasetKeys
from ..wrangler.exception_thread import ExceptionThread

from .constants import Matcher, RangeMethod
from .wrangler_base import WranglerBase
from .wrangler_result import WranglerResult
from .logger import Logger, Level

log = Logger(__file__, level=logging.DEBUG, to_stdout=True).logger()

# pylint: disable=too-many-statements


class DistributedWrangler(WranglerBase):
    '''The wrangler is the central control object for distributed algorithms.'''
    _results: Queue[WranglerResult]
    _stop: bool = False
    _splitter: Splitter
    _dataloader_fit_thread: Optional[ExceptionThread] = None
    _async_fit_thread: Optional[ExceptionThread] = None
    _async_fit_lock: threading.Lock
    _async_fit_next_data: Optional[Dataset] = None

    def __init__(self, *args,
                 searcher: Optional[Type[Searcher]] = None,
                 my_id: Optional[int] = None,
                 **kwargs):
        log.info("Distributed wrangler starting.")
        self._results = Queue()
        self._async_fit_lock = threading.Lock()
        super().__init__(*args, **kwargs)

        # Inject the DistributedConfig as a hyperparam called 'distributed'
        #   for all distributed algorithms.
        distributed_overrides = Overrides()
        config = self._pd.get_conf('distributed')
        assert isinstance(config, DistributedConfig)
        if my_id is not None:
            config.my_id = NodeID(my_id)

        distributed_overrides.append(
            Override(
                selector=Selector({
                    Matcher.TAGS: {'distributed': 'true'}
                }),
                params=ParamRanges(distributed=ParamRange(
                    method=RangeMethod.FIXED,
                    prange=config
                )),
                no_show=True
            )
        )

        self._searcher = (searcher or SearcherImpl)(
            hyperparams=self._pd.hyperparams,
            inject=distributed_overrides)

        self._bound_pipelines = self._build_pipelines()
        executable_pipelines: Dict[Designator, ExecutablePipeline] = {
            pipeline.designator: self._instantiator_factory.instantiate(
                kind=self._executor.kind, pipeline=pipeline
            )
            for pipeline in self._bound_pipelines.values()
        }
        self._all_executable_pipelines = executable_pipelines
        self._current_executable_pipelines = executable_pipelines
        # We must init the data loader before we start the fitter thread.
        # The MemoryDataLoader can not search the stack for variables from a thread.
        self._find_data_loader()

    @property
    def all_distributed_instances(self) -> Iterable[DistributedAlgorithmInstance]:
        '''Fetch all the DistributedAlgorithmInstances.'''
        for pipeline in (self._current_executable_pipelines or {}).values():
            for instance in pipeline.all_instances:
                if isinstance(instance, DistributedAlgorithmInstance):
                    yield instance

    def laplacians(self) -> Dict[str, List[List[int]]]:
        '''Calculate the laplacians for all distributed instances.'''
        retval = {}
        print("DEBUG: calculating laplacians")
        for instance in self.all_distributed_instances:
            print("DEBUG: calculating laplacian for instance", instance)
            print("DEBUG: calculating laplacian for instance.designator", instance.algorithm.name)
            retval[str(instance.algorithm.name)] = instance.neighbor_manager.laplacian()
        return retval

    def wait_til_all_fit(self) -> None:
        '''Wait until all distributed instances have fit.'''
        while not self.all_trained:
            pass

    def _dataloader_fit_loop(self, stop: Callable[[], bool]):
        '''This function is the data thread to process data.'''
        distributed = self._pd.get_conf('distributed')
        assert isinstance(distributed, DistributedConfig)
        while not stop():
            next_data = self._find_data_loader().poll(timeout=distributed.polling_interval)
            if next_data is not None:
                self.fit(next_data)  # sets self._current_trained_pipelines

    def _async_fit_loop(self, stop: Callable[[], bool]):
        '''This function is handles fit calls from the REST API asynchronously.'''
        distributed = self._pd.get_conf('distributed')
        assert isinstance(distributed, DistributedConfig)
        log.debug('async fit thread starting')
        while not stop():
            with self._async_fit_lock:
                next_data = self._async_fit_next_data
                self._async_fit_next_data = None
                log.log(Level.VERBOSE, "Checking async data")
            if next_data is None:
                time.sleep(distributed.polling_interval)
            else:
                log.debug('fitting')
                self.fit(next_data)  # sets self._current_trained_pipelines

    def lookup_templates(self) -> Dict[str, PipelineTemplate]:
        '''Look up the templates that match the problem definition.

        An example of how to specify the 'just', 'memory', and 'templated' pipeline loaders in
        the problem def:

        .. code-block:: Python

            {
                'distributed': {
                    'pipelines': {
                        'just': ['autonLogisticRegression', 'some other algorithm']
                        'memory': ['my_memory_pipeline']
                        'templated': [
                            {
                                'template': 'binary_tabular_classification',
                                'alg': 'AutonLogisticRegression'
                            },
                            {
                                'data_type': 'tabular',
                                'task': 'binary_classification',
                                'alg': 'some_other_alg'
                            }
                        ]
                    }
                }
            }
        '''
        distributed = self._pd.get_conf('distributed')
        assert isinstance(distributed, DistributedConfig)

        retval: Dict[str, PipelineTemplate] = {}

        for loader_name, arguments in distributed.pipelines.items():
            pipeline_loader = self._pipeline_loader_catalog.lookup_by_name(loader_name)
            for argument in arguments:
                if isinstance(argument, str):
                    argument = [argument]
                args = []
                kwargs = {}
                if isinstance(argument, list):
                    args = argument
                if isinstance(argument, dict):
                    kwargs = argument
                loaded_pipeline = pipeline_loader.load(*args, **kwargs)
                retval[loaded_pipeline.designator] = loaded_pipeline

        return retval

    def results(self) -> Queue[WranglerResult]:
        '''Return the results queue.'''
        return self._results

    def start(self) -> None:
        '''Start the wrangler threads.'''

        log.debug('DistributedWrangler starting wrangler threads: %x', id(self))
        self._stop = False
        assert self._all_executable_pipelines is not None
        for executable_pipeline in self._all_executable_pipelines.values():
            log.debug('DistributedWrangler starting pipeline: %s(%x)',
                      executable_pipeline, id(executable_pipeline))
            executable_pipeline.start()

        if self._dataloader_fit_thread is None:
            self._dataloader_fit_thread = ExceptionThread(target=self._dataloader_fit_loop, kwargs={
                'stop': lambda: self._stop
            })
        self._dataloader_fit_thread.start()

        if self._async_fit_thread is None:
            self._async_fit_thread = ExceptionThread(target=self._async_fit_loop, kwargs={
                'stop': lambda: self._stop
            })
        self._async_fit_thread.start()

    def stop(self) -> None:
        '''Stop the wrangler threads.'''
        log.debug('DistributedWrangler stopping wrangler threads: %x', id(self))
        self._stop = True
        if self._dataloader_fit_thread is not None:
            self._dataloader_fit_thread.join()
            self._dataloader_fit_thread = None
        if self._async_fit_thread is not None:
            self._async_fit_thread.join()
            self._async_fit_thread = None
        assert self._all_executable_pipelines is not None
        for executable_pipeline in self._all_executable_pipelines.values():
            log.debug('DistributedWrangler stopping pipeline: %s(%x)',
                      executable_pipeline, id(executable_pipeline))
            executable_pipeline.stop()

    def build_dataset_from_json(self, json_data: Dict) -> Dataset:
        '''Build a dataset from JSON data.'''
        return self._find_data_loader().build_dataset_from_json(json_data)

    def server(self, host='127.0.0.1', port=8080) -> Callable[[], None]:
        '''Start the REST node server.'''
        app = Flask(__name__)

        @app.get('/wrangler/v1.0/status')
        def status(**kwargs):
            return dict(kwargs, status='OK' if self.all_trained else 'UNTRAINED')

        @app.route('/wrangler/v1.0/fit', methods=['GET', 'POST'])
        def fit():
            if request.method == 'GET':
                return status()
            if request.method == 'POST':
                try:
                    log.info('Calling fit REST API.')
                    dataset = self.build_dataset_from_json(request.json)
                    log.debug('Input Data: %s', dataset)
                    with self._async_fit_lock:
                        self._async_fit_next_data = dataset
                except BaseException as e:  # pylint: disable=broad-except
                    return Flask.make_response({'error': str(e)}, 500)
                return status()
            raise ValueError(f'Invalid request method {request.method}')

        @app.route('/wrangler/v1.0/predict', methods=['GET', 'POST'])
        def predict():
            if request.method == 'GET':
                return status()
            if request.method == 'POST':
                try:
                    log.info('Calling predict REST API.')
                    dataset = self.build_dataset_from_json(request.json)
                    log.debug('Input Data: %s', dataset)
                    result = self.predict(new_data=dataset)
                    log.debug('Predictions: %s', result)
                    retval = {}
                    for typed_des, res in result.items():
                        des = str(typed_des)
                        retval[des] = {}

                        pred = res.prediction
                        assert pred is not None

                        retval[des] = pred.to_prejson()

                    log.debug('Sending message with predictions: %s', retval)
                    log.debug("json.dumps(retval)=%s", json.dumps(retval))

                    return retval
                except BaseException as e:  # pylint: disable=broad-except
                    return {'error': str(e)}
            raise ValueError(f'Invalid request method {request.method}')

        @app.route('/wrangler/v1.0/predict_and_score', methods=['GET', 'POST'])
        def predict_and_score() -> Dict[str, Any]:
            if request.method == 'GET':
                return status()
            if request.method == 'POST':
                try:
                    log.info('Calling predict_and_score REST API.')
                    input_json = request.json
                    assert input_json is not None

                    dataset = self.build_dataset_from_json(input_json)
                    log.debug('Input Data: %s', dataset)

                    ground_truth: Optional[Dataset] = None
                    if DatasetKeys.GROUND_TRUTH_TABLE.value in dataset:
                        ground_truth = dataset.output()
                        ground_truth.ground_truth_table = dataset.pop(
                            DatasetKeys.GROUND_TRUTH_TABLE.value)

                    result = self.predict(new_data=dataset)
                    log.debug('Predictions: %s', result)

                    metrics: Dict[str, Metric] = {}
                    metric_names = input_json.get('metrics', [])
                    for m in metric_names:
                        metric: Metric = self._metric_catalog.lookup_by_name(m)
                        metrics[metric.name] = metric

                    # Evaluate a metric for each pipeline
                    retval: Dict[str, Dict[str, Any]] = {}
                    for typed_des, res in result.items():
                        pred = res.prediction

                        des = str(typed_des)
                        assert pred is not None, (
                            f'BUG: {res} prediction is None.'
                        )
                        retval[des] = pred.to_prejson()

                        if metrics:
                            retval[des]['metrics'] = {}
                            for metric_name, metric in metrics.items():
                                score = metric.calculate(pred=pred,
                                                         ground_truth=ground_truth)
                                retval[des]['metrics'][metric_name] = score
                    log.debug('Return json: %s', retval)
                    return retval
                except BaseException as e:  # pylint: disable=broad-except
                    return {'error': str(e)}
            raise ValueError(f'Invalid request method {request.method}')

        @app.route('/wrangler/v1.0/wait_til_all_fit', methods=['GET'])
        def wait_til_all_fit() -> Dict[str, Any]:
            if request.method == 'GET':
                log.info('Calling wait_til_all_fit REST API.')
                self.wait_til_all_fit()
            return status()

        @app.route('/wrangler/v1.0/adjacency_graph_laplacians', methods=['GET'])
        def laplacians() -> Dict[str, Any]:
            if request.method == 'GET':
                retval = self.laplacians()
                return status(laplacians=retval)
            return status()

        def retval():
            self.start()
            log.info('DistributedWrangler starting server on %s:%s', host, port)
            app.run(host=host, port=port)

        return retval
