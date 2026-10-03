"""Declared oblique SOURCE/material phase interval overlay. HOST rationals, no float/RN/GPU."""
from pathlib import Path
from fractions import Fraction as F
import base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-source-material-interval-HOST-v1"
CASES=("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60")
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-V2-EGRESS-HOST-001-CODEX.json"
PARENT_SHA="75d7bece210984fc2c30d761946a7285f1f2bcacce68208b5b44d71e5e85972a"
GEOMETRY="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
GEOMETRY_SHA="139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def require(ok,message):
    if not ok:raise ValueError(message)
def rational(v):
    require(type(v)is list and len(v)==2 and all(type(n)is int for n in v),"typed_rational")
    require(v[1]>0 and max(abs(v[0]).bit_length(),v[1].bit_length())<=256,"bounded_rational")
    q=F(*v);require(abs(q)<=10**6,"rational_magnitude");return q
def interval(v):
    require(type(v)is list and len(v)==2,"phase_interval")
    a,b=map(rational,v);require(a<=b,"ordered_interval");return a,b
def sealed(path,h):
    raw=(ROOT/path).read_bytes();require(sha(raw)==h,"receipt_identity");r=json.loads(raw)
    for p,s in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==s,"ancestral_pin")
    t=r["test_run"];raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    require(len(raw)==t["stdout_bytes"]and sha(raw)==t["stdout_sha256"]and t["rc"]==0 and not t["timed_out"],"capture_integrity")
    d=json.loads(raw);require(d["status"]=="PASS","parent_status");return d["data"]
def load_evidence():
    e=sealed(PARENT,PARENT_SHA)["evidence"];g=sealed(GEOMETRY,GEOMETRY_SHA)["inputs"]
    return {c:dict(e[c],geometry=g[c.removeprefix("parent_")])for c in CASES}
def request(case,e):
    p=e[case]["packet"]
    return dict(case=case,parent_receipt_sha256=PARENT_SHA,original_scene_sha256=p["scene_sha256"],
          literal_request_sha256=p["literal_sha256"],overlay="NEW_DECLARED_PHASE_OVERLAY",
          units=dict(phase="cycles",cap="rad"),authentication="DECLARED_NOT_PHYSICALLY_AUTHENTICATED",
          sources=[dict(record_id="S"+str(j),branch_id="S"+str(j)+"/mirror",phase_interval_cycles=[[0,1],[0,1]])for j in range(2)],
          material=dict(object_id="oblique_common_fixture",primitive_id=1,
                  profile="DECLARED_COMPLETE_SHARED_COEFFICIENT_PHASE_CYCLES",phase_interval_cycles=[[1,2],[1,2]]))
