'''Auton Lab's implementation of a decision tree classifier for distributed data.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=duplicate-code,too-many-lines

import copy
from typing import Callable, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from ...catalog.catalog import upcast
from ...config_components.distributed_config import DistributedConfig
from ...problem_def.task import DataType, TaskType
from ...tables.impl.table import TableFactory
from ...wrangler.constants import Defaults
from ...wrangler.dataset import Dataset
from ...wrangler.logger import Logger, Level

from ..impl.distributed_algorithm_instance import DistributedAlgorithmInstance, NeighborState
from ..impl.algorithm import Algorithm, HyperparamError, MemoryAlgorithmCatalog

from .auton_decision_tree_neighbor import AutonDecisionTreeNeighbor

log = Logger(__file__, to_stdout=False,
             level=Level.INFO).logger()


def loss_gini(v: np.ndarray) -> float:
    '''Standard gini loss function'''
    return 1 - (v ** 2).sum(axis=-1)


class AutonDecisionTreeInstance(DistributedAlgorithmInstance):
    '''Implementation of Gaussian Mixture Models for distributed data.'''
    _neighbor_constructor = AutonDecisionTreeNeighbor

    _predict_state: Optional[AutonDecisionTreeNeighbor] = None
    _max_depth: Optional[int] = None
    _min_sample_weight: float = 0.0
    _min_vol: float = 0.0
    _ccp_alpha: float = 0.0
    _loss_fn: Callable[[np.ndarray], float]

    _random_state: np.random.RandomState  # pylint: disable=no-member,line-too-long

    def __init__(self,
                 parent: Algorithm,
                 distributed: DistributedConfig,
                 **kwargs):
        hyperparams = parent.hyperparams(**kwargs)

        _random_seed = hyperparams.pop('random_seed', None)
        self._random_state = np.random.RandomState(_random_seed)  # pylint: disable=no-member,line-too-long

        if not isinstance(distributed, DistributedConfig):
            raise HyperparamError(
                f'{self.__class__.__name__} distributed must be a DistributedConfig, instead found '
                f'{distributed} of type {type(distributed)}')

        max_depth = hyperparams.pop('max_depth')
        self._max_depth = None if max_depth is None else int(max_depth)
        self._min_sample_weight = float(hyperparams.pop('min_sample_weight'))
        self._min_vol = float(hyperparams.pop('min_vol'))
        self._ccp_alpha = float(hyperparams.pop('ccp_alpha'))
        self._loss_fn = hyperparams.pop('loss_fn')
        # Either max_depth, min_sample_weight, min_vol or ccp_alpha should be set or trees can
        #   grow very large.
        # TODO(Merritt): Is there a way to solve this without a warning?
        if self._max_depth is None and self._min_sample_weight == 0.0 and (
            self._min_vol == 0.0 and (
                self._ccp_alpha == 0.0)):
            log.warning(
                'No stopping condition set so nothing to limit tree growth. '
                'Consider setting max_depth, min_sample_weight, '
                'min_vol or ccp_alpha.')

        # TODO(Merritt): allow setting lower and upper bound & number of classes via hyperparam

        super().__init__(parent, distributed=distributed, **hyperparams)

    @property
    def _neighbor_models_iter(self) -> Iterator[AutonDecisionTreeNeighbor]:
        for v in super()._neighbor_models_iter:
            assert isinstance(v, AutonDecisionTreeNeighbor), (
                'BUG: expected neighbor_models to contain AutonDecisionTreeNeighbor, '
                f'instead found {v} of type {type(v)}'
            )
            yield v

    @property  # type: ignore[override]
    def _my_state(self) -> Optional[AutonDecisionTreeNeighbor]:
        retval = DistributedAlgorithmInstance._my_state.fget(self)  # type: ignore[attr-defined] # pylint: disable=assignment-from-no-return,line-too-long
        assert retval is None or isinstance(retval, AutonDecisionTreeNeighbor), (
            'BUG: expected _my_state to be None or an AutonDecisionTreeNeighbor.')
        return retval

    @_my_state.setter
    def _my_state(self, value: Optional[AutonDecisionTreeNeighbor]) -> None:
        assert value is None or isinstance(value, AutonDecisionTreeNeighbor), (
            'BUG: expected value to be None or an AutonDecisionTreeNeighbor.')
        DistributedAlgorithmInstance._my_state.fset(self, value)  # type: ignore[attr-defined]

    def _decode(self, serialized_model: bytes) -> NeighborState:
        '''Decode a message from distributed neighbors. '''
        return AutonDecisionTreeNeighbor.decode(serialized_model)

    def _is_leaf(self, i: int) -> bool:
        '''Is node i a leaf?'''
        assert self._predict_state is not None, (
            'BUG: _predict_state must exist when calling is_leaf.')
        return self._predict_state.is_leaf(i)

    def _internal_node_info(self, i: int) -> Tuple[int, float, bool, int, int]:
        '''Return (feature, threshold, equal, children_left, children_right)

        while asserting that this node is not a leaf.
        '''
        assert self._predict_state is not None, (
            'BUG: _predict_state must not be None when calling internal_node_info'
        )
        return self._predict_state.internal_node_info(i)

    def _reconcile_class_list(self,
                              data_classes: Optional[List[str]],
                              prev_fit_class_list: Optional[List[str]]) -> List[str]:
        '''Reconcile recorded class list with neighbor class list and classes in the data.

        data_classes: classes observed in the data, or None if fitting with no data
        class_list: recorded class list from previous fit, or None if first fit

        Returns new class list.
        '''

        trees = list(self._neighbor_models_iter)
        some_neighbor_class_list = None if len(trees) == 0 else trees[0].class_list

        assert any([data_classes, prev_fit_class_list, some_neighbor_class_list])

        all_class_lists: List[List[str]] = []
        if prev_fit_class_list is not None:
            all_class_lists.append(prev_fit_class_list)
        if data_classes is not None:
            data_classes = sorted(data_classes)
            all_class_lists.append(data_classes)
        if len(trees) > 0:
            all_class_lists += [m.class_list for m in trees]

        # if all class lists match: nothing to do
        assert len(all_class_lists) > 0
        some_class_list = all_class_lists[0]
        if all(cl == some_class_list for cl in all_class_lists):
            return some_class_list

        new_class_list = sorted(set().union(*all_class_lists))
        new_n_out = len(new_class_list)

        log.log(Level.VERBOSE,
                'Prev fit class list: %s\nData class list: %s\n'
                'Neighbor class lists: %s\nNew class list: %s',
                prev_fit_class_list, data_classes, [m.class_list for m in trees], new_class_list)

        # modify trees in place
        def permute_values(t: Optional[AutonDecisionTreeNeighbor],
                           to_: np.ndarray, from_: np.ndarray, new_n_out: int) -> None:
            if t is None:
                return
            for i, old_val in enumerate(t.value):
                if old_val is None:
                    log.debug('Index %d skipping None old_val', i)
                    continue
                v = np.zeros(new_n_out)

                # from_ represents indices in old_val and to_ represents corresponding indices in v
                assert len(to_) == len(from_)
                assert all(i < len(v) for i in to_)
                assert all(i < len(old_val) for i in from_)
                v[to_] = old_val[from_]
                t.value[i] = v

        for i, m in enumerate(trees):
            _, to_, from_ = np.intersect1d(
                new_class_list, m.class_list, assume_unique=True, return_indices=True)
            try:
                permute_values(m, to_, from_, new_n_out)
                m.modify_classes(class_list=new_class_list)
            except AssertionError as err:
                msg = ('Error while reconciling class list has been '
                       f'encountered on tree {i}.\n'
                       f'Prev fit class list: {prev_fit_class_list}\n'
                       f'Data class list: {data_classes}\n',
                       f'Neighbor class lists: {[m.class_list for m in trees]}\n'
                       f'New class list: {new_class_list}\n')
                raise AssertionError(msg) from err
            # TODO(Merritt): is it fine to modify local representations of neighbors?  talk to kyle

        # modify self
        if self._my_state is not None:
            old_class_list = self._my_state.class_list
            _, to_, from_ = np.intersect1d(
                new_class_list, old_class_list, assume_unique=True, return_indices=True)
            permute_values(self.my_state, to_, from_, new_n_out)
            self._my_state.modify_classes(class_list=new_class_list)

        return new_class_list

    def _append_leaf(self, v: np.ndarray, w: float) -> None:
        '''Modify our state in-place to append a leaf.'''
        assert self._my_state is not None, (
            'BUG: cannot append leaf before state is initialized.')
        self._my_state.children_left.append(None)
        self._my_state.children_right.append(None)
        self._my_state.feature.append(None)
        self._my_state.threshold.append(None)
        self._my_state.equal.append(None)
        self._my_state.value.append(v)
        self._my_state.sample_weight.append(w)

    def _prepare_data(self,
                      dataset: Optional[Dataset]) -> Tuple[
                          np.float64, np.ndarray, np.ndarray, List[Union[int, str]]]:
        if dataset is None:
            assert self._neighbor_metadata, (
                'BUG: expected either dataset or neighbor metadata to be non-None'
            )
            # No data so we only synthesize neighbor models
            # Set omega to 1 (no self-regularization)
            _omega = np.float64(1.0)
            # Create blank data with 0 rows and a number of columns matching neighbors
            ncol = next(self._neighbor_models_iter).n_in
            cols = next(self._neighbor_models_iter).columns
            assert cols is not None, (
                'BUG: found neighbor model with no recored columns'
            )
            if any(model.n_in != ncol for model in self._neighbor_models_iter):
                raise NotImplementedError(
                    'Neighbor models disagree about number of columns '
                    'and reconciling cols is not implemented.')
            x = np.zeros(shape=(0, ncol))
            y = np.zeros(shape=(0, 1))
            log.debug("preparing data for empty dataset: _omega: %s, x: %s, y: %s, cols: %s",
                      _omega, x, y, cols)
        else:
            _omega = self._omega
            target = dataset.metadata.target
            assert target is not None, 'BUG: found no target col'
            x = dataset.covariates_table.as_(np.ndarray)
            y = dataset.target_table.as_(np.ndarray).flatten()
            cols = dataset.dataframe_table.columns
            log.debug("preparing data with non-empty dataset: _omega: %s, x: %s, y: %s, cols: %s",
                      _omega, x, y, cols)

        return _omega, x, y, cols

    def _reconcile_bounds(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        lower_bound_candidates: List[np.ndarray] = []
        upper_bound_candidates: List[np.ndarray] = []
        if x.shape[0] > 0:
            # we have data
            lower_bound_candidates.append(x.min(0))
            upper_bound_candidates.append(x.max(0))
        if self._my_state is not None:
            # we have a previous fit
            lower_bound_candidates.append(self._my_state.lower_bound)
            upper_bound_candidates.append(self._my_state.upper_bound)
        trees = list(self._neighbor_models_iter)
        lower_bound_candidates += [m.lower_bound for m in trees]
        upper_bound_candidates += [m.upper_bound for m in trees]
        lower_bound: np.ndarray = np.stack(lower_bound_candidates).min(0)
        upper_bound: np.ndarray = np.stack(upper_bound_candidates).max(0)
        return (lower_bound, upper_bound)

    def _fit(self,  # pylint: disable=too-many-statements,too-many-locals
             dataset: Optional[Dataset],
             **kwargs) -> None:
        '''Fit the model to the data. This is the actual implementation of fit.'''
        if dataset is None and not self._neighbor_metadata:
            # No data or neighbor models; cannot fit
            return
        log.debug("fit on dataset: %s \n self._neighbor_metadata: %s \n",
                  dataset, self._neighbor_metadata)
        _omega, x, y, cols = self._prepare_data(dataset=dataset)
        lower_bound, upper_bound = self._reconcile_bounds(x=x)

        # reconcile class list
        old_class_list = None if self.my_state is None else self.my_state.class_list
        if y.shape[0] == 0:
            class_list = self._reconcile_class_list(
                data_classes=None,
                prev_fit_class_list=old_class_list
            )
            new_n_out = len(class_list)
        elif y.ndim == 1:
            # y is 1 column: format y as one-hot labels
            data_classes = np.unique(y).tolist()
            class_list = self._reconcile_class_list(
                data_classes=data_classes, prev_fit_class_list=old_class_list)
            new_n_out = len(class_list)
            y1hot = np.zeros((x.shape[0], new_n_out))
            for i, c in enumerate(class_list):
                y1hot[y == c, i] = 1
            y = y1hot.reshape((*y.shape, new_n_out))
        else:
            # y is already formatted as one-hot labels
            # HACK assume one-hot columns correspond to class-ids (naive)
            data_classes = np.arange(y.shape[1]).tolist()
            class_list = self._reconcile_class_list(
                data_classes=data_classes, prev_fit_class_list=class_list)
            new_n_out = len(class_list)

        # prepare other trees
        trees = list(self._neighbor_models_iter)
        if self._my_state is not None:
            trees = [self._my_state] + trees

            tree_weights = self._lambda * np.ones(len(trees))
            tree_weights[0] *= (1 - _omega) / _omega
        else:
            tree_weights = self._lambda * np.ones(len(trees))

        for i, tree in enumerate(trees):
            assert tree.num_nodes > 0, (
                f'Tree {i} is empty: {tree}'
            )
            assert len(tree.value[0]) == len(tree.class_list), (
                f'Tree {i} has values mismatched with its class list. \n'
                f'Values: {tree.value} \n'
                f'Class list: {tree.class_list} \n'
                f'My state: {self.my_state}\n'
            )
            assert tree.class_list == trees[0].class_list

        n_in = x.shape[1]
        self._my_state = AutonDecisionTreeNeighbor.init_tree(
            n_in, new_n_out, lower_bound, upper_bound, class_list,
            columns=cols
        )

        def recursive_fit(d: int,  # pylint: disable=too-many-statements,too-many-locals,too-many-branches
                          x: np.ndarray,
                          y: np.ndarray,
                          lb: np.ndarray,
                          ub: np.ndarray,
                          n: float) -> int:
            '''
            d: depth of this node  [varies]
            x: local data (covariates)  [constant]
            y: local data (target) [constant]
            lb: lower bound of this subtree in the input space [varies]
            up: upper bound of this subtree in the input space [varies]
            n: number of samples plus total weight of all other trees; [constant]
                used to normalize the loss for subtrees

            Returns: this node's index

            notation in this section
            s: the sum of label weights for each class in a given region
            w: the weight of samples and other trees' influence in a given region
            v: the distribution of labels in a given region, v = s/w
            t: the threshold value for splitting
            eq: flag to mark a threshold as x <= t, as opposed to x < t
            ds: the instantaneous change in s at a given threshold
            dsdt: the rate of change of s with respect to t in a given region
            ddsdt: the instantaneous change in dsdt at a given threshold
            {x}L: the value of some variable {x} for the left child
            {x}R: the value of some variable {x} for the right child
            '''
            log.debug('calling recursive fit, d=%s', d)
            assert self._my_state is not None

            # get thresholds from other trees
            tree_thresholds = [tree.get_thresholds(lb, ub) for tree in trees]

            # compute loss for the current node
            s = sum(
                [w * ss for w, (ss, _) in zip(tree_weights, tree_thresholds) if w > 0],
                np.zeros(self._my_state.n_out)
            )
            s += y.sum(0)
            w = s.sum()  # this assumes this is a classifier
            if d == 0 and w == 0:
                # special case: our previous fit and all of our neighbors have the
                # same, zero-length domain in the imput data
                log.warning('Domain of all trees and input data is length 0. '
                            'Copying an arbitrary tree. '
                            'Trees include any neighbors and any previous fit.\n'
                            'Trees: %s\nTrain target: %s',
                            trees, y)
                some_tree = next(iter(trees))
                self._my_state = copy.deepcopy(some_tree)
                return 0

            assert w > 0, (
                'BUG: a split with weight zero will cause infinite recursion.'
                f'w: {w}\ns: {s}\ny: {y}\n'
                f'tree_thresholds: {tree_thresholds}\n'
                f'tree_weights: {tree_weights}\n'
            )
            log.debug('weight of this subtree: %s', w)
            v = s / w
            v_l: float = self._loss_fn(v)
            vol = np.prod(ub - lb)

            # if at depth zero, set the total weight of samples and other trees
            if d == 0:
                n = w

            # check stopping conditions
            best_feat = -1  # used as a flag for whether a suitable split was found
            best_thres = None
            best_equal = None
            if (self._max_depth is None or d < self._max_depth) \
                    and w >= 2 * self._min_sample_weight \
                    and vol >= 2 * self._min_vol \
                    and v_l > 0:
                log.debug('splitting')
                # loop over features to evaluate candidate splits
                best_loss = v_l - self._ccp_alpha * n / w
                # permute to break ties randomly
                for f in self._random_state.permutation(self._my_state.n_in):
                    # compile candidate splits from data and other trees into arrays
                    t_list = []
                    eq_list = []
                    ddsdt_list = []
                    for weight, (ss, thres) in zip(tree_weights, tree_thresholds):
                        if weight > 0:
                            t_list += thres.ts[f]
                            eq_list += thres.eqs[f]
                            ddsdt_list += [weight * ddsdt for ddsdt in thres.ddsdts[f]]
                    t = np.concatenate((x[:, f], x[:, f], np.array(t_list)))
                    eq = np.concatenate((np.zeros(x.shape[0], dtype=bool),
                                         np.ones(x.shape[0], dtype=bool),
                                         np.array(eq_list)))
                    ds = np.zeros((t.shape[0], self._my_state.n_out))
                    if y.shape[0] > 0:
                        ds[y.shape[0]:2 * y.shape[0]] = y
                    ddsdt = np.zeros((t.shape[0], self._my_state.n_out))
                    if len(ddsdt_list) > 0:
                        ddsdt[-len(ddsdt_list):] = np.array(ddsdt_list)

                    # sort the split information by ascending threshold value
                    idx: np.ndarray = np.lexsort((eq, t))
                    t = t[idx]
                    eq = eq[idx]
                    ds = ds[idx]
                    ddsdt = ddsdt[idx]

                    # compute s for the left child at each candidate split via running sums
                    dt = t[1:] - t[:-1]
                    dsdt = np.cumsum(ddsdt, axis=0)
                    ds[1:] += dsdt[:-1] * dt[:, None]
                    s_l = np.cumsum(ds, axis=0)

                    # Correct for numerical error introduced by a long cumulative sum
                    # s_l[0] should be zero, s_l[-1] should be the same as s
                    # scale the valeus in s_l to ensure this is always correct.
                    s_l *= (s / np.where(s_l[-1] == 0, 1, s_l[-1]))[None, :]

                    # compute the loss for each candidate split
                    # TODO(Merritt): pair w Jack to implement solution for weights being 0 from KDDT
                    w_l: np.ndarray = s_l.sum(axis=1)
                    # ^ assumes this is a classifier, change to implement regression
                    v_l_: np.ndarray = s_l / (w_l[:, None] + 1e-12)
                    s_r: np.ndarray = s - s_l
                    w_r: np.ndarray = w - w_l
                    v_r: np.ndarray = s_r / (w_r[:, None] + 1e-12)

                    len_along_f: np.ndarray = ub[f] - lb[f]
                    vol_l: Union[int, np.ndarray] = (
                        0 if len_along_f == 0
                        else vol * (t - lb[f]) / len_along_f
                    )
                    vol_r: np.ndarray = vol - vol_l
                    loss: np.ndarray = (
                        w_l * self._loss_fn(v_l_) + w_r * self._loss_fn(v_r)
                    ) / (w + 1e-12)  # HACK TODO

                    # mask out splits that violate stopping conditions
                    loss[w_l < self._min_sample_weight] = np.inf
                    loss[w_r < self._min_sample_weight] = np.inf
                    loss[vol_l < self._min_vol] = np.inf
                    loss[vol_r < self._min_vol] = np.inf

                    # if weight of one split is 0, we would run forever.
                    loss[w_l == 0] = np.inf
                    loss[w_r == 0] = np.inf

                    # first and last element are splits where one child is identical to its parent,
                    # and should never be chosen.
                    loss[0] = np.inf
                    loss[-1] = np.inf

                    # avoid trying to split two data points with same value for f
                    # if threshold is lt and previous threshold is same it needs to be masked
                    loss[
                        np.logical_and(
                            np.logical_not(eq),
                            t == np.roll(t, 1)
                        )
                    ] = np.inf
                    # if threshold is lte and next threshold is same it needs to be masked
                    loss[
                        np.logical_and(
                            eq,
                            t == np.roll(t, -1)
                        )
                    ] = np.inf

                    # find the split with the best loss
                    # i and j are the lower and upper bounds of a range of
                    #   equivalent best candidate thresholds
                    i: int = int(loss.argmin())
                    j: int = i

                    # center splits in regions with (nearly) no change in label weights
                    eps = self._tol  # a tolerance to accommodate numerical imprecision
                    while i > 0 and ds[i].sum() < eps:
                        i -= 1
                    while j < ds.shape[0] - 1 and ds[j + 1].sum() < eps:
                        j += 1

                    # update best split
                    if loss[i] < best_loss:
                        best_loss = loss[i]
                        best_feat = f
                        best_thres = t[i] if j == i else (t[i] + t[j]) / 2
                        best_equal = eq[i] if j == i else False
                        best_split_weight_lower = (w_l[i], w_r[i])
                        best_split_weight_upper = (w_l[j], w_r[j])
                        log.debug('best split on %s weight lower: %s', f, best_split_weight_lower)
                        log.debug('best split on %s weight upper: %s', f, best_split_weight_upper)
            else:
                log.debug('not splitting')

            # assign values to this node (as a leaf)
            i = len(self._my_state.children_left)
            self._append_leaf(v, w)

            # if a good split was found, perform the split and make this node internal
            if best_feat >= 0:
                assert best_thres is not None and best_equal is not None
                # grow left subtree
                mask = x[:, best_feat] <= best_thres if best_equal else x[:, best_feat] < best_thres
                old = ub[best_feat]
                ub[best_feat] = best_thres
                self._my_state.children_left[i] = recursive_fit(d + 1, x[mask], y[mask], lb, ub, n)
                ub[best_feat] = old

                # grow right subtree
                mask = np.logical_not(mask)
                old = lb[best_feat]
                lb[best_feat] = best_thres
                self._my_state.children_right[i] = recursive_fit(d + 1, x[mask], y[mask], lb, ub, n)
                lb[best_feat] = old

                # set this node's split parameters
                self._my_state.feature[i] = best_feat
                self._my_state.threshold[i] = best_thres
                self._my_state.equal[i] = best_equal

            # return this node's index so its parent can point to it
            return i

        _ = recursive_fit(0, x, y, self._my_state.lower_bound, self._my_state.upper_bound, 0)
        assert self.my_state is not None and len(self.my_state.feature) > 0, (
            'BUG: ended fit with an empty tree. '
            f'Input data: \n {dataset}'
        )

    def _predict_proba(self, x: np.ndarray) -> np.ndarray:
        def forward(i: int, x: np.ndarray) -> np.ndarray:
            log.debug('calling forward on node %s', i)
            assert self._predict_state is not None
            if self._is_leaf(i):
                return np.ones(x.shape[0])[:, None] * self._predict_state.value[i][None, :]
            (f, t, eq, left, right) = self._internal_node_info(i)
            out = np.zeros((x.shape[0], self._predict_state.n_out))
            assert f < x.shape[1], (
                f'BUG: feature {f} is out of bounds, x only has {x.shape[1]} features.  x:\n{x}'
            )
            mask = x[:, f] <= t if eq else x[:, f] < t
            out[mask] = forward(left, x[mask])
            mask = np.logical_not(mask)
            out[mask] = forward(right, x[mask])
            return out
        return forward(0, x)

    def _predict(self, dataset: Optional[Dataset], **kwargs) -> Optional[Dataset]:
        '''Predict the labels of the data. This is the actual implementation of predict.'''
        assert self._predict_state is not None, (
            'BUG: self._predict_state should not be None when predict is called.'
        )
        assert isinstance(self._predict_state, AutonDecisionTreeNeighbor), (
            'BUG: expected self._predict_state to be an AutonDecisionTreeNeighbor, '
            f'instead found {self._predict_state} of type {type(self._predict_state)}'
        )

        if dataset is None:
            log.error('Predict called on no data.')
            return None

        try:
            x = dataset.covariates_table.as_(np.ndarray)
        except KeyError as err:
            log.error('Predict error: %s', err)
            return None

        assert x.shape[1] == self._predict_state.n_in, (
            f'BUG: Data given to predict has {x.shape[1]} columns but n_in is '
            f'{self._predict_state.n_in}.  Input data: \n{dataset}'
        )

        proba = self._predict_proba(x)
        # shape should be (x_nrow, n_out)
        assert proba.shape == (x.shape[0], self._predict_state.n_out)

        # shape should be (x_nrow, 1)
        # value for each row is the index of its prediction in the class list.
        predictions_class_id = np.argmax(proba, axis=1)

        predictions_class_name = [
            self._predict_state.class_list[i] for i in predictions_class_id
        ]

        target_col = dataset.metadata.target
        assert target_col is not None, 'must have target'

        proba_df = pd.DataFrame(proba, columns=self._predict_state.class_list)
        pred_df = pd.DataFrame({target_col.name: predictions_class_name})

        retval = dataset.output()

        retval.predictions_table = TableFactory(pred_df)
        retval.probabilities = TableFactory(proba_df)  # type: ignore[abstract] # pylint: disable=abstract-class-instantiated
        return retval

    def norm2_diff(self, other: 'AutonDecisionTreeInstance') -> float:
        '''Compute the squared norm of the difference between two models.'''
        if self._predict_state is None or other.my_state is None:
            raise ValueError('Model must be trained before computing norm2_diff.')
        return self._predict_state.norm2_diff(other.my_state)

    @property
    def my_state(self) -> Optional[AutonDecisionTreeNeighbor]:
        '''Get the state of the model.

        Needed for type reconciliation.
        '''
        retval = super().my_state
        assert retval is None or isinstance(retval, AutonDecisionTreeNeighbor)
        return retval

    @property
    def my_state_copy(self) -> Optional[AutonDecisionTreeNeighbor]:
        '''Safely get a copy the state of the model.

        Needed for type reconciliation.
        '''
        retval = super().my_state_copy
        assert retval is None or isinstance(retval, AutonDecisionTreeNeighbor)
        return retval


class AutonDecisionTreeModel(Algorithm):
    '''Implementation of a decision tree classifier for distributed data.'''
    _name = 'auton_decision_tree_model'
    _instance_constructor = AutonDecisionTreeInstance
    _tags: Dict[str, List[str]] = {
        'task': [TaskType.MULTICLASS_CLASSIFICATION.name, TaskType.BINARY_CLASSIFICATION.name],
        'data_type': [DataType.TABULAR.name],
        'source': ['autonlab'],
        'distributed': ['true'],
        'supports_random_seed': ['true'],
    }
    _default_hyperparams = {
        'Lambda': 10.0,
        'omega': 2.0 / 3.0,
        'random_seed': Defaults.SEED,
        'tol': 1e-03,
        'maxiter': None,
        'max_depth': None,
        'min_sample_weight': 0.0,
        # minimum number of weighted samples in an area needed to split
        'min_vol': 0.0,
        # Smallest volume of hyperrectangle within input space before we no longer split
        'ccp_alpha': 0.0,
        # cost complexity pruning: if gain in discrimination power is too small, we stop
        'loss_fn': loss_gini
    }


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = AutonDecisionTreeModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
