"""Independent overlay receipt verifier: no consumer/producer/compiler import."""
from pathlib import Path
from fractions import Fraction as F
import ast,base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json"
MODEL="precision-oblique-source-material-interval-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-V2-EGRESS-HOST-001-CODEX.json"
PSHA="75d7bece210984fc2c30d761946a7285f1f2bcacce68208b5b44d71e5e85972a"
GEOMETRY="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
CASES=("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60")
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(v):return [v.numerator,v.denominator]
def capture(r):
    t=r["test_run"];raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert len(raw)==t["stdout_bytes"]and sha(raw)==t["stdout_sha256"]and t["rc"]==0 and not t["timed_out"]
    v=json.loads(raw);assert v["status"]=="PASS";return v
def need(v,msg):
    if not v:raise ValueError(msg)
def rat(q):
    need(type(q)is list and len(q)==2 and all(type(n)is int for n in q),"typed_rational")
    need(q[1]>0 and all(abs(n).bit_length()<=256 for n in q),"bounded_rational")
    v=F(q[0],q[1]);need(abs(v)<=1000000,"rational_magnitude");return v
def span(q):
    need(type(q)is list and len(q)==2,"phase_interval")
    a,b=map(rat,q);need(b>=a,"ordered_interval");return (a+b)/2,(b-a)/2
def independent(run,e):
    q=run["request"];diagnostics=[]
    try:
        need(run["model"]==MODEL,"model")
        need(type(q)is dict and set(q)=={"case","parent_receipt_sha256","original_scene_sha256","literal_request_sha256",
               "overlay","units","authentication","sources","material"},"closed_request")
        need(q["case"]in CASES,"case");entry=e[q["case"]];p=entry["packet"];rows=entry["rows"];geom=entry["geometry"]
        need((q["parent_receipt_sha256"],q["original_scene_sha256"],q["literal_request_sha256"])==
                (PSHA,p["scene_sha256"],p["literal_sha256"]),"parent_ORIGINAL_literal")
        need(q["overlay"]=="NEW_DECLARED_PHASE_OVERLAY"and q["units"]=={"phase":"cycles","cap":"rad"}
                and q["authentication"]=="DECLARED_NOT_PHYSICALLY_AUTHENTICATED","explicit_declared_units")
        assert digest(geom["scene"])==p["scene_sha256"]
        need(type(q["sources"])is list and len(q["sources"])==2,"ALL_SOURCE")
        gamma=[]
        for j,s in enumerate(q["sources"]):
            need(type(s)is dict and set(s)=={"record_id","branch_id","phase_interval_cycles"}and
                 (s["record_id"],s["branch_id"])==("S"+str(j),"S"+str(j)+"/mirror"),"SOURCE_branch_order")
            gamma.append(span(s["phase_interval_cycles"]))
        m=q["material"];need(type(m)is dict and set(m)=={"object_id","primitive_id","profile","phase_interval_cycles"},"closed_material")
        need(type(m["primitive_id"])is int and m["primitive_id"]==1 and
             m["profile"]=="DECLARED_COMPLETE_SHARED_COEFFICIENT_PHASE_CYCLES","material_primitive_profile")
        need(m["object_id"]=="oblique_common_fixture","material_object")
        mu,mrad=span(m["phase_interval_cycles"]);fits=[]
        for j,r in enumerate(rows[:2]):
            a,b=map(rat,r["interval"]);v=rat(r["pair_value"]);gm,gr=gamma[j]
            midpoint=(a+b)/2+gm+mu;radius=(b-a)/2+gr+mrad
            nominal=v+gm+mu
            bound=8*(abs(v-(a+b)/2)+(b-a)/2+gr+mrad)
            cap=rat(r["literal_cap_rad"]);assert cap==rat(p["source_literal_caps"][j])==rat(geom["request"]["source_width_caps_rad"][j])
            diagnostics.append(dict(record_id="S"+str(j),branch_id="S"+str(j)+"/mirror",
                 nominal_declared_cycles=pair(nominal),interval_cycles=[pair(midpoint-radius),pair(midpoint+radius)],
                 error_bound_rad=pair(bound),literal_cap_rad=pair(cap),fits=bound<=cap));fits.append(bound<=cap)
        r=rows[2];a,b=map(rat,r["parent_relative_CONTROL_ONLY"]["interval"]);v=rat(r["pair_value"])
        offset=gamma[0][0]-gamma[1][0];radius=(b-a)/2+gamma[0][1]+gamma[1][1]
        mid=(a+b)/2+offset;nominal=v+offset
        bound=8*(abs(v-(a+b)/2)+(b-a)/2+gamma[0][1]+gamma[1][1]);cap=rat(r["literal_cap_rad"])
        assert cap==rat(p["retained_CPU_budget"]["literal_cap_rad"])==rat(geom["request"]["relative_width_cap_rad"])
        diagnostics.append(dict(record_id="S0-minus-S1",branch_id="relative",nominal_declared_cycles=pair(nominal),
                interval_cycles=[pair(mid-radius),pair(mid+radius)],error_bound_rad=pair(bound),
                literal_cap_rad=pair(cap),fits=bound<=cap,shared_material_cancellation="DECLARED_SAME_VARIABLE_ONLY",
                propagation_only_V2_cycles=r["pair_value"],source_phase_offset_cycles=pair(offset)))
        need(all(fits),"ALL_SOURCE_cap");need(bound<=cap,"relative_cap")
        return None,diagnostics
    except ValueError as ex:return str(ex),diagnostics
