"""Work identity/cost readiness tests from sealed captures, no old producers."""
from pathlib import Path
import copy,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location("work",ROOT/"Blender/benchmarks/capacity_audit/oblique_total_phase_equal_work_HOST_v1.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def full(kind):
    return dict(evidence_kind=kind,boundary=m.BOUNDARY,stage_ns={k:1 for k in m.STAGES},
        host_peak_bytes=2048,device_peak_bytes=0,energy_joule_interval=[1,1],
        artifact=dict(path="CONTROL_NOT_AN_ACTUAL_ARTIFACT.json",sha256="a"*64,bytes=1))
def main():
    e=m.load_evidence();descriptions=[];comparisons=[]
    for c,a in e.items():
        r=m.describe(m.MODEL,m.selector(c))
        reason=None if a["native_result"]["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY"else "parent_STOP:"+str(a["native_result"]["reason"])
        assert r["reason"]==reason,(c,r["reason"],reason)
        assert r["status"]==("STOP"if reason else "HOST_DECLARED_WORK_MANIFEST_ONLY")
        descriptions.append(dict(case=c,model=m.MODEL,request=m.selector(c),result=r))
    valid=[v["case"]for v in descriptions if v["result"]["work"]is not None]
    assert len(valid)==11
    costs=dict(left=m.cost_unknown(),right=m.cost_unknown())
    def run(label,left,right,cost=costs,reason=None,leftreq=None,rightreq=None,model=m.MODEL):
        assert label not in {v["id"]for v in comparisons}
        l=m.selector(left)if leftreq is None else leftreq;r=m.selector(right)if rightreq is None else rightreq
        out=m.compare(model,l,r,cost)
        assert out["reason"]==reason,(label,out["reason"],reason)
        assert out["promotion"]=="STOP"and out["cost_ready"]is False and out["speed_ratio"]is None and out["winner"]is None
        comparisons.append(dict(id=label,model=model,left_request=l,right_request=r,costs=cost,result=out))
    for c in valid:run("self_"+c,c,c,reason="MISSING_FULL_COSTS;MISSING_FULL_COSTS")
    collision=("parent_oblique","parent_direction_scaled","bounded_source_uncertainty","new_gamma_2m120")
    desc={v["case"]:v["result"]for v in descriptions}
    assert len({desc[c]["static_ledger"]["native_expected_output_sha256"]for c in collision})==1
    assert len({desc[c]["work_sha256"]for c in collision})==4
    for left in collision:
        for right in collision:
            if left!=right:run("samebytes_"+left+"_"+right,left,right,reason="DIFFERENT_SCENE_PHASE_WORK")
    c="parent_oblique"
    run("synthetic_full",c,c,cost=dict(left=full("SYNTHETIC_CONTROL"),right=full("SYNTHETIC_CONTROL")),
        reason="SYNTHETIC_COSTS_NOT_MEASUREMENTS;SYNTHETIC_COSTS_NOT_MEASUREMENTS")
    run("unbound_external",c,c,cost=dict(left=full("DECLARED_EXTERNAL_MEASUREMENT"),right=full("DECLARED_EXTERNAL_MEASUREMENT")),
        reason="EXTERNAL_COST_ARTIFACT_NOT_BOUND;EXTERNAL_COST_ARTIFACT_NOT_BOUND")
    run("filled_unmeasured",c,c,cost=dict(left=full("UNMEASURED"),right=full("UNMEASURED")),
        reason="UNMEASURED_VALUES_NOT_AUTHENTICATED;UNMEASURED_VALUES_NOT_AUTHENTICATED")
    run("QA_capture",c,c,cost=dict(left=full("QA_CAPTURE"),right=full("QA_CAPTURE")),reason="QA_TIMING_NOT_FULL_PIPELINE;QA_TIMING_NOT_FULL_PIPELINE")
    mutations=[
        ("dispatch_only","boundary","DISPATCH_ONLY","full_pipeline_boundary"),
        ("legacy_hot_boundary","boundary","sourceupdate_export_pack_transfer_dispatch_sync_readback_decode_ONLY","full_pipeline_boundary"),
        ("bool_host_memory","host_peak_bytes",True,"memory_bytes_integer_or_unknown"),
        ("bad_energy","energy_joule_interval",[2,1],"energy_interval_joules_or_unknown"),
        ("negative_device_memory","device_peak_bytes",-1,"memory_bytes_integer_or_unknown"),
        ("fake_artifact","artifact",dict(path="fake",sha256="bad",bytes=1),"cost_artifact_metadata"),
        ("bad_kind","evidence_kind","VERIFIED_BY_SELF","cost_evidence_kind")]
    for label,k,value,reason in mutations:
        q=full("SYNTHETIC_CONTROL");q[k]=value
        run(label,c,c,cost=dict(left=q,right=full("SYNTHETIC_CONTROL")),reason=reason)
    for label,key,value,reason in(("bool_stage","dispatch",True,"stage_ns_integer_or_unknown"),
        ("float_stage","dispatch",1.0,"stage_ns_integer_or_unknown"),("negative_stage","dispatch",-1,"stage_ns_integer_or_unknown"),
        ("zero_total","full_pipeline_cold",0,"positive_full_pipeline_ns")):
        q=full("SYNTHETIC_CONTROL");q["stage_ns"][key]=value
        run(label,c,c,cost=dict(left=q,right=full("SYNTHETIC_CONTROL")),reason=reason)
    q=full("SYNTHETIC_CONTROL");del q["stage_ns"]["scene_inference_geometry"]
    run("missing_scene_stage",c,c,cost=dict(left=q,right=full("SYNTHETIC_CONTROL")),reason="complete_stage_schema")
    q=full("SYNTHETIC_CONTROL");q["GPU_launch_allowed"]=True
    run("extra_cost_GPU",c,c,cost=dict(left=q,right=full("SYNTHETIC_CONTROL")),reason="closed_cost_record")
    run("missing_right_cost",c,c,cost=dict(left=m.cost_unknown()),reason="closed_cost_pair")
    q=m.selector(c);q["intent"]="GPU";run("bad_intent",c,c,leftreq=q,reason="left:selector_identity")
    q=m.selector(c);q["egress_receipt_sha256"]="wrong";run("bad_receipt",c,c,leftreq=q,reason="left:selector_identity")
    q=m.selector(c);q["case"]="unknown";run("unknown_case",c,c,leftreq=q,reason="left:case")
    q=m.selector(c);q["caps_override"]=[1,1];run("cap_override",c,c,leftreq=q,reason="left:closed_selector")
    run("wrong_model",c,c,model="RT_NETWORK",reason="left:model")
    run("boundary_parent_STOP","new_declared_cap_edge_mu_tenth",c,reason="left:parent_STOP:ALL_SOURCE_cap_after_encoding_arithmetic")
    assert all(v["result"]["cost_ledger"]==m.cost_unknown()for v in descriptions if v["case"]in valid)
    assert len({desc[c]["work_sha256"]for c in valid})==11
    print(json.dumps(dict(status="PASS",groups=5,data=dict(descriptions=descriptions,comparisons=comparisons,
        same_output_different_work=collision,new_RN64_operations=0,producer_replays=0,compiler_calls=0)),sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
