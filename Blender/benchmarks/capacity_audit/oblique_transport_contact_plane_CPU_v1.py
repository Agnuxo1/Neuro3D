"""Opt-in CPU plane condition from literal hi-lo32 point and DECLARED error intervals."""
from fractions import Fraction as F
import hashlib
import struct


def pair(x):
    return [x.numerator,x.denominator]


def fraction(p):
    if type(p)is not list or len(p)!=2 or any(type(x)is not int for x in p):
        raise ValueError("canonical rational required")
    if p[1]<=0 or max(abs(x).bit_length()for x in p)>4096:
        raise ValueError("bounded positive denominator required")
    x=F(*p)
    if pair(x)!=p or abs(x)>1000000:
        raise ValueError("noncanonical or out-of-domain error")
    return x


def decode(word):
    if type(word)is not int or not 0<=word<=0xffffffff:
        raise ValueError("uint32 required")
    e,m,s=(word>>23)&255,word&0x7fffff,word>>31
    if e==255 or (e==0 and m==0 and s):
        raise ValueError("nonfinite or negative zero")
    power=e-150 if e else -149
    x=F((-1 if s else 1)*((1<<23)+m if e else m))
    x=x*(1<<power) if power>=0 else x/(1<<-power)
    if abs(x)>1000000:raise ValueError("outside declared raw32 domain")
    return x


def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def dot(a,b):
    return sum((x*y for x,y in zip(a,b)),F(0))


def audit_plane(point_words,triangle_words,direction_words,declared_errors=None):
    """No SOURCE authentication, no triangle-interior proof, no launch exclusion."""
    for v,n in ((point_words,6),(triangle_words,9),(direction_words,3)):
        if type(v)is not list or len(v)!=n:
            raise ValueError("fixed raw word lists required")
    decoded=[decode(w)for w in point_words+triangle_words+direction_words]
    point=tuple(decoded[2*i]+decoded[2*i+1]for i in range(3))
    verts=[tuple(decoded[j:j+3])for j in (6,9,12)]
    direction=tuple(decoded[15:18])
    if not any(direction):raise ValueError("zero direction")
    if any(abs(x)>1000000 for x in point):raise ValueError("point outside domain")
    out={"scope":"CPU_DECLARED_BOX_INFINITE_PLANE_ONLY_NOT_NATIVE_OR_TRIANGLE_HIT",
         "input_words_sha256":hashlib.sha256(struct.pack("<18I",*(point_words+triangle_words+direction_words))).hexdigest(),
         "literal_pair_point":[pair(x)for x in point],"point_box":None,
         "normal_exact":None,"plane_residual_interval":None,"normal_dot_direction":None,
         "plane_parameter_interval":None,"GPU_launch_allowed":False,
         "launch_exclusion_allowed":False,"native_precision_certified":False,
         "native_point_budget_authenticated":False,"triangle_hit_certified":False,
         "full_path_visibility_certified":False,"phase_certified":False,
         "phase_error_bound":None,"full_costs":"UNKNOWN_NOT_ZERO"}
    if any((w&0x7f800000)==0 and (w&0x7fffff)!=0 for w in point_words):
        return dict(out,status="STOP_SUBNORMAL_POINT_WIRE")
    if any((w&0x7f800000)==0 and (w&0x7fffff)!=0 for w in triangle_words+direction_words):
        raise ValueError("subnormal geometry/direction outside contract")
    if declared_errors is None:
        return dict(out,status="STOP_MISSING_DECLARED_POINT_BUDGET")
    if type(declared_errors)is not list or len(declared_errors)!=3:
        raise ValueError("three error intervals required")
    box=[]
    for center,interval in zip(point,declared_errors):
        if type(interval)is not list or len(interval)!=2:raise ValueError("error interval required")
        lo,hi=(fraction(p)for p in interval)
        if lo>hi or max(abs(center+lo),abs(center+hi))>1000000:
            raise ValueError("inverted/out-of-domain box")
        box.append((center+lo,center+hi))
    a,b,c=verts;n=cross(sub(b,a),sub(c,a))
    out["point_box"]=[[pair(x)for x in interval]for interval in box]
    out["normal_exact"]=[pair(x)for x in n]
    if not any(n):return dict(out,status="STOP_DEGENERATE_PLANE")
    residual=[F(0),F(0)]
    for ni,ai,interval in zip(n,a,box):
        products=[ni*(x-ai)for x in interval]
        residual[0]+=min(products);residual[1]+=max(products)
    den=dot(n,direction)
    out["plane_residual_interval"]=[pair(x)for x in residual]
    out["normal_dot_direction"]=pair(den)
    if not den:return dict(out,status="STOP_ZERO_PLANE_DENOMINATOR")
    tau=sorted([-x/den for x in residual])
    out["plane_parameter_interval"]=[pair(x)for x in tau]
    status=("CPU_ZERO_PLANE_CONTACT_ONLY" if residual==[0,0]
            else "CPU_STRICT_PLANE_SEPARATION_ONLY" if residual[1]<0 or residual[0]>0
            else "CPU_UNCERTAIN_PLANE_CONTACT_STOP")
    return dict(out,status=status)
