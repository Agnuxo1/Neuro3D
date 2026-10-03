"""Declared scene/phase equal-work and missing-cost gate; CPU HOST only."""
from pathlib import Path
import base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-total-phase-equal-work-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-EGRESS-HOST-001-CODEX.json"
PSHA="c39ab94d56294e22b8ec110e373e20e1c5f598dcb3efd144a667df4c41cfcc6b"
INTENT="HOST_SCENE_PHASE_EQUAL_WORK_ONLY"
STAGES=("startup","scene_load_validate","scene_inference_geometry","interval_certification",
    "phase_parameter_encoding","phase_arithmetic","compile_cold","cache_build_update",
    "input_serialization","host_to_device","dispatch","sync_fence","device_to_host",
    "readback_decode","output_validation","full_pipeline_cold","full_pipeline_warm")
BOUNDARY="DECLARED_SCENE_PHASE_FULL_PIPELINE_COLD_AND_WARM"
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(canonical(v))
def need(v,msg):
    if not v:raise ValueError(msg)
def capture(t):
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    need(t["rc"]==0 and not t["timed_out"]and len(b)==t["stdout_bytes"]and sha(b)==t["stdout_sha256"],"capture_integrity")
    return json.loads(b)
def load_evidence():
    b=(ROOT/PARENT).read_bytes();need(sha(b)==PSHA,"parent_identity");r=json.loads(b)
    for path,h in r["code_doc_sha256"].items():need(sha((ROOT/path).read_bytes())==h,"ancestral_pin")
    need(capture(r["independent_final_pre"])["status"]=="PASS","parent_independent_capture")
    return capture(r["test_run"])["data"]["evidence"]
def selector(case):return dict(case=case,egress_receipt_sha256=PSHA,intent=INTENT)
def cost_unknown():
    return dict(evidence_kind="UNMEASURED",boundary=BOUNDARY,stage_ns={k:None for k in STAGES},
        host_peak_bytes=None,device_peak_bytes=None,energy_joule_interval=None,artifact=None)
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,work=None,work_sha256=None,static_ledger=None,
        cost_ledger=None,same_work=None,left_work_sha256=None,right_work_sha256=None,
        promotion="STOP",GPU_launch_allowed=False,GPU_executed=False,native_promotion_allowed=False,
        scene_authenticated=False,material_authenticated=False,physical_field_certified=False,
        cost_ready=False,cost_measurement_authenticated=False,winner=None,speed_ratio=None,
        RN64_operations=0,producer_replays=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")