def main():
    raw=(ROOT/RECEIPT).read_bytes();r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
    suite=capture(r);assert suite["groups"]==5;d=suite["data"];e=d["evidence"]
    assert sha((ROOT/PARENT).read_bytes())==PSHA
    assert sha((ROOT/GEOMETRY).read_bytes())=="139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
    ed=capture(json.loads((ROOT/PARENT).read_bytes()))["data"]["evidence"]
    gd=capture(json.loads((ROOT/GEOMETRY).read_bytes()))["data"]["inputs"]
    assert set(e)==set(CASES)
    for c in CASES:assert e[c]==dict(ed[c],geometry=gd[c.removeprefix("parent_")])
    tree=ast.parse((ROOT/"Blender/benchmarks/capacity_audit/oblique_source_material_interval_HOST_v1.py").read_bytes())
    pub=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=="evaluate")
    assert [a.arg for a in pub.args.args]==["model","q"]and pub.args.kwarg is None
    assert any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=="load_evidence"for n in ast.walk(pub))
    ids=set();passed=0;stopped=0
    for run in d["runs"]:
        assert run["id"]not in ids;ids.add(run["id"])
        reason,diags=independent(run,e);out=run["result"]
        assert out["reason"]==reason and out["diagnostics"]==diags,run["id"]
        assert out["status"]==("HOST_DECLARED_TOTAL_PHASE_INTERVAL_ONLY"if reason is None else "STOP")
        assert out["rows"]==(diags if reason is None else [])and out["promotion"]=="STOP"
        for k in("GPU_executed","GPU_launch_allowed","scene_authenticated","material_authenticated","physical_field_certified",
                 "native_promotion_allowed","interference_phase_certified","V2_total_phase_backend_bound"):assert out[k]is False
        assert out["amplitude"]is out["field"]is out["power"]is None
        assert out["compiler_calls"]==out["new_RN_operations"]==out["frozen_producer_replays"]==0
        assert out["full_costs"]=="UNMEASURED_NOT_ZERO"
        if diags:assert out["request_sha256"]==digest(run["request"])
        if reason is None:
            passed+=1;assert out["geometry_original_sha256"]==e[run["request"]["case"]]["packet"]["scene_sha256"]
            assert out["scope"]=="RATIONAL_OVERLAY_NOT_ENCODED_NOT_GPU_ARITHMETIC_NOT_FIELD"
        else:stopped+=1
    required=set(CASES)|{"source1_eighth_cycle","complete_coefficient_plus_one","large_shared_declared_not_encoded",
       "shared_material_uncertainty_SOURCE_FAIL_relative_fits","source0_uncertainty_FAIL","source1_uncertainty_FAIL",
       "bounded_source_uncertainty","opposite_source_phase","missing_SOURCE","reordered_SOURCE","cross_SOURCE_branch",
       "missing_phase_not_zero","unknown_phase_not_zero","reversed_phase_interval","bool_rational","zero_denominator",
       "oversized_rational","bool_primitive","wrong_material_primitive","wrong_material_object","implicit_material_sign",
       "unknown_material_not_zero","separate_materials_not_shared","cap_override","asserted_physical_auth","wrong_units","wrong_model"}
    required|={"wrong_"+k for k in("parent_receipt_sha256","original_scene_sha256","literal_request_sha256")}
    assert ids==required and passed==9 and stopped==len(ids)-9
    counter=next(q for q in d["runs"]if q["id"]=="shared_material_uncertainty_SOURCE_FAIL_relative_fits")["result"]
    assert counter["diagnostics"][2]["fits"]and not counter["diagnostics"][0]["fits"]and counter["rows"]==[]
    assert r["promotion"]=="STOP"and r["GPU_launch_allowed"]is r["V2_total_phase_backend_bound"]is False
    print(json.dumps(dict(status="PASS",cases=len(ids),admitted_declared=passed,stopped=stopped,pins=len(r["code_doc_sha256"]),
            shared_material_no_SOURCE_rescue=True,GPU_launch_allowed=False,V2_total_phase_backend_bound=False)))
if __name__=="__main__":main()
