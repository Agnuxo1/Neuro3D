"""Ideal represented CPU path lengths from a complete verified event tree.

Rational squared distances, outward sqrt enclosures and rational sums.
Not a native rounding bound or a proof about prior Blender float32 inputs.
Terminal modes must be exactly forward-collinear in this opt-in contract.
"""
from fractions import Fraction as F
import math
from history_completeness_cpu_v1 import validate_complete_tree
from history_lineage_cpu_v2 import scene_binding, triangles, vec, sub, dot, cross


def sqrt_interval(q):
    q=F(q)
    if q<0: raise ValueError('negative squared length')
    if q==0: return F(0),F(0)
    x=math.sqrt(float(q))
    if not math.isfinite(x) or x==0: raise ValueError('sqrt outside CPU pilot range')
    low=high=x
    while F(low)*F(low)>q: low=math.nextafter(low,-math.inf)
    while F(high)*F(high)<q: high=math.nextafter(high,math.inf)
    return F(low),F(high)


def encoded_interval(lo,hi):
    a,b=float(lo),float(hi)
    if not math.isfinite(a) or not math.isfinite(b): raise ValueError('length outside finite pilot range')
    if F(a)>lo: a=math.nextafter(a,-math.inf)
    if F(b)<hi: b=math.nextafter(b,math.inf)
    return {'rational_lower':[lo.numerator,lo.denominator],
            'rational_upper':[hi.numerator,hi.denominator],
            'outward_float_BU':[a,b]}


def reconstruct_lengths(snapshot,records):
    complete=validate_complete_tree(snapshot,records)
    _,packed=scene_binding(snapshot); geometry=triangles(packed)
    accepted={}; ledger=[]; terminals=[]
    for r in records:
        rid=r['id'];parent_id=r['parent_id']
        if parent_id is None:
            lo=hi=F(0); squared=F(0)
        else:
            delta=sub(vec(r['origin_BU']),vec(accepted[parent_id]['record']['origin_BU']))
            squared=dot(delta,delta); a,b=sqrt_interval(squared)
            lo=accepted[parent_id]['lo']+a;hi=accepted[parent_id]['hi']+b
        row={'id':rid,'parent_id':parent_id,'source_id':r['source_id'],
             'segment_squared_BU2':[squared.numerator,squared.denominator],
             'cumulative_length':encoded_interval(lo,hi)}
        if r['event'] in ('detect','escape'):
            owner=geometry[r['primitive_id']][0];name=packed.geometry.object_ids[owner]
            obj=snapshot['objects'][name];d=vec(r['direction']);axis=vec(obj['mode_direction'])
            if cross(d,axis)!=(0,0,0) or dot(d,axis)<=0:
                raise ValueError('exact forward-collinear terminal mode required')
            normlo,normhi=sqrt_interval(dot(d,d))
            numerator=dot(d,sub(vec(obj['mode_origin_BU']),vec(r['origin_BU'])))
            quotients=(numerator/normlo,numerator/normhi)
            correctionlo,correctionhi=min(quotients),max(quotients)
            row.update(port=name,event=r['event'],
                       reference_correction=encoded_interval(correctionlo,correctionhi),
                       effective_length=encoded_interval(lo+correctionlo,hi+correctionhi))
            terminals.append(row)
        ledger.append(row);accepted[rid]={'record':r,'lo':lo,'hi':hi}
    return {'schema':'exp005-history-lengths-CPU-v1','scene_binding_sha256':complete['scene_binding_sha256'],
            'scope':'ideal represented CPU complete tree lengths; NO native error/phase/field certification',
            'records':ledger,'terminals':terminals,'terminal_mode_rule':'exact forward collinearity',
            'length_unit':'BU','squared_length_unit':'BU^2','native_exemption_allowed':False,
            'fields_computed':False,'phase_error_certified':False}
