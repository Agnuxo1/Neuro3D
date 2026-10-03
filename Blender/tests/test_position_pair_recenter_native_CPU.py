"""Bounded native pair subtraction; scalar STOP branch retained and inexact control."""
import inspect,json,sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_pair_recenter_native_CPU_v1 as m

def compact(r):
    v=dict(r);v.pop("rows");v["rows_mode"]="EMPTY"if r["status"]=="STOP"else "DIAGNOSTICS";v["result_sha256"]=m.digest(r);return v

def main():
    e,pins=m.retained();runs=[]
    for record,x in e.items():
        q=m.selector(record,e);r=m._audit(m.MODEL,q,e);blocked=x["ingress"]["result"]["status"]=="STOP"
        assert r["status"]==("STOP"if blocked else "CPU_POSITION_PAIR_RECENTER_ONLY"),(record,r)
        if blocked:assert r["reason"]=="ingress_STOP_not_rescued"and r["RN64_operations"]==0 and r["diagnostics"]==[]
        else:
            assert r["RN64_operations"]==390 and r["CPU_native_executed"]and r["exact_pair_recenter_verified"]
            d=r["rows"][0];assert all(v["exact_pair_difference"]and v["error_abs_BU"]==[0,1]for v in d["coordinates"])
            assert d["translated_separator"]["signed_best_gap_BU"]==x["certificate"]["signed_best_gap_BU"]
            if ":outside_2m60"in record:assert x["scalar_RNE64"]["result"]["status"]=="STOP"and d["scalar_RNE64_retained_status"]=="STOP"
        runs.append(dict(id="retained:"+record,request=q,result=r))
    record="retained:HOST_HILO32:synthetic:xy:0:outside_2m60";q=m.selector(record,e)
    for k in q:
        bad=dict(q);bad[k]="wrong";r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"and r["RN64_operations"]==0
        runs.append(dict(id="selector:"+k,request=bad,result=r))
    for label,bad in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"and r["RN64_operations"]==0;runs.append(dict(id="selector:"+label,request=bad,result=r))
    r=m._audit("GPU",q,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",request=q,result=r))
    g=2.**-60;t=2.**-120;helpers=[]
    for label,a,b,exact in(("small_gap",(1.,g),(1.,0.),True),("keep_pair",(1.,g),(0.,0.),True),
        ("negative_pair",(-1.,-g),(0.,0.),True),("zero",(0.,0.),(0.,0.),True),("three_scales_inexact",(1.,g),(0.,t),False)):
        h=m.subtract(a,b);assert h["exact_pair_difference"]is exact and h["native_RN64_operations"]==26
        if not exact:assert F(*h["error_abs_BU"])==F(1,2**120)
        helpers.append(dict(id=label,input_a=[m.pair(F.from_float(v))for v in a],input_b=[m.pair(F.from_float(v))for v in b],result=h,
            status="CONTROL_ONLY_NOT_SCENE_ADMISSION"))
    rejected=m.subtract((float("inf"),0.),(0.,0.));assert rejected["status"]=="STOP"and rejected["native_RN64_operations"]==0
    public=m.audit(m.MODEL,q);assert public==next(v["result"]for v in runs if v["id"]=="retained:"+record)
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q);m.retained=saved;assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    saved=m.subtract
    def injected(a,b):
        return dict(status="CONTROL_ONLY",reason=None,native_RN64_operations=0,CPU_native_executed=False,GPU_executed=False,
            exact_pair_difference=False,target_debug_BU=[0,1],error_abs_BU=[1,2**120],trace=dict(nodes=[],eft=[]))
    m.subtract=injected;inexact=m._audit(m.MODEL,q,e);m.subtract=saved
    assert inexact["reason"]=="inexact_difference_cannot_use_translation_cache"and inexact["rows"]==[]and inexact["RN64_operations"]==0
    assert list(inspect.signature(m.audit).parameters)==["model","request"]
    for r in[v["result"]for v in runs]+[public,missing,inexact]:
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","scene_authenticated","uncertainty_authenticated","full_visibility_certified",
            "phase_certified","physical_field_certified","object_wide_skip","previous_zero_exemption"))
        assert r["promotion"]=="STOP"and r["scalar_RNE64_branch_preserved"]is True and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if r["status"]=="STOP":assert r["rows"]==[]and not r["exact_pair_recenter_verified"]and r["relative_geometry"]is None and r["output_pairs"]==[]
    assert len(runs)==31 and sum(r["result"]["RN64_operations"]for r in runs)==3120
    for r in runs:r["result"]=compact(r["result"])
    print(json.dumps(dict(status="PASS",test_groups=5,capture_schema="ROWS_DEDUP_V1",data=dict(runs=runs,helpers=helpers,nonfinite_helper=rejected,
        public=compact(public),missing=compact(missing),simulated_inexact=compact(inexact),pins=len(pins),
        census=dict(main=31,native_pair_recenter=8,STOP=23,parent_STOP=12,selector_model_STOP=11,thin_HILO_recenter=4),
        main_cost=dict(native_RN64_operations=3120,word32_widens=240,pair_differences=120,translated_certificates=8),
        helper_native_operations=130,GPU_executed=False,compiler_calls=0,producer_replays=0)),sort_keys=True))
if __name__=="__main__":main()
