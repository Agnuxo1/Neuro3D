"""Synthetic byte-contract QA, no old numerical replay or native execution."""
from pathlib import Path
import sys, json, copy, base64
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"benchmarks/capacity_audit"))
import oblique_native_evidence_binding_HOST_v1 as m

def pack(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def fixture():
    cases = []
    a = {"backend": b"SYNTHETIC_NOT_EXECUTABLE_NATIVE_CODE"}
    for i in range(6):
        case = "fixture-" + str(i)
        inp = b"SYNTHETIC-original-input-" + bytes([i])
        a[case+"/input"] = inp
        a[case+"/output"] = bytes([i+1])*16
        cases.append(dict(case=case, scene_sha256=m.sha(b"scene"+bytes([i])),
            query_sha256=m.sha(b"query"+bytes([i])), input_buffer_sha256=m.sha(inp), source_ids=["S0","S1"]))
    plan = dict(schema=m.SCHEMA, anchor_sha256=m.PSHA, cases=cases,
        output_scope="ordered_SOURCE_raw_bytes_opaque_ABI_not_semantic_precision_proof",
        cost_components=list(m.COMPONENTS))
    ioh = {k:m.sha(v) for k,v in a.items() if "/" in k}
    kind = "synthetic_contract_fixture"
    job = "SYNTHETIC-NO-REAL-JOB"
    cost = dict(job_id=job, evidence_kind=kind, plan_sha256=m.digest(plan),
        io_sha256=ioh, backend_sha256=m.sha(a["backend"]), regime="cold", amortization_runs=1,
        total_wall_ns=14, clock="single_monotonic_ns",
        components=[dict(component=k,start_ns=i,end_ns=i+1,status="measured",reason="") for i,k in enumerate(m.COMPONENTS)],
        sampled_RAM_max_bytes=0,sampled_VRAM_max_bytes=0,
        upload_bytes=sum(len(v) for k,v in a.items() if k.endswith("/input")),
        readback_bytes=sum(len(v) for k,v in a.items() if k.endswith("/output")),
        memory_scope="sampled_maximum_not_global_peak",
        energy=dict(status="unavailable",microjoules=None,method="fixture no measured energy"))
    a["cost_ledger"]=pack(cost)
    guard = dict(job_id=job,evidence_kind=kind,plan_sha256=m.digest(plan),io_sha256=ioh,
        backend_sha256=m.sha(a["backend"]),cost_ledger_sha256=m.sha(a["cost_ledger"]),
        policy=copy.deepcopy(m.POLICY),status="completed",child_exit_code=0,reasons=[],
        child_start_utc="2026-10-01T00:00:00+00:00",child_end_utc="2026-10-01T00:00:01+00:00",
        recorded_deadline_utc="2026-10-01T00:02:00+00:00",timeout_s=120,job_kind="pilot")
    a["guard"]=pack(guard)
    manifest = dict(schema=m.SCHEMA,plan=copy.deepcopy(plan),job_id=job,evidence_kind=kind,
        backend_kind="GPU_ALU_digital",work_origin="scene_traversal_not_U_GEMM_or_lookup",
        outputs=[dict(t,ABI_id="SYNTHETIC-opaque-v1",SOURCE_stride_bytes=8,
            output_sha256=m.sha(a[t["case"]+"/output"])) for t in cases],
        phase_error_bound=None,**{k:False for k in m.FALSE})
    seal(manifest,a)
    return plan,manifest,a

def seal(x,a):
    x["artifact_sha256"]={k:m.sha(v) for k,v in a.items()}
    x["artifact_bytes"]={k:len(v) for k,v in a.items()}

def safe(r):
    assert all(r[k]is False for k in m.FALSE) and r["phase_error_bound"]is None

def main():
    plan,pins=m.load_plan()
    original=m.inspect_bundle()
    safe(original)
    assert original["status"]=="STOP_EVIDENCE" and original["reason"]=="missing_native_bundle_no_filler_load"
    p,x,a=fixture()
    positive=m.validate(p,x,a)
    safe(positive)
    assert positive["content_matched"] and positive["synthetic_fixture_only"]
    evidence=dict(original_missing_bundle=original,original_plan=plan,pins=pins,
        synthetic_plan=p,synthetic_manifest=x,
        synthetic_raw_base64={k:base64.b64encode(v).decode() for k,v in a.items()},
        positive=positive,negative=[],parser=[],public=[])
    mutations=[
        ("scene", "output", "scene_sha256", "0"*64),
        ("query", "output", "query_sha256", "0"*64),
        ("input_pointer", "output", "input_buffer_sha256", "0"*64),
        ("SOURCE_reverse", "output", "source_ids", ["S1","S0"]),
        ("stride_bool", "output", "SOURCE_stride_bytes", True),
        ("stride_size", "output", "SOURCE_stride_bytes", 12),
        ("ABI_empty", "output", "ABI_id", ""),
        ("output_hash", "output", "output_sha256", "0"*64),
        ("guard_job", "guard", "job_id", "other"),
        ("guard_origin", "guard", "evidence_kind", "retained_native_content"),
        ("guard_rc_bool", "guard", "child_exit_code", False),
        ("guard_status", "guard", "status", "in_progress"),
        ("guard_timeout", "guard", "timeout_s", 121),
        ("guard_deadline", "guard", "recorded_deadline_utc", "2026-09-30T00:00:00+00:00"),
        ("guard_timezone", "guard", "child_end_utc", "2026-10-01T00:00:01+01:00"),
        ("guard_cost_hash", "guard", "cost_ledger_sha256", "0"*64),
        ("cost_job", "cost_ledger", "job_id", "other"),
        ("cost_origin", "cost_ledger", "evidence_kind", "retained_native_content"),
        ("cold_amortization", "cost_ledger", "amortization_runs", 2),
        ("cost_wall_bool", "cost_ledger", "total_wall_ns", True),
        ("cost_clock", "cost_ledger", "clock", "mixed_clocks"),
        ("cost_upload_bool", "cost_ledger", "upload_bytes", True),
        ("cost_upload_zero", "cost_ledger", "upload_bytes", 0),
        ("cost_readback_zero", "cost_ledger", "readback_bytes", 0),
        ("cost_memory_peak_claim", "cost_ledger", "memory_scope", "global_peak"),
        ("backend_RT", "manifest", "backend_kind", "RT"),
        ("backend_Bpy", "manifest", "backend_kind", "Bpyfloat32"),
        ("backend_GEMM", "manifest", "work_origin", "compiled_U_GEMM"),
        ("fake_phase_bound", "manifest", "phase_error_bound", 0),
        ("bool_size", "manifest", "artifact_bytes", None)]
    for key in m.FALSE:
        mutations.append(("false_flag_"+key,"manifest",key,True))
    extra=("input_byte_drift","output_byte_drift","missing_output","missing_cost","cost_gap","cost_tail",
           "cost_component_missing","cost_NA_no_reason","energy_unknown_zero","policy_override","policy_bool",
           "plan_query","plan_SOURCE_bool","extra_artifact","declared_shape_float","transfer_NA")
    for label,area,key,value in mutations+[(v,"custom",None,None) for v in extra]:
        pp,xx,aa=fixture()
        if area=="output":xx["outputs"][0][key]=value
        elif area=="manifest":
            if label=="bool_size":xx["artifact_bytes"]["backend"]=True
            else:xx[key]=value
        elif area in ("guard","cost_ledger"):
            obj=m.parse(aa[area]);obj[key]=value;aa[area]=pack(obj)
        else:
            if label=="input_byte_drift":aa["fixture-0/input"]+=b"!"
            elif label=="output_byte_drift":aa["fixture-0/output"]+=b"!"
            elif label=="missing_output":del aa["fixture-0/output"]
            elif label=="missing_cost":del aa["cost_ledger"]
            elif label=="extra_artifact":aa["foreign"]=b"not executed"
            elif label=="plan_query":xx["plan"]["cases"][0]["query_sha256"]="0"*64
            elif label=="plan_SOURCE_bool":xx["plan"]["cases"][0]["source_ids"]=[True,"S1"]
            elif label=="declared_shape_float":xx["outputs"][0]["SOURCE_stride_bytes"]=8.0
            elif label.startswith("policy"):
                obj=m.parse(aa["guard"]);obj["policy"]["RAM_free_after_budget_min_bytes"]=int(1.5*2**30) if label=="policy_override" else True;aa["guard"]=pack(obj)
            else:
                obj=m.parse(aa["cost_ledger"])
                if label=="cost_gap":obj["components"][0]["start_ns"]=1;obj["components"][0]["end_ns"]=2
                elif label=="cost_tail":obj["total_wall_ns"]=15
                elif label=="cost_component_missing":obj["components"].pop()
                elif label=="cost_NA_no_reason":obj["components"][0].update(status="not_applicable",end_ns=0)
                elif label=="energy_unknown_zero":obj["energy"]["microjoules"]=0
                elif label=="transfer_NA":
                    obj["components"][5].update(status="not_applicable",end_ns=5,reason="SYNTHETIC_claim")
                    obj["components"][4]["end_ns"]=6
                aa["cost_ledger"]=pack(obj)
        # Re-seal altered content: semantic rejection must not rely on stale outer raw SHA.
        if "cost_ledger" in aa and area!="guard" and label!="guard_cost_hash":
            obj=m.parse(aa["guard"]);obj["cost_ledger_sha256"]=m.sha(aa["cost_ledger"]);aa["guard"]=pack(obj)
        if label!="bool_size":seal(xx,aa)
        try:m.validate(pp,xx,aa)
        except(ValueError,KeyError,TypeError)as ex:reason=str(ex)
        else:raise AssertionError("unrejected:"+label)
        evidence["negative"].append(dict(id=label,reason=reason,status="STOP_CONTENT"))
    for label,raw in (("duplicate",b'{"x":1,"x":2}'),("NaN",b'{"x":NaN}'),
        ("infinite_exponent",b'{"x":1e309}'),("oversize",b" "* (m.MAX_JSON+1)),
        ("depth",b"["*66+b"0"+b"]"*66)):
        try:m.parse(raw)
        except(ValueError,RecursionError)as ex:reason=str(ex)
        else:raise AssertionError(label)
        evidence["parser"].append(dict(id=label,reason=reason))
    # Actual pinned plan cannot be substituted by the synthetic pure-unit fixture.
    r=m.inspect_bundle(pack(x),a);safe(r);assert r["status"]=="STOP_EVIDENCE"
    evidence["public"].append(dict(id="fake_plan_rejected",result=r))
    historical=Path(m.ROOT/"coordinacion/respuestas/RT-CAP-006-CLAUDE-FINAL.json").read_bytes()
    r=m.inspect_bundle(historical,{});safe(r);assert r["status"]=="STOP_EVIDENCE"
    evidence["public"].append(dict(id="historical_RT006_rejected",sha256=m.sha(historical),result=r))
    # Same overlapping interval is legal; no summed-cost/efficiency claim.
    pp,xx,aa=fixture();cost=m.parse(aa["cost_ledger"])
    for row in cost["components"]:row.update(start_ns=0,end_ns=14)
    aa["cost_ledger"]=pack(cost);g=m.parse(aa["guard"]);g["cost_ledger_sha256"]=m.sha(aa["cost_ledger"]);aa["guard"]=pack(g);seal(xx,aa)
    overlap=m.validate(pp,xx,aa);safe(overlap);assert overlap["overlap_spans_not_summed"]
    evidence["overlap_content_only"]=overlap
    print(json.dumps(dict(status="PASS",evidence=evidence,summary=dict(
        original_cases=6,SOURCE_inputs=12,synthetic_negative=len(evidence["negative"]),
        parser_stops=5,public_STOPS=3,raw_artifacts=15,
        native_admission=False,GPU_used=False,old_numeric_replays=0,
        phase_error_bound=None,costs_authenticated=False)),sort_keys=True,allow_nan=False))

if __name__=="__main__":
    main()
