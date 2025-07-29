# flake8: noqa
# type: ignore
# pylint: skip-file

# ngautonml's Gaussian mixture implementation is adapted from this code made by Kyle Miller
# We are keeping it here for now to compare and make sure we adapted it right.
# There is a test that compares the ngautonml implementation against this code.

if __name__=="__main__":
    from DistAIModel import DistAIModel
else:
    from .DistAIModel import DistAIModel
import pickle
from typing import Any

import numpy as np
from scipy.linalg import solve_triangular
from scipy.special import logsumexp

from scipy.optimize import minimize, LinearConstraint, Bounds

def _logdet2d(cov_tril):
    return 2*np.log(np.diag(cov_tril)).sum()

def logdeterminants(cov_tril):
    if cov_tril.ndim==2: # diagonal covariances
        return np.log(cov_tril).sum(1)
    K = cov_tril.shape[0]
    return np.array([_logdet2d(cov_tril[k]) for k in range(K)])

def log_likelihoods(X,means,cov_tril):
    '''
    compute the log likelihood of observations X under each component of a GMM
    '''
    n,d = X.shape
    K = means.shape[0]
    Xmeaned = X[:,None,:]-means[None,:,:] # (n,.,d),(.,K,d)->(n,K,d)
    logdets = logdeterminants(cov_tril)
    if cov_tril.ndim==2: # diagonal covariances
        logprob = -0.5*np.einsum('kd,nkd->nk',1./cov_tril,Xmeaned**2) -0.5*logdets[None,:] -d*0.5*np.log(2*np.pi)
    else:
        z = np.stack([solve_triangular(cov_tril[k], Xmeaned[:,k,:].T, lower=True) for k in range(K)],2) # shape (d,n,K)
        logprob = -0.5*(z**2).sum(0) -0.5*logdets[None,:] -d*0.5*np.log(2*np.pi)
    return logprob # shape=(n,K)

def lp(X,mix,means,cov_tril):
    '''
    compute the log likelihood of observations X under a GMM
    '''
    logprob = log_likelihoods(X,means,cov_tril) # shape=(n,K)
    return np.apply_along_axis(logsumexp,1,logprob + np.log(mix)[None,:]).sum() # scalar

def grad_lp(X,mix,means,cov_tril,wrt_cov=None):
    '''
    compute the log likelihood of observations X under a GMM and gradients
      compute grad of cov_tril with respect to wrt_cov (i.e. sigma = L@L.T+M@M.T, and want gradient with respect to L)
         only needed for full covariances
    '''
    n,d = X.shape
    K = means.shape[0]
    Xmeaned = X[:,None,:]-means[None,:,:] # (n,.,d),(.,K,d)->(n,K,d)
    logdets = logdeterminants(cov_tril)
    if cov_tril.ndim==2: # diagonal covariances
        logprob = -0.5*np.einsum('kd,nkd->nk',1./cov_tril,Xmeaned**2) -0.5*logdets[None,:] -d*0.5*np.log(2*np.pi) # shape = (n,K)
        grad_means = Xmeaned/cov_tril[None,:,:] # shape = (n,K,d)
        grad_cov_tril = 0.5*(Xmeaned**2-cov_tril[None,:,:])/cov_tril[None,:,:]**2 # shape = (n,K,d)
    else:
        z = np.stack([solve_triangular(cov_tril[k], Xmeaned[:,k,:].T, lower=True) for k in range(K)],2) # shape (d,n,K)
        logprob = -0.5*(z**2).sum(0) -0.5*logdets[None,:] -d*0.5*np.log(2*np.pi) # shape (n,k)
        grad_means = np.stack([solve_triangular(cov_tril[k].T, z[:,:,k], lower=False) for k in range(K)],1).T # shape (n,K,d)
        grad_cov_tril = np.stack([np.einsum('ni,nj->nij',z[:,:,k].T,z[:,:,k].T) - np.eye(d)[None,:,:] for k in range(K)],1) # shape (n,K,d,d)
    #
    weights = logprob + np.log(mix)[None,:] # shape = (n,k)
    mx = weights.max(1)
    weights = np.exp( weights - mx[:,None] )
    wtot = weights.sum(1)
    wtotinv = 1./wtot
    #
    lp_ = np.log(wtot).sum()+mx.sum() # row-wise logsumexp -> scalar
    #
    grad_mix = np.einsum('nk,k,n->k',weights,1./mix,wtotinv) # shape = (k,)
    #
    grad_means = np.einsum('nk,nki,n->ki',weights,grad_means,wtotinv) # shape = (k,d)
    #
    if cov_tril.ndim==2: # diagonal covariances
        grad_cov_tril = np.einsum('nk,nki,n->ki',weights,grad_cov_tril,wtotinv)
    else:
        grad_cov_tril = np.einsum('nk,nkij,n->kij',weights,grad_cov_tril,wtotinv)
        if wrt_cov is not None:
            grad_cov_tril = np.stack([solve_triangular(cov_tril[k].T,grad_cov_tril[k]@solve_triangular(cov_tril[k],wrt_cov[k],lower=True),lower=False) for k in range(K)],0)
        else:
            grad_cov_tril = np.stack([solve_triangular(cov_tril[k].T,grad_cov_tril[k],lower=False) for k in range(K)],0)
        ri, ci = np.triu_indices(d,k=1)
        for k in range(K): grad_cov_tril[k,ri,ci] = 0
    #
    return lp_,grad_mix,grad_means,grad_cov_tril

