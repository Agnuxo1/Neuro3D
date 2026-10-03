"""Independent scene/phase work identity and unknown-cost verifier; no core imports."""
from pathlib import Path
import ast,base64,copy,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-OBLIQUE-TOTAL-PHASE-EQUAL-WORK-HOST-001"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-EGRESS-HOST-001-CODEX.json"
PSHA="c39ab94d56294e22b8ec110e373e20e1c5f598dcb3efd144a667df4c41cfcc6b"
MODEL="precision-oblique-total-phase-equal-work-HOST-v1";INTENT="HOST_SCENE_PHASE_EQUAL_WORK_ONLY"
STAGES=("startup","scene_load_validate","scene_inference_geometry","interval_certification","phase_parameter_encoding",
    "phase_arithmetic","compile_cold","cache_build_update","input_serialization","host_to_device","dispatch",
    "sync_fence","device_to_host","readback_decode","output_validation","full_pipeline_cold","full_pipeline_warm")
BOUNDARY="DECLARED_SCENE_PHASE_FULL_PIPELINE_COLD_AND_WARM"
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(canonical(v))
def capture(t):
    assert t["rc"]==0 and t["timed_out"]is False and t["stderr"]==""
    assert t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60 and 0<=t["elapsed_seconds"]<=65
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True));assert sha(b)==t["stdout_sha256"]and len(b)==t["stdout_bytes"]
    return json.loads(b)
def sel(c):return dict(case=c,egress_receipt_sha256=PSHA,intent=INTENT)
def unknown():
    return dict(evidence_kind="UNMEASURED",boundary=BOUNDARY,stage_ns={k:None for k in STAGES},
        host_peak_bytes=None,device_peak_bytes=None,energy_joule_interval=None,artifact=None)
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,work=None,work_sha256=None,static_ledger=None,
        cost_ledger=None,same_work=None,left_work_sha256=None,right_work_sha256=None,promotion="STOP",
        GPU_launch_allowed=False,GPU_executed=False,native_promotion_allowed=False,scene_authenticated=False,
        material_authenticated=False,physical_field_certified=False,cost_ready=False,cost_measurement_authenticated=False,
        winner=None,speed_ratio=None,RN64_operations=0,producer_replays=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")
