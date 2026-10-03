"""Bounded conditional-box separation controls; no parent producer replay."""
import copy,inspect,itertools,json,sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import coplanar_clearance_CPU_v1 as m
def uncertainty(radius):
    return dict(schema="DECLARED_INDEPENDENT_COORDINATE_BOXES_ONLY",points_BU=[[m.pair(F(radius))for k in range(3)]for i in range(5)])
def main():
    e,pins=m.retained();runs=[];g=F(1,2**60)
    def run(label,case,u,expected,reason=None):
        q=m.selector(case,e);r=m._audit(m.MODEL,q,u,e)
        assert r["status"]==expected
        if reason is not None:assert r["reason"]==reason
        runs.append(dict(id=label+":"+case,request=q,uncertainty=u,result=r))
        return r
    good="CPU_CONDITIONAL_DECLARED_BOX_SEPARATION_ONLY"
    misses=[case for case,x in e.items()if x["result"]["status"]=="CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY"]
    contacts=[case for case in e if case not in misses]
    assert len(misses)==72 and len(contacts)==8
    for case in misses:
        run("zero",case,uncertainty(0),good)
        run("huge",case,uncertainty(10**6),"STOP","uncertainty_exhausts_separator")
    thin=[case for case in misses if case.endswith(":outside_2m60")];assert len(thin)==24
    for case in thin:
        r=run("quarter_each",case,uncertainty(g/4),good)
        assert F(*r["clearance_lower_BU"])==g/2
        for label,rad in (("half_each",g/2),("full_each",g)):
            run(label,case,uncertainty(rad),"STOP","uncertainty_exhausts_separator")
    for case in contacts:
        for label,rad in(("contact_zero",0),("contact_huge",10**6)):
            run(label,case,uncertainty(rad),"STOP","parent_contact_STOP")
    case="synthetic:xy:0:outside_2m60";q=m.selector(case,e)
    for i in range(5):
        u=uncertainty(0);u["points_BU"][i]=[m.pair(F(10))for k in range(3)]
        run("single_point_"+str(i),case,u,"STOP","uncertainty_exhausts_separator")
    for key in q:
        bad=dict(q);bad[key]="wrong";r=m._audit(m.MODEL,bad,uncertainty(0),e);assert r["status"]=="STOP"
        runs.append(dict(id="selector:"+key,request=bad,uncertainty=uncertainty(0),result=r))
    for label,bad in(("extra",dict(q,extra="x")),("bool_case",dict(q,case=False)),("missing",{k:v for k,v in q.items()if k!="intent"})):
        r=m._audit(m.MODEL,bad,uncertainty(0),e);assert r["status"]=="STOP"and r["diagnostics"]==[]
        runs.append(dict(id="selector:"+label,request=bad,uncertainty=uncertainty(0),result=r))
    r=m._audit("GPU",q,uncertainty(0),e);assert r["reason"]=="explicit_model"
    runs.append(dict(id="wrong_model",request=q,uncertainty=uncertainty(0),result=r))
    malformed=[]
    for label in("negative","den0","bool","float","oversize","radius_bound","short_points","short_vector","extra","schema","missing","none"):
        u=uncertainty(0)
        if label=="negative":u["points_BU"][0][0]=[-1,1]
        elif label=="den0":u["points_BU"][0][0]=[1,0]
        elif label=="bool":u["points_BU"][0][0]=[True,1]
        elif label=="float":u["points_BU"][0][0]=[float("inf"),1]
        elif label=="oversize":u["points_BU"][0][0]=[1,2**129]
        elif label=="radius_bound":u["points_BU"][0][0]=[1000001,1]
        elif label=="short_points":u["points_BU"].pop()
        elif label=="short_vector":u["points_BU"][0].pop()
        elif label=="extra":u["extra"]=0
        elif label=="schema":u["schema"]="MEASURED_GPU"
        elif label=="missing":del u["points_BU"]
        else:u=None
        r=m._audit(m.MODEL,q,u,e);assert r["status"]=="STOP"and r["diagnostics"]==[]
        malformed.append(dict(id=label,result=r))
    public=m.audit(m.MODEL,q,uncertainty(g/4));assert public["status"]==good
    saved=m.retained
    def missing():raise ValueError("simulated_missing_receipt")
    m.retained=missing;absent=m.audit(m.MODEL,q,uncertainty(0));m.retained=saved
    assert absent["reason"]=="evidence_integrity:simulated_missing_receipt"
    assert list(inspect.signature(m.audit).parameters)==["model","request","declared_uncertainty"]
    for r in [x["result"]for x in runs]+[x["result"]for x in malformed]+[public,absent]:
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","scene_authenticated","uncertainty_authenticated",
            "full_visibility_certified","phase_certified","physical_field_certified","object_wide_skip","previous_zero_exemption"))
        assert r["promotion"]=="STOP"and r["epsilon_BU"]==[0,1]and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert (r["compiler_calls"],r["producer_replays"],r["RN64_operations"])==(0,0,0)
        if r["status"]=="STOP":assert r["rows"]==[]and r["verified_queries"]==0 and r["clearance_lower_BU"]is None
    assert len(runs)==246
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,malformed_controls=malformed,public=public,missing=absent,
        census=dict(main=246,conditional=96,STOP=150,malformed=12,auxiliary=2,thin=24,single_point_controls=5),
        GPU_executed=False,compiler_calls=0,RN64_operations=0,producer_replays=0)),sort_keys=True))
if __name__=="__main__":main()
