"""Opt-in rational CLOSED segment / triangle coplanar diagnostic.
All real contact remains STOP; a synthetic miss is not phase or GPU admission.
"""
from pathlib import Path
from fractions import Fraction as F
import base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-coplanar-finite-segment-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SEGMENT-VISIBILITY-CPU-001-CODEX.json"
PSHA="caeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5"
SEAL="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-VISIBILITY-JOIN-HOST-001-CODEX.json"
SSHA="df45c70348c50838ba4ebc9169f13dacf05bbb9da3cf576cb212f2b3ff3953dc"
INTENT="DECLARED_COPLANAR_FINITE_QUERY_ONLY"
def need(v,msg):
    if not v:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def p(x):return [x.numerator,x.denominator]
def f(x):
    need(type(x)is list and len(x)==2 and all(type(y)is int for y in x),"typed_rational")
    need(x[1]>0 and max(abs(x[0]).bit_length(),x[1].bit_length())<=128,"bounded_rational")
    return F(*x)
def vec(v):
    need(type(v)is list and len(v)==3,"vector3")
    a=tuple(map(f,v));need(all(abs(x)<=10**6 for x in a),"coordinate_bound");return a
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def area(a,b):return a[0]*b[1]-a[1]*b[0]
def capture(t):
    z=zlib.decompressobj();b=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),2097153)
    need(len(b)<=2097152 and z.eof and not z.unused_data and not z.unconsumed_tail,"capture_extent")
    need(t["rc"]==0 and t["timed_out"]is False and len(b)==t["stdout_bytes"]and sha(b)==t["stdout_sha256"],"capture_identity")
    return json.loads(b)
def retained():
    raw=(ROOT/SEAL).read_bytes();need(sha(raw)==SSHA,"seal_identity");seal=json.loads(raw)
    pins=dict(seal["code_doc_sha256"])
    for q,s in pins.items():
        t=Path(q);need(sha((t if t.is_absolute()else ROOT/t).read_bytes())==s,"ancestral_pin:"+q)
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    need(capture(r["independent_pre"])["status"]=="PASS","sealed_parent_oracle")
    records=capture(r["test_run"])["runs"]
    e={x["id"]:x for x in records if x["result"]["reason"]=="coplanar_ambiguity"}
    need(set(e)=={"oblique/coplanar","tiny_gap_2m60/coplanar"},"two_retained_coplanar_scenes")
    for x in e.values():
        need(x["parent_result"]["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY","sealed_length_ready")
        need(digest(x["scene"])==x["request"]["original_scene_sha256"]==x["parent_result"]["original_scene_sha256"],"sealed_scene")
        need(digest(x["request"])==x["parent_result"]["literal_request_sha256"],"sealed_literal")
        need([y["source_id"]for y in x["parent_result"]["paths"]]==["S0","S1"],"sealed_SOURCE_paths")
    pins[SEAL]=SSHA
    return e,pins
def selector(case,source_id,segment,primitive_id,e):
    x=e[case]
    return dict(case=case,source_id=source_id,segment=segment,primitive_id=primitive_id,
        parent_receipt_sha256=PSHA,scene_sha256=digest(x["scene"]),literal_request_sha256=digest(x["request"]),
        paths_sha256=digest(x["parent_result"]["paths"]),intent=INTENT)
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,rows=[],diagnostics=[],verified_queries=0,
        promotion="STOP",GPU_launch_allowed=False,GPU_executed=False,scene_authenticated=False,
        full_visibility_certified=False,native_hit_coverage_certified=False,physical_field_certified=False,
        phase_certified=False,field=None,amplitude=None,power=None,epsilon_BU=[0,1],object_wide_skip=False,
        previous_zero_exemption=False,RN64_operations=0,compiler_calls=0,producer_replays=0,full_costs="UNMEASURED_NOT_ZERO")
