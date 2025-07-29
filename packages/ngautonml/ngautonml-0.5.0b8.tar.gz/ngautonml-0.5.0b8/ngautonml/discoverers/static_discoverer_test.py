'''Tests for static_discoverer.py'''

from ..communicators.stub_communicator import CommunicatorStub
from ..config_components.distributed_config import DistributedConfig
from ..neighbor_manager.node_id import NodeID

from .static_discoverer import StaticDiscoverer


def test_lapacian():
    '''Test the lapacian function'''
    config = DistributedConfig(clause={
        'discoverer': {
            'name': 'static',
            'static': {
                'adjacency': {
                    '6': [4],
                    '5': [1, 2, 4],
                    '4': [3, 5, 6],
                    '3': [2, 4],
                    '2': [1, 3, 5],
                    '1': [2, 5],
                },
            },
        },
        'communicator': {'name': 'stub'},
        'my_id': 1
    })

    # See https://en.wikipedia.org/wiki/Laplacian_matrix https://tinyurl.com/mr2vu3hd
    want = [
        [ 2, -1,  0,  0, -1,  0],   # noqa: E241, E201
        [-1,  3, -1,  0, -1,  0],   # noqa: E241, E201
        [ 0, -1,  2, -1,  0,  0],   # noqa: E241, E201
        [ 0,  0, -1,  3, -1, -1],   # noqa: E241, E201
        [-1, -1,  0, -1,  3,  0],   # noqa: E241, E201
        [ 0,  0,  0, -1,  0,  1]    # noqa: E241, E201
    ]

    communicator = CommunicatorStub(my_id=NodeID(1))
    discoverer = StaticDiscoverer(config=config, communicator=communicator)

    got = discoverer.laplacian()
    assert want == got