def _describe(model,request,e):
    out=baseline()
    try:
        need(model==MODEL,"model")
        need(type(request)is dict and set(request)=={"case","egress_receipt_sha256","intent"},"closed_selector")
        need(type(request["case"])is str and request["case"]in e,"case")
        need(request==selector(request["case"]),"selector_identity")
        a=e[request["case"]];r=a["native_result"]
        need(r["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY","parent_STOP:"+str(r["reason"]))
        entry=a["registry_entry"];q=entry["request"];g=entry["fixture"]["geometry"]
        need(digest(g["scene"])==q["original_scene_sha256"],"ORIGINAL_scene_identity")
        need(digest(g["request"])==q["literal_request_sha256"],"geometry_literal_identity")
        need(digest(q)==a["native_request"]["phase_request_sha256"],"phase_overlay_identity")
        source_rows=entry["fixture"]["rows"][:2]
        need([v["record_id"]for v in r["rows"]]==["S0","S1","S0-minus-S1"],"ALL_SOURCE_output_schema")
        work=dict(schema="declared-oblique-scene-phase-work-v1",
            entrypoint="DECLARED_ORIGINAL_SCENE_PLUS_EXPLICIT_NEW_PHASE_OVERLAY",
            geometry_model=g["model"],declared_scene=g["scene"],geometry_literal=g["request"],phase_overlay=q,
            output_contract=dict(quantity="TOTAL_DECLARED_PHASE_CYCLES_NOT_COMPLEX_FIELD",
                order=["S0","S1","S0-minus-S1"],source_count=2,relative_count=1,
                source_branch_order=[v["branch_id"]for v in q["sources"]],
                interval_semantics="ALL_SOURCE_AND_RELATIVE_CAPS_INCLUSIVE_ATOMIC",
                literal_caps_rad=[v["literal_cap_rad"]for v in r["rows"]],
                representation="CPU_PAIR64_WORDS_UNATTESTED",CPU_wire_tag=0x43545031,CPU_wire_bytes=64,
                amplitude=None,field=None,power=None),
            precision_contract="ORIGINAL_INTERVALS_PLUS_SOURCE_AND_SHARED_MATERIAL_ENCODING_AND_ALL_ADDITION_ERRORS")
        raw=b"".join(v.to_bytes(4,"little")for v in(0x43545031,6,2,1))+b"".join(bytes.fromhex(v[k])for v in r["rows"]for k in("hi","lo"))
        es=dict(case=request["case"],native_request_sha256=digest(a["native_request"]),
            phase_request_sha256=a["native_request"]["phase_request_sha256"],
            original_scene_sha256=q["original_scene_sha256"],literal_request_sha256=q["literal_request_sha256"],
            abi_tag=0x43545031,intent="HOST_CPU_TOTAL_PHASE_EGRESS_ONLY")
        logical=b"".join(bytes.fromhex(v[k]["word_le_hex"])for v in source_rows for k in("hi","lo"))
        logical+=b"".join(bytes.fromhex(v[k])for v in r["encodings"]for k in("hi","lo"))
        need(len(logical)==80 and len(raw)==64,"static_layout")
        ledger=dict(canonical_work_utf8_bytes=len(canonical(work)),canonical_scene_utf8_bytes=len(canonical(g["scene"])),
            canonical_geometry_literal_utf8_bytes=len(canonical(g["request"])),canonical_phase_overlay_utf8_bytes=len(canonical(q)),
            logical_captured_input_pair_payload_bytes=80,input_pair_framing_bytes=None,input_pair_ABI=None,
            output_envelope_bytes=64,output_sidecar_canonical_utf8_bytes=len(canonical(es)),
            output_envelope_plus_sidecar_canonical_bytes=64+len(canonical(es)),native_expected_output_sha256=sha(raw),
            captured_native_RN64_arithmetic_per_case=r["RN64_arithmetic_operations"],
            captured_native_RN64_parameter_casts_per_case=r["RN64_parameter_casts"],
            new_RN64_operations=0,geometry_operations=None,scope="SERIALIZED_SIZES_AND_CAPTURED_COUNTS_NOT_RUNTIME_COSTS")
        out.update(status="HOST_DECLARED_WORK_MANIFEST_ONLY",work=work,work_sha256=digest(work),static_ledger=ledger,cost_ledger=cost_unknown())
    except(ValueError,KeyError,TypeError,IndexError,OSError)as ex:out["reason"]=str(ex)
    return out
def describe(model,request):
    try:e=load_evidence()
    except(ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _describe(model,request,e)
def _cost_reason(c):
    need(type(c)is dict and set(c)==set(cost_unknown()),"closed_cost_record")
    need(c["evidence_kind"]in("UNMEASURED","SYNTHETIC_CONTROL","DECLARED_EXTERNAL_MEASUREMENT","QA_CAPTURE"),"cost_evidence_kind")
    need(c["boundary"]==BOUNDARY,"full_pipeline_boundary")
    need(type(c["stage_ns"])is dict and set(c["stage_ns"])==set(STAGES),"complete_stage_schema")
    for k,v in c["stage_ns"].items():need(v is None or(type(v)is int and v>=0),"stage_ns_integer_or_unknown")
    for k in("host_peak_bytes","device_peak_bytes"):
        v=c[k];need(v is None or(type(v)is int and v>=0),"memory_bytes_integer_or_unknown")
    v=c["energy_joule_interval"]
    need(v is None or(type(v)is list and len(v)==2 and all(type(n)is int and n>=0 for n in v)and v[0]<=v[1]),"energy_interval_joules_or_unknown")
    a=c["artifact"]
    need(a is None or(type(a)is dict and set(a)=={"path","sha256","bytes"}and type(a["path"])is str and type(a["sha256"])is str
        and len(a["sha256"])==64 and set(a["sha256"])<=set("0123456789abcdef")and type(a["bytes"])is int and a["bytes"]>0),"cost_artifact_metadata")
    if c["evidence_kind"]=="QA_CAPTURE":return "QA_TIMING_NOT_FULL_PIPELINE"
    if any(v is None for v in c["stage_ns"].values())or any(c[k]is None for k in("host_peak_bytes","device_peak_bytes","energy_joule_interval")):
        return "MISSING_FULL_COSTS"
    need(c["stage_ns"]["full_pipeline_cold"]>0 and c["stage_ns"]["full_pipeline_warm"]>0,"positive_full_pipeline_ns")
    if c["evidence_kind"]=="SYNTHETIC_CONTROL":return "SYNTHETIC_COSTS_NOT_MEASUREMENTS"
    if c["evidence_kind"]=="UNMEASURED":return "UNMEASURED_VALUES_NOT_AUTHENTICATED"
    return "EXTERNAL_COST_ARTIFACT_NOT_BOUND"
def _compare(model,left,right,costs,e):
    out=baseline()
    try:
        l=_describe(model,left,e);r=_describe(model,right,e)
        need(l["status"]=="HOST_DECLARED_WORK_MANIFEST_ONLY","left:"+str(l["reason"]))
        need(r["status"]=="HOST_DECLARED_WORK_MANIFEST_ONLY","right:"+str(r["reason"]))
        out.update(left_work_sha256=l["work_sha256"],right_work_sha256=r["work_sha256"],same_work=l["work_sha256"]==r["work_sha256"])
        need(out["same_work"],"DIFFERENT_SCENE_PHASE_WORK")
        need(type(costs)is dict and set(costs)=={"left","right"},"closed_cost_pair")
        reasons=[_cost_reason(costs[k])for k in("left","right")]
        out.update(status="HOST_SAME_WORK_ONLY_COSTS_STOP",reason=";".join(reasons),cost_ledger=costs)
        # No attested full-pipeline measurement backend is implemented in this HOST contract.
    except(ValueError,KeyError,TypeError,IndexError)as ex:out["reason"]=str(ex)
    return out
def compare(model,left,right,costs):
    try:e=load_evidence()
    except(ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _compare(model,left,right,costs,e)
