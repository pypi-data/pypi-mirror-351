'''Contains information on hyperparam overrides to use for indexing dictionaries.'''
from collections import defaultdict
from typing import Dict

from frozendict import frozendict


class FrozenOverrides(frozendict[str, frozendict[str, str]]):
    '''Contains information on hyperparam overrides to use in building Designator

    The contents look like this\\:

    .. code-block:: Python

        {
            'pipeline_designator_component': {
                'hyperparam_name': 'hyperparam_value_str'
            }
        }

    '''

    @classmethod
    def freeze(cls, inp: Dict[str, Dict[str, str]]) -> 'FrozenOverrides':
        '''Turn a dict of dicts into a deeply immutable OverridesInfo'''
        cool: Dict[str, frozendict[str, str]] = {
            k: frozendict(v) for k, v in inp.items()}
        return FrozenOverrides(cool)

    def thaw(self) -> Dict[str, Dict[str, str]]:
        '''Turn self into a deeply mutable dict of dicts.'''
        retval: Dict[str, Dict[str, str]] = defaultdict(dict)
        for step_des, hyperparams in self.items():
            retval[step_des].update(hyperparams)
        return retval

    def update(self, other: Dict[str, Dict[str, str]]) -> 'FrozenOverrides':
        '''Update self with values in other'''
        tmp = self.thaw()
        for step_des, hyperparams in tmp.items():
            if step_des in other:
                hyperparams.update(other[step_des])
        for step_des, hyperparams in other.items():
            if step_des not in tmp:
                tmp[step_des] = hyperparams
        return self.__class__.freeze(tmp)
