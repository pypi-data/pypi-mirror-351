'''Tests for distributed_wrangler.py.'''

from copy import deepcopy
from multiprocessing import Process
import os
import pickle
import queue
import select
import socket
import time
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import pytest
import requests
from sklearn import datasets  # type: ignore[import]

from ..algorithms.impl.synchronous import advance
from ..conftest import Clearer, Waiter
from ..generator.designator import Designator
from ..instantiator.executable_pipeline import PipelineResults
from ..metrics.impl.metric_auto import MetricCatalogAuto
from ..problem_def.problem_def import ProblemDefinition
from ..tables.impl.table_auto import TableCatalogAuto
from ..wrangler.base_port import BasePort
from ..wrangler.constants import JSONKeys
from ..wrangler.dataset import df_to_dict_json_friendly, DatasetKeys
from ..wrangler.logger import Logger

from .distributed_wrangler import DistributedWrangler

# pylint: disable=missing-function-docstring, missing-class-docstring, duplicate-code, unused-variable
# pylint: disable=too-many-locals,no-member, too-many-lines
# pylint: disable=duplicate-code, redefined-outer-name

log = Logger(__file__).logger()
_ = TableCatalogAuto()  # pylint: disable=pointless-statement
base_port = BasePort()


def load_classification_dataframes(
        reduced_train: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Load the breast cancer dataset
    bc_x_full, bc_y_series = datasets.load_breast_cancer(return_X_y=True, as_frame=True)
    assert isinstance(bc_x_full, pd.DataFrame)
    assert isinstance(bc_y_series, pd.Series)
    bc_y = pd.DataFrame({'target': bc_y_series})

    # restrict number of attributes for wider variability of results
    bc_x = bc_x_full.iloc[:, :3]

    test_size = 50
    # Split the data into training/testing sets
    bc_x_train = bc_x[:-test_size]
    bc_x_test = bc_x[-test_size:].reset_index(drop=True)

    # Split the targets into training/testing sets
    bc_y_train = bc_y[:-test_size]
    bc_y_test = bc_y[-test_size:].reset_index(drop=True)

    train_df = pd.concat([bc_x_train, bc_y_train], axis=1)
    test_df = bc_x_test
    gt_df = bc_y_test

    if reduced_train:
        train_df = train_df.iloc[516:519].copy()
        train_df['target'] = [1, 0, 0]

    return (train_df, test_df, gt_df)


LOOPBACK = '127.0.0.1'
SUNNY_DAY_RECEIVER_PORT = base_port.next()
SUNNY_DAY_SENDER_PORT = base_port.next()


def test_sunny_day(assert_no_exceptions: Clearer,
                   wait_til_all_fit: Waiter) -> None:
    '''Train on bad data, recieve a message from a neighbor with good training,

    and check that we've improved.
    '''
    train_df, test_df, gt_df = load_classification_dataframes(reduced_train=True)  # noqa: F841

    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'memory',
            'params': {
                'train_data': 'train_df',
                'test_data': 'test_df',
            },
            'column_roles': {
                'target': {
                    'name': 'target',
                    'pos_label': 0
                },
            },
        },
        'distributed': {
            'polling_interval': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': [],
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (LOOPBACK, SUNNY_DAY_RECEIVER_PORT)),
                    ],
                },
            },
            'my_id': 1,
            'split': {
                'num_nodes': 2,
                'seed': 1234,
            },
            'pipelines': {
                'just': ['Auton_Logistic_Regression'],
            }
        },
        'problem_type': {
            'task': 'binary_classification',
        }
    })

    dut = DistributedWrangler(problem_definition=pdef)
    ground_truth = dut.ez_dataset(data=gt_df, key='ground_truth_table')
    test_dataset = dut.ez_dataset(data=test_df)

    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind((LOOPBACK, SUNNY_DAY_SENDER_PORT))

    # These parameters were hand-extracted from a successful fit.
    message = pickle.dumps((
        1,
        np.array([5.72550884, 0.09525482, -0.89685941, 0.0]),
        None
    ))

    metric_catalog = MetricCatalogAuto()
    metric = metric_catalog.lookup_by_name('accuracy_score')
    try:
        dut.start()

        assert wait_til_all_fit(dut.all_distributed_instances, convergence_check=True), (
            'Failed to fit in time'
        )
        res1: Optional[PipelineResults] = dut.predict(test_dataset)
        assert res1 is not None
        assert len(res1) == 1

        # Confirm that the training is very bad.
        assert metric.calculate(pred=next(iter(res1.values())).prediction,
                                ground_truth=ground_truth
                                ) == pytest.approx(expected=0.06, abs=0.01)
        sock.sendto(message, (LOOPBACK, SUNNY_DAY_RECEIVER_PORT))
        # Wait until we have neighbor state.
        for d in dut.all_distributed_instances:
            while not list(d._neighbor_models_iter):  # pylint: disable=protected-access
                time.sleep(0.1)

        # Wait for the new state to get processed.
        assert wait_til_all_fit(
            dut.all_distributed_instances, min_time=1.0, convergence_check=True), (
            'Failed to fit in time for second time')

        res2 = dut.predict(test_dataset)
        assert res2 is not None
        assert len(res2) == 1

        # Confirm that the training is now better.
        assert metric.calculate(pred=next(iter(res2.values())).prediction,
                                ground_truth=ground_truth
                                ) >= 0.8
        assert_no_exceptions(dut.all_distributed_instances)
    finally:
        sock.close()
        dut.stop()