def _clip(origin,end,triangle):
    need(type(triangle)is list and len(triangle)==3,"triangle3")
    o=vec(origin);d=sub(vec(end),o);a,b,c=map(vec,triangle);n=cross(sub(b,a),sub(c,a))
    need(n!=(0,0,0),"nondegenerate_triangle");need(dot(d,d)>0,"positive_segment")
    need(dot(n,sub(o,a))==0 and dot(n,d)==0,"coplanar_only")
    drop=max(range(3),key=lambda k:abs(n[k]));keep=[k for k in range(3)if k!=drop]
    project=lambda v:tuple(v[k]for k in keep)
    vs=list(map(project,(a,b,c)));oo=project(o);dd=project(d)
    determinant=area(sub(vs[1],vs[0]),sub(vs[2],vs[0]));need(determinant!=0,"projected_nondegenerate")
    sign=1 if determinant>0 else -1
    lower=F(0);upper=F(1);edges=[];parallel_outside=[]
    for i,v in enumerate(vs):
        edge=sub(vs[(i+1)%3],v);start=sign*area(edge,sub(oo,v));slope=sign*area(edge,dd)
        if slope==0:
            if start<0:parallel_outside.append(i)
        elif slope>0:lower=max(lower,-start/slope)
        else:upper=min(upper,-start/slope)
        edges.append(dict(edge=i,start=p(start),slope=p(slope)))
    empty=bool(parallel_outside)or lower>upper
    return dict(domain_t=[[0,1],[1,1]],origin_BU=origin,end_BU=end,triangle_BU=triangle,
        normal=[p(x)for x in n],drop_axis=drop,orientation=p(determinant),edges=edges,
        clipped_lower=p(lower),clipped_upper=p(upper),parallel_outside_edges=parallel_outside,
        empty=empty,contact_interval_t=None if empty else [p(lower),p(upper)],
        contact_kind="NONE"if empty else ("POINT"if lower==upper else "SPAN"))
def _classify(origin,end,triangle,context):
    out=baseline()
    try:
        cert=_clip(origin,end,triangle);cert["context"]=context;out["diagnostics"]=[cert]
        need(cert["empty"],"actual_coplanar_contact")
        out.update(status="CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY",rows=[cert],verified_queries=1)
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out
def _audit(model,q,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("case"))is str and q["case"]in e,"closed_case")
        need(type(q.get("source_id"))is str and q["source_id"]in("S0","S1"),"typed_SOURCE")
        need(type(q.get("segment"))is int and q["segment"]in(0,1),"typed_segment")
        need(type(q.get("primitive_id"))is int,"typed_primitive")
        expected=selector(q["case"],q["source_id"],q["segment"],q["primitive_id"],e)
        need(set(q)==set(expected) and all(type(q[k])is type(expected[k])for k in q)and q==expected,"closed_selector_identity")
        x=e[q["case"]];paths=x["parent_result"]["paths"];i=int(q["source_id"][1])
        need(paths[i]["source_id"]==x["scene"]["sources"][i]["id"]==q["source_id"],"SOURCE_path_binding")
        ss=paths[i]["segments"];need(ss[0]["from_BU"]==x["scene"]["sources"][i]["position_BU"]and ss[0]["to_BU"]==ss[1]["from_BU"],"path_continuity")
        need(ss[1]["to_BU"]==x["request"]["detector_point_BU"],"detector_endpoint")
        triangles=[t for t in x["scene"]["triangles"]if t["primitive_id"]==q["primitive_id"]]
        need(len(triangles)==1,"unique_declared_primitive")
        s=ss[q["segment"]]
        need(dot(sub(vec(s["to_BU"]),vec(s["from_BU"])),sub(vec(s["to_BU"]),vec(s["from_BU"])))==f(s["squared_BU2"]),"segment_certificate_binding")
        context=dict(provenance="SEALED_DECLARED_SCENE_CPU_ONLY",selector=q,parent_visibility_status=x["result"]["status"],
            parent_visibility_reason=x["result"]["reason"],parent_STOP_preserved=True)
        return _classify(s["from_BU"],s["to_BU"],triangles[0]["vertices_BU"],context)
    except(ValueError,TypeError,KeyError,IndexError)as ex:out["reason"]=str(ex)
    return out
def audit(model,request):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _audit(model,request,e)
