"""Consumer rounding changes the geometry even with a byte-matching hi-lo frame."""
import inspect,json,sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_hilo_reconstruct_CPU_v1 as m

def main():
    e,pins=m.evidence();runs=[]
    for record,x in e.items():
        if record=="__certificates__":continue
        for consumer in m.CONSUMERS:
            q=m.selector(record,consumer,e);r=m._audit(m.MODEL,q,e)
            blocked=x["result"]["status"]=="STOP"
            lost=not blocked and ":outside_2m60"in record
            assert r["status"]==("STOP"if blocked or lost else "CPU_ROUNDED_POSITION_SEPARATION_ONLY"),(record,consumer,r)
            if blocked:assert r["reason"]=="parent_STOP_not_rescued"and r["diagnostics"]==[]and all(v==0 for v in r["HOST_cost"].values())
            elif lost:
                assert "HOST_HILO32:"in record and r["reason"]=="consumer_rounding_exhausts_separator"
                assert r["HOST_cost"]["new_separator_evaluations"]==1 and r["HOST_cost"]["cached_separator_reuses"]==0
                assert F(*r["diagnostics"][0]["separator"]["signed_best_gap_BU"])==0
            else:assert r["HOST_cost"]["cached_separator_reuses"]==1 and r["HOST_cost"]["new_separator_evaluations"]==0
            runs.append(dict(id=consumer+":"+record,request=q,result=r))
    record="retained:HOST_HILO32:synthetic:xy:0:outside_2m60";q=m.selector(record,"ANALYTICAL_RNE64",e)
    for key in q:
        bad=dict(q);bad[key]="wrong";r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"and r["diagnostics"]==[]
        runs.append(dict(id="selector:"+key,request=bad,result=r))
    for label,bad in(("extra",dict(q,extra="x")),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,consumer=64))):
        r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"and r["diagnostics"]==[]
        runs.append(dict(id="selector:"+label,request=bad,result=r))
    r=m._audit("GPU",q,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",request=q,result=r))
    helpers=[]
    for consumer,(_,p,emin,emax,_)in m.CONSUMERS.items():
        values=[F(0),F(1),F(-1),F(1)+F(1,2**p),F(1)+F(3,2**p),-(F(1)+F(1,2**p)),F(1,10),F(2)**emin]
        for i,v in enumerate(values):helpers.append(dict(id=consumer+":"+str(i),consumer=consumer,original_BU=m.pair(v),rounded=m.rounded(v,consumer)))
    negatives=[]
    for consumer,(_,p,emin,emax,_)in m.CONSUMERS.items():
        values=[("subnormal",F(2)**(emin-1)),("overflow_domain",F(2)**(emax+1)),("overflow_round",F(2)**(emax+1)-F(2)**(emax-p))]
        for label,v in values:
            try:m.rounded(v,consumer)
            except ValueError as ex:negatives.append(dict(id=consumer+":"+label,status="STOP",reason=str(ex)))
            else:raise AssertionError("negative admitted")
    for label,v,consumer in(("non_fraction",1,"ANALYTICAL_RNE64"),("unknown",F(1),"RN64"),("bool",F(1),True)):
        try:m.rounded(v,consumer)
        except ValueError as ex:negatives.append(dict(id=label,status="STOP",reason=str(ex)))
        else:raise AssertionError("negative admitted")
    public=m.audit(m.MODEL,q);assert public==next(x["result"]for x in runs if x["id"]=="ANALYTICAL_RNE64:"+record)
    saved=m.evidence
    def missing():raise ValueError("simulated_missing_receipt")
    m.evidence=missing;absent=m.audit(m.MODEL,q);m.evidence=saved
    assert absent["reason"]=="evidence_integrity:simulated_missing_receipt"
    assert list(inspect.signature(m.audit).parameters)==["model","request"]
    for r in[x["result"]for x in runs]+[public,absent]:
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","scene_authenticated","uncertainty_authenticated",
            "full_visibility_certified","phase_certified","physical_field_certified","object_wide_skip","previous_zero_exemption"))
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"and r["epsilon_BU"]==[0,1]
        if r["status"]=="STOP":assert not r["consumer_error_derived"]and r["rows"]==[]and r["rounded_geometry"]is None and r["consumer_words"]==[]
    costs={k:sum(x["result"]["HOST_cost"][k]for x in runs)for k in m.baseline()["HOST_cost"]}
    assert costs==dict(RNE_rounds=3600,original_error_differences=3600,new_separator_evaluations=48,cached_separator_reuses=192)
    assert len(runs)==330 and len(helpers)==16 and len(negatives)==9
    def compact(r):
        # Lossless relative to sealed ancestor: keep fresh bounds, reference exact cached certificate.
        z=dict(r);z.pop("rows");z["rows_mode"]="EMPTY"if r["status"]=="STOP"else "DIAGNOSTICS"
        z["result_sha256"]=m.digest(r);z["diagnostics"]=[dict(d)for d in r["diagnostics"]]
        if z["diagnostics"]and z["diagnostics"][0]["separator_source"]=="SEALED_PARENT_CERTIFICATE":
            d=z["diagnostics"][0];d["cached_separator_sha256"]=m.digest(d.pop("separator"))
        return z
    for x in runs:x["result"]=compact(x["result"])
    print(json.dumps(dict(status="PASS",test_groups=5,capture_schema="ROWS_AND_PINNED_CERTIFICATE_DEDUP_V1",data=dict(runs=runs,helpers=helpers,negative_helpers=negatives,public=compact(public),missing=compact(absent),
        pins=len(pins),main_cost=costs,census=dict(main=330,CPU_separation=192,STOP=138,parent_STOP=80,consumer_gaploss_STOP=48,selector_model_STOP=10),
        GPU_executed=False,compiler_calls=0,producer_replays=0)),sort_keys=True))
if __name__=="__main__":main()
