'''Tests for SimpleParallelStep'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ...algorithms.connect import ConnectorModel
from ...generator.bound_pipeline import BoundPipeline
from ...wrangler.dataset import Dataset

from .simple_parallel_executable_step import SimpleParallelExecutableStep
from .simple_executable_pipeline import SimpleExecutablePipeline

# pylint: disable=missing-function-docstring,duplicate-code

DATASET = Dataset(
    a='a_value',
    b='b_value'
)


def test_sunny_day() -> None:
    pipeline = BoundPipeline(name='Fake_bound_pipeline')
    pipe1 = pipeline.new(name='at')
    pipe1.step(ConnectorModel(c='a')).set_name('connector_pipe1')
    pipe2 = pipeline.new(name='dt')
    pipe2.step(ConnectorModel(d='b')).set_name('connector_pipe2')
    step = pipeline.parallel(left=pipe1, right=pipe2).set_name('parallel_step')

    dut = SimpleParallelExecutableStep(step, SimpleExecutablePipeline)

    dut.fit(dataset=DATASET)
    got = dut.predict(dataset=DATASET)
    assert got == Dataset(
        left=Dataset(c='a_value'),
        right=Dataset(d='b_value')
    )
