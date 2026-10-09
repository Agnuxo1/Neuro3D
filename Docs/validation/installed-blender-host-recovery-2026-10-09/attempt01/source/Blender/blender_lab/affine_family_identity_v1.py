"""Exact independent-to-producer affine expression identity, no sample fitting."""
from fractions import Fraction as F
from Tools.audit_captured_pilot_result_v1 import need


def certify_affine_identity(independent,producer):
    need(independent.graph==producer.graph,'Same exact audited base graph required')
    count=0
    for name,jets in [('origins',producer.origin_jets),('points',producer.point_jets)]:
        rows=getattr(independent,name)
        need(len(rows)==len(jets)==len(independent.graph['nodes']),'Every affine vector state required')
        for i,(row,jet) in enumerate(zip(rows,jets)):
            base=independent.graph['nodes'][i]['origin' if name=='origins' else 'point']
            need(len(row)==len(jet)==3,'Complete affine vector required')
            for a,b,value in zip(row,jet,base):
                need(a.base==F(value) and a.coefficients==tuple(b),'Independent affine vector identity failed:'+name)
                count+=1
    for name,jets,key in [('segments',producer.segment_jets,'segment_parameter'),('references',producer.reference_jets,'reference_parameter')]:
        need(len(getattr(independent,name))==len(jets)==len(independent.graph['nodes']),'Every affine scalar state required')
        for i,(a,b) in enumerate(zip(getattr(independent,name),jets)):
            if a is None:need(b is None,'Reference presence must match');continue
            need(a.base==F(independent.graph['nodes'][i][key]) and a.coefficients==tuple(b),'Independent affine scalar identity failed:'+name)
            count+=1
    need(set(independent.shifts)==set(producer.shifts),'Every translated object binding required')
    for name,vectors in independent.shifts.items():
        need(len(vectors)==len(producer.shifts[name])==3,'Complete object translation vector required')
        for a,b in zip(vectors,producer.shifts[name]):
            need(a.base==0 and a.coefficients==tuple(b),'Independent translation binding identity failed');count+=1
    need(len(independent.origins)==len(producer.origin_jets),'Every geometric state required')
    return {'status':'CERTIFIED_EXACT_AFFINE_EXPRESSION_IDENTITY','scalar_expressions_compared':count,'states':len(independent.graph['nodes']),
            'scope':'Exact base and all parameter coefficients; no fitted/sample transfer matrix. Continuous topology proof still required.'}


def require_box_membership(box,values):
    need(len(box)==len(values),'Complete parameter vector required')
    for (lo,hi),value in zip(box,values):
        need(F(lo)<=F(float(value))<=F(hi),'Parameter outside proved continuous family')
    return {'status':'EXACT_PARAMETER_MEMBERSHIP_VERIFIED','parameters':len(values)}
