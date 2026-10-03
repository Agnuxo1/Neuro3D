"""Opt-in conditional separation bound for sealed coplanar query geometry.
Input boxes are DECLARED ONLY, not measured uncertainty or phase admission.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,base64,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-coplanar-clearance-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-COPLANAR-FINITE-SEGMENT-CPU-001-CODEX.json"
PSHA="8ea19cd01ea348a381f739f7cd480ebe264718d7f680408f8aa6ff23367147b9"
INTENT="CONDITIONAL_DECLARED_BOX_SEPARATION_ONLY"
def need(v,s):
    if not v:raise ValueError(s)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def frac(v):
    need(type(v)is list and len(v)==2 and all(type(x)is int for x in v),"typed_rational")
    need(v[1]>0 and max(abs(v[0]).bit_length(),v[1].bit_length())<=128,"bounded_rational")
    return F(*v)
def vector(v):
    need(type(v)is list and len(v)==3,"vector3")
    a=tuple(map(frac,v));need(all(abs(x)<=10**6 for x in a),"coordinate_bound");return a
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def capture(t):
    z=zlib.decompressobj();b=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),2097153)
    need(len(b)<=2097152 and z.eof and not z.unconsumed_tail and not z.unused_data,"capture_extent")
    need(t["rc"]==0 and not t["timed_out"]and sha(b)==t["stdout_sha256"]and len(b)==t["stdout_bytes"],"capture_identity")
    return json.loads(b)
def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():
        need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    data=capture(r["test_run"])["data"];e={}
    for x in data["runs"]:
        if x["result"]["status"]=="CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY"or x["id"].startswith("sealed:"):
            need(len(x["result"]["diagnostics"])==1,"one_parent_certificate");e[x["id"]]=x
    need(len(e)==80 and sum(x["scope"]=="SEALED_DECLARED_CPU"for x in e.values())==8,"closed_retained_grid")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins
def geometry(x):
    c=x["result"]["diagnostics"][0]
    return dict(origin_BU=c["origin_BU"],end_BU=c["end_BU"],triangle_BU=c["triangle_BU"],context=c["context"])
def selector(case,e):
    x=e[case]
    return dict(case=case,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),geometry_sha256=digest(geometry(x)),intent=INTENT)
def boxes(v):
    need(type(v)is dict and set(v)=={"schema","points_BU"}and v["schema"]=="DECLARED_INDEPENDENT_COORDINATE_BOXES_ONLY","closed_declared_boxes")
    need(type(v["points_BU"])is list and len(v["points_BU"])==5,"five_point_boxes")
    b=list(map(vector,v["points_BU"]));need(all(y>=0 for x in b for y in x),"nonnegative_radii")
    return b
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,rows=[],diagnostics=[],verified_queries=0,clearance_lower_BU=None,
        promotion="STOP",GPU_launch_allowed=False,GPU_executed=False,scene_authenticated=False,
        uncertainty_authenticated=False,full_visibility_certified=False,phase_certified=False,physical_field_certified=False,
        field=None,amplitude=None,power=None,epsilon_BU=[0,1],object_wide_skip=False,previous_zero_exemption=False,
        compiler_calls=0,producer_replays=0,RN64_operations=0,full_costs="UNMEASURED_NOT_ZERO")
def _bound(g,rr):
    o,end=vector(g["origin_BU"]),vector(g["end_BU"]);need(type(g["triangle_BU"])is list and len(g["triangle_BU"])==3,"triangle3")
    tri=list(map(vector,g["triangle_BU"]));a,b,c=tri;normal=cross(sub(b,a),sub(c,a));d=sub(end,o)
    need(normal!=(0,0,0)and dot(d,d)>0,"nondegenerate_geometry")
    need(dot(normal,sub(o,a))==0 and dot(normal,d)==0,"nominal_coplanarity")
    axes=[cross(normal,sub(tri[(i+1)%3],tri[i]))for i in range(3)]+[cross(normal,d),(F(1),F(0),F(0)),(F(0),F(1),F(0)),(F(0),F(0),F(1))]
    points=[o,end]+tri;records=[]
    for index,raw in enumerate(axes):
        scale=sum(abs(x)for x in raw);need(scale>0,"nonzero_axis")
        axis=tuple(x/scale for x in raw);centers=[dot(axis,p)for p in points]
        supports=[sum(abs(axis[k])*rad[k]for k in range(3))for rad in rr]
        lower=[x-y for x,y in zip(centers,supports)];upper=[x+y for x,y in zip(centers,supports)]
        seg=[min(lower[:2]),max(upper[:2])];triangle=[min(lower[2:]),max(upper[2:])]
        gaps=[triangle[0]-seg[1],seg[0]-triangle[1]]
        records.append(dict(index=index,axis_L1=list(map(pair,axis)),centers=list(map(pair,centers)),supports=list(map(pair,supports)),
            segment_projection=list(map(pair,seg)),triangle_projection=list(map(pair,triangle)),signed_gaps=list(map(pair,gaps))))
    best=max(max(map(lambda v:F(*v),x["signed_gaps"]))for x in records)
    winner=next(x["index"]for x in records if max(F(*v)for v in x["signed_gaps"])==best)
    return dict(geometry=g,radii_BU=[[pair(y)for y in x]for x in rr],axes=records,best_axis=winner,
        signed_best_gap_BU=pair(best),clearance_lower_BU=pair(max(F(0),best)),basis="ALL_ENDPOINT_AND_VERTEX_BOX_SUPPORTS_L1_AXIS",
        guarantee="CONDITIONAL_ON_DECLARED_BOXES_ONLY",correlation_assumed=False)
def _audit(model,q,uncertainty,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("case"))is str and q["case"]in e,"closed_case")
        expected=selector(q["case"],e);need(set(q)==set(expected)and all(type(q[k])is str for k in q)and q==expected,"closed_selector_identity")
        rr=boxes(uncertainty);x=e[q["case"]]
        need(x["result"]["status"]=="CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY","parent_contact_STOP")
        cert=_bound(geometry(x),rr);out["diagnostics"]=[cert]
        need(F(*cert["signed_best_gap_BU"])>0,"uncertainty_exhausts_separator")
        out.update(status="CPU_CONDITIONAL_DECLARED_BOX_SEPARATION_ONLY",rows=[cert],verified_queries=1,clearance_lower_BU=cert["clearance_lower_BU"])
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out
def audit(model,request,declared_uncertainty):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _audit(model,request,declared_uncertainty,e)
