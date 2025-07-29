'''Catalog for metrics that can be used to evaulate pipelines'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Dict, List, Optional, Union

from ...catalog.memory_catalog import MemoryCatalog
from ...metrics.impl.metric import Metric
from ...problem_def.problem_def import ProblemDefinition


class MetricCatalog(MemoryCatalog[Metric], metaclass=abc.ABCMeta):
    '''Base class for metric catalogs'''

    def register(self, obj: Metric, name: Optional[str] = None,
                 tags: Optional[Dict[str, Union[str, List[str]]]] = None) -> str:
        return super().register(obj, name, tags)

    def lookup_metrics(self, pd: ProblemDefinition) -> Dict[str, Metric]:
        '''Get metric objects from metric catalog based on problem definition.'''
        task = pd.task
        metric_confs = pd.metric_configs

        task_type = "None"
        if task.task_type is not None:
            task_type = task.task_type.name

        # TODO(piggy): Allow hyperparams for metrics.
        if len(metric_confs) == 0:
            metrics = self.lookup_by_tag_and(task=task_type, implements_calculate='true')
        else:
            metrics = {}
            for conf in metric_confs.values():
                metric = self.lookup_by_name(conf.catalog_name)
                metrics[metric.name] = metric

        return metrics


class MetricCatalogStub(MetricCatalog):
    '''stub'''
