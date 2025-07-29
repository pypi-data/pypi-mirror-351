'''A step representing a query to the model catalog

The generator will build a bound pipeline for every model that fits the query.
This type of step cannot exist in bound pipelines.
'''
import logging
from typing import Dict, Iterable, List, Union

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...algorithms.impl.algorithm import AlgorithmCatalog, Algorithm

from ...generator.designator import Designator
from .pipeline_step import PipelineStep


class QueryStep(PipelineStep):
    '''A step representing a query to the model catalog.'''

    _algorithm_catalog: AlgorithmCatalog
    _query_tags: Dict[str, Union[str, Iterable[str]]]

    def __init__(self,
                 algorithm_catalog: AlgorithmCatalog,
                 **query_tags: Union[str, Iterable[str]]):
        super().__init__()
        self._query_tags = query_tags
        self._algorithm_catalog = algorithm_catalog

    def generate(self,
                 future_steps: List['PipelineStep']
                 ) -> Dict[Designator, List['PipelineStep']]:
        '''Generate pipeline sketches (lists of bound steps) for this step and all subsequent steps.

        This and subsequent query steps may expand into multiple 'pipeline sketches'.

        Handles the QueryStep case.
        '''
        models: Dict[str, Algorithm] = self._algorithm_catalog.lookup_by_tag_and(**self._query_tags)
        # Only use distributed algrithms if they are explicitly requested.
        if 'distributed' not in self._query_tags or 'true' not in self._query_tags['distributed']:
            models = {
                k: m for k, m in models.items()
                if 'distributed' not in m.tags or 'false' in m.tags['distributed']
            }
        logging.info('query found %d models with tags: %r', len(models), self._query_tags)
        new_steps = {
            Designator(model_name): [
                PipelineStep(model=model).set_name(model_name).mark_queried()
            ]
            for model_name, model in models.items()
        }
        if len(future_steps) == 0:
            return new_steps

        step0 = future_steps[0]
        sketches = step0.generate(future_steps[1:])
        retval: Dict[Designator, List['PipelineStep']] = {}
        for _, model_step in new_steps.items():
            for future_key, future_rest in sketches.items():
                retval[Designator(
                    f'{model_step[0].pipeline_designator_component}:{future_key}')] = (
                    model_step + future_rest[:])
        return retval