def norm2(mix,means,cov_tril):
    return inner_product(mix,means,cov_tril,mix,means,cov_tril)

def grad_norm2(mix,means,cov_tril):
    norm2_, grad_mix, grad_means, grad_cov_tril = grad_inner_product(mix,means,cov_tril,mix,means,cov_tril)
    return norm2_, 2*grad_mix, 2*grad_means, 2*grad_cov_tril

def inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril):
    K,d = means.shape
    inner_product_ = 0.
    for i in range(K):
        for j in range(K):
            if cov_tril.ndim==2: # diagonal covariances
                cov = cov_tril[i]+other_cov_tril[j]
                z = (means[i]-other_means[j])/np.sqrt(cov)
                logdet = np.log(cov).sum()
            else:
                L = np.linalg.cholesky(cov_tril[i]@cov_tril[i].T+other_cov_tril[j]@other_cov_tril[j].T)
                z = solve_triangular(L,other_means[j]-means[i],lower=True)
                logdet = _logdet2d(L)
            inner_product_ += mix[i]*other_mix[j]*np.exp( -0.5*z@z -0.5*logdet -d*0.5*np.log(2*np.pi) )
    return inner_product_

def grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril):
    K,d = means.shape
    inner_product_ = 0.
    grad_mix = np.zeros(K)
    grad_means = np.zeros((K,d))
    grad_cov_tril = np.zeros(cov_tril.shape)
    for j in range(K):
        if cov_tril.ndim==2: # diagonal covariances
            cov = cov_tril+other_cov_tril[j][None,:]
        else:
            cov = np.stack([np.linalg.cholesky(cov_tril[i]@cov_tril[i].T+other_cov_tril[j]@other_cov_tril[j].T) for i in range(K)],0)
        lp_, grad_mix_, grad_means_, grad_cov_tril_ = grad_lp(other_means[j][None,:],mix,means,cov,cov_tril)
        p = np.exp(lp_)
        inner_product_ += other_mix[j]*p
        grad_mix += other_mix[j]*p*grad_mix_
        grad_means += other_mix[j]*p*grad_means_
        grad_cov_tril += other_mix[j]*p*grad_cov_tril_
    return inner_product_, grad_mix, grad_means, grad_cov_tril

#################################################################
#################################################################
# Gaussian mixture model

