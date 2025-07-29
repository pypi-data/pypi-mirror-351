'''Tests for pipeline_loader.py'''

# pylint: disable=missing-function-docstring, missing-class-docstring,duplicate-code

from ...generator.bound_pipeline import BoundPipeline

from .pipeline_loader import PipelineLoader


class FakePipelineLoader(PipelineLoader):
    def _load(self, *unused_args, **unused_kwargs) -> BoundPipeline:
        return BoundPipeline(name='fake_pipeline_loader')


def test_load() -> None:
    dut = FakePipelineLoader()
    got = dut.load(name='fake_pipeline_loader')
    assert isinstance(got, BoundPipeline)
