'''Tests for neighbor_manager.py'''

import os
from filelock import FileLock
import mlflow  # type: ignore

# pylint: disable=missing-function-docstring,duplicate-code

from .event import Recv
from .neighbor_manager import NeighborManagerStub
from .node_id import NodeID

LOCK_PATH = f'/var/tmp/neighbor-manager-mlflow-{os.environ.get("USER")}.lock'


def test_send_all_logging() -> None:
    with FileLock(LOCK_PATH, timeout=90):
        dut = NeighborManagerStub()
        with mlflow.start_run(nested=True) as r:
            dut.send_all(b'lorem ipsum')
            run = r
    assert run is not None

    client = mlflow.tracking.MlflowClient()

    metrics = client.get_metric_history(run_id=run.info.run_id, key='PayloadSize')
    assert len(metrics) == 1
    assert metrics[0].value == len(b'lorem ipsum')


def test_send_logging() -> None:
    with FileLock(LOCK_PATH, timeout=90):
        dut = NeighborManagerStub()
        with mlflow.start_run(nested=True) as r:
            dut.send([NodeID(1)], b'lorem ipsum')
            run = r
    assert run is not None

    client = mlflow.tracking.MlflowClient()

    metrics = client.get_metric_history(run_id=run.info.run_id, key='PayloadSize')
    assert len(metrics) == 1
    assert metrics[0].value == len(b'lorem ipsum')


def test_poll_for_events():
    with FileLock(LOCK_PATH, timeout=90):
        dut = NeighborManagerStub()
        with mlflow.start_run(nested=True) as r:
            events = dut.poll_for_events()
            run = r
        assert events == [Recv(NodeID(1), b'hello, world!')]

    assert run is not None

    client = mlflow.tracking.MlflowClient()
    recv_len = client.get_metric_history(run_id=run.info.run_id, key='RecvLen')
    assert recv_len[0].value == float(len('hello, world!'))
    recv_neighbor = client.get_metric_history(run_id=run.info.run_id, key='RecvNeighbor')
    assert recv_neighbor[0].value == float(1)
