'''Pipeline loader that loads a single algorithm.'''

from ..generator.bound_pipeline import BoundPipeline
from .impl.pipeline_loader import (
    MissingArgumentsError, PipelineLoader, UnknownArgumentsError)
from .impl.pipeline_loader_catalog import PipelineLoaderCatalog


class Just(PipelineLoader):
    '''Load a pipeline with Just one algorithm.'''
    name = 'just'
    tags = {}

    def _load(self, *args, alg: str = '', **kwargs) -> BoundPipeline:
        '''Load the pipeline.'''

        if alg == '':
            if len(args) > 0:
                alg = args[0]
                args = args[1:]
            else:
                raise MissingArgumentsError(
                    'Missing argument "alg" (algorithm name) '
                    f'to {self.__class__.__name__}'
                )

        if len(args) > 0 or len(kwargs) > 0:
            raise UnknownArgumentsError(
                f'Found unknown arguments to {self.__class__.__name__}:'
                f'*args={args}, **kwargs={kwargs}'
            )

        assert self._algorithm_catalog is not None, f'algorithm_catalog is required for {self.name}'

        algorithm = self._algorithm_catalog.lookup_by_name(alg)

        pipeline = BoundPipeline(name=algorithm.name, tags={})
        pipeline.step(model=algorithm)

        return pipeline


def register(catalog: PipelineLoaderCatalog, **kwargs):
    '''Register all the metrics in this file.'''
    catalog.register(Just(**kwargs))