def description(model,request,ev):
    out=baseline();reason=None
    if model!=MODEL:reason="model"
    elif type(request)is not dict or set(request)!={"case","egress_receipt_sha256","intent"}:reason="closed_selector"
    elif type(request["case"])is not str or request["case"]not in ev:reason="case"
    elif request!=sel(request["case"]):reason="selector_identity"
    elif ev[request["case"]]["native_result"]["status"]!="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY":
        reason="parent_STOP:"+str(ev[request["case"]]["native_result"]["reason"])
    if reason:out["reason"]=reason;return out
    a=ev[request["case"]];ent=a["registry_entry"];q=ent["request"];g=ent["fixture"]["geometry"];r=a["native_result"]
    assert digest(g["scene"])==q["original_scene_sha256"]and digest(g["request"])==q["literal_request_sha256"]
    assert digest(q)==a["native_request"]["phase_request_sha256"]
    assert [v["record_id"]for v in r["rows"]]==["S0","S1","S0-minus-S1"]
    work=dict(schema="declared-oblique-scene-phase-work-v1",
        entrypoint="DECLARED_ORIGINAL_SCENE_PLUS_EXPLICIT_NEW_PHASE_OVERLAY",geometry_model=g["model"],declared_scene=g["scene"],
        geometry_literal=g["request"],phase_overlay=q,output_contract=dict(quantity="TOTAL_DECLARED_PHASE_CYCLES_NOT_COMPLEX_FIELD",
            order=["S0","S1","S0-minus-S1"],source_count=2,relative_count=1,source_branch_order=[v["branch_id"]for v in q["sources"]],
            interval_semantics="ALL_SOURCE_AND_RELATIVE_CAPS_INCLUSIVE_ATOMIC",literal_caps_rad=[v["literal_cap_rad"]for v in r["rows"]],
            representation="CPU_PAIR64_WORDS_UNATTESTED",CPU_wire_tag=0x43545031,CPU_wire_bytes=64,amplitude=None,field=None,power=None),
        precision_contract="ORIGINAL_INTERVALS_PLUS_SOURCE_AND_SHARED_MATERIAL_ENCODING_AND_ALL_ADDITION_ERRORS")
    raw=bytes.fromhex("31505443060000000200000001000000")+b"".join(bytes.fromhex(v[k])for v in r["rows"]for k in("hi","lo"))
    side=dict(case=request["case"],native_request_sha256=digest(a["native_request"]),phase_request_sha256=digest(q),
        original_scene_sha256=digest(g["scene"]),literal_request_sha256=digest(g["request"]),abi_tag=0x43545031,intent="HOST_CPU_TOTAL_PHASE_EGRESS_ONLY")
    # Count captured byte strings independently; do not invent a framing or runtime ABI.
    allwords=[v[k]["word_le_hex"]for v in ent["fixture"]["rows"][:2]for k in("hi","lo")]
    allwords += [v[k]for v in r["encodings"]for k in("hi","lo")]
    assert len(allwords)==10 and all(len(bytes.fromhex(v))==8 for v in allwords)
    assert all((int.from_bytes(bytes.fromhex(v),"little")>>52)&2047!=2047 for v in allwords)
    assert r["RN64_arithmetic_operations"]==130 and r["RN64_parameter_casts"]==6
    ledger=dict(canonical_work_utf8_bytes=len(canonical(work)),canonical_scene_utf8_bytes=len(canonical(g["scene"])),
        canonical_geometry_literal_utf8_bytes=len(canonical(g["request"])),canonical_phase_overlay_utf8_bytes=len(canonical(q)),
        logical_captured_input_pair_payload_bytes=sum(len(bytes.fromhex(v))for v in allwords),input_pair_framing_bytes=None,input_pair_ABI=None,
        output_envelope_bytes=len(raw),output_sidecar_canonical_utf8_bytes=len(canonical(side)),
        output_envelope_plus_sidecar_canonical_bytes=len(raw)+len(canonical(side)),native_expected_output_sha256=sha(raw),
        captured_native_RN64_arithmetic_per_case=130,captured_native_RN64_parameter_casts_per_case=6,new_RN64_operations=0,
        geometry_operations=None,scope="SERIALIZED_SIZES_AND_CAPTURED_COUNTS_NOT_RUNTIME_COSTS")
    out.update(status="HOST_DECLARED_WORK_MANIFEST_ONLY",work=work,work_sha256=digest(work),static_ledger=ledger,cost_ledger=unknown())
    return out
def cost_reason(c):
    if type(c)is not dict or set(c)!=set(unknown()):return "closed_cost_record"
    if c["evidence_kind"]not in("UNMEASURED","SYNTHETIC_CONTROL","DECLARED_EXTERNAL_MEASUREMENT","QA_CAPTURE"):return "cost_evidence_kind"
    if c["boundary"]!=BOUNDARY:return "full_pipeline_boundary"
    if type(c["stage_ns"])is not dict or set(c["stage_ns"])!=set(STAGES):return "complete_stage_schema"
    if any(v is not None and (type(v)is not int or v<0)for v in c["stage_ns"].values()):return "stage_ns_integer_or_unknown"
    if any(c[k]is not None and(type(c[k])is not int or c[k]<0)for k in("host_peak_bytes","device_peak_bytes")):return "memory_bytes_integer_or_unknown"
    v=c["energy_joule_interval"]
    if v is not None and(type(v)is not list or len(v)!=2 or any(type(n)is not int or n<0 for n in v)or v[0]>v[1]):return "energy_interval_joules_or_unknown"
    a=c["artifact"]
    if a is not None and(type(a)is not dict or set(a)!={"path","sha256","bytes"}or type(a["path"])is not str or type(a["sha256"])is not str
        or len(a["sha256"])!=64 or any(ch not in"0123456789abcdef"for ch in a["sha256"])or type(a["bytes"])is not int or a["bytes"]<=0):return "cost_artifact_metadata"
    if c["evidence_kind"]=="QA_CAPTURE":return "QA_TIMING_NOT_FULL_PIPELINE"
    if any(v is None for v in c["stage_ns"].values())or any(c[k]is None for k in("host_peak_bytes","device_peak_bytes","energy_joule_interval")):return "MISSING_FULL_COSTS"
    if c["stage_ns"]["full_pipeline_cold"]<=0 or c["stage_ns"]["full_pipeline_warm"]<=0:return "positive_full_pipeline_ns"
    return {"SYNTHETIC_CONTROL":"SYNTHETIC_COSTS_NOT_MEASUREMENTS","UNMEASURED":"UNMEASURED_VALUES_NOT_AUTHENTICATED"}.get(c["evidence_kind"],"EXTERNAL_COST_ARTIFACT_NOT_BOUND")
