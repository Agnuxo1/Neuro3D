"""Exact declared-segment visibility over sealed CPU paths. No scene/GPU authentication."""
from pathlib import Path
from fractions import Fraction as F
import base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-segment-visibility-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
PSHA="139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
SEAL="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-EQUAL-WORK-HOST-001-CODEX.json"
SSHA="2e9eee5cf10def39dcf882044fe3c2e8678aeb260cc7d1a1c2f7fa57d78e8ae0"
INTENT="SEALED_DECLARED_SEGMENT_VISIBILITY_ONLY"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def need(v,msg):
    if not v:raise ValueError(msg)
def p(v):return [v.numerator,v.denominator]
def f(v):
    need(type(v)is list and len(v)==2 and all(type(x)is int for x in v),"typed_rational")
    need(v[1]>0 and max(abs(v[0]).bit_length(),v[1].bit_length())<=128,"bounded_rational")
    return F(*v)
def vec(v):
    need(type(v)is list and len(v)==3,"vector3")
    r=tuple(map(f,v));need(all(abs(x)<=10**6 for x in r),"coordinate_bound");return r
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,visibility_rows=[],diagnostics=[],
        SOURCE_segments_admitted=0,epsilon_BU=[0,1],object_wide_skip=False,
        promotion="STOP",GPU_launch_allowed=False,GPU_executed=False,scene_authenticated=False,
        native_hit_coverage_certified=False,physical_field_certified=False,
        producer_replays=0,RN64_operations=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")
def capture(t):
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    need(t["rc"]==0 and not t["timed_out"] and len(b)==t["stdout_bytes"] and sha(b)==t["stdout_sha256"],"capture_integrity")
    return json.loads(b)
def load_evidence():
    b=(ROOT/SEAL).read_bytes();need(sha(b)==SSHA,"seal_identity");seal=json.loads(b)
    for path,h in seal["code_doc_sha256"].items():need(sha((ROOT/path).read_bytes())==h,"ancestral_pin")
    b=(ROOT/PARENT).read_bytes();need(sha(b)==PSHA,"parent_identity");r=json.loads(b)
    need(capture(r["independent_pre_commit"])["status"]=="PASS","parent_oracle")
    return capture(r["test_run"])["data"]