def _evaluate_fixture(model,q,e):
    out=dict(model=MODEL,status="STOP",reason=None,rows=[],diagnostics=[],promotion="STOP",
        GPU_executed=False,GPU_launch_allowed=False,scene_authenticated=False,material_authenticated=False,
        physical_field_certified=False,native_promotion_allowed=False,interference_phase_certified=False,
        amplitude=None,field=None,power=None,full_costs="UNMEASURED_NOT_ZERO",new_RN_operations=0,
        compiler_calls=0,frozen_producer_replays=0,V2_total_phase_backend_bound=False)
    try:
        require(model==MODEL,"model")
        keys={"case","parent_receipt_sha256","original_scene_sha256","literal_request_sha256","overlay","units","authentication","sources","material"}
        require(type(q)is dict and set(q)==keys,"closed_request");require(q["case"]in CASES,"case")
        c=q["case"];p=e[c]["packet"];rows=e[c]["rows"];g=e[c]["geometry"]
        require(q["parent_receipt_sha256"]==PARENT_SHA and q["original_scene_sha256"]==p["scene_sha256"]
                and q["literal_request_sha256"]==p["literal_sha256"],"parent_ORIGINAL_literal")
        require(q["overlay"]=="NEW_DECLARED_PHASE_OVERLAY"and q["units"]==dict(phase="cycles",cap="rad")
                and q["authentication"]=="DECLARED_NOT_PHYSICALLY_AUTHENTICATED","explicit_declared_units")
        require(digest(g["scene"])==p["scene_sha256"]and g["request"]["original_scene_sha256"]==p["scene_sha256"],"geometry_binding")
        require(len(rows)==3 and [r["record_id"]for r in rows]==["S0","S1","S0-minus-S1"],"parent_completeness")
        require(type(q["sources"])is list and len(q["sources"])==2,"ALL_SOURCE")
        source_phase=[]
        for j,s in enumerate(q["sources"]):
            require(type(s)is dict and set(s)=={"record_id","branch_id","phase_interval_cycles"}
                    and s["record_id"]=="S"+str(j)and s["branch_id"]=="S"+str(j)+"/mirror","SOURCE_branch_order")
            source_phase.append(interval(s["phase_interval_cycles"]))
        m=q["material"];require(type(m)is dict and set(m)=={"object_id","primitive_id","profile","phase_interval_cycles"},"closed_material")
        require(type(m["primitive_id"])is int and m["primitive_id"]==g["request"]["root_primitive_id"]==1
                and m["profile"]=="DECLARED_COMPLETE_SHARED_COEFFICIENT_PHASE_CYCLES","material_primitive_profile")
        primitive=next(t for t in g["scene"]["triangles"]if t["primitive_id"]==m["primitive_id"])
        require(m["object_id"]==primitive["object_id"]=="oblique_common_fixture","material_object")
        mu=interval(m["phase_interval_cycles"]);mu_mid=sum(mu)/2;pending=[];nominals=[];bounds=[]
        for j,r in enumerate(rows[:2]):
            require(r["original_scene_sha256"]==p["scene_sha256"]and r["literal_request_sha256"]==p["literal_sha256"],"SOURCE_parent_identity")
            lo,hi=map(rational,r["interval"]);v=rational(r["pair_value"]);ga,gb=source_phase[j];gm=(ga+gb)/2
            low,high=lo+ga+mu[0],hi+gb+mu[1];nominal=v+gm+mu_mid
            bound=8*max(abs(nominal-low),abs(nominal-high));cap=rational(r["literal_cap_rad"])
            require(cap==rational(p["source_literal_caps"][j])and cap==rational(g["request"]["source_width_caps_rad"][j]),"SOURCE_cap_identity")
            row=dict(record_id=r["record_id"],branch_id=r["branch_id"],nominal_declared_cycles=pair(nominal),
                interval_cycles=[pair(low),pair(high)],error_bound_rad=pair(bound),literal_cap_rad=pair(cap),fits=bound<=cap)
            pending.append(row);bounds.append(bound<=cap);nominals.append((v,gm))
        relative_interval=rows[2]["parent_relative_CONTROL_ONLY"]["interval"]
        lo,hi=map(rational,relative_interval)
        low,high=lo+source_phase[0][0]-source_phase[1][1],hi+source_phase[0][1]-source_phase[1][0]
        value=rational(rows[2]["pair_value"])+nominals[0][1]-nominals[1][1]
        bound=8*max(abs(value-low),abs(value-high));cap=rational(rows[2]["literal_cap_rad"])
        require(cap==rational(p["retained_CPU_budget"]["literal_cap_rad"])and cap==rational(g["request"]["relative_width_cap_rad"]),"relative_cap_identity")
        rel=dict(record_id="S0-minus-S1",branch_id="relative",nominal_declared_cycles=pair(value),
            interval_cycles=[pair(low),pair(high)],error_bound_rad=pair(bound),literal_cap_rad=pair(cap),fits=bound<=cap,
            shared_material_cancellation="DECLARED_SAME_VARIABLE_ONLY",propagation_only_V2_cycles=rows[2]["pair_value"],
            source_phase_offset_cycles=pair(nominals[0][1]-nominals[1][1]))
        out["diagnostics"]=pending+[rel];out["request_sha256"]=digest(q)
        require(all(bounds),"ALL_SOURCE_cap");require(rel["fits"],"relative_cap")
        out.update(status="HOST_DECLARED_TOTAL_PHASE_INTERVAL_ONLY",rows=pending+[rel],geometry_original_sha256=p["scene_sha256"],
                  scope="RATIONAL_OVERLAY_NOT_ENCODED_NOT_GPU_ARITHMETIC_NOT_FIELD",
                  costs=dict(source_records=2,relative_records=1,geometry="REUSED_SEALED",phase_encoding="UNMEASURED_NOT_ZERO",
                             phase_backend="NOT_IMPLEMENTED",all_lifecycle="UNMEASURED_NOT_ZERO"))
    except (ValueError,TypeError,KeyError,IndexError,StopIteration,OverflowError,OSError)as ex:out["reason"]=str(ex)
    return out
def evaluate(model,q):
    try:e=load_evidence()
    except (ValueError,TypeError,KeyError,OSError)as ex:
        r=_evaluate_fixture("INVALID_EVIDENCE",q,{});r["reason"]="evidence_integrity:"+str(ex);return r
    return _evaluate_fixture(model,q,e)
