"""New V2 HOST egress tests; consume sealed captures only."""
from pathlib import Path
import copy, importlib.util, json, struct
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("egress",ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_v2_egress_HOST_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def main():
    e=m.load_evidence(); runs=[]
    def run(label,case,raw,request=None,model=m.MODEL,origin=m.ORIGIN,fault=None,reason=None):
        ev=copy.deepcopy(e)
        if fault=="missing_source":ev[case]["rows"].pop(0)
        elif fault=="source_identity":ev[case]["rows"][0]["original_scene_sha256"]="0"*64
        elif fault=="source_bits":ev[case]["rows"][0]["lo"]["word_le_hex"]="0000000000000000"
        elif fault=="source_cap":ev[case]["rows"][0]["literal_cap_rad"]=[1,1<<120];ev[case]["packet"]["source_literal_caps"][0]=[1,1<<120]
        elif fault=="relative_identity":ev[case]["rows"][2]["literal_request_sha256"]="0"*64
        elif fault=="relative_interval":ev[case]["rows"][2]["parent_relative_CONTROL_ONLY"]["interval"]=[[0,1],[0,1]]
        elif fault=="relative_cap":ev[case]["rows"][2]["literal_cap_rad"]=[1,1<<120];ev[case]["packet"]["retained_CPU_budget"]["literal_cap_rad"]=[1,1<<120]
        req=m.selector(case,ev) if request is None else request
        r=m._compare_fixture(model,req,raw,origin,ev) if fault else m.compare(model,req,raw,origin)
        assert r["status"]==("HOST_UNATTESTED_BYTES_MATCH" if reason is None else "STOP"),(label,r)
        assert r["reason"]==reason,(label,r["reason"],reason)
        assert r["promotion"]=="STOP" and not any(r[k] for k in ("GPU_executed","GPU_launch_allowed","GPU_guard_certified",
                    "scene_authenticated","fence_readback_authenticated","physical_field_certified","native_promotion_allowed"))
        runs.append(dict(id=label,case=case,request=req,raw_hex=raw.hex(),model=model,origin=origin,fault=fault,result=r))
    for case in m.CASES:
        good=bytes.fromhex(e[case]["packet"]["expected_CONTROL_ONLY_hex"])
        run(case,case,good)
        run(case+"_short",case,good[:-1],reason="output_extent")
        run(case+"_long",case,good+b"\0",reason="output_extent")
        for j in range(4):
            b=bytearray(good);b[4*j:4*j+4]=struct.pack("<I",0)
            run(case+"_header"+str(j),case,bytes(b),reason="output_header")
        for j in (16,24):
            b=bytearray(good);b[j:j+8]=(0x7ff0000000000000).to_bytes(8,"little")
            run(case+"_nonfinite"+str(j),case,bytes(b),reason="nonfinite_raw")
        run(case+"_marker_only",case,good[:16]+bytes(16),reason="relative_cap")
    case=m.CASES[0];good=bytes.fromhex(e[case]["packet"]["expected_CONTROL_ONLY_hex"])
    run("hi_only",case,good[:24]+bytes(8),reason="relative_cap")
    b=bytearray(good);b[24]^=1
    run("within_cap_wrong_bits",case,bytes(b),reason="native_bits_mismatch")
    for key in ("packet_sha256","original_scene_sha256","literal_request_sha256","shader_sha256","intent"):
        req=m.selector(case,e);req[key]="wrong";run("selector_"+key,case,good,request=req,reason="selector_identity")
    req=m.selector(case,e);req["cap_override"]=[1,1]
    run("selector_extra",case,good,request=req,reason="closed_selector")
    req=m.selector(case,e);del req["intent"]
    run("selector_missing",case,good,request=req,reason="closed_selector")
    req=m.selector(case,e);req["case"]="unknown"
    run("selector_unknown_case",case,good,request=req,reason="case")
    run("wrong_model",case,good,model="V1",reason="model")
    for origin in ("GPU_READBACK","GPU_ATTESTED","CPU_AUTHENTICATED"):
        run("origin_"+origin,case,good,origin=origin,reason="unattested_origin_only")
    for fault,reason in (("missing_source","source_completeness"),("source_identity","source_identity"),
                        ("source_bits","source_bits"),("source_cap","source_cap"),("relative_identity","relative_identity"),
                        ("relative_interval","relative_interval"),("relative_cap","relative_cap")):
        run("fault_"+fault,case,good,fault=fault,reason=reason)
    # Same bytes can be copied under a correct selector; a HOST match is NOT provenance.
    shared=m.CASES[2];scaled=m.CASES[1]
    assert e[case]["packet"]["expected_CONTROL_ONLY_hex"]==e[scaled]["packet"]["expected_CONTROL_ONLY_hex"]
    assert e[case]["packet"]["expected_CONTROL_ONLY_hex"]==e[shared]["packet"]["expected_CONTROL_ONLY_hex"]
    run("same_bytes_shared_reference_unattested",shared,good)
    req=m.selector(case,e);req["case"]=shared
    run("same_bytes_wrong_identity",shared,good,request=req,reason="selector_identity")
    assert len({r["id"] for r in runs})==len(runs)
    print(json.dumps(dict(status="PASS",groups=5,data=dict(evidence=e,runs=runs,
          equal_payload_witness=dict(cases=[case,scaled,shared],bytes_hex=good.hex(),
             establishes_provenance=False,measured_GPU_execution=False))),sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
