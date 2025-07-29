'''Representation of a neighbor for Auton Lab's distributed decision tree.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.


import pickle
from typing import List, NamedTuple, Optional, Tuple, Union

import numpy as np

from ...wrangler.logger import Logger, Level

from ..impl.distributed_algorithm_instance import NeighborState


log = Logger(__file__, to_stdout=False,
             level=Level.INFO).logger()


class Acorn(NamedTuple):
    '''Minimal information needed to represent a decision tree.

    See AutonDecisionTreeNeighbor for more info about what these mean.'''
    n_in: int
    n_out: int
    children_left: List[Optional[int]]
    children_right: List[Optional[int]]
    feature: List[Optional[int]]
    threshold: List[Optional[float]]
    equal: List[Optional[bool]]
    value: List[np.ndarray]
    sample_weight: List[float]
    lower_bound: np.ndarray
    upper_bound: np.ndarray
    class_list: List[str]


class Thresholds(NamedTuple):
    '''Threshold information.

    ts: length n_in.
        each element is a list of threshold candidates
    eqs: length n_in.
        each element is a list of bools indicating which threshold candidates are equal
    ddsdts: length n_in.
        each element has the same length as the corresponding element in ts and eqs
    '''
    ts: List[List[float]]
    eqs: List[List[bool]]
    ddsdts: List[List[float]]


class AutonDecisionTreeNeighbor(NeighborState):  # pylint: disable=too-many-public-methods
    '''State of a neighbor for a decision tree classifier.'''
    # TODO(Merritt/Kyle): rethink what NeighborState is (do we just want it to be what we send?)
    _acorn: Acorn

    def __init__(self,
                 acorn: Acorn,
                 columns: Optional[List[Union[int, str]]] = None):
        super().__init__(columns=columns)
        self._acorn = acorn

    @classmethod
    def init_tree(cls,
                  n_in: int,
                  n_out: int,
                  lower_bound: np.ndarray,
                  upper_bound: np.ndarray,
                  class_list: List[str],
                  columns: Optional[List[Union[int, str]]] = None
                  ) -> 'AutonDecisionTreeNeighbor':
        '''Create an empty tree to be built'''
        return cls(
            acorn=Acorn(
                n_in=n_in,
                n_out=n_out,
                children_left=[],
                children_right=[],
                feature=[],
                threshold=[],
                equal=[],
                value=[],
                sample_weight=[],
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                class_list=class_list),
            columns=columns)

    def __str__(self):
        return (f'{self.__class__.__name__}('
                f'lower_bound = {self.lower_bound}, \n'
                f'upper_bound = {self.upper_bound}, \n'
                f'class_list = {self.class_list}, \n'
                f'n_in = {self.n_in}, n_out = {self.n_out}, \n'
                f'number of nodes: {len(self.feature)}.\n')

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'acorn = {self._acorn})')

    def encode(self) -> bytes:
        '''Encode the state of the neighbor.'''
        retval = pickle.dumps((self._acorn, self._columns))
        return retval

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'AutonDecisionTreeNeighbor':
        '''Decode the state of the neighbor.'''
        (acorn, cols) = pickle.loads(serialized_model)
        assert isinstance(acorn, Acorn), (
            'BUG: expecting first element of message to be type Acorn, '
            f'instead found {acorn} of type {type(acorn)}'
        )
        return cls(columns=cols, acorn=acorn)

    def norm2(self) -> float:
        '''Compute the norm of the state.'''
        return self.inner_product(self)

    def norm2_diff(self, other: 'AutonDecisionTreeNeighbor') -> float:
        '''Compute numerical representation of distance between models
        (||f-g||^2)
        '''
        self_norm = self.norm2()
        other_norm = other.norm2()
        inprod = self.inner_product(other)
        retval = self_norm + other_norm - 2.0 * inprod
        retval = round(retval, ndigits=5)  # Account for floating point error.
        assert retval >= 0.0, (
            f'BUG: norm2_diff should never be negative.  Got {retval}. '
            f'self.norm2() = {self_norm}; other.norm2() = {other_norm}, '
            f'self.inner_product(other) = {inprod}.'
        )
        return retval

    def distance(self, other: 'AutonDecisionTreeNeighbor') -> float:
        if self.class_list != other.class_list:
            return float('inf')

        return self.norm2_diff(other)

    def inner_product(self, other: 'AutonDecisionTreeNeighbor') -> float:
        '''Compute the inner product of two Decision trees.'''
        assert len(self.feature) > 0, 'BUG: taking inner product of an empty tree (self).'
        assert len(other.feature) > 0, 'BUG: taking inner product of an empty tree (other).'

        # this could be optimized, but probably doesn't need it
        # so this is the simple implementation
        lb = np.minimum(self.lower_bound, other.lower_bound)
        ub = np.maximum(self.upper_bound, other.upper_bound)
        feature_lengths = ub - lb
        # ignore all zero-length dimensions when computing the volume
        feature_lengths[feature_lengths == 0] = 1
        totl_vol = feature_lengths.prod()

        assert self.class_list == other.class_list, (
            'BUG: trying to take the inner product of decision trees with '
            'different class lists. \n'
            f'Self: {self.class_list} \n'
            f'Other: {other.class_list}'
        )

        def trav(i: int, lb: np.ndarray, ub: np.ndarray) -> float:
            if self.is_leaf(i):
                if other is self:
                    sub_feature_lengths = ub - lb
                    sub_feature_lengths[feature_lengths == 0] = 1
                    vol = sub_feature_lengths.prod()
                    retval = vol * np.sum(np.square(self.value[i]))
                    assert not np.isnan(retval)
                    return retval
                s = other.get_thresholds(lb, ub)[0]
                retval = s @ self.value[i]
                assert not np.isnan(retval)
                return retval
            f, t, _, left, right = self.internal_node_info(i)
            tot: float = 0.0
            old = ub[f]
            ub[f] = t
            tot += trav(left, lb, ub)
            ub[f] = old
            old = lb[f]
            lb[f] = t
            tot += trav(right, lb, ub)
            lb[f] = old
            return tot

        retval = trav(0, self.lower_bound.copy(), self.upper_bound.copy()) / totl_vol
        assert not np.isnan(retval)
        return retval

    def is_leaf(self, i: int) -> bool:
        '''Is node i a leaf?'''
        assert i < len(self._acorn.feature), (
            f'BUG: Asking if node {i} is a leaf but there are only '
            f'{len(self._acorn.feature)} nodes.')

        return self._acorn.feature[i] is None

    def internal_node_info(self, i: int) -> Tuple[int, float, bool, int, int]:
        '''Return (feature, threshold, equal, children_left, children_right)

        while asserting that this node is not a leaf.
        '''
        f = self.feature[i]
        t = self.threshold[i]
        eq = self.equal[i]
        left = self.children_left[i]
        right = self.children_right[i]
        assert (
            f is not None and t is not None and eq is not None
            and left is not None and right is not None), (
            'BUG: a non-leaf node must have non-None values for '
            f'feature (found {f}), threshold (for {t}), '
            f'equal (found {eq}), children_left (found {left}), '
            f'and children_right (found {right}).'
        )
        assert f < self.n_in, (
            f'BUG: feature {f} referenced with only {self.n_in} features.  '
            f'Full state: {repr(self)}'
        )
        return (f, t, eq, left, right)

    def get_thresholds(self,
                       lb: np.ndarray,
                       ub: np.ndarray
                       ) -> Tuple[np.ndarray, Thresholds]:
        '''return ss, ts, eqs, ddsdts

        ss: length n_out.
            something involving the sum of label weights for each class in a given region

        thresh: Threshold information.  Contains:
            ts: length n_in.
                each element is a list of threshold candidates
            eqs: length n_in.
                each element is a list of bools indicating which threshold candidates are equal
            ddsdts: length n_in.
                each element has the same length as the corresponding element in ts and eqs
        '''

        # initialize a list of outputs per input feature
        ss = np.zeros(self.n_out)

        thresh = Thresholds(
            ts=[[] for _ in range(self.n_in)],
            eqs=[[] for _ in range(self.n_in)],
            ddsdts=[[] for _ in range(self.n_in)]
        )

        if len(self.feature) == 0:
            # No threshold candidates as tree is empty
            log.warning('Calling get_thresholds on an empty tree: %s', repr(self))
            return ss, thresh

        # initialize bounds
        if self.lower_bound is not None:
            lb = np.maximum(lb, self.lower_bound)
        if self.upper_bound is not None:
            ub = np.minimum(ub, self.upper_bound)
        if np.any(lb >= ub):
            # No threshold candidates as domain is empty
            return ss, thresh

        def forward(i: int,  # pylint: disable=too-many-locals
                    lb: np.ndarray,
                    ub: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
            '''traverse tree

            i: index of tree-node
            lb: lower bound (n_in)
            ub: upper bound (n_in)

            returns:
                dsdt on the lower edge of the subtree (n_in x n_out)
                dsdt on the upper edge of the subtree (n_in x n_out)'''
            nonlocal ss
            if self.is_leaf(i):
                # leaves: compute dsdt for each edge
                w = ub - lb
                s: np.ndarray = self.value[i] * np.prod(w)
                ss += s
                dsdt = s[None, :] / w[:, None]
                return dsdt, dsdt
            # internal nodes: split left and right
            f, t, eq, child_l, child_r = self.internal_node_info(i)
            left = t > lb[f]
            right = t < ub[f]
            if left:
                old = ub[f]
                assert isinstance(old, float), f'Expected float, got type {type(old)} ({old})'
                ub[f] = min(old, t)
                dsdtl_l, dsdtu_l = forward(child_l, lb, ub)
                ub[f] = old
                if not right:
                    return dsdtl_l, dsdtu_l
            if right:
                old = lb[f]
                assert isinstance(old, float), f'Expected float, got type {type(old)} ({old})'
                lb[f] = max(old, t)
                dsdtl_r, dsdtu_r = forward(child_r, lb, ub)
                lb[f] = old
                if not left:
                    return dsdtl_r, dsdtu_r
            # append a threshold candidate for this internal node's split
            thresh.ts[f].append(t)
            thresh.eqs[f].append(eq)
            thresh.ddsdts[f].append(dsdtl_r[f] - dsdtu_l[f])
            # compute edge dsdt from child values
            dsdtl = dsdtl_l + dsdtl_r
            dsdtu = dsdtu_l + dsdtu_r
            dsdtl[f] -= dsdtl_r[f]
            dsdtu[f] -= dsdtu_l[f]
            return dsdtl, dsdtu

        # get thresholds from this tree's splits
        dsdtls, dsdtus = forward(0, lb, ub)

        # get thresholds for global bounds
        for t, eq, ddsdt, l, u, dsdtl, dsdtu in zip(
            thresh.ts, thresh.eqs, thresh.ddsdts, lb, ub, dsdtls, dsdtus
        ):
            t.append(l)
            eq.append(False)
            ddsdt.append(dsdtl)
            t.append(u)
            eq.append(True)
            ddsdt.append(-dsdtu)

        return ss, thresh

    def modify_classes(self, class_list: List[str]) -> None:
        '''Modify self in-place to have a new class list'''
        assert len(self.value[0]) == len(class_list), (
            'Mismatch between value and class list: '
            f'{len(self.value[0])} != {len(class_list)}'
        )
        self._acorn = Acorn(
            n_in=self.n_in,
            n_out=len(class_list),
            children_left=self.children_left,
            children_right=self.children_right,
            feature=self.feature,
            threshold=self.threshold,
            equal=self.equal,
            value=self.value,
            sample_weight=self.sample_weight,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            class_list=class_list
        )

    @property
    def n_in(self) -> int:
        '''Number of features'''
        return self._acorn.n_in

    @property
    def n_out(self) -> int:
        '''Number of classes'''
        return self._acorn.n_out

    @property
    def children_left(self) -> List[Optional[int]]:
        '''id of the left child of node i or None if leaf node.

        Length = number of nodes in the tree.
        '''
        return self._acorn.children_left

    @property
    def children_right(self) -> List[Optional[int]]:
        '''id of the right child of node i or None if leaf node.

        Length = number of nodes in the tree.
        '''
        return self._acorn.children_right

    @property
    def feature(self) -> List[Optional[int]]:
        '''feature used for splitting node i or None if leaf.

        Length = number of nodes in the tree.
        '''
        return self._acorn.feature

    @property
    def threshold(self) -> List[Optional[float]]:
        '''threshold value at node i or None if leaf.

        Length = number of nodes in the tree.
        '''
        return self._acorn.threshold

    @property
    def equal(self) -> List[Optional[bool]]:
        '''If true, decision threshold is <=; otherwise <  (None if leaf).'''
        return self._acorn.equal

    @property
    def value(self) -> List[np.ndarray]:
        '''Class probabilities at each leaf node.

        Each element is size n_out [not sure what it is at non-leafs].
        '''
        return self._acorn.value

    @property
    def sample_weight(self) -> List[float]:
        '''Representation of total amount of data present at each node in the tree.

        Length = number of nodes in the tree.
        '''
        return self._acorn.sample_weight

    @property
    def lower_bound(self) -> np.ndarray:
        '''Defines lower bound of the domain of the tree.

        Length n_in.
        '''
        return self._acorn.lower_bound

    @property
    def upper_bound(self) -> np.ndarray:
        '''Defines upper bound of the domain of the tree.

        Length n_in.
        '''
        return self._acorn.upper_bound

    @property
    def class_list(self) -> List[str]:
        '''List of observed classes in order.

        Length n_out.
        '''
        return self._acorn.class_list

    @property
    def num_nodes(self) -> int:
        '''Number of nodes in the tree.'''
        return len(self._acorn.threshold)


def register(catalog, *args, **kwargs) -> None:  # pylint: disable=unused-argument
    '''Nothing to register.'''