class GMM(DistAIModel):

    def __init__(self, config):
        super(GMM, self).__init__()
        if config is None: return
        self.K = int( config['K'] )
        self.full_covariance = config['covariance'].lower()=='full'
        self.Lambda = float( config['lambda'] )
        self.omega = float( config['omega'] )
        self.fit_time = None
        self.ID = None
        self.mix = None
        self.means = None
        self.cov_tril = None
        self.random_state = np.random.RandomState(1701)

    def serialize(self): # returns serialized model
        # care should be taken to make message size as small as possible. self.ID is required.
        # the deserialized model must be able to run norm2, inner_product, and metrics. It need not run fit.
        if self.full_covariance:
            d = self.means.shape[1]
            cov = np.stack([self.cov_tril[k][np.tril_indices(d)] for k in range(self.K)],0)
        else:
            cov = self.cov_tril
        return pickle.dumps((self.ID,self.mix,self.means,cov))

    @staticmethod
    def deserialize(serialized_model): # returns model instance
        # care should be taken to make message size as small as possible. self.ID is required.
        # the deserialized model must be able to run norm2, inner_product, and metrics. It need not run fit.
        obj = pickle.loads(serialized_model)
        m = GMM(None)
        m.ID = obj[0]
        m.mix = obj[1]
        m.means = obj[2]
        K,d = m.means.shape
        m.K = K
        cov = obj[3]
        if cov.shape[1] > m.means.shape[1]:
            m.full_covariance = True
            m.cov_tril = np.zeros((K,d,d))
            for k in range(K):
                m.cov_tril[k][np.tril_indices(d)] = cov[k]
        else:
            m.full_covariance = False
            m.cov_tril = cov
        return m

    def sample(self,n):
        # sample
        pass

    def lp(self,X): # log_probability of X. X shape=(n,d)
        '''
        Log-likelihood of the data
        '''
        return lp(X,self.mix,self.means,self.cov_tril) #scalar

    def idx(self,X): # log_probability of X. X shape=(n,d)
        '''
        Maximum likelihood component index for each observation
        '''
        ll = log_likelihoods(X,self.means,self.cov_tril) # shape = (n,K)
        return np.argmax( ll+np.log(self.mix)[None,:], 1)

    def p(self,X):
        '''
        likelihood of data
        '''
        return np.exp(self.lp(X)) #scalar

    @staticmethod
    def flatten(mix,means,cov_tril):
        if cov_tril.ndim==2:
            return np.concatenate((mix,means.flatten(),cov_tril.flatten()))
        K,d = means.shape
        idx = np.tril_indices(d)
        return np.concatenate([mix,means.flatten()]+[cov_tril[k][idx] for k in range(K)])

    @staticmethod
    def unflatten(x,K,d,full):
        if not full:
            return x[:K], x[K:(K+K*d)].reshape((K,d)), x[(K+K*d):].reshape((K,d))
        cov = x[(K+K*d):]
        cov_tril = np.zeros((K,d,d))
        s = (d*(d+1))//2
        idx = np.tril_indices(d)
        for k in range(K):
            cov_tril[k][idx] = cov[(k*s):((k+1)*s)]
        return x[:K], x[K:(K+K*d)].reshape((K,d)), cov_tril

    def fit(self, data, neighbor_models): # returns nothing, fits model to data and other models
        d = data.shape[1]
        K = self.K
        # initial setup
        last_fit = None
        Nneighbors = len(neighbor_models)
        if self.means is None: # first fit
            self.means = self.random_state.rand(K,d)*(data.max(0)-data.min(0)+1e-6)[None,:] + data.min(0) if data.shape[0]>0 else self.random_state.rand(K,d)-0.5
            self.mix = np.ones(K)/K
            if self.full_covariance:
                self.cov_tril = np.zeros((K,d,d)) + np.eye(d)[None,:,:]
            else:
                self.cov_tril = np.ones((K,d))
        else:
            last_fit = GMM.deserialize( self.serialize() )
        # objective
        x0 = GMM.flatten(self.mix,self.means,self.cov_tril)
        def fun(x):
            mix, means, cov_tril = GMM.unflatten(x,K,d,self.full_covariance)
            JacMix = np.eye(mix.size)/mix.sum()-mix[None,:]/mix.sum()**2
            mix = mix/mix.sum()
            # local data
            lp_, grad_mix, grad_means, grad_cov_tril = grad_lp(data,mix,means,cov_tril)
            grad = GMM.flatten(JacMix@grad_mix,grad_means,grad_cov_tril)
            if last_fit is None:
                return -lp_, -grad
            # regularization
            reg = 0
            reg_grad = np.zeros(x.size)
            nrm2, grad_mix, grad_means, grad_cov_tril = grad_norm2(mix,means,cov_tril)
            reg += 1./self.omega*nrm2
            reg_grad += 1./self.omega*GMM.flatten(JacMix@grad_mix,grad_means,grad_cov_tril)
            ip, grad_mix, grad_means, grad_cov_tril = grad_inner_product(mix,means,cov_tril,last_fit.mix,last_fit.means,last_fit.cov_tril)
            reg += 2.*(1.-1./self.omega)*ip
            reg_grad += 2.*(1.-1./self.omega)*GMM.flatten(JacMix@grad_mix,grad_means,grad_cov_tril)
            for n in range(Nneighbors):
                ip, grad_mix, grad_means, grad_cov_tril = grad_inner_product(mix,means,cov_tril,neighbor_models[n].mix,neighbor_models[n].means,neighbor_models[n].cov_tril)
                reg += -2./Nneighbors*ip
                reg_grad += -2./Nneighbors*GMM.flatten(JacMix@grad_mix,grad_means,grad_cov_tril)
            #
            return -lp_+self.Lambda*reg, -grad+self.Lambda*reg_grad
        lb = (-np.inf)*np.ones(x0.size)
        ub = (np.inf)*np.ones(x0.size)
        lb[:K] = 1e-6
        ub[:K] = 1.
        if not self.full_covariance:
            lb[(K+K*d):] = 1e-4
        else:
            ri,ci=np.tril_indices(d)
            lb[(K+K*d)+np.where(np.tile(ri==ci,K))[0]] = 1e-2 # constrain diagonal of cov_tril to be positive
        bnds = Bounds(lb=lb,ub=ub,keep_feasible=True)
        soln = minimize(fun, x0, method='L-BFGS-B', jac=True, bounds=bnds)
        self.mix, self.means, self.cov_tril = GMM.unflatten(soln.x,K,d,self.full_covariance)
        self.mix = self.mix/self.mix.sum()

    def norm2(self): # returns scalar
        return norm2(self.mix,self.means,self.cov_tril)

    def inner_product(self,other): # returns scalar
        return inner_product(self.mix,self.means,self.cov_tril,other.mix,other.means,other.cov_tril)

    def metrics(self,data): # returns a dictionary with string keys recording any sort of metrics Dict[str, Any]
        return {'LogProb':self.lp(data)/data.shape[0]} # mean log probability

