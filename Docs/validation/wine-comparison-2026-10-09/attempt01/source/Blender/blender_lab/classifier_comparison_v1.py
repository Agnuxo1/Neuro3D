"""Training-only convex baselines and explicit represented-field capacity."""
import math
import time
import numpy as np
from Tools.audit_captured_pilot_result_v1 import need


def encode_real_features(raw, train_indices, source_ids):
    raw=np.asarray(raw,dtype=np.float64)
    need(raw.ndim==2 and raw.shape[1]==4 and np.isfinite(raw).all(),'four finite features required')
    need(len(source_ids)==5 and set(source_ids)=={'r0','r1','c0','c1','c2'},'declared five coherent sources required')
    train=np.asarray(train_indices,dtype=int)
    need(len(train)>0 and len(set(train))==len(train) and np.all((train>=0)&(train<len(raw))),'valid unique training rows required')
    low,high=raw[train].min(axis=0),raw[train].max(axis=0)
    need(np.all(high>low),'positive training feature ranges required')
    scaled=(raw-low)/(high-low)
    x=np.zeros((len(raw),5),dtype=np.float64)
    for j,sid in enumerate(('r0','r1','c0','c1')):x[:,source_ids.index(sid)]=scaled[:,j]
    x[:,source_ids.index('c2')]=1
    x/=np.sqrt(np.sum(x*x,axis=1,keepdims=True))
    return x,{'fit_rows':train.tolist(),'lo':low.tolist(),'hi':high.tolist(),'test_clipping':False,'reference_amplitude':1,'encoding':'REAL_COMMON_COHERENCE_UNIT_INPUT_POWER'}


def design_matrix(x, kind):
    x=np.asarray(x,dtype=np.float64)
    need(x.ndim==2 and x.shape[1]==5 and np.isfinite(x).all(),'complete real encoded input required')
    if kind=='linear':return x
    need(kind=='quadratic','known baseline kind required')
    return np.column_stack([x[:,i]*x[:,j] for i in range(5) for j in range(i,5)])


def softmax_objective(flat, z, y, regularization):
    weights=np.asarray(flat).reshape(3,z.shape[1]);scores=z@weights.T
    shifted=scores-scores.max(axis=1,keepdims=True);e=np.exp(shifted);prob=e/e.sum(axis=1,keepdims=True)
    loss=np.mean(np.log(e.sum(axis=1))-shifted[np.arange(len(y)),y])+.5*regularization*np.sum(weights*weights)
    diff=prob.copy();diff[np.arange(len(y)),y]-=1
    gradient=diff.T@z/len(y)+regularization*weights
    return float(loss),gradient.ravel()


def fit_baseline(x_train, y_train, kind, configuration):
    from scipy.optimize import minimize
    z=design_matrix(x_train,kind);y=np.asarray(y_train,dtype=np.int64)
    need(y.shape==(len(z),) and set(y)=={0,1,2},'three training classes required')
    t=time.perf_counter()
    result=minimize(softmax_objective,np.zeros(3*z.shape[1]),args=(z,y,configuration['l2']),jac=True,method='L-BFGS-B',
                    options={'maxiter':configuration['maxiter'],'gtol':configuration['gtol'],'ftol':configuration['ftol'],'maxls':50})
    duration=time.perf_counter()-t
    need(result.success and np.max(np.abs(result.jac))<=configuration['maximum_gradient_abs'],'convex baseline optimization failed convergence gate')
    return {'kind':kind,'weights':result.x.reshape(3,z.shape[1]).tolist(),'fit_seconds':duration,
            'objective':float(result.fun),'iterations':int(result.nit),'function_evaluations':int(result.nfev),
            'max_gradient_abs':float(np.max(np.abs(result.jac))),'success':bool(result.success),
            'nominal_parameters':3*z.shape[1],'logit_difference_parameters':2*z.shape[1],
            'scope':'Same coherent encoded real inputs; unconstrained learned logits, L2-regularized convex optimum; not a physically equivalent optical architecture'}


def baseline_scores(model,x):return design_matrix(x,model['kind'])@np.asarray(model['weights']).T


def wilson_interval(correct,count):
    need(isinstance(correct,int) and isinstance(count,int) and count>0 and 0<=correct<=count,'valid binomial counts required')
    z=1.959963984540054;p=correct/count;den=1+z*z/count
    center=(p+z*z/(2*count))/den;radius=z*math.sqrt(p*(1-p)/count+z*z/(4*count*count))/den
    return [center-radius,center+radius]


def classification_metrics(predictions,labels):
    p=np.asarray(predictions);y=np.asarray(labels)
    need(p.shape==y.shape and p.ndim==1 and np.all((p>=0)&(p<3)) and np.all((y>=0)&(y<3)),'valid three-class predictions/labels required')
    confusion=np.zeros((3,3),dtype=int)
    for a,b in zip(y,p):confusion[a,b]+=1
    correct=int(np.sum(p==y));count=len(y)
    return {'correct':correct,'count':count,'accuracy':correct/count,'confusion':confusion.tolist(),
            'wilson_95_interval':wilson_interval(correct,count),'interval_scope':'Descriptive binomial approximation; no IID guarantee, no pooled repeated-seed sample inflation'}


def paired_comparison(a,b,labels):
    a=np.asarray(a)==labels;b=np.asarray(b)==labels
    wins=int(np.sum(a&~b));losses=int(np.sum(~a&b));n=wins+losses
    p=min(1.,2*sum(math.comb(n,k) for k in range(min(wins,losses)+1))/2**n) if n else 1.
    return {'own_only_correct':wins,'baseline_only_correct':losses,'paired_accuracy_difference':float(np.mean(a)-np.mean(b)),
            'mcnemar_exact_two_sided_p':p,'scope':'Exploratory unadjusted paired comparison; repeated seeds share one heldout split; no superiority claim or multiplicity-adjusted confirmatory inference'}


def equivalent_real_quadratic(net,deltas,x):
    basis=net.forward(np.eye(5,dtype=np.complex128),deltas,gradients=False)['fields'].T
    # q=|u.x|^2=x^T(aa^T+bb^T)x for real x. Real rank <=2, not rank1.
    matrices=np.asarray([np.outer(u.real,u.real)+np.outer(u.imag,u.imag) for u in basis])
    dense=np.einsum('ni,oi->no',x,basis)
    powers=np.einsum('ni,oij,nj->no',x,matrices,x)
    native=net.forward(x,deltas,gradients=False)
    field_error=float(np.max(np.abs(native['fields']-dense)))
    power_error=float(np.max(np.abs(native['powers']-powers)))
    eigenvalues=np.linalg.eigvalsh(matrices)
    ranks=[int(np.sum(e>1e-10)) for e in eigenvalues]
    need(field_error<=1e-11 and power_error<=1e-11 and max(ranks)<=2 and eigenvalues.min()>=-1e-12,'real quadratic equivalence/capacity gate')
    return {'basis_real':basis.real.tolist(),'basis_imag':basis.imag.tolist(),'real_quadratic_matrices':matrices.tolist(),
            'field_max_absolute_difference':field_error,'power_max_absolute_difference':power_error,
            'real_quadratic_numerical_ranks':ranks,'rank_threshold':1e-10,'min_eigenvalue':float(eigenvalues.min()),
            'mathematical_scope':'Ideal coherent fixed-path linear field then square-law detection. Each real-input detector PSD quadratic has rank <=2; difference of two detectors rank <=4. Complex Hermitian detector quadratic rank<=1. No intermediate optical nonlinearity or universal-classifier claim.'}
