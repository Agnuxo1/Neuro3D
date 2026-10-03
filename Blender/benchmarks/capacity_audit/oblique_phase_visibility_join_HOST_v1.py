"""Opt-in exact scene/path join of sealed visibility and TOTALphase controls.
Matching copied HOST inputs is not device, scene or physical authentication.
"""
from pathlib import Path
import json
import oblique_total_phase_readback_HOST_v1 as rb
import visibility_ledger_coverage_HOST_v1 as vc
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-total-phase-visibility-join-HOST-v1"
ORIGIN=rb.ORIGIN
READBACK="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-READBACK-HOST-001-CODEX.json"
RSHA="0921d0ead6cfbba22145d3adc908210df22324f1f3b00b8f07ff9e444e456889"
COVERAGE="coordinacion/respuestas/PRECISION-VISIBILITY-LEDGER-COVERAGE-HOST-001-CODEX.json"
CSHA="dda978eced1bf958c61325e3d29f013b713ad5524ed9f39bc474d9ab9028f45f"
LENGTH="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
LSHA="139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
INTENT="HOST_UNATTESTED_SAME_SCENE_PATH_JOIN_ONLY"

def need(v,why):
    if not v:raise ValueError(why)

def exact(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return set(a)==set(b) and all(exact(a[k],b[k])for k in a)
    if type(a)is list:return len(a)==len(b) and all(exact(x,y)for x,y in zip(a,b))
    return a==b

def sealed(path,h,pins):
    raw=(ROOT/path).read_bytes();need(rb.sha(raw)==h,"receipt_identity:"+path)
    r=json.loads(raw)
    for p,s in r["code_doc_sha256"].items():
        need(p not in pins or pins[p]==s,"pin_conflict")
        q=Path(p);need(rb.sha((q if q.is_absolute()else ROOT/q).read_bytes())==s,"ancestral_pin:"+p)
        pins[p]=s
    pins[path]=h
    return r

def retained():
    pins={}
    a=sealed(READBACK,RSHA,pins);b=sealed(COVERAGE,CSHA,pins)
    need(rb.capture(a["test_run"])["status"]=="PASS" and rb.capture(b["test_run"])["status"]=="PASS","parent_test_capture")
    phases,_=rb.retained();visibility=vc.load_evidence()
    native=rb.capture(json.loads((ROOT/rb.NATIVE).read_bytes())["test_run"])["data"]
    length=sealed(LENGTH,LSHA,pins);ld=rb.capture(length["test_run"])["data"]
    geometries={}
    for case,entry in phases.items():
        if entry["input"]is None:continue
        reg=native["registry"][case];g=reg["fixture"]["geometry"];q=reg["request"]
        scene=rb.digest(g["scene"]);literal=rb.digest(g["request"])
        need(scene==entry["original_scene_sha256"]==q["original_scene_sha256"],"phase_scene_chain")
        need(literal==entry["literal_request_sha256"]==q["literal_request_sha256"],"phase_literal_chain")
        need(rb.digest(q)==entry["phase_request_sha256"],"phase_overlay_chain")
        matches=[k for k,x in ld["inputs"].items()if exact(x,g)]
        need(len(matches)==1,"unique_sealed_geometry")
        lr=ld["results"][matches[0]]
        need(lr["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY" and lr["original_scene_sha256"]==scene and lr["literal_request_sha256"]==literal,"sealed_length_chain")
        paths=lr["paths"];need([p["source_id"]for p in paths]==["S0","S1"],"SOURCE_path_order")
        need([x["record_id"]for x in q["sources"]]==["S0","S1"] and [x["branch_id"]for x in q["sources"]]==["S0/mirror","S1/mirror"],"phase_SOURCE_order")
        need(q["material"]["primitive_id"]==g["request"]["root_primitive_id"],"material_root_binding")
        geometries[case]=dict(geometry=g,paths=paths,paths_sha256=rb.digest(paths),phase_request=q)
    need(len(phases)==46 and len(geometries)==11 and len(visibility)==44,"sealed_census")
    return dict(phases=phases,visibility=visibility,geometries=geometries),pins

def selector(phase_case,visibility_case,e):
    g=e["geometries"].get(phase_case)
    return dict(phase_case=phase_case,visibility_case=visibility_case,
        phase_readback_receipt_sha256=RSHA,visibility_coverage_receipt_sha256=CSHA,
        phase_selector=rb.selector(phase_case,e["phases"]),visibility_selector=vc.selector(visibility_case),
        paths_sha256=g["paths_sha256"]if g else None,intent=INTENT)

def baseline():
    return dict(model=MODEL,status="STOP",reason=None,rows=[],verified_phase_rows=0,verified_visibility_rows=0,
        joined_scene_sha256=None,joined_literal_sha256=None,joined_paths_sha256=None,output_sha256=None,
        phase_diagnostics=None,visibility_diagnostics=None,promotion="STOP",
        GPU_launch_allowed=False,GPU_executed=False,GPU_guard_certified=False,
        scene_authenticated=False,material_authenticated=False,ledger_authenticated=False,
        device_egress_authenticated=False,fence_readback_authenticated=False,native_promotion_allowed=False,
        physical_field_certified=False,amplitude=None,field=None,power=None,full_costs="UNMEASURED_NOT_ZERO",
        RN64_operations=0,compiler_calls=0,producer_replays=0)

def _compare(model,request,ledger,input_bytes,output_bytes,origin,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(origin)is str and origin==ORIGIN,"only_unattested_HOST_origin")
        need(type(request)is dict and type(request.get("phase_case"))is str and request["phase_case"]in e["phases"],"closed_phase_case")
        need(type(request.get("visibility_case"))is str and request["visibility_case"]in e["visibility"],"closed_visibility_case")
        pc=request["phase_case"];vi=request["visibility_case"]
        need(exact(request,selector(pc,vi,e)),"closed_selector_identity")
        phase=e["phases"][pc];vr=e["visibility"][vi];r=vr["result"]
        need(phase["input"]is not None,"phase_parent_STOP:"+str(phase["native"]["reason"]))
        need(r["status"]=="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY","visibility_parent_STOP:"+str(r["reason"]))
        g=e["geometries"][pc];geo=g["geometry"]
        need(exact(geo["scene"],vr["scene"]) and rb.digest(vr["scene"])==phase["original_scene_sha256"]==r["original_scene_sha256"],"same_ORIGINAL_scene")
        need(exact(geo["request"],vr["request"]) and rb.digest(vr["request"])==phase["literal_request_sha256"]==r["literal_request_sha256"],"same_literal_request")
        need(exact(g["paths"],vr["parent_result"]["paths"]) and rb.digest(vr["parent_result"]["paths"])==request["paths_sha256"],"same_SOURCE_paths_certificates")
        vv=vc._validate(vc.MODEL,request["visibility_selector"],ledger,e["visibility"])
        out["visibility_diagnostics"]=vv
        need(vv["status"]=="HOST_UNATTESTED_VISIBILITY_LEDGER_MATCH","visibility_ledger:"+str(vv["reason"]))
        pp=rb._compare(rb.MODEL,request["phase_selector"],input_bytes,output_bytes,origin,e["phases"])
        out["phase_diagnostics"]=pp
        need(pp["status"]=="HOST_UNATTESTED_TOTAL_PHASE_MATCH","phase_readback:"+str(pp["reason"]))
        out.update(status="HOST_UNATTESTED_SAME_SCENE_PATH_PHASE_VISIBILITY_MATCH",
            rows=pp["rows"],verified_phase_rows=3,verified_visibility_rows=vv["verified_rows"],
            joined_scene_sha256=phase["original_scene_sha256"],joined_literal_sha256=phase["literal_request_sha256"],
            joined_paths_sha256=g["paths_sha256"],output_sha256=pp["output_sha256"])
    except(ValueError,KeyError,TypeError,IndexError,OSError)as ex:out["reason"]=str(ex)
    return out

def compare(model,request,ledger,input_bytes,output_bytes,origin):
    try:e,_=retained()
    except(ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _compare(model,request,ledger,input_bytes,output_bytes,origin,e)
