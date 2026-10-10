import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ[v]="1"
import sys, time, numpy as np
sys.path.insert(0,'D:/PROJECTS/9_NEBULA_NEW/Benchmarks/escala-modos')
from malla import Mesh, layer_coeffs, apply_layers
def bench(f,n=1000,reps=7):
    for _ in range(100): f()
    r=[]
    for _ in range(reps):
        t=time.perf_counter()
        for _ in range(n): f()
        r.append((time.perf_counter()-t)/n)
    return np.median(r)*1e6
for N in (8,16,32,64):
    m=Mesh(N); p=np.random.default_rng(0).uniform(0,2*np.pi,m.n_params); co=layer_coeffs(m,p)
    x=np.random.default_rng(1).normal(size=N); x/=np.linalg.norm(x)
    full=bench(lambda: apply_layers(m,co,x))
    # mismas llamadas numpy por capa pero con 1 solo MZI por capa (aritmetica ~N/2 veces menor)
    co1=[tuple(c[:1] for c in t) for t in co]
    def one():
        a=x.astype(complex)[:,None]
        for l in range(N):
            o=m.off[l]; t00,t01,t10,t11=co1[l]
            a0=a[o:o+2:2]; a1=a[o+1:o+2:2]
            n0=t00*a0+t01*a1; n1=t10*a0+t11*a1
            a=a.copy(); a[o:o+2:2]=n0; a[o+1:o+2:2]=n1
        return a
    red=bench(one)
    D=np.random.default_rng(2).normal(size=(N,N))+1j*np.random.default_rng(3).normal(size=(N,N)); xc=x.astype(complex)
    dense=bench(lambda: D@xc)
    print(f'N={N} capas completas {full:.1f} us | mismas llamadas, 1 MZI/capa {red:.1f} us | matvec denso {dense:.2f} us')