def comparison(item,ev):
    out=baseline()
    l=description(item["model"],item["left_request"],ev);r=description(item["model"],item["right_request"],ev)
    if l["status"]!="HOST_DECLARED_WORK_MANIFEST_ONLY":out["reason"]="left:"+str(l["reason"]);return out
    if r["status"]!="HOST_DECLARED_WORK_MANIFEST_ONLY":out["reason"]="right:"+str(r["reason"]);return out
    out.update(left_work_sha256=l["work_sha256"],right_work_sha256=r["work_sha256"],same_work=l["work_sha256"]==r["work_sha256"])
    if not out["same_work"]:out["reason"]="DIFFERENT_SCENE_PHASE_WORK";return out
    c=item["costs"]
    if type(c)is not dict or set(c)!={"left","right"}:out["reason"]="closed_cost_pair";return out
    reasons=[cost_reason(c[k])for k in("left","right")]
    structural={"closed_cost_record","cost_evidence_kind","full_pipeline_boundary","complete_stage_schema",
        "stage_ns_integer_or_unknown","memory_bytes_integer_or_unknown","energy_interval_joules_or_unknown",
        "cost_artifact_metadata","positive_full_pipeline_ns"}
    # First structural failure aborts atomically even if other record has a readiness reason.
    for reason in reasons:
        if reason in structural:out["reason"]=reason;return out
    out.update(status="HOST_SAME_WORK_ONLY_COSTS_STOP",reason=";".join(reasons),cost_ledger=c)
    return out
def full(kind):
    return dict(evidence_kind=kind,boundary=BOUNDARY,stage_ns={k:1 for k in STAGES},host_peak_bytes=2048,
        device_peak_bytes=0,energy_joule_interval=[1,1],artifact=dict(path="CONTROL_NOT_AN_ACTUAL_ARTIFACT.json",sha256="a"*64,bytes=1))
