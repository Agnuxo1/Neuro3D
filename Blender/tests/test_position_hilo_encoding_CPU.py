"""Original-bound HOST RNE32 encoding, cache identity and lost-gap controls."""
import inspect,json,sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_hilo_encoding_CPU_v1 as m
def main():
    e,pins=m.retained();runs=[];totals=m.cost()
    for case,x in e.items():
        for mode in m.MODES:
            q=m.selector(case,mode,e);r=m._audit(m.MODEL,q,e)
            contact=x["original"]["result"]["status"]=="STOP";lost=case.endswith(":outside_2m60")and mode=="HOST_SINGLE32"
            assert r["status"]==("STOP"if contact or lost else "HOST_POSITION_ENCODING_SEPARATION_ONLY")
            if contact:assert r["reason"]=="parent_contact_STOP"and r["diagnostics"]==[]
            elif lost:
                assert r["reason"]=="encoding_exhausts_separator"
                assert r["HOST_cost"]["new_separator_evaluations"]==1 and r["HOST_cost"]["cached_separator_reuses"]==0
                assert any(F(*v["error_abs_BU"])>0 for v in r["diagnostics"][0]["coordinates"])
            else:assert r["HOST_cost"]["cached_separator_reuses"]==1 and r["HOST_cost"]["new_separator_evaluations"]==0
            for k in totals:totals[k]+=r["HOST_cost"][k]
            runs.append(dict(id=mode+":"+case,request=q,result=r))
    case="synthetic:xy:0:outside_2m60";q=m.selector(case,"HOST_HILO32",e)
    for key in q:
        bad=dict(q);bad[key]="wrong";r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"and r["diagnostics"]==[]
        runs.append(dict(id="selector:"+key,request=bad,result=r))
    for label,bad in(("extra",dict(q,extra="x")),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool_mode",dict(q,mode=False))):
        r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"and r["diagnostics"]==[]
        runs.append(dict(id="selector:"+label,request=bad,result=r))
    r=m._audit("GPU",q,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",request=q,result=r))
    helpers=[];helper_cost=m.cost()
    values=[F(0),F(1),F(-1),F(1)+F(1,2**24),F(1)+F(3,2**24),-(F(1)+F(1,2**24)),F(1,10),F(1,2**126)]
    for i,v in enumerate(values):
        for mode in m.MODES:
            item=m.encode(v,mode,helper_cost);assert F(*item["error_abs_BU"])==abs(F(*item["center_BU"])-v)
            helpers.append(dict(id=str(i)+":"+mode,mode=mode,encoding=item))
    assert helpers[6]["encoding"]["hi_bits"]==0x3f800000
    assert helpers[8]["encoding"]["hi_bits"]==0x3f800002
    negatives=[]
    controls=[("subnormal",lambda:m.rn32(F(1,2**127))),("overflow",lambda:m.rn32(F(1,1)*2**128)),("non_fraction",lambda:m.rn32(1)),
        ("residual_subnormal",lambda:m.encode(F(1)+F(1,2**127),"HOST_HILO32",m.cost()))]
    for word in(0x7f800000,0xff800000,0x7fc00000,0x7f800001,1,-1,2**32,True):
        controls.append(("decode:"+str(word),lambda w=word:m.decode(w)))
    for label,fn in controls:
        try:fn()
        except(ValueError,TypeError)as ex:negatives.append(dict(id=label,status="STOP",reason=str(ex)))
        else:raise AssertionError("negative admitted:"+label)
    assert len(negatives)==12
    public=m.audit(m.MODEL,q);assert public["status"]=="HOST_POSITION_ENCODING_SEPARATION_ONLY"
    saved=m.retained
    def missing():raise ValueError("simulated_missing_receipt")
    m.retained=missing;absent=m.audit(m.MODEL,q);m.retained=saved
    assert absent["reason"]=="evidence_integrity:simulated_missing_receipt"
    assert list(inspect.signature(m.audit).parameters)==["model","request"]
    for r in [x["result"]for x in runs]+[public,absent]:
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","scene_authenticated","uncertainty_authenticated","full_visibility_certified",
            "phase_certified","physical_field_certified","object_wide_skip","previous_zero_exemption"))
        assert r["promotion"]=="STOP"and r["epsilon_BU"]==[0,1]and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert (r["RN64_operations"],r["compiler_calls"],r["producer_replays"])==(0,0,0)
        if r["status"]=="STOP":assert r["rows"]==[]and r["packet_words"]==[]and r["packet_sha256"]is None and r["encoding_error_derived"]is False
    assert len(runs)==170 and totals==dict(RN32_rounds=3240,exact_decodes=3240,exact_residuals=1080,exact_reconstructions=1080,new_separator_evaluations=24,cached_separator_reuses=120)
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,helpers=helpers,helper_cost=helper_cost,negative_helpers=negatives,
        public=public,missing=absent,main_cost=totals,census=dict(main=170,HOST_separation=120,STOP=50,single32_gaploss_STOP=24,parent_contact_STOP=16,
            selector_model_STOP=10,helpers=16,negative_helpers=12,auxiliary=2),GPU_executed=False,compiler_calls=0,producer_replays=0,RN64_operations=0)),sort_keys=True))
if __name__=="__main__":main()
