"""Focused SOURCE/material overlay tests, no old producer or compiler execution."""
from pathlib import Path
import copy,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("phase_overlay",ROOT/"Blender/benchmarks/capacity_audit/oblique_source_material_interval_HOST_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def point(v):return [v,v]
def main():
    e=m.load_evidence();runs=[]
    def run(label,q,reason=None,model=m.MODEL):
        r=m.evaluate(model,q);assert r["status"]==("HOST_DECLARED_TOTAL_PHASE_INTERVAL_ONLY"if reason is None else "STOP"),(label,r)
        assert r["reason"]==reason,(label,r["reason"],reason)
        assert not r["rows"]if reason else len(r["rows"])==3
        assert r["promotion"]=="STOP"and all(r[k]is False for k in("GPU_executed","GPU_launch_allowed","scene_authenticated",
            "material_authenticated","physical_field_certified","native_promotion_allowed","interference_phase_certified","V2_total_phase_backend_bound"))
        runs.append(dict(id=label,request=q,model=model,result=r))
    for c in m.CASES:run(c,m.request(c,e))
    c=m.CASES[0];base=m.request(c,e)
    q=copy.deepcopy(base);q["sources"][1]["phase_interval_cycles"]=point([1,8]);run("source1_eighth_cycle",q)
    q=copy.deepcopy(base);q["material"]["phase_interval_cycles"]=point([0,1]);run("complete_coefficient_plus_one",q)
    q=copy.deepcopy(base);q["material"]["phase_interval_cycles"]=point([524288,1]);run("large_shared_declared_not_encoded",q)
    q=copy.deepcopy(base);q["material"]["phase_interval_cycles"]=[[-1,1<<80],[1,1<<80]];run("shared_material_uncertainty_SOURCE_FAIL_relative_fits",q,"ALL_SOURCE_cap")
    q=copy.deepcopy(base);q["sources"][0]["phase_interval_cycles"]=[[-1,1<<80],[1,1<<80]];run("source0_uncertainty_FAIL",q,"ALL_SOURCE_cap")
    q=copy.deepcopy(base);q["sources"][1]["phase_interval_cycles"]=[[-1,1<<80],[1,1<<80]];run("source1_uncertainty_FAIL",q,"ALL_SOURCE_cap")
    q=copy.deepcopy(base);q["sources"][0]["phase_interval_cycles"]=[[-1,1<<85],[1,1<<85]];run("bounded_source_uncertainty",q)
    q=copy.deepcopy(base);q["sources"][1]["phase_interval_cycles"]=point([-1,8]);run("opposite_source_phase",q)
    for key in("parent_receipt_sha256","original_scene_sha256","literal_request_sha256"):
        q=copy.deepcopy(base);q[key]="0"*64;run("wrong_"+key,q,"parent_ORIGINAL_literal")
    q=copy.deepcopy(base);q["sources"].pop();run("missing_SOURCE",q,"ALL_SOURCE")
    q=copy.deepcopy(base);q["sources"].reverse();run("reordered_SOURCE",q,"SOURCE_branch_order")
    q=copy.deepcopy(base);q["sources"][1]["branch_id"]="S0/mirror";run("cross_SOURCE_branch",q,"SOURCE_branch_order")
    q=copy.deepcopy(base);del q["sources"][0]["phase_interval_cycles"];run("missing_phase_not_zero",q,"SOURCE_branch_order")
    q=copy.deepcopy(base);q["sources"][0]["phase_interval_cycles"]=None;run("unknown_phase_not_zero",q,"phase_interval")
    q=copy.deepcopy(base);q["sources"][0]["phase_interval_cycles"]=[[1,1],[0,1]];run("reversed_phase_interval",q,"ordered_interval")
    q=copy.deepcopy(base);q["sources"][0]["phase_interval_cycles"]=[[True,1],[0,1]];run("bool_rational",q,"typed_rational")
    q=copy.deepcopy(base);q["sources"][0]["phase_interval_cycles"]=[[0,0],[0,1]];run("zero_denominator",q,"bounded_rational")
    q=copy.deepcopy(base);q["sources"][0]["phase_interval_cycles"]=point([1,1<<257]);run("oversized_rational",q,"bounded_rational")
    q=copy.deepcopy(base);q["material"]["primitive_id"]=True;run("bool_primitive",q,"material_primitive_profile")
    q=copy.deepcopy(base);q["material"]["primitive_id"]=0;run("wrong_material_primitive",q,"material_primitive_profile")
    q=copy.deepcopy(base);q["material"]["object_id"]="other";run("wrong_material_object",q,"material_object")
    q=copy.deepcopy(base);q["material"]["profile"]="IMPLICIT_MINUS_ONE";run("implicit_material_sign",q,"material_primitive_profile")
    q=copy.deepcopy(base);q["material"]["phase_interval_cycles"]=None;run("unknown_material_not_zero",q,"phase_interval")
    q=copy.deepcopy(base);q["material"]=[q["material"],q["material"]];run("separate_materials_not_shared",q,"closed_material")
    q=copy.deepcopy(base);q["cap_override"]=[1,1];run("cap_override",q,"closed_request")
    q=copy.deepcopy(base);q["authentication"]="PHYSICAL";run("asserted_physical_auth",q,"explicit_declared_units")
    q=copy.deepcopy(base);q["units"]["phase"]="rad";run("wrong_units",q,"explicit_declared_units")
    run("wrong_model",base,"model","V2_GPU")
    r=next(x["result"]for x in runs if x["id"]=="shared_material_uncertainty_SOURCE_FAIL_relative_fits")
    assert r["diagnostics"][2]["fits"]is True and not r["diagnostics"][0]["fits"]and r["rows"]==[]
    assert len({x["id"]for x in runs})==len(runs)
    print(json.dumps(dict(status="PASS",groups=5,data=dict(evidence=e,runs=runs)),sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
