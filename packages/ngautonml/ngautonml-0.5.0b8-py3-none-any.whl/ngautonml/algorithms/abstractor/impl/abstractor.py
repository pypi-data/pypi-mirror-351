'''An Abstractor presents a view of the training space of neighbors.'''

from ...impl.algorithm import Algorithm

from .abstractor_instance import AbstractorInstance


class Abstractor(Algorithm):
    '''An abstractor algorithm.'''
    _name = 'abstractor'
    _default_hyperparams = {}

    def instantiate(self, **hyperparams) -> AbstractorInstance:
        raise NotImplementedError('instantiate is not implemented in Abstractor.')
