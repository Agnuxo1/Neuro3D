"""Independent Hermitian Gram, LDL and Rayleigh interval witnesses.

Euclidean represented channel normalization is not calibrated optical flux.
No numerical eigensolver result is treated as a proof.
"""
import math
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit.rational_interval_v1 import Interval as I, upward_float
from Blender.blender_lab.state_graph_enclosure_v1 import cmultiply


def conjugate(z): return z[0], -z[1]
def add(a,b): return a[0]+b[0],a[1]+b[1]
def subtract(a,b): return a[0]-b[0],a[1]-b[1]
def norm2(z): return z[0].square()+z[1].square()
def zero(): return I(0),I(0)


def gram_enclosure(rows):
    if not rows or not rows[0] or any(len(row)!=len(rows[0]) for row in rows):
        raise ValueError('nonempty rectangular interval matrix required')
    n=len(rows[0]);gram=[[zero() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        gram[i][i]=(sum((norm2(row[i]) for row in rows),I(0)),I(0))
        for j in range(i+1,n):
            value=zero()
            for row in rows:value=add(value,cmultiply(conjugate(row[i]),row[j]))
            gram[i][j]=value;gram[j][i]=conjugate(value)
    return gram


def positive_ldl(gram):
    n=len(gram);lower=[[zero() for _ in range(n)] for _ in range(n)];pivots=[]
    for i in range(n):
        pivot=gram[i][i][0]-sum((norm2(lower[i][k])*pivots[k] for k in range(i)),I(0))
        if pivot.lo<=0:
            return {'status':'UNKNOWN_POSITIVE_RANK_NOT_PROVED','failed_pivot':i,'pivot':pivot.wire(),'positive_pivots':[p.wire() for p in pivots]}
        pivots.append(pivot);lower[i][i]=I(1),I(0)
        for j in range(i+1,n):
            value=gram[j][i]
            for k in range(i):
                term=cmultiply(lower[j][k],conjugate(lower[i][k]));value=subtract(value,(term[0]*pivots[k],term[1]*pivots[k]))
            lower[j][i]=value[0]/pivot,value[1]/pivot
    return {'status':'CERTIFIED_FULL_COLUMN_RANK','rank':n,'positive_pivots':[p.wire() for p in pivots]}


def rayleigh(gram,vector):
    if len(vector)!=len(gram):raise ValueError('complete complex vector required')
    v=[(I(F(z[0])),I(F(z[1]))) for z in vector];denominator=sum((norm2(z) for z in v),I(0))
    if denominator.lo<=0:raise ValueError('strictly nonzero represented vector required')
    total=zero()
    for i in range(len(v)):
        for j in range(len(v)):
            total=add(total,cmultiply(conjugate(v[i]),cmultiply(gram[i][j],v[j])))
    if not total[1].contains(0):raise ValueError('Hermitian imaginary consistency failed')
    return total[0]/denominator


def norm_bounds(gram):
    lowers=[];uppers=[]
    for i,row in enumerate(gram):
        radius=sum((norm2(z).sqrt().hi for j,z in enumerate(row) if j!=i),F(0))
        lowers.append(row[i][0].lo-radius);uppers.append(row[i][0].hi+radius)
    low=max(F(0),min(lowers));high=max(uppers)
    downward=float(low)
    if F(downward)>low:downward=math.nextafter(downward,-math.inf)
    return {'eigenvalue_lower':[low.numerator,low.denominator],'eigenvalue_upper':[high.numerator,high.denominator],
            'eigenvalue_lower_downward_float':downward,'eigenvalue_upper_upward_float':upward_float(high),
            'operator_norm_upper_upward_float':upward_float(I(high).sqrt().hi)}


def normalization(gram,vector,tolerance):
    bounds=norm_bounds(gram);upper=F(*bounds['eigenvalue_upper']);witness=rayleigh(gram,vector)
    if witness.lo>1+tolerance:status='CERTIFIED_NONCONTRACTIVE_EUCLIDEAN_CHANNEL_NORMALIZATION';metric=0
    elif upper<=1+tolerance:status='CERTIFIED_APPROXIMATE_EUCLIDEAN_CONTRACTIVITY';metric=1
    else:status='UNKNOWN_EUCLIDEAN_CONTRACTIVITY';metric=None
    return {'status':status,'contractivity_metric':metric,'bounds':bounds,'represented_witness_reim':vector,
            'rayleigh_enclosure':witness.wire(),'rayleigh_lower_downward_float':-upward_float(-witness.lo),
            'rayleigh_upper_upward_float':upward_float(witness.hi),'tolerance':[tolerance.numerator,tolerance.denominator]}