def test_lookup_templates() -> None:
    '''Test 3 ways of specifying pipeline loader args in the problem def.

    (single arg, multiple *args list, and **kwargs dict)
    '''
    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'ignore'
        },
        'problem_type': {
            'task': 'test_task'
        },
        'distributed': {
            'communicator': {
                'name': 'stub_communicator'
            },
            'split': {
                'my_id': 1,
            },
            'pipelines': {
                'just': [
                    'auton_Logistic_Regression',
                    ['connect'],
                    {'alg': 'identity'}
                ]
            }
        }
    })
    dut = DistributedWrangler(problem_definition=pdef)
    dut.stop()
    got = dut.bound_pipelines
    want = {
        Designator('auton_logistic_regression'),
        Designator('connect'),
        Designator('identity'),
    }
    assert {pipe.designator for pipe in got.values()} == want


SUNNY_DAY_SERVER_MY_PORT = base_port.next()
SUNNY_DAY_SERVER_NEIGHBOR_PORT = base_port.next()
SUNNY_DAY_SERVER_WEB_PORT = base_port.next()


def test_server_sunny_day() -> None:
    '''Test the REST web server with a fit and predict request.'''
    train_df, test_df, gt_df = load_classification_dataframes(reduced_train=False)  # noqa: F841

    empty_df = pd.DataFrame()  # noqa: F841

    poll_queue: queue.Queue[pd.DataFrame] = queue.Queue()  # noqa: F841

    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'ignore',
            'column_roles': {
                'target': {
                    'name': 'target',
                    'pos_label': 1,
                },
            },
        },
        'distributed': {
            'polling_interval': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': ['2'],
                        '2': ['1'],
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (LOOPBACK, SUNNY_DAY_SERVER_MY_PORT)),
                        ('2', (LOOPBACK, SUNNY_DAY_SERVER_NEIGHBOR_PORT)),
                    ],
                },
            },
            'my_id': 1,
            'split': {
                'num_nodes': 2,
                'seed': 1234,
            },
            'pipelines': {
                'just': ['Auton_Logistic_regression'],
            }
        },
        'problem_type': {
            'task': 'binary_classification',
        }
    })

    dut = DistributedWrangler(problem_definition=pdef)

    train_msg = {
        'target': {'target': train_df['target'].tolist()},
        'covariates': train_df.drop(columns=['target']).to_dict(orient='list'),
    }

    test_msg = {
        'dataframe': test_df.to_dict(orient='list'),
    }

    # These parameters were hand-extracted from a successful fit.
    want_fit_message = (1, [-0.5086850644825086, 2.3477418500057716,
                        -0.26560121189885955, 19.2694391248473])

    # Create a fake neighbor to receive dut's state
    neighbor = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    neighbor.bind((LOOPBACK, SUNNY_DAY_SERVER_NEIGHBOR_PORT))
    neighbor.setblocking(False)
    server = None
    exception = None
    try:
        # Start web server.
        server = Process(target=dut.server(host=LOOPBACK, port=SUNNY_DAY_SERVER_WEB_PORT))
        server.start()

        time.sleep(2.0)

        # post a REST request to fit and provide data
        r = requests.post(f'http://localhost:{SUNNY_DAY_SERVER_WEB_PORT}/wrangler/v1.0/fit',
                          json={
                              'data': train_msg,
                          },
                          timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        assert r.text == '{"status":"UNTRAINED"}\n'
        # The dut should fit on the new data and send its state the neighbor.

        # Collect the state update from dut.
        ready = select.select([neighbor], [], [], 60.0)
        if ready[0]:
            neighbor_response = neighbor.recv(1024)
        else:
            raise TimeoutError('Timeout waiting for neighbor to respond')

        # Check that this looks like a properly fit state.
        response = pickle.loads(neighbor_response)
        assert response[1] == pytest.approx(want_fit_message[1], abs=0.01)

        # Ask dut to predict on test data.
        r = requests.post(f'http://localhost:{SUNNY_DAY_SERVER_WEB_PORT}/wrangler/v1.0/predict',
                          json={
                              'data': test_msg,
                          },
                          timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        got = r.json()

        assert 'auton_logistic_regression' in got

        # Check that the predictions are good.
        prediction = dut.ez_dataset(
            got['auton_logistic_regression'][JSONKeys.PREDICTIONS.value],
            key=DatasetKeys.PREDICTIONS_TABLE.value)

        assert [str(k)
                for k in got['auton_logistic_regression'][JSONKeys.PREDICTIONS.value].keys()] == [
            'target']
        assert [str(k)
                for k in got['auton_logistic_regression'][JSONKeys.PROBABILITIES.value].keys()] == [
            '0', '1']

        metric_catalog = MetricCatalogAuto()
        metric = metric_catalog.lookup_by_name('accuracy_score')
        ground_truth = dut.ez_dataset(data=gt_df, key='ground_truth_table')

        assert metric.calculate(pred=prediction,
                                ground_truth=ground_truth) == pytest.approx(0.88, abs=0.01)

    except Exception as e:  # pylint: disable=broad-except
        exception = e
        log.error("exception %s in test_server_sunny_day", e)
    finally:
        if server is not None:
            server.terminate()
            server.join()
        neighbor.close()

    if exception is not None:
        raise exception


MY_ID_SERVER_MY_PORT = base_port.next()
MY_ID_SERVER_NEIGHBOR_PORT = base_port.next()
MY_ID_SERVER_WEB_PORT = base_port.next()


def test_server_set_my_id() -> None:
    '''Test starting the web server with a specified my_id.'''
    train_df, test_df, gt_df = load_classification_dataframes(reduced_train=True)  # noqa: F841

    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'ignore',
            'column_roles': {
                'target': {
                    'name': 'target',
                    'pos_label': 1,
                },
            },
        },
        'distributed': {
            'polling_interval': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': ['2'],
                        '2': ['1'],
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (LOOPBACK, MY_ID_SERVER_MY_PORT)),
                        ('2', (LOOPBACK, MY_ID_SERVER_NEIGHBOR_PORT)),
                    ],
                },
            },
            'my_id': 0,
            'split': {
                'num_nodes': 2,
                'seed': 1234,
            },
            'pipelines': {
                'just': ['Auton_Logistic_regression'],
            }
        },
        'problem_type': {
            'task': 'binary_classification',
        }
    })

    dut = DistributedWrangler(problem_definition=pdef, my_id=1)

    train_msg = {
        JSONKeys.TARGET.value: {'target': train_df['target'].tolist()},
        JSONKeys.COVARIATES.value: train_df.drop(columns=['target']).to_dict(orient='list'),
    }

    neighbor = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    neighbor.bind((LOOPBACK, MY_ID_SERVER_NEIGHBOR_PORT))
    neighbor.setblocking(False)
    server = None
    exception = None
    try:
        server = Process(target=dut.server(host=LOOPBACK, port=MY_ID_SERVER_WEB_PORT))
        server.start()

        time.sleep(2.0)

        r = requests.post(f'http://localhost:{MY_ID_SERVER_WEB_PORT}/wrangler/v1.0/fit',
                          json={
                              'data': train_msg,
                          },
                          timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        assert r.text == '{"status":"UNTRAINED"}\n'

        ready = select.select([neighbor], [], [], 60.0)
        if ready[0]:
            _, response_addr = neighbor.recvfrom(1024)
        else:
            raise TimeoutError('Timeout waiting for neighbor to respond')

        assert response_addr == (LOOPBACK, MY_ID_SERVER_MY_PORT)

    except Exception as e:  # pylint: disable=broad-except
        exception = e
        log.error("exception %s in test_server_sunny_day", e)
    finally:
        if server is not None:
            server.terminate()
            server.join()

    if exception is not None:
        raise exception


SERVER_METRICS_MY_PORT = base_port.next()
SERVER_METRICS_WEB_PORT = base_port.next()


def test_server_predict_and_score() -> None:
    '''Test the REST web server with a request to evaluate metrics.'''
    train_df, test_df, gt_df = load_classification_dataframes(reduced_train=False)  # noqa: F841

    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'ignore',
            'column_roles': {
                'target': {
                    'name': 'target',
                    'pos_label': 1,
                },
            },
        },
        'distributed': {
            'polling_interval': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': [],
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (LOOPBACK, SERVER_METRICS_MY_PORT)),
                    ],
                },
            },
            'my_id': 1,
            'split': {
                'num_nodes': 2,
                'seed': 1234,
            },
            'pipelines': {
                'just': ['Auton_Logistic_regression'],
            }
        },
        'problem_type': {
            'task': 'binary_classification',
        }
    })

    dut = DistributedWrangler(problem_definition=pdef)

    train_msg = {
        JSONKeys.TARGET.value: {'target': train_df['target'].tolist()},
        JSONKeys.COVARIATES.value: train_df.drop(columns=['target']).to_dict(orient='list'),
    }

    test_msg = {
        JSONKeys.DATAFRAME.value: test_df.to_dict(orient='list'),
        JSONKeys.GROUND_TRUTH.value: gt_df.to_dict(orient='list')
    }

    server = None
    exception = None
    try:
        # Start web server.
        server = Process(target=dut.server(host=LOOPBACK, port=SERVER_METRICS_WEB_PORT))
        server.start()

        time.sleep(2.0)

        # post a REST request to fit and provide data
        r = requests.post(f'http://localhost:{SERVER_METRICS_WEB_PORT}/wrangler/v1.0/fit',
                          json={
                              'data': train_msg,

                          },
                          timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        assert r.text == '{"status":"UNTRAINED"}\n'
        # The dut should fit on the new data and send its state to the neighbor.
        r = requests.get(
            f'http://localhost:{SERVER_METRICS_WEB_PORT}/wrangler/v1.0/wait_til_all_fit',
            timeout=30)
        assert r.ok, (
            f'Response code to wait_til_all_fit was {r}'
        )

        # Ask dut to predict on test data.
        r = requests.post(
            f'http://localhost:{SERVER_METRICS_WEB_PORT}/wrangler/v1.0/predict_and_score',
            json={
                'data': test_msg,
                'metrics': ['accuracy_score'],
            },
            timeout=None)
        assert r.ok, (
            f'Response code to predict_and_score was {r}'
        )

        got = r.json()

        # want = {
        #     'auton_logistic_regression': {
        #         'predictions': ...,
        #         'metrics': {
        #             'accuracy_score': 0.88
        #         }
        #     },
        # }

        assert list(got.keys()) == ['auton_logistic_regression'], (
            f'Got keys {list(got.keys())} and values {got.values()}'
        )
        assert got['auton_logistic_regression']['metrics']['accuracy_score'] == pytest.approx(
            0.88, rel=0.0001
        )
        assert JSONKeys.PREDICTIONS.value in got['auton_logistic_regression']
        assert JSONKeys.PREDICTIONS.value in got['auton_logistic_regression']
        assert [str(k)
                for k in got['auton_logistic_regression'][JSONKeys.PREDICTIONS.value].keys()] == [
                    'target']
        assert [str(k)
                for k in got['auton_logistic_regression'][JSONKeys.PROBABILITIES.value].keys()] == [
                    '0', '1']

    except Exception as e:  # pylint: disable=broad-except
        exception = e
        log.error("exception %s in test_server_predict_and_score", e)
    finally:
        if server is not None:
            server.terminate()
            server.join()

    if exception is not None:
        raise exception


@pytest.mark.skipif(os.getenv("RUN_LONG_NGAUTONML_TESTS") == "",
                    reason="Takes 47 seconds to run, so skip on CI by default.")
def test_2_wranglers(assert_no_exceptions: Clearer) -> None:
    '''2 distributed wranglers are given the same data, we want them to converge with no errors.'''
    breast_cancer = datasets.load_breast_cancer(as_frame=True)
    df = breast_cancer.frame

    train_df = df.iloc[0:-100,]  # noqa: F841 pylint: disable=unused-variable
    test_df = df.tail(50)
    del test_df['target']
    loopback = '127.0.0.1'

    pdef_dict_1 = {
        "dataset": {
            "config": "memory",
            "params": {
                "train_data": "train_df",
                "test_data": "test_df"
            },
            "column_roles": {
                "target": {
                    "name": "target",
                    "pos_label": 1
                }
            }
        },
        "problem_type": {
            "data_type": "tabular",
            "task": "binary_classification"
        },
        "metrics": {
            "accuracy_score": {},
            "roc_auc_score": {}
        },
        'distributed': {
            'polling_interval': 0.5,
            'fit_eps': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': [2],
                        '2': [1]
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (loopback, 65001)),
                        ('2', (loopback, 65002)),
                    ],
                },
            },
            'my_id': 1,
            'split': {
                'num_nodes': 2
            },
            'pipelines': {
                'just': ['Auton_Logistic_Regression'],
            }
        },
        'hyperparams': [
            {
                '_comments': [
                    'Apply standard parameters to instances of Auton_Logistic_Regression.',
                    'Note that algorithm is the name of the algorithm associated with',
                    'the step where name is name of the step.'
                ],
                'select': {
                    'algorithm': 'Auton_Logistic_Regression'
                },
                'params': {
                    'L2': {
                        'fixed': 5.0
                    },
                    'Lambda': {
                        'fixed': 10000000
                    },
                    'omega': {
                        'fixed': 0.6
                    },
                    'synchronous': {
                        'fixed': True
                    },
                },
            }
        ]
    }

    # The second node's problem def is identical aside from my_id
    pdef_dict_2 = deepcopy(pdef_dict_1)
    dist_clause = pdef_dict_2['distributed']
    assert isinstance(dist_clause, dict)
    dist_clause['my_id'] = 2

    pdef_1 = ProblemDefinition(pdef_dict_1)
    pdef_2 = ProblemDefinition(pdef_dict_2)

    dut1 = DistributedWrangler(problem_definition=pdef_1)
    dut2 = DistributedWrangler(problem_definition=pdef_2)

    try:

        # fit on local train data from the problem def and start listening for messages
        dut1.start()
        dut2.start()

        # assert that we converge
        all_instances = list(dut1.all_distributed_instances) + list(dut2.all_distributed_instances)
        for _ in range(5):
            advance(all_instances)

        assert_no_exceptions(all_instances)

    finally:
        dut1.stop()
        dut2.stop()