def selector(case):return dict(case=case,parent_sha256=PSHA,intent=INTENT)
def _audit(scene,q,r):
    out=baseline()
    try:
        need(r["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY","parent_STOP:"+str(r["reason"]))
        need(digest(scene)==q["original_scene_sha256"]==r["original_scene_sha256"],"scene_binding")
        need(digest(q)==r["literal_request_sha256"],"literal_binding")
        need(q["source_ids"]==["S0","S1"] and len(scene["sources"])==2,"ALL_SOURCE")
        ts=scene["triangles"];need(type(ts)is list and 2<=len(ts)<=4,"bounded_triangles")
        triangles=[];ids=[]
        for tr in ts:
            need(type(tr)is dict and set(tr)=={"primitive_id","object_id","vertices_BU"},"closed_triangle")
            pid=tr["primitive_id"];need(type(pid)is int and 0<=pid<2**31 and pid not in ids,"unique_primitive")
            need(type(tr["object_id"])is str and 0<len(tr["object_id"])<=64,"object_identity")
            need(type(tr["vertices_BU"])is list and len(tr["vertices_BU"])==3,"vertices")
            a,b,c=map(vec,tr["vertices_BU"]);e0=sub(b,a);e1=sub(c,a);n=cross(e0,e1)
            need(dot(n,n)>0,"nondegenerate");triangles.append((pid,a,e0,e1,n));ids.append(pid)
        paths=r["paths"];need(type(paths)is list and len(paths)==2,"ALL_SOURCE_paths")
        rows=[]
        for i,path in enumerate(paths):
            need(path["source_id"]=="S"+str(i)==scene["sources"][i]["id"],"source_order")
            targets=[q["root_primitive_id"],q["detector_primitive_id"]]
            need(path["primitive_ids"]==targets and all(type(v)is int and v in ids for v in targets)and targets[0]!=targets[1],"path_primitives")
            ss=path["segments"];need(type(ss)is list and len(ss)==2,"two_segments")
            need(ss[0]["from_BU"]==scene["sources"][i]["position_BU"] and ss[0]["to_BU"]==ss[1]["from_BU"],"continuity")
            need(ss[1]["to_BU"]==q["detector_point_BU"],"detector_endpoint")
            total_lo=F(0);total_hi=F(0)
            for j,s in enumerate(ss):
                o=vec(s["from_BU"]);end=vec(s["to_BU"]);d=sub(end,o);squared=dot(d,d)
                need(squared>0 and squared==f(s["squared_BU2"]),"positive_segment_squared")
                lo,hi=map(f,s["length_interval_BU"]);need(0<=lo<=hi and lo*lo<=squared<=hi*hi,"retained_length_certificate")
                total_lo+=lo;total_hi+=hi
                if j==0:
                    direction=vec(scene["sources"][i]["direction"])
                    need(dot(direction,d)>0 and cross(direction,d)==(0,0,0),"incoming_direction")
                else:
                    prior=next(t for t in triangles if t[0]==targets[0]);n=prior[-1];incoming=sub(vec(ss[0]["to_BU"]),vec(ss[0]["from_BU"]))
                    reflected=tuple(incoming[k]-2*dot(incoming,n)*n[k]/dot(n,n)for k in range(3))
                    need(dot(reflected,d)>0 and cross(reflected,d)==(0,0,0),"reflection_direction")
                endpoint=0
                for pid,a,e0,e1,n in triangles:
                    denom=dot(n,d);plane=dot(n,sub(a,o))
                    row=dict(source_id=path["source_id"],segment=j,primitive_id=pid,t=None,barycentric=None,classification=None)
                    if denom==0:
                        row["classification"]="PARALLEL_DISJOINT" if plane!=0 else "COPLANAR_STOP"
                        rows.append(row);out["diagnostics"]=rows;need(plane!=0,"coplanar_ambiguity");continue
                    t=plane/denom;row["t"]=p(t)
                    if t<0 or t>1:row["classification"]="OUTSIDE_SEGMENT";rows.append(row);continue
                    h=tuple(o[k]+t*d[k]for k in range(3));v=sub(h,a)
                    aa=dot(e0,e0);bb=dot(e0,e1);cc=dot(e1,e1);dd=dot(v,e0);ee=dot(v,e1);det=aa*cc-bb*bb
                    u=(cc*dd-bb*ee)/det;w=(aa*ee-bb*dd)/det
                    row["barycentric"]=[p(1-u-w),p(u),p(w)]
                    if u<0 or w<0 or u+w>1:row["classification"]="OUTSIDE_TRIANGLE";rows.append(row);continue
                    if t==0 and j==1 and pid==targets[0]:row["classification"]="EXACT_PREVIOUS_ZERO"
                    elif t==1 and pid==targets[j]:row["classification"]="EXPECTED_ENDPOINT";endpoint+=1
                    else:
                        row["classification"]="UNEXPECTED_CONTACT_STOP";rows.append(row);out["diagnostics"]=rows
                        raise ValueError("unexpected_segment_contact")
                    rows.append(row)
                need(endpoint==1,"exact_target_endpoint")
            need([p(total_lo),p(total_hi)]==path["length_interval_BU"],"retained_total_length")
            need(f(path["interval_width_bound_rad"])<=f(q["source_width_caps_rad"][i]),"SOURCE_cap")
        need(f(r["relative_diagnostic"]["interval_width_bound_rad"])<=f(q["relative_width_cap_rad"]),"relative_cap")
        out.update(status="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY",visibility_rows=rows,diagnostics=rows,
            SOURCE_segments_admitted=4,original_scene_sha256=digest(scene),literal_request_sha256=digest(q))
    except(ValueError,KeyError,TypeError,IndexError,StopIteration)as ex:out["reason"]=str(ex)
    return out
def audit(model,request):
    try:
        need(type(model)is str and model==MODEL,"model")
        need(type(request)is dict and set(request)=={"case","parent_sha256","intent"},"closed_selector")
        need(type(request["case"])is str and request==selector(request["case"]),"selector_identity")
        e=load_evidence();case=request["case"];need(case in e["inputs"],"case")
        inp=e["inputs"][case];return _audit(inp["scene"],inp["request"],e["results"][case])
    except(ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]="selector_or_evidence:"+str(ex);return out
