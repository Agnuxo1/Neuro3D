"""Two CPU-converted words, hi-only failure, inexact pair and subnormal STOP."""
import inspect,json,sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_pair64_encoder_CPU_v1 as m
def main():
    e,pins=m.retained();runs=[]
    for record,x in e.items():
        q=m.selector(record,e);r=m._audit(m.MODEL,q,e);positive=x["result"]["geometric_budget_conditional"]
        assert r["geometric_encoding_budget_conditional"]is positive,(record,r)
        assert r["RN64_conversions"]==(2 if positive else 0)
        runs.append(dict(id="retained:"+record,record_id=record,request=q,result=r))
    record=next(iter(e));q=m.selector(record,e)
    for k in q:
        bad=dict(q);bad[k]="wrong";r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"and r["RN64_conversions"]==0
        runs.append(dict(id="selector:"+k,record_id=record,request=bad,result=r))
    for label,bad in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP";runs.append(dict(id="selector:"+label,record_id=record,request=bad,result=r))
    r=m._audit("GPU",q,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",record_id=record,request=q,result=r))
    helpers=[]
    cases=[
      ("tiny_signal_pair_needed",m.pair(1+F(1,2**60)),m.pair(m.CAP/8-F(1,2**62)),True,2),
      ("pair_inexact_budget_exhausted",m.pair(1+F(1,2**60)+F(1,2**120)),m.pair(m.CAP/8-F(1,2**121)),False,2),
      ("negative_signal",m.pair(-1-F(1,2**60)),[0,1],True,2),
      ("zero",[0,1],[0,1],True,2),
      ("third",[1,3],[0,1],True,2),
      ("subnormal_center",[1,2**1023],[0,1],False,0),
      ("subnormal_residual",m.pair(1+F(1,2**1023)),[0,1],False,1),
      ("typed_bool",[True,1],[0,1],False,0),
      ("bad_radius",[1,1],[-1,1],False,0),
      ("huge_internal",[1,2**2048],[0,1],False,0)]
    for ID,center,radius,positive,calls in cases:
        r=m.encode(center,radius);assert r["geometric_encoding_budget_conditional"]is positive and r["RN64_conversions"]==calls,(ID,r)
        if ID=="tiny_signal_pair_needed":
            d=r["diagnostics"][0];assert not d["hi_only_budget_passes"]and F(*d["encoding_error_turns"])==0 and F(*d["decoded_pair_exact_HOST"])==1+F(1,2**60)
        if ID=="pair_inexact_budget_exhausted":assert F(*r["diagnostics"][0]["encoding_error_turns"])==F(1,2**120)and r["reason"]=="pair_encoding_geometric_budget_exhausted"
        if ID=="subnormal_residual":assert r["conversion_trace"][0]["word_LE"]=="000000000000f03f"
        helpers.append(dict(id=ID,center=center,radius=radius,result=r))
    public=m.audit(m.MODEL,q);assert public==runs[0]["result"];saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q);m.retained=saved;assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    flags=("GPU_launch_allowed","GPU_executed","CPU_native_executed","scene_authenticated","uncertainty_authenticated","wavelength_authenticated","total_phase_certified","full_visibility_certified","phase_certified","physical_field_certified","optical_reference_certified","correlation_assumed","periodic_wrapping_used","native_scalar_sum_executed")
    for x in runs+helpers+[dict(result=public),dict(result=missing)]:
        r=x["result"];assert all(r[k]is False for k in flags)
        assert r["root_calls"]==r["RN64_operations"]==r["producer_replays"]==0 and r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert r["CPU_binary64_conversion_executed"]is(r["RN64_conversions"]>0)
        assert len(r["conversion_trace"])==r["RN64_conversions"]
        if r["status"]=="STOP":assert r["rows"]==[]and r["pair_words_LE"]is None and not r["geometric_encoding_budget_conditional"]
    assert list(inspect.signature(m.audit).parameters)==["model","request"]
    assert len(runs)==103 and sum(x["result"]["geometric_encoding_budget_conditional"]for x in runs)==13
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,helpers=helpers,public=public,missing=missing,pins=len(pins),
        census=dict(main=103,CPU_word_pairs=13,STOP=90,parent_records=91,parent_STOP=78,selector_model=12,helper_PASS=4,helper_STOP=6),
        main_RN64_conversions=26,helper_RN64_conversions=11,GPU_executed=False,native_scalar_sum_executed=False,root_calls=0,producer_replays=0)),sort_keys=True))
if __name__=="__main__":main()
