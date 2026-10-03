"""New native CPU phase pair tests; parent capture status retained without replay."""
from pathlib import Path
import copy,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("total_pair",ROOT/"Blender/benchmarks/capacity_audit/oblique_total_phase_pair64_CPU_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
    e=m.load_evidence();runs=[]
    def run(label,req,reason=None,model=m.MODEL):
        assert label not in {v["id"] for v in runs},"unique_case_before_execution"
        r=m.compute(model,req)
        assert r["status"]==("CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY"if reason is None else "STOP"),(label,r["reason"])
        assert r["reason"]==reason,(label,r["reason"],reason)
        assert r["rows"]==([]if reason else r["diagnostics"])
        assert r["promotion"]=="STOP"and all(r[k]is False for k in("GPU_executed","GPU_launch_allowed",
            "physical_field_certified","scene_authenticated","material_authenticated","native_promotion_allowed","V2_total_phase_backend_bound"))
        runs.append(dict(id=label,request=req,model=model,result=r))
    for c,a in e.items():
        reason=None
        if a["declared"]is not None and a["declared"]["status"]=="STOP":reason="parent_STOP:"+a["declared"]["reason"]
        elif c=="new_declared_cap_edge_mu_tenth":reason="ALL_SOURCE_cap_after_encoding_arithmetic"
        run(c,m.selector(c,e),reason)
    base=m.selector("parent_oblique",e)
    run("native_wrong_model",base,"model","V2_TOTAL_GPU")
    for key in("phase_request_sha256","original_scene_sha256","literal_request_sha256","representation","intent"):
        req=copy.deepcopy(base);req[key]="wrong";run("bad_"+key,req,"selector_identity")
    req=copy.deepcopy(base);req["case"]="unknown";run("unknown_case",req,"case")
    req=copy.deepcopy(base);req["launch_GPU"]=True;run("extra_launch",req,"closed_selector")
    req=copy.deepcopy(base);del req["intent"];run("missing_intent",req,"closed_selector")
    out={r["id"]:r["result"]for r in runs}
    computed=[r for r in out.values()if r["trace"]]
    assert len(computed)==12 and all(len(r["trace"])==130 and r["RN64_parameter_casts"]==6 for r in computed)
    edge=out["new_declared_cap_edge_mu_tenth"]
    assert edge["analytic_interval_admitted"]and edge["rows"]==[]and any(not r["fits"]for r in edge["diagnostics"][:2])
    assert m.f(edge["encodings"][2]["error_cycles"])>0
    small=out["new_gamma_2m120"];assert any(m.f(r["gamma_add_error_cycles"])>0 for r in small["rows"][:2])
    assert len({r["id"]for r in runs})==len(runs)
    print(json.dumps(dict(status="PASS",groups=5,data=dict(registry=e,runs=runs,total_new_arithmetic_RN=sum(r["RN64_arithmetic_operations"]for r in out.values()),
           total_new_parameter_RN=sum(r["RN64_parameter_casts"]for r in out.values()),parent_producer_replays=0)),sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