#################################################################
#################################################################

if __name__=="__main__":
    '''
    Do gradient checks:
    NOTE:  d/dA f(Ainv) = -Ainv.T @ df/dAinv @ Ainv.T

    dlogrpob( x | mu, sigma )/dmu = inv(sigma)(x-mu)

    dlogprob( x | mu, sigma )/dsigma_inv = -0.5(x-mu)(x-mu).T + 0.5*sigma
    dlogprob( x | mu, sigma )/dsigma = -inv(sigma).T@(-0.5(x-mu)(x-mu).T + 0.5*sigma)@inv(sigma).T
    dlogprob( x | mu, L@L.T + M@M.T )/dL = 2*(-inv(sigma).T@(-0.5(x-mu)(x-mu).T + 0.5*sigma)@inv(sigma).T)@L
                                         = inv(R.T)@( (inv(R)(x-mu))(inv(R)(x-mu)).T - I )@inv(R)@L   where R=cholesky(sigma)
    '''
    seed = 0
    np.random.seed(seed)
    full_cov = False
    eps = 1e-4
    n,d,K = 10,2,3
    X = np.random.random((n,d))
    #
    if not full_cov:
        cov_tril = np.random.random((K,d))
    else:
        cov_tril = np.random.random((K,d,d))
        for k in range(K): cov_tril[k] = np.linalg.cholesky( cov_tril[k]@cov_tril[k].T )
    #
    means = np.random.random((K,d))
    mix = np.random.random(K)
    mix = mix/mix.sum()
    def chk(X,mix,means,cov_tril):
        return grad_lp(X,mix,means,cov_tril)[0]
    #
    print("lp")
    print(lp(X,mix,means,cov_tril),grad_lp(X,mix,means,cov_tril)[0])
    #grad check mix
    print("mix lp")
    grad = np.zeros(K)
    for i in range(K):
        mix_p = mix.copy()
        mix_p[i] += eps
        mix_m = mix.copy()
        mix_m[i] -= eps
        grad[i] = (chk(X,mix_p,means,cov_tril)-chk(X,mix_m,means,cov_tril))/(2*eps)
    print( np.abs(grad-grad_lp(X,mix,means,cov_tril)[1]).max(), np.abs((grad-grad_lp(X,mix,means,cov_tril)[1])/grad).max() )
    #
    #grad check means
    print("mean lp")
    grad = np.zeros((K,d))
    for i in range(K):
        for j in range(d):
            means_p = means.copy()
            means_p[i,j] += eps
            means_m = means.copy()
            means_m[i,j] -= eps
            grad[i,j] = (chk(X,mix,means_p,cov_tril)-chk(X,mix,means_m,cov_tril))/(2*eps)
    print( np.abs(grad-grad_lp(X,mix,means,cov_tril)[2]).max(), np.abs((grad-grad_lp(X,mix,means,cov_tril)[2])/grad).max() )
    #
    #grad check cov
    print("cov lp")
    grad = np.zeros(cov_tril.shape)
    for k in range(K):
        for i in range(d):
            if not full_cov:
                cov_tril_p = cov_tril.copy()
                cov_tril_p[k,i] += eps
                cov_tril_m = cov_tril.copy()
                cov_tril_m[k,i] -= eps
                grad[k,i] = (chk(X,mix,means,cov_tril_p)-chk(X,mix,means,cov_tril_m))/(2*eps)
            else:
                for j in range(i+1):
                    cov_tril_p = cov_tril.copy()
                    cov_tril_p[k,i,j] += eps
                    cov_tril_m = cov_tril.copy()
                    cov_tril_m[k,i,j] -= eps
                    grad[k,i,j] = (chk(X,mix,means,cov_tril_p)-chk(X,mix,means,cov_tril_m))/(2*eps)
    print( np.abs(grad-grad_lp(X,mix,means,cov_tril)[3]).max(), np.abs((grad-grad_lp(X,mix,means,cov_tril)[3])/(grad+1e-60)).max() )
    #######
    def chk(mix,means,cov_tril):
        return grad_norm2(mix,means,cov_tril)[0]
    #
    print("norm2")
    print(norm2(mix,means,cov_tril),grad_norm2(mix,means,cov_tril)[0])
    #grad check mix
    print("mix norm2")
    grad = np.zeros(K)
    for i in range(K):
        mix_p = mix.copy()
        mix_p[i] += eps
        mix_m = mix.copy()
        mix_m[i] -= eps
        grad[i] = (chk(mix_p,means,cov_tril)-chk(mix_m,means,cov_tril))/(2*eps)
    print( np.abs(grad-grad_norm2(mix,means,cov_tril)[1]).max(), np.abs((grad-grad_norm2(mix,means,cov_tril)[1])/grad).max() )
    #
    #grad check means
    print("mean norm2")
    grad = np.zeros((K,d))
    for i in range(K):
        for j in range(d):
            means_p = means.copy()
            means_p[i,j] += eps
            means_m = means.copy()
            means_m[i,j] -= eps
            grad[i,j] = (chk(mix,means_p,cov_tril)-chk(mix,means_m,cov_tril))/(2*eps)
    print( np.abs(grad-grad_norm2(mix,means,cov_tril)[2]).max(), np.abs((grad-grad_norm2(mix,means,cov_tril)[2])/grad).max() )
    #
    #grad check cov
    print("cov norm2")
    grad = np.zeros(cov_tril.shape)
    for k in range(K):
        for i in range(d):
            if not full_cov:
                cov_tril_p = cov_tril.copy()
                cov_tril_p[k,i] += eps
                cov_tril_m = cov_tril.copy()
                cov_tril_m[k,i] -= eps
                grad[k,i] = (chk(mix,means,cov_tril_p)-chk(mix,means,cov_tril_m))/(2*eps)
            else:
                for j in range(i+1):
                    cov_tril_p = cov_tril.copy()
                    cov_tril_p[k,i,j] += eps
                    cov_tril_m = cov_tril.copy()
                    cov_tril_m[k,i,j] -= eps
                    grad[k,i,j] = (chk(mix,means,cov_tril_p)-chk(mix,means,cov_tril_m))/(2*eps)
    print( np.abs(grad-grad_norm2(mix,means,cov_tril)[3]).max(), np.abs((grad-grad_norm2(mix,means,cov_tril)[3])/(grad+1e-60)).max() )
    #######
    def chk(mix,means,cov_tril):
        return grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[0]
    #
    print("inner product")
    if not full_cov:
        other_cov_tril = np.random.random((K,d))
    else:
        other_cov_tril = np.random.random((K,d,d))
        for k in range(K): other_cov_tril[k] = np.linalg.cholesky( other_cov_tril[k]@other_cov_tril[k].T )
    #
    other_means = np.random.random((K,d))
    other_mix = np.random.random(K)
    other_mix = other_mix/other_mix.sum()
    print(inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril),grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[0])
    #grad check mix
    print("mix inner product")
    grad = np.zeros(K)
    for i in range(K):
        mix_p = mix.copy()
        mix_p[i] += eps
        mix_m = mix.copy()
        mix_m[i] -= eps
        grad[i] = (chk(mix_p,means,cov_tril)-chk(mix_m,means,cov_tril))/(2*eps)
    print( np.abs(grad-grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[1]).max(), np.abs((grad-grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[1])/grad).max() )
    #
    #grad check means
    print("mean inner product")
    grad = np.zeros((K,d))
    for i in range(K):
        for j in range(d):
            means_p = means.copy()
            means_p[i,j] += eps
            means_m = means.copy()
            means_m[i,j] -= eps
            grad[i,j] = (chk(mix,means_p,cov_tril)-chk(mix,means_m,cov_tril))/(2*eps)
    print( np.abs(grad-grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[2]).max(), np.abs((grad-grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[2])/grad).max() )
    #
    #grad check cov
    print("cov inner product")
    grad = np.zeros(cov_tril.shape)
    for k in range(K):
        for i in range(d):
            if not full_cov:
                cov_tril_p = cov_tril.copy()
                cov_tril_p[k,i] += eps
                cov_tril_m = cov_tril.copy()
                cov_tril_m[k,i] -= eps
                grad[k,i] = (chk(mix,means,cov_tril_p)-chk(mix,means,cov_tril_m))/(2*eps)
            else:
                for j in range(i+1):
                    cov_tril_p = cov_tril.copy()
                    cov_tril_p[k,i,j] += eps
                    cov_tril_m = cov_tril.copy()
                    cov_tril_m[k,i,j] -= eps
                    grad[k,i,j] = (chk(mix,means,cov_tril_p)-chk(mix,means,cov_tril_m))/(2*eps)
    print( np.abs(grad-grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[3]).max(), np.abs((grad-grad_inner_product(mix,means,cov_tril,other_mix,other_means,other_cov_tril)[3])/(grad+1e-60)).max() )

    #####################################
    import matplotlib.pyplot as plt

    # test GMM
    n = [50,25,40]
    mu = [[-1,0],[0.2,-0.2],[0,0.5]]
    cov = [[[0.025,0],[0,0.025]],[[0.025,0.0125],[0.0125,0.025]],[[0.05,-0.01],[-0.01,0.05]]]
    rng = np.random.default_rng(seed=seed)
    X = []
    for i in range(len(n)):
        X.append( rng.multivariate_normal(mu[i],cov[i],n[i]) )

    X = np.concatenate(X)
    plt.scatter(X[:,0],X[:,1])
    plt.show()

    config = {'K':3,'covariance':'full','lambda':1.,'omega':0.667}

    model = GMM(config)

    model.fit(X,[])
    idx = model.idx(X)
    for i in range(config['K']):
        plt.scatter(X[idx==i,0],X[idx==i,1])
        plt.scatter(model.means[i,0],model.means[i,1],marker='^')
    plt.show()
    print(model.means)
    print(model.cov_tril)
    print(model.mix)

    model.fit(X,[])
    idx = model.idx(X)
    for i in range(config['K']):
        plt.scatter(X[idx==i,0],X[idx==i,1])
        plt.scatter(model.means[i,0],model.means[i,1],marker='^')
    plt.show()
    print(model.means)
    print(model.cov_tril)
    print(model.mix)

def register(catalog: Any, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''