def manifest(ev):
    valid=[c for c,a in ev.items()if a["native_result"]["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY"]
    items=[]
    def add(label,left,right,cost=None,lq=None,rq=None,model=MODEL):
        items.append(dict(id=label,model=model,left_request=sel(left)if lq is None else lq,
            right_request=sel(right)if rq is None else rq,costs=dict(left=unknown(),right=unknown())if cost is None else cost))
    for c in valid:add("self_"+c,c,c)
    collision=("parent_oblique","parent_direction_scaled","bounded_source_uncertainty","new_gamma_2m120")
    for left in collision:
        for right in collision:
            if left!=right:add("samebytes_"+left+"_"+right,left,right)
    c="parent_oblique"
    for label,kind in(("synthetic_full","SYNTHETIC_CONTROL"),("unbound_external","DECLARED_EXTERNAL_MEASUREMENT"),
        ("filled_unmeasured","UNMEASURED"),("QA_capture","QA_CAPTURE")):add(label,c,c,dict(left=full(kind),right=full(kind)))
    for label,k,v in(("dispatch_only","boundary","DISPATCH_ONLY"),("legacy_hot_boundary","boundary","sourceupdate_export_pack_transfer_dispatch_sync_readback_decode_ONLY"),
        ("bool_host_memory","host_peak_bytes",True),("bad_energy","energy_joule_interval",[2,1]),
        ("negative_device_memory","device_peak_bytes",-1),("fake_artifact","artifact",dict(path="fake",sha256="bad",bytes=1)),
        ("bad_kind","evidence_kind","VERIFIED_BY_SELF")):
        q=full("SYNTHETIC_CONTROL");q[k]=v;add(label,c,c,dict(left=q,right=full("SYNTHETIC_CONTROL")))
    for label,k,v in(("bool_stage","dispatch",True),("float_stage","dispatch",1.0),("negative_stage","dispatch",-1),("zero_total","full_pipeline_cold",0)):
        q=full("SYNTHETIC_CONTROL");q["stage_ns"][k]=v;add(label,c,c,dict(left=q,right=full("SYNTHETIC_CONTROL")))
    q=full("SYNTHETIC_CONTROL");del q["stage_ns"]["scene_inference_geometry"];add("missing_scene_stage",c,c,dict(left=q,right=full("SYNTHETIC_CONTROL")))
    q=full("SYNTHETIC_CONTROL");q["GPU_launch_allowed"]=True;add("extra_cost_GPU",c,c,dict(left=q,right=full("SYNTHETIC_CONTROL")))
    add("missing_right_cost",c,c,dict(left=unknown()))
    for label,k,v in(("bad_intent","intent","GPU"),("bad_receipt","egress_receipt_sha256","wrong"),("unknown_case","case","unknown"),("cap_override","caps_override",[1,1])):
        q=sel(c);q[k]=v;add(label,c,c,lq=q)
    add("wrong_model",c,c,model="RT_NETWORK")
    add("boundary_parent_STOP","new_declared_cap_edge_mu_tenth",c)
    return items,collision
def main():
    rec=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes());pins=rec["code_doc_sha256"]
    assert len(pins)==141
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,("pin",path)
    b=(ROOT/PARENT).read_bytes();assert sha(b)==PSHA and pins[PARENT]==PSHA;par=json.loads(b)
    assert len(par["code_doc_sha256"])==136 and all(pins[k]==v for k,v in par["code_doc_sha256"].items())
    assert capture(par["independent_final_pre"])["status"]=="PASS"
    ev=capture(par["test_run"])["data"]["evidence"]
    d=capture(rec["test_run"]);assert d["status"]=="PASS"and d["groups"]==5;data=d["data"]
    desc=data["descriptions"];assert len(desc)==46 and {v["case"]for v in desc}==set(ev)
    for v in desc:
        assert v["model"]==MODEL and v["request"]==sel(v["case"])
        assert v["result"]==description(v["model"],v["request"],ev),v["case"]
    valid=[v for v in desc if v["result"]["work"]is not None];assert len(valid)==11
    assert len({v["result"]["work_sha256"]for v in valid})==11
    items,collision=manifest(ev);actual=data["comparisons"]
    assert len(items)==len(actual)==47 and len({v["id"]for v in actual})==47
    assert {v["id"]:v for v in items}=={v["id"]:{k:v[k]for k in items[0]}for v in actual}
    for v in actual:assert v["result"]==comparison(v,ev),v["id"]
    lookup={v["case"]:v["result"]for v in valid}
    assert data["same_output_different_work"]==list(collision)
    assert len({lookup[c]["static_ledger"]["native_expected_output_sha256"]for c in collision})==1
    assert len({lookup[c]["work_sha256"]for c in collision})==4
    assert len([v for v in actual if v["id"].startswith("samebytes_")and v["result"]["same_work"]is False])==12
    assert all(data[k]==0 for k in("new_RN64_operations","producer_replays","compiler_calls"))
    assert capture(rec["initial_probe"])==dict(status="STOP",reason="'branch'",ledger=None)
    text=(ROOT/"Blender/benchmarks/capacity_audit/oblique_total_phase_equal_work_HOST_v1.py").read_text(encoding="utf-8")
    assert text==rec["initial_core_source"].replace('source_branch_order=[v["branch"]for v in q["sources"]]','source_branch_order=[v["branch_id"]for v in q["sources"]]')
    tree=ast.parse(text)
    for name,args in(("describe",["model","request"]),("compare",["model","left","right","costs"])):
        fun=next(v for v in tree.body if isinstance(v,ast.FunctionDef)and v.name==name)
        assert [v.arg for v in fun.args.args]==args and not fun.args.defaults and fun.args.kwarg is None
        assert any(isinstance(v,ast.Call)and isinstance(v.func,ast.Name)and v.func.id=="load_evidence"for v in ast.walk(fun))
    print(json.dumps(dict(status="PASS",descriptions=46,manifests=11,parent_STOP=35,comparisons=47,
        same_output_different_work_rejections=12,pins=141,all_cost_readiness_STOP=True,
        initial_branch_mapping_STOP_preserved=True,RN64_operations=0,producer_replays=0,GPU_launch_allowed=False)))
if __name__=="__main__":main()
