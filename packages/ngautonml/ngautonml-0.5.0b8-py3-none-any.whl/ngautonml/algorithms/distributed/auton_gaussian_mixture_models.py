'''Auton Labs implementation of Gaussian Mixture Models for distributed data.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import pickle
from math import isclose
from typing import Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
from scipy.linalg import solve_triangular  # type: ignore[import]
from scipy.optimize import Bounds, minimize  # type: ignore[import]
from scipy.special import logsumexp  # type: ignore[import]


from ...catalog.catalog import upcast
from ...config_components.distributed_config import DistributedConfig
from ...problem_def.task import DataType, TaskType
from ...tables.impl.table import TableFactory
from ...wrangler.constants import Defaults  # type: ignore[import]
from ...wrangler.dataset import Dataset, Metadata
from ...wrangler.logger import Logger

from ..impl.distributed_algorithm_instance import DistributedAlgorithmInstance, NeighborState
from ..impl.algorithm import Algorithm, HyperparamError, MemoryAlgorithmCatalog


logger = Logger(__file__, to_stdout=False).logger()


class AutonGaussianMixtureModelsNeighbor(NeighborState):  # pylint: disable=too-many-public-methods

    '''State of a neighborfor Gaussian Mixture Models.'''
    # TODO(Piggy): Consider extracting the state manipulation methods into a separate type.
    # This would solve the problem of the return type of the grad_* functions, and the
    # too-man-public-methods warning.
    _K: int  # pylint: disable=invalid-name

    _full_covariance: bool = True
    _mix: np.ndarray
    _means: np.ndarray
    _cov: np.ndarray
    _cov_tril: np.ndarray

    def __init__(self,
                 mix: np.ndarray,
                 means: np.ndarray,
                 cov_tril: np.ndarray,
                 full: bool,
                 K: Optional[int] = None,  # pylint: disable=invalid-name,
                 columns: Optional[List[Union[int, str]]] = None
                 ):
        super().__init__(columns=columns)
        if K is None:
            K = mix.shape[0]
        self._mix = mix
        self._means = means
        self._cov_tril = cov_tril
        self._full_covariance = full
        self._K = K  # pylint: disable=invalid-name

    def __str__(self):
        return (f'AutonGaussianMixtureModelsNeighbor(K={self._K}, '
                f'mix shape: {self._mix.shape}, '
                f'means shape: {self._means.shape}, '
                f'cov_tril shape: {self._cov_tril.shape}, '
                f'full: {self._full_covariance})')

    def __repr__(self):
        return (f'AutonGaussianMixtureModelsNeighbor(K={self._K},\n'
                f'mix={self._mix},\n'
                f'means={self._means},\n'
                f'cov_tril={self._cov_tril},\n'
                f'full={self._full_covariance})')

    def encode(self) -> bytes:
        '''Encode the state of the neighbor.'''
        if self._full_covariance:
            _, d = self._means.shape
            cov = np.stack(
                [self._cov_tril[k][np.tril_indices(d)] for k in range(self._K)],
                0)
        else:
            cov = self._cov_tril
        retval = pickle.dumps((self._mix, self._means, cov, self.columns))
        return retval

    @classmethod
    def decode(cls, serialized_model: bytes) -> 'AutonGaussianMixtureModelsNeighbor':
        '''Decode the state of the neighbor.'''
        mix, means, cov, cols = pickle.loads(serialized_model)
        # TODO(Merritt): add some asserts here
        K, d = means.shape  # pylint: disable=invalid-name
        if cov.shape[1] > means.shape[1]:
            full_covariance = True
            cov_tril = np.zeros((K, d, d))
            for k in range(K):
                cov_tril[k][np.tril_indices(d)] = cov[k]
        else:
            full_covariance = False
            cov_tril = cov
        if cols is not None:
            # allow for columns to be none
            cols = cls._cast_columns(cols)
        return cls(K=K, mix=mix, means=means, cov_tril=cov_tril, full=full_covariance, columns=cols)

    @property
    def mix(self) -> np.ndarray:
        '''Get the mixture coefficients.'''
        return self._mix

    @property
    def means(self) -> np.ndarray:
        '''Get the means of the Gaussian components.'''
        return self._means

    @property
    def nfeatures(self) -> int:
        '''Get the number of features observed in the dataset.'''
        return self._means.shape[1]

    @property
    def cov_tril(self) -> np.ndarray:
        '''Get the lower triangular matrix of the covariance matrices.'''
        return self._cov_tril

    @property
    def full_covariance(self) -> bool:
        '''Get whether the covariance matrices are full.'''
        return self._full_covariance

    @property
    def K(self) -> int:  # pylint: disable=invalid-name
        '''Get the number of Gaussian components.'''
        return self._K

    def copy(self) -> 'AutonGaussianMixtureModelsNeighbor':
        '''Copy the state of the neighbor.'''
        return self.__class__(K=self._K,
                              mix=self._mix.copy(),
                              means=self._means.copy(),
                              cov_tril=self._cov_tril.copy(),
                              full=self._full_covariance,
                              columns=self.columns)

    @classmethod
    def unflatten(cls,
                  x: np.ndarray,
                  K: int,  # pylint: disable=invalid-name
                  d: int,
                  full: bool) -> 'AutonGaussianMixtureModelsNeighbor':
        '''Unflatten the state of the neighbor.'''
        if not full:
            return cls(K=K,
                       mix=x[:K],
                       means=x[K:(K + K * d)].reshape((K, d)),
                       cov_tril=x[(K + K * d):].reshape((K, d)),
                       full=full)
        cov = x[(K + K * d):]
        cov_tril = np.zeros((K, d, d))
        s = (d * (d + 1)) // 2
        idx = np.tril_indices(d)
        for k in range(K):
            cov_tril[k][idx] = cov[(k * s):((k + 1) * s)]
        return cls(
            K=K,
            full=full, mix=x[:K],
            means=x[K:(K + K * d)].reshape((K, d)),
            cov_tril=cov_tril)

    def flatten(self) -> np.ndarray:
        '''Flatten the state of the neighbor.'''
        if self._cov_tril.ndim == 2:
            return np.concatenate((self._mix, self._means.flatten(), self._cov_tril.flatten()))
        K, d = self._means.shape  # pylint: disable=invalid-name
        idx = np.tril_indices(d)
        return np.concatenate([self._mix, self._means.flatten()]
                              + [self._cov_tril[k][idx] for k in range(K)])

    def jac_mix(self) -> np.ndarray:
        '''Jacobian of the mixture coefficients.'''
        return np.eye(self.mix.size) / self.mix.sum() - self.mix[None, :] / self.mix.sum() ** 2

    def divide_mix_by_sum(self) -> None:
        '''Divide the mixture coefficients by their sum.'''
        self._mix = self._mix / self._mix.sum()

    def log_likelihoods(self, x_: np.ndarray) -> np.ndarray:
        '''
        compute the log likelihood of observations X under each component of a GMM
        '''
        _, d = x_.shape
        _k = self._means.shape[0]
        x_meaned = x_[:, None, :] - self._means[None, :, :]  # (n,.,d),(.,K,d)->(n,K,d)
        logdets = self.logdeterminants()
        if self._cov_tril.ndim == 2:  # diagonal covariances
            logprob = (-0.5 * np.einsum('kd,nkd->nk', 1.0 / self.cov_tril, x_meaned ** 2)
                       - 0.5 * logdets[None, :] - d * 0.5 * np.log(2 * np.pi))
        else:
            z = np.stack([solve_triangular(self._cov_tril[k], x_meaned[:, k, :].T, lower=True)
                          for k in range(_k)],
                         2)  # shape (d,n,K)
            logprob = -0.5 * (z ** 2).sum(0) - 0.5 * logdets[None, :] - d * 0.5 * np.log(2 * np.pi)
        return logprob  # shape=(n, K)

    def log_pdf(self, x_: np.ndarray) -> np.ndarray:
        '''
        compute the log likelihood of observations X under a GMM
        '''
        logprob = self.log_likelihoods(x_)  # shape=(n,K)
        return np.apply_along_axis(logsumexp, 1, logprob + np.log(self._mix)[None, :])

    def grad_lp(self, x, wrt_cov=None) -> Tuple[np.float64, 'AutonGaussianMixtureModelsNeighbor']:
        '''compute the log likelihood of observations X under a GMM and gradients

        compute grad of cov_tril with respect to wrt_cov (i.e. sigma = L@L.T+M@M.T, and want
        gradient with respect to L)
        only needed for full _trilcovariances
        '''
        _, d = x.shape
        K = self._means.shape[0]  # pylint: disable=invalid-name
        x_mean_ed = x[:, None, :] - self._means[None, :, :]  # (n,.,d),(.,K,d)->(n,K,d)
        logdets = self.logdeterminants()
        if self._cov_tril.ndim == 2:  # diagonal covariances
            logprob = (-0.5 * np.einsum('kd,nkd->nk', 1.0 / self._cov_tril, x_mean_ed ** 2)
                       - 0.5 * logdets[None, :] - d * 0.5 * np.log(2 * np.pi))  # shape = (n, K)
            grad_means = x_mean_ed / self.cov_tril[None, :, :]  # shape = (n, K, d)
            grad_cov_tril = (0.5 * (x_mean_ed**2 - self.cov_tril[None, :, :])
                             / self.cov_tril[None, :, :]**2)  # shape = (n, K, d)
        else:
            z = np.stack([solve_triangular(self._cov_tril[k], x_mean_ed[:, k, :].T, lower=True)
                          for k in range(K)],
                         2)  # shape (d, n, K)
            logprob = (-0.5 * (z**2).sum(0)
                       - 0.5 * logdets[None, :]
                       - d * 0.5 * np.log(2 * np.pi))  # shape (n,k)
            grad_means = np.stack([solve_triangular(self._cov_tril[k].T, z[:, :, k], lower=False)
                                   for k in range(K)], 1).T  # shape (n, K, d)
            grad_cov_tril = np.stack(
                [np.einsum('ni,nj->nij', z[:, :, k].T, z[:, :, k].T) - np.eye(d)[None, :, :]
                 for k in range(K)],
                1)  # shape (n,K,d,d)
        #
        weights = logprob + np.log(self._mix)[None, :]  # shape = (n,k)
        mx = weights.max(1)
        weights = np.exp(weights - mx[:, None])
        wtot = weights.sum(1)
        wtotinv = 1.0 / wtot
        #
        lp_ = np.log(wtot).sum() + mx.sum()  # row-wise logsumexp -> scalar
        #
        grad_mix = np.einsum('nk,k,n->k', weights, 1.0 / self.mix, wtotinv)  # shape = (k,)
        #
        grad_means = np.einsum('nk,nki,n->ki', weights, grad_means, wtotinv)  # shape = (k,d)
        #
        if self._cov_tril.ndim == 2:  # diagonal covariances
            grad_cov_tril = np.einsum('nk,nki,n->ki', weights, grad_cov_tril, wtotinv)
        else:
            grad_cov_tril = np.einsum('nk,nkij,n->kij', weights, grad_cov_tril, wtotinv)
            if wrt_cov is not None:
                grad_cov_tril = np.stack([
                    solve_triangular(
                        self._cov_tril[k].T,
                        grad_cov_tril[k]
                        @ solve_triangular(self._cov_tril[k], wrt_cov[k], lower=True),
                        lower=False) for k in range(K)],
                    0)
            else:
                grad_cov_tril = np.stack([
                    solve_triangular(self._cov_tril[k].T, grad_cov_tril[k], lower=False)
                    for k in range(K)],
                    0)
            ri, ci = np.triu_indices(d, k=1)
            for k in range(K):
                grad_cov_tril[k, ri, ci] = 0
        #
        return lp_, self.__class__(
            K=self._K,
            mix=grad_mix,
            means=grad_means,
            cov_tril=grad_cov_tril,
            full=self._full_covariance)

    def norm2(self) -> np.float64:
        '''Compute the norm of the state.'''
        return self.inner_product(self)

    def grad_norm2(self) -> Tuple[np.float64, 'AutonGaussianMixtureModelsNeighbor']:
        '''Compute the gradient of the norm of the state.'''
        # TODO(Piggy): the AutonGaussianMixtureModelsNeighbor this returns represents a gradient
        #       rather than a neighbor's state.
        #       Perhaps use a type alias to make that explicit?
        norm2_, grad_state = self.grad_inner_product(self)
        return norm2_, self.__class__(
            K=self._K,
            mix=2 * grad_state.mix,
            means=2 * grad_state.means,
            cov_tril=2 * grad_state.cov_tril,
            full=self._full_covariance)

    def grad_inner_product(self, other: 'AutonGaussianMixtureModelsNeighbor') -> Tuple[
            np.float64, 'AutonGaussianMixtureModelsNeighbor']:
        '''Compute the inner product of two Gaussian Mixture Models.'''
        K, d = self.means.shape  # pylint: disable=invalid-name
        inner_product_ = np.float64(0.0)
        grad_mix = np.zeros(K)
        grad_means = np.zeros((K, d))
        grad_cov_tril = np.zeros(self._cov_tril.shape)
        cov = self._cov_tril
        for j in range(K):
            if cov.ndim == 2:  # diagonal covariances
                cov = self._cov_tril + other.cov_tril[j][None, :]
            else:
                cov = np.stack([
                    np.linalg.cholesky(self._cov_tril[i] @ self._cov_tril[i].T
                                       + other.cov_tril[j] @ other.cov_tril[j].T)
                    for i in range(K)],
                    0)
            lp_state = self.__class__(
                K=self._K,
                mix=self.mix,
                means=self.means,
                cov_tril=cov,
                full=self._full_covariance)
            lp_, grad_state = lp_state.grad_lp(other.means[j][None, :], self._cov_tril)
            p = np.exp(lp_)
            inner_product_ += other.mix[j] * p
            grad_mix += other.mix[j] * p * grad_state.mix
            grad_means += other.mix[j] * p * grad_state.means
            grad_cov_tril += other.mix[j] * p * grad_state.cov_tril
        return inner_product_, self.__class__(
            K=self._K,
            mix=grad_mix,
            means=grad_means,
            cov_tril=grad_cov_tril,
            full=self._full_covariance)

    def norm2_diff(self, other: 'AutonGaussianMixtureModelsNeighbor') -> np.float64:
        '''Compute numerical representation of distance between models
        (||f-g||^2)
        '''
        retval = self.norm2() + other.norm2() - 2.0 * self.inner_product(other)
        retval = round(retval, ndigits=5)  # Account for floating point error.
        assert retval >= 0.0, (
            'BUG: norm2_diff should never be negative.'
        )
        return retval

    def distance(self, other: 'AutonGaussianMixtureModelsNeighbor') -> float:
        return float(self.norm2_diff(other))

    def grad_norm2_diff(self, other: 'AutonGaussianMixtureModelsNeighbor'
                        ) -> Tuple[np.float64, 'AutonGaussianMixtureModelsNeighbor']:
        '''
        compute grad ||f-g||^2, w.r.t mixture f
        '''
        n2_f, grad_state_f = self.grad_norm2()
        n2_g = other.norm2()
        ip, grad_state_ip = self.grad_inner_product(other)
        n2_diff = n2_f + n2_g - 2.0 * ip
        grad_mix = grad_state_f.mix - 2.0 * grad_state_ip.mix
        grad_means = grad_state_f.means - 2.0 * grad_state_ip.means
        grad_cov_tril = grad_state_f.cov_tril - 2.0 * grad_state_ip.cov_tril
        return n2_diff, self.__class__(
            K=self._K,
            mix=grad_mix,
            means=grad_means,
            cov_tril=grad_cov_tril,
            full=self._full_covariance)

    def logdeterminants(self) -> np.ndarray:
        '''Compute the log determinants of the covariance matrices.'''
        if self._cov_tril.ndim == 2:  # diagonal covariances
            return np.log(self._cov_tril).sum(1)
        K = self._cov_tril.shape[0]  # pylint: disable=invalid-name
        return np.array([self._logdet2d(self._cov_tril[k]) for k in range(K)])

    def _logdet2d(self, cov_tril) -> np.float64:
        return 2 * np.log(np.diag(cov_tril)).sum()

    def inner_product(self, other: 'AutonGaussianMixtureModelsNeighbor') -> np.float64:
        '''Compute the inner product of two Gaussian Mixture Models.'''
        K, d = self._means.shape  # pylint: disable=invalid-name
        inner_product_ = np.float64(0.0)
        for i in range(K):
            for j in range(K):
                if self._cov_tril.ndim == 2:  # diagonal covariances
                    cov = self._cov_tril[i] + other.cov_tril[j]
                    z = (self._means[i] - other.means[j]) / np.sqrt(cov)
                    logdet = np.log(cov).sum()
                else:
                    L = (  # pylint: disable=invalid-name
                        np.linalg.cholesky(self._cov_tril[i] @ self._cov_tril[i].T
                                           + other.cov_tril[j] @ other.cov_tril[j].T)
                    )
                    z = solve_triangular(L, other.means[j] - self._means[i], lower=True)
                    logdet = self._logdet2d(L)
                inner_product_ += (self.mix[i] * other.mix[j]
                                   * np.exp(
                                       -0.5 * z @ z - 0.5 * logdet - d * 0.5 * np.log(2 * np.pi)))
        return inner_product_


class AutonGaussianMixtureModelsInstance(DistributedAlgorithmInstance):
    '''Implementation of Gaussian Mixture Models for distributed data.'''
    _neighbor_constructor = AutonGaussianMixtureModelsNeighbor

    _predict_state: Optional[AutonGaussianMixtureModelsNeighbor] = None

    _K: int  # pylint: disable=invalid-name
    _full_covariance: bool
    _random_state: np.random.RandomState  # pylint: disable=no-member,line-too-long

    def __init__(self,
                 parent: Algorithm,
                 distributed: DistributedConfig,
                 **kwargs):
        hyperparams = parent.hyperparams(**kwargs)
        _K = hyperparams.pop('K')  # pylint: disable=invalid-name
        _full_covariance = hyperparams.pop('full_covariance')
        _random_seed = hyperparams.pop('random_seed', None)
        self._random_state = np.random.RandomState(_random_seed)  # pylint: disable=no-member,line-too-long
        if _K is None:
            raise HyperparamError('K must be specified for Gaussian Mixture Models.')

        if not isinstance(distributed, DistributedConfig):
            raise HyperparamError(
                f'{self.__class__.__name__} distributed must be a DistributedConfig, instead found '
                f'{distributed} of type {type(distributed)}')

        self._K = _K  # pylint: disable=invalid-name
        self._full_covariance = _full_covariance
        self._random_seed = _random_seed
        self._last_dataset = None
        super().__init__(parent, distributed=distributed, **hyperparams)

    @property
    def _neighbor_models_iter(self) -> Iterator[AutonGaussianMixtureModelsNeighbor]:
        for v in super()._neighbor_models_iter:
            assert isinstance(v, AutonGaussianMixtureModelsNeighbor), (
                'BUG: expected neighbor_models to contain AutonGaussianMixtureModelsNeighbor, '
                f'instead found {v} of type {type(v)}'
            )
            yield v

    @property  # type: ignore[override]
    def _my_state(self) -> Optional[AutonGaussianMixtureModelsNeighbor]:
        retval = DistributedAlgorithmInstance._my_state.fget(self)  # type: ignore[attr-defined] # pylint: disable=assignment-from-no-return, line-too-long
        assert retval is None or isinstance(retval, AutonGaussianMixtureModelsNeighbor), (
            'BUG: expected _my_state to be None or an AutonGaussianMixtureModelsNeighbor.')
        return retval

    @_my_state.setter
    def _my_state(self, value: Optional[AutonGaussianMixtureModelsNeighbor]) -> None:
        assert value is None or isinstance(value, AutonGaussianMixtureModelsNeighbor), (
            'BUG: expected value to be None or an AutonGaussianMixtureModelsNeighbor.')
        DistributedAlgorithmInstance._my_state.fset(self, value)  # type: ignore[attr-defined]

    def _decode(self, serialized_model: bytes) -> NeighborState:
        '''Decode a message from distributed neighbors. '''
        return AutonGaussianMixtureModelsNeighbor.decode(serialized_model)

    def _fit(self, dataset: Optional[Dataset], **kwargs) -> None:
        '''Fit the model to the data. This is the actual implementation of fit.'''
        # TODO(Piggy): This function is too long. Refactor it.
        # pylint: disable=too-many-locals, too-many-statements
        _omega = self._omega
        if dataset is None:
            if not self._neighbor_metadata:
                # No data or neighbor models; cannot fit
                return
            logger.debug('No data provided to fit.')
            # No data so we only synthesize neighbor models
            # Set omega to 1 (no self-regularization)
            _omega = np.float64(1.0)
            # Create blank data with 0 rows and a number of columns matching neighbors
            neighbor_models = self._neighbor_models_iter
            ncol: int = next(neighbor_models).nfeatures
            if any(model.nfeatures != ncol for model in neighbor_models):
                raise NotImplementedError(
                    'Neighbor models disagree about number of columns '
                    'and reconciling cols is not implemented.')
            data = np.zeros(shape=(0, ncol))
        else:
            data = dataset.dataframe_table.as_(np.ndarray)
        d = data.shape[1]
        K = self._K  # pylint: disable=invalid-name
        # initial setup
        last_fit = None
        if self._my_state is None:  # first fit
            if dataset is None:
                # Just pick the state of some neighbor.
                self._my_state = next(self._neighbor_models_iter).copy()
            else:
                means = (self._random_state.rand(K, d)
                         * (data.max(0) - data.min(0) + 1e-6)[None, :]
                         + data.min(0) if data.shape[0] > 0 else self._random_state.rand(K, d)
                         - 0.5)
                mix = np.ones(K) / K
                if self._full_covariance:
                    cov_tril = np.zeros((K, d, d)) + np.eye(d)[None, :, :]
                else:
                    cov_tril = np.ones((K, d))
                self._my_state = AutonGaussianMixtureModelsNeighbor(
                    K=K, mix=mix, means=means, cov_tril=cov_tril, full=self._full_covariance,
                    columns=self._columns)
        else:
            last_fit = self._my_state.copy()
        x0 = self._my_state.flatten()

        def fun(x: np.ndarray) -> Tuple[np.float64, np.ndarray]:
            '''Objective function for the fit procedure.'''
            state = AutonGaussianMixtureModelsNeighbor.unflatten(
                x=x, K=K, d=d, full=self._full_covariance)
            jac_mix = state.jac_mix()
            state.divide_mix_by_sum()
            # local data
            lp_, grad_state = state.grad_lp(data)
            jac_grad_state = state.__class__(
                mix=jac_mix @ grad_state.mix,
                means=grad_state.means,
                cov_tril=grad_state.cov_tril,
                full=self._full_covariance)
            grad = jac_grad_state.flatten()

            if last_fit is None:
                return -lp_, -grad
            assert self._my_state is not None, (
                'BUG: model state must be set in fit.'
            )
            state = self._my_state
            # regularization
            reg = np.float64(0.0)
            reg_grad = np.zeros(x.size)
            # self regularization
            nrm2, grad_state = state.grad_norm2_diff(last_fit)
            reg += (1.0 - _omega) / _omega * nrm2
            jac_grad_state = state.__class__(
                mix=jac_mix @ grad_state.mix,
                means=grad_state.means,
                cov_tril=grad_state.cov_tril,
                full=self._full_covariance)
            reg_grad += (1.0 - _omega) / _omega * jac_grad_state.flatten()
            # neighbor regularization
            num_neighbors = len(self._neighbor_metadata)
            for model in self._neighbor_models_iter:
                nrm2, grad_state = state.grad_norm2_diff(model)
                reg += 1.0 / num_neighbors * nrm2
                jac_grad_state = state.__class__(
                    mix=jac_mix @ grad_state.mix,
                    means=grad_state.means,
                    cov_tril=grad_state.cov_tril,
                    full=self._full_covariance)
                reg_grad += (1.0 - _omega) / _omega * jac_grad_state.flatten()
            #
            return np.float64(-lp_ + self._lambda * reg), -grad + self._lambda * reg_grad

        lb = (-np.inf) * np.ones(x0.size)
        ub = (np.inf) * np.ones(x0.size)
        lb[:K] = 1e-6
        ub[:K] = 1.0
        if not self._full_covariance:
            lb[(K + K * d):] = 1e-4
        else:
            ri, ci = np.tril_indices(d)
            # constrain diagonal of cov_tril to be positive
            lb[(K + K * d) + np.where(np.tile(ri == ci, K))[0]] = 1e-2
        bnds = Bounds(lb=lb, ub=ub, keep_feasible=True)
        soln = minimize(fun, x0, method='L-BFGS-B', jac=True, bounds=bnds)
        new_state = self._my_state.__class__.unflatten(
            soln.x, K, d, self._full_covariance)
        new_state.columns = self._columns
        self._my_state = new_state
        self._my_state.divide_mix_by_sum()

    def _predict(self, dataset: Optional[Dataset], **kwargs) -> Optional[Dataset]:
        '''Predict the labels of the data. This is the actual implementation of predict.'''
        if dataset is None:
            return None
        return self.log_pdf(dataset)

    def log_pdf(self, dataset: Dataset) -> Dataset:
        '''Compute the log likelihood of the data under the model.'''
        if self._predict_state is None:
            raise ValueError('Model must be trained before computing log likelihood.')
        data = dataset.dataframe_table.as_(np.ndarray)
        retval = dataset.output()
        retval.dataframe_table = TableFactory(self._predict_state.log_pdf(data))
        return retval

    def mean_log_pdf(self, dataset: Dataset) -> np.float64:
        '''Compute the log likelihood of the data under the model.'''
        if self._predict_state is None:
            raise ValueError('Model must be trained before computing log likelihood.')
        data = dataset.dataframe_table.as_(np.ndarray)
        return self._predict_state.log_pdf(data).mean()

    def score(self, dataset: Dataset) -> np.float64:
        '''Compute the log likelihood of the data under the model.

        Name provided for compatability with sklearn.
        '''
        return self.mean_log_pdf(dataset)

    def sample(self,
               n: int,
               random_state: Optional[np.random.RandomState] = None) -> Dataset:  # pylint: disable=no-member,line-too-long
        '''Sample from the model.

        Args:
            n: The number of samples to generate.
        Returns:
            A sample of size n from the distributed computed in fit().
            A numpy array of shape (n, d) where d is the dimension of the data.
        '''
        # TODO(Piggy): lock sample()
        if not self.trained:
            raise ValueError('Model must be trained before sampling.')
        state = self._my_state
        assert state is not None, (
            'BUG: model state must be set in fit.'
        )

        random_state = random_state or np.random.RandomState(1)  # pylint: disable=no-member,line-too-long
        print("DEBUG: sum(state.mix)", sum(state.mix))
        assert isclose(sum(state.mix), 1, abs_tol=1e-5), (
            'BUG: mixture coefficients must sum to 1.'
        )
        choices = random_state.choice(len(state.mix), size=n, p=state.mix)
        if self._full_covariance:
            data = np.array(
                [random_state.multivariate_normal(state.means[k],
                                                  state.cov_tril[k] @ state.cov_tril[k].T)
                 for k in choices])
        else:
            data = np.array(
                [random_state.multivariate_normal(state.means[k], np.diag(state.cov_tril[k]))
                 for k in choices])

        retval = Dataset(
            metadata=Metadata(),
        )
        retval.dataframe_table = TableFactory(data)
        return retval

    def norm2_diff(self, other: 'AutonGaussianMixtureModelsInstance') -> np.float64:
        '''Compute the squared norm of the difference between two models.'''
        if self._predict_state is None or other.my_state is None:
            raise ValueError('Model must be trained before computing norm2_diff.')
        return self._predict_state.norm2_diff(other.my_state)

    @property
    def my_state(self) -> Optional[AutonGaussianMixtureModelsNeighbor]:
        '''Get the state of the model.

        Needed for type reconciliation.
        '''
        retval = super().my_state
        assert isinstance(retval, AutonGaussianMixtureModelsNeighbor)
        return retval

    @property
    def my_state_copy(self) -> Optional[AutonGaussianMixtureModelsNeighbor]:
        '''Safely get a copy the state of the model.

        Needed for type reconciliation.
        '''
        retval = super().my_state_copy
        assert isinstance(retval, AutonGaussianMixtureModelsNeighbor)
        return retval


class AutonGaussianMixtureModels(Algorithm):
    '''Implementation of Gaussian Mixture Models for distributed data.'''
    _name = 'auton_gaussian_mixture_models'
    _instance_constructor = AutonGaussianMixtureModelsInstance
    _tags: Dict[str, List[str]] = {
        'task': [TaskType.DENSITY_ESTIMATION.name],
        'data_type': [DataType.TABULAR.name],
        'source': ['autonlab'],
        'distributed': ['true'],
        'supports_random_seed': ['true'],
    }
    _default_hyperparams = {
        'K': None,
        'full_covariance': True,
        'Lambda': 10.0,
        'omega': 2.0 / 3.0,
        'random_seed': Defaults.SEED,
        'tol': 0.000000001,
        'maxiter': None,
    }


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = AutonGaussianMixtureModels(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