SERVER_PROBA_MY_PORT = base_port.next()
SERVER_PROBA_WEB_PORT = base_port.next()


def test_server_proba() -> None:
    '''Test the REST web server returning probabilities for classification.'''
    train_df, test_df, gt_df = load_classification_dataframes(reduced_train=False)  # noqa: F841

    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'ignore',
            'column_roles': {
                'target': {
                    'name': 'target',
                    'pos_label': 1,
                },
            },
        },
        'distributed': {
            'polling_interval': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': [],
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (LOOPBACK, SERVER_PROBA_MY_PORT)),
                    ],
                },
            },
            'my_id': 1,
            'pipelines': {
                'just': ['Auton_Decision_Tree_Model'],
            }
        },
        'problem_type': {
            'task': 'binary_classification',
        }
    })

    dut = DistributedWrangler(problem_definition=pdef)

    train_msg = {
        JSONKeys.TARGET.value: {'target': train_df['target'].tolist()},
        JSONKeys.COVARIATES.value: train_df.drop(columns=['target']).to_dict(orient='list'),
    }

    test_msg = {
        JSONKeys.DATAFRAME.value: test_df.to_dict(orient='list'),
        JSONKeys.GROUND_TRUTH.value: gt_df.to_dict(orient='list')
    }

    server = None
    exception = None
    try:
        # Start web server.
        server = Process(target=dut.server(host=LOOPBACK, port=SERVER_PROBA_WEB_PORT))
        server.start()

        time.sleep(2.0)

        # post a REST request to fit and provide data
        r = requests.post(f'http://localhost:{SERVER_PROBA_WEB_PORT}/wrangler/v1.0/fit',
                          json={
                              'data': train_msg,
                          },
                          timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        assert r.text == '{"status":"UNTRAINED"}\n'
        # The dut should fit on the new data and send its state the neighbor.

        r = requests.get(f'http://localhost:{SERVER_PROBA_WEB_PORT}/wrangler/v1.0/wait_til_all_fit',
                         timeout=20)
        assert r.ok, (
            f'Response code to wait_til_all_fit was {r}'
        )

        # Post a REST request to predict, as well as predict_and_score (we want to test both.)
        gots = []

        r = requests.post(
            f'http://localhost:{SERVER_PROBA_WEB_PORT}/wrangler/v1.0/predict',
            json={
                'data': test_msg,
            },
            timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        gots.append(r.json())

        r = requests.post(
            f'http://localhost:{SERVER_PROBA_WEB_PORT}/wrangler/v1.0/predict_and_score',
            json={
                'data': test_msg,
                'metrics': ['accuracy_score'],
            },
            timeout=None)
        assert r.ok, (
            f'Response code to predict_and_score was {r}'
        )

        gots.append(r.json())

        for i, got in enumerate(gots):
            assert list(got.keys()) == ['auton_decision_tree_model'], (
                f'Error in got[{i}]: {got}'
            )
            assert 'probabilities' in got['auton_decision_tree_model']
            df = pd.DataFrame(got['auton_decision_tree_model']['probabilities'])
            assert df.shape == (test_df.shape[0], 2)
            assert list(df.columns) == ['0', '1']
            # If these are class probabilities, every row should sum to 1
            #       (Accounting for float imprecision)
            assert all(s == pytest.approx(1.0) for s in (df['0'] + df['1']))

    except Exception as e:  # pylint: disable=broad-except
        exception = e
        log.error("exception %s in test_server_proba", e)
    finally:
        if server is not None:
            server.terminate()
            server.join()

    if exception is not None:
        raise exception


SERVER_MEAN_MY_PORT = base_port.next()
SERVER_MEAN_WEB_PORT = base_port.next()


def test_server_mean() -> None:
    '''Test that the REST server works with AutonMean'''
    train_df = pd.DataFrame(
        {
            'a': [None, None, 1],
            'b': [None, 2, 3],
            'c': [4, 5, 6],
        }
    )

    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'ignore',
            'column_roles': {
                'target': {
                    'name': 'a',
                },
            },
        },
        'distributed': {
            'polling_interval': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': [],
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (LOOPBACK, SERVER_MEAN_MY_PORT)),
                    ],
                },
            },
            'my_id': 1,
            'pipelines': {
                'just': ['Auton_Mean'],
            }
        },
        'problem_type': {
            'task': 'other',
        }
    })

    dut = DistributedWrangler(problem_definition=pdef)

    msg = {
        'data': {
            JSONKeys.DATAFRAME.value: df_to_dict_json_friendly(train_df)
        }
    }

    server = None
    exception = None
    try:
        # Start web server.
        server = Process(target=dut.server(host=LOOPBACK, port=SERVER_MEAN_WEB_PORT))
        server.start()

        time.sleep(2.0)

        # post a REST request to fit and provide data
        r = requests.post(f'http://localhost:{SERVER_MEAN_WEB_PORT}/wrangler/v1.0/fit',
                          json=msg,
                          timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        assert r.text == '{"status":"UNTRAINED"}\n'

        # The dut should fit on the new data and send its state to the neighbor.
        r = requests.get(f'http://localhost:{SERVER_MEAN_WEB_PORT}/wrangler/v1.0/wait_til_all_fit',
                         timeout=20)
        assert r.ok, (
            f'Response code to wait_til_all_fit was {r}'
        )

        # Post a REST request to predict to get the mean
        r = requests.post(
            f'http://localhost:{SERVER_MEAN_WEB_PORT}/wrangler/v1.0/predict',
            json=msg,
            timeout=None)
        assert r.ok, (
            f'Response code to predict was {r}'
        )
        got = r.json()
        assert list(got.keys()) == ['auton_mean'], (
            f'Error in got: {got}'
        )
        pred_df = pd.DataFrame(got['auton_mean'][JSONKeys.PREDICTIONS.value])

        pd.testing.assert_frame_equal(
            pred_df,
            pd.DataFrame({'a': [1.0], 'b': [2.5], 'c': [5.0]}))

    except Exception as e:  # pylint: disable=broad-except
        exception = e
        log.error("exception %s in test_server_mean", e)
    finally:
        if server is not None:
            server.terminate()
            server.join()

    if exception is not None:
        raise exception


SERVER_LAPLACIAN_MY_PORT = base_port.next()
SERVER_LAPLACIAN_WEB_PORT = base_port.next()


def test_server_laplacian() -> None:
    '''Test that the REST server laplacian works.'''
    pdef = ProblemDefinition(clause={
        'dataset': {
            'config': 'ignore',
            'column_roles': {
                'target': {
                    'name': 'a',
                },
            },
        },
        'distributed': {
            'polling_interval': 0.5,
            'discoverer': {
                'name': 'static',
                'static': {
                    'adjacency': {
                        '1': [2, 3, 4, 5],
                        '2': [1],
                        '3': [1],
                        '4': [1],
                        '5': [1],
                    },
                },
            },
            'communicator': {
                'name': 'sockets',
                'sockets': {
                    'nodes_and_endpoints': [
                        ('1', (LOOPBACK, SERVER_LAPLACIAN_MY_PORT)),
                    ],
                },
            },
            'my_id': 1,
            'pipelines': {
                'just': ['auton_mean'],
            }
        },
        'problem_type': {
            'task': 'other',
        }
    })

    dut = DistributedWrangler(problem_definition=pdef)

    server = None
    exception = None
    try:
        # Start web server.
        server = Process(target=dut.server(host=LOOPBACK, port=SERVER_LAPLACIAN_WEB_PORT))
        server.start()

        time.sleep(2.0)

        # post a REST request to fit and provide data
        r = requests.get(f'http://localhost:{SERVER_LAPLACIAN_WEB_PORT}'
                         '/wrangler/v1.0/adjacency_graph_laplacians',
                         timeout=None)
        assert r.ok, (
            f'Response code to laplacian was {r}'
        )
        assert r.json() == {
            'status': 'UNTRAINED',
            'laplacians': {
                'auton_mean': [
                    [4, -1, -1, -1, -1],
                    [-1, 1, 0, 0, 0],
                    [-1, 0, 1, 0, 0],
                    [-1, 0, 0, 1, 0],
                    [-1, 0, 0, 0, 1]
                ],
            },
        }

    except Exception as e:  # pylint: disable=broad-except
        exception = e
        log.error("exception %s in test_server_laplacian", e)
    finally:
        if server is not None:
            server.terminate()
            server.join()

    if exception is not None:
        raise exception
