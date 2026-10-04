"""New opt-in scene-bound exact launch-point exclusion; no distance bias/object skip.
CPU rational synthetic geometry only, not native ALU32/64 raycasting or optical phase.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,zlib,base64
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-launch-contact-guard-CPU-v1"
POLICY="EXCLUDE_ONLY_CERTIFIED_PREVIOUS_PRIMITIVE_POINT_AT_EXACT_ZERO_KEEP_ALL_OTHER_CONTACT"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-DIFFERENCE-MATH-ENCLOSURE-HOST-001-CODEX.json"
PSHA="b799a6a17bb59561bf7a90e78189b6db821c82dcbd1119b784c9efa0a55f8e03"
VIS="coordinacion/respuestas/PRECISION-OBLIQUE-SEGMENT-VISIBILITY-CPU-001-CODEX.json"
VSHA="caeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5"
TOKEN_KEYS={"version","scene_sha256","query_sha256","path_sha256","source_id","segment",
            "previous_primitive_id","launch_point_BU","previous_barycentric","scope"}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def rat(p):
    need(type(p)is list and len(p)==2 and all(type(v)is int for v in p)and p[1]>0,"typed_rational")
    need(max(abs(v).bit_length()for v in p)<=128,"bounded_rational")
    q=F(*p);need(pair(q)==p,"canonical_rational");return q
def vec(p):
    need(type(p)is list and len(p)==3,"vector3")
    q=tuple(map(rat,p));need(all(abs(x)<=10**6 for x in q),"coordinate_bound");return q
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])

def capture(c):
    need(c["rc"]==0 and c["timed_out"]is False,"successful_capture")
    z=zlib.decompressobj();b=z.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),4194305)
    need(len(b)<=4194304 and z.eof and not z.unconsumed_tail and not z.unused_data,"bounded_capture")
    need(sha(b)==c["stdout_sha256"]and len(b)==c["stdout_bytes"],"capture_seal");return json.loads(b)

def retained():
    b=(ROOT/PARENT).read_bytes();need(sha(b)==PSHA and len(b)==217631,"parent_seal")
    rec=json.loads(b);pins=dict(rec["code_doc_sha256"]);need(len(pins)==331,"parent_pins")
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    need(capture(rec["independent_pre"])["status"]=="PASS","parent_oracle")
    need(pins[VIS]==VSHA,"visibility_pin")
    v=json.loads((ROOT/VIS).read_bytes());need(capture(v["independent_pre"])["status"]=="PASS","visibility_oracle")
    d=capture(v["test_run"]);need(d["status"]=="PASS","visibility_suite")
    rows=d["runs"];e={x["id"]:x for x in rows};need(len(e)==len(rows)==44,"closed44")
    pins[PARENT]=PSHA
    return e,pins

def selector(k,source,pid,e):
    x=e[k];return dict(model=MODEL,policy=POLICY,case=k,source_id=source,segment=1,primitive_id=pid,
        scene_sha256=digest(x["scene"]),query_sha256=digest(x["request"]),
        record_sha256=digest(x),parent_receipt_sha256=PSHA,visibility_receipt_sha256=VSHA)

def launch(x,source):
    scene=x["scene"];q=x["request"];r=x["parent_result"]
    need(x["result"]["status"]=="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY","retained_visibility_stop")
    need(r["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY","retained_length_stop")
    need(digest(scene)==q["original_scene_sha256"]==r["original_scene_sha256"],"same_scene")
    need(digest(q)==r["literal_request_sha256"],"same_query")
    need(q["source_ids"]==[s["id"]for s in scene["sources"]]==["S0","S1"],"ALL_SOURCE_order")
    paths=r["paths"];need([p["source_id"]for p in paths]==["S0","S1"],"ALL_SOURCE_paths")
    need(source in ("S0","S1"),"SOURCE_identity")
    p=paths[("S0","S1").index(source)];ss=p["segments"]
    need(len(ss)==2 and ss[0]["to_BU"]==ss[1]["from_BU"]==p["hit_points_BU"][0],"launch_continuity")
    need(ss[0]["from_BU"]==scene["sources"][("S0","S1").index(source)]["position_BU"],"original_source_position")
    need(ss[1]["to_BU"]==q["detector_point_BU"]==p["hit_points_BU"][1],"detector_endpoint")
    need(p["primitive_ids"]==[q["root_primitive_id"],q["detector_primitive_id"]],"primitive_path")
    prev=p["primitive_ids"][0];need(type(prev)is int,"primitive_type")
    matches=[t for t in scene["triangles"]if type(t["primitive_id"])is int and t["primitive_id"]==prev]
    need(len(matches)==1,"unique_previous_primitive")
    tri=matches[0];verts=list(map(vec,tri["vertices_BU"]));point=vec(ss[1]["from_BU"])
    bary=list(map(rat,p["barycentric"][0]))
    need(len(bary)==3 and min(bary)>=0 and sum(bary)==1,"previous_barycentric")
    need(tuple(sum(bary[j]*verts[j][i]for j in range(3))for i in range(3))==point,"previous_point_on_triangle")
    rows=x["result"]["visibility_rows"]
    incoming=[v for v in rows if v["source_id"]==source and v["segment"]==0 and v["primitive_id"]==prev]
    departing=[v for v in rows if v["source_id"]==source and v["segment"]==1 and v["primitive_id"]==prev]
    need(len(incoming)==len(departing)==1,"sealed_previous_contact_rows")
    need(incoming[0]["classification"]=="EXPECTED_ENDPOINT"and incoming[0]["t"]==[1,1],"sealed_previous_endpoint")
    need(departing[0]["classification"]=="EXACT_PREVIOUS_ZERO"and departing[0]["t"]==[0,1],"sealed_launch_point")
    need(incoming[0]["barycentric"]==departing[0]["barycentric"]==p["barycentric"][0],"same_previous_barycentric")
    return dict(version=1,scene_sha256=digest(scene),query_sha256=digest(q),path_sha256=digest(p),
        source_id=source,segment=1,previous_primitive_id=prev,launch_point_BU=ss[1]["from_BU"],
        previous_barycentric=p["barycentric"][0],scope="DECLARED_SYNTHETIC_LAUNCH_NOT_PHYSICAL"),ss[1],tri

def baseline():
    return dict(model=MODEL,status="STOP_INPUT",action="DO_NOT_EXCLUDE",reason=None,
        exclusion_allowed=False,contact=None,geometry_evaluations=0,epsilon_BU=[0,1],t_min=[0,1],
        object_wide_skip=False,SOURCE_shared_token=False,scene_authenticated=False,full_visibility_certified=False,
        native_hit_coverage_certified=False,phase_certified=False,physical_field_certified=False,
        GPU_used=False,Bpy_used=False,new_native_RN=0,new_root_calls=0,old_numeric_replays=0,
        full_costs="UNKNOWN_NOT_ZERO",phase_error_bound=None)

def guard(origin,end,candidate,credential,expected):
    """expected must come from launch() or explicit independent synthetic test context.
    Never accepts caller-reported t, an epsilon, an object exclusion or a SOURCE alias.
    """
    out=baseline()
    try:
        need(type(credential)is dict and set(credential)==TOKEN_KEYS and credential==expected,"closed_bound_launch_credential")
        need(type(credential["version"])is int and credential["version"]==1,"token_version")
        need(type(credential["segment"])is int and credential["segment"]==1,"token_segment")
        need(type(credential["previous_primitive_id"])is int and credential["previous_primitive_id"]>=0,"token_primitive")
        need(credential["source_id"]in ("S0","S1")and credential["scope"]=="DECLARED_SYNTHETIC_LAUNCH_NOT_PHYSICAL","token_SOURCE_scope")
        need(all(type(credential[k])is str and len(credential[k])==64 and all(c in "0123456789abcdef"for c in credential[k])
                 for k in ("scene_sha256","query_sha256","path_sha256")),"token_hashes")
        need(origin==credential["launch_point_BU"],"exact_launch_origin")
        # Python True==1 is NOT a valid typed rational credential.
        vec(credential["launch_point_BU"])
        need(type(credential["previous_barycentric"])is list and len(credential["previous_barycentric"])==3,"token_barycentric3")
        credential_bary=list(map(rat,credential["previous_barycentric"]))
        need(min(credential_bary)>=0 and sum(credential_bary)==1,"token_barycentric_simplex")
        need(type(candidate)is dict and set(candidate)=={"primitive_id","object_id","vertices_BU"},"closed_candidate")
        pid=candidate["primitive_id"];need(type(pid)is int and 0<=pid<2**31,"candidate_primitive")
        need(type(candidate["object_id"])is str and 0<len(candidate["object_id"])<=64,"candidate_object")
        need(type(candidate["vertices_BU"])is list and len(candidate["vertices_BU"])==3,"triangle3")
        o=vec(origin);e=vec(end);d=sub(e,o);need(dot(d,d)>0,"positive_segment")
        a,b,c=map(vec,candidate["vertices_BU"]);ab=sub(b,a);ac=sub(c,a);n=cross(ab,ac)
        need(dot(n,n)>0,"nondegenerate_triangle")
        out["geometry_evaluations"]=1
        den=dot(n,d);numer=dot(n,sub(a,o))
        if den==0:
            if numer==0:
                out.update(status="STOP_COPLANAR",reason="point_only_exemption_cannot_exclude_coplanar_span")
            else:out.update(status="CPU_DECLARED_NO_CONTACT_ONLY",action="NO_CONTACT",reason="parallel_disjoint")
            return out
        t=numer/den
        if t<0 or t>1:
            out.update(status="CPU_DECLARED_NO_CONTACT_ONLY",action="NO_CONTACT",reason="outside_closed_segment",plane_t=pair(t));return out
        h=tuple(o[i]+t*d[i]for i in range(3));v=sub(h,a)
        aa=dot(ab,ab);bb=dot(ab,ac);cc=dot(ac,ac);dd=dot(v,ab);ee=dot(v,ac);det=aa*cc-bb*bb
        u=(cc*dd-bb*ee)/det;w=(aa*ee-bb*dd)/det;bary=[1-u-w,u,w]
        if min(bary)<0:
            out.update(status="CPU_DECLARED_NO_CONTACT_ONLY",action="NO_CONTACT",reason="outside_triangle",plane_t=pair(t));return out
        out["contact"]=dict(primitive_id=pid,t=pair(t),point_BU=[pair(v)for v in h],barycentric=[pair(v)for v in bary])
        if t==0 and pid==credential["previous_primitive_id"]:
            need(out["contact"]["barycentric"]==credential["previous_barycentric"],"previous_barycentric_identity")
            out.update(status="CPU_DECLARED_EXACT_LAUNCH_EXCLUSION_ONLY",action="EXCLUDE_THIS_ZERO_POINT_ONLY",
                exclusion_allowed=True,reason="bound_previous_primitive_point_at_exact_zero")
        else:
            out.update(status="CPU_DECLARED_KEEP_CONTACT_ONLY",action="KEEP_CONTACT_FOR_DOWNSTREAM",
                reason="other_primitive_or_positive_t_never_excluded")
    except(ValueError,KeyError,TypeError,IndexError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out

def evaluate(k,q,e,credential_override=None):
    out=baseline()
    try:
        need(k in e,"case");need(type(q)is dict,"selector")
        need(type(q.get("source_id"))is str and q["source_id"]in ("S0","S1"),"selector_SOURCE")
        need(type(q.get("primitive_id"))is int and type(q.get("segment"))is int,"selector_integer_types")
        expected=selector(k,q["source_id"],q["primitive_id"],e)
        need(q==expected and set(q)==set(expected),"closed_selector_binding")
        x=e[k];need(q["primitive_id"]in [v["primitive_id"]for v in x["scene"]["triangles"]],"original_candidate")
        if x["result"]["status"]!="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY":
            out.update(status="STOP_UPSTREAM",reason=x["result"].get("reason"),retained_status=x["result"]["status"]);return out
        token,segment,previous=launch(x,q["source_id"])
        cand=next(v for v in x["scene"]["triangles"]if v["primitive_id"]==q["primitive_id"])
        out=guard(segment["from_BU"],segment["to_BU"],cand,token if credential_override is None else credential_override,token)
        out.update(case=k,source_id=q["source_id"],scene_sha256=q["scene_sha256"],query_sha256=q["query_sha256"],
            launch_credential=token,launch_credential_sha256=digest(token),upstream_visibility_status=x["result"]["status"],
            visibility_not_recertified=True)
    except(ValueError,KeyError,TypeError,IndexError,StopIteration)as ex:out["reason"]=str(ex)
    return out

def run(k,q):
    try:e,pins=retained();return evaluate(k,q,e)
    except(OSError,ValueError,KeyError,TypeError)as ex:
        out=baseline();out.update(status="STOP_DEPENDENCY",reason=str(ex));return out
