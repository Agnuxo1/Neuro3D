"""Explicit geometric SOURCE lambda/error bound; no phase total or circular rescue."""
import inspect,json,sys
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_box_wavelength_budget_HOST_v1 as m
def main():
    e,pins=m.retained();runs=[]
    def run(ID,record,p,expected):
        q=m.selector(record,e,p);r=m._audit(m.MODEL,q,p,e);assert r["geometric_budget_conditional"]is expected,(ID,r)
        runs.append(dict(id=ID,record_id=record,request=q,parameters=p,result=r));return r
    for record,x in e.items():
        run("retained:"+record,record,m.parameters(record,e),x["result"]["conditional_difference_certified"])
    for plane in("xy","xz","yz"):
        zero=next(k for k in e if k.startswith("zero:")and ":HOST_HILO32:synthetic:"+plane+":0:outside_2m60"in k)
        p=m.parameters(zero,e);p["wavelength_BU"]=[1,2**120];run(plane+":small_lambda",zero,p,True)
        p=deepcopy(p);p["wavelength_radius_BU"]=[1,2**122];run(plane+":lambda_uncertain",zero,p,False)
        under=plane+":end_x_2m125";p=m.parameters(under,e);p["wavelength_BU"]=[1,2**120]
        run(plane+":position_uncertain",under,p,False)
        p=m.parameters(zero,e);p["wavelength_BU"]=[1,2**120];p["wavelength_radius_BU"]=[1,2**120]
        r=run(plane+":zero_lambda_lower",zero,p,False);assert r["reason"]=="nonpositive_lambda_lower_NO_EPSILON"and r["HOST_cost"]["exact_divisions"]==0
    record=next(iter(e));p=m.parameters(record,e);q=m.selector(record,e,p)
    for k in q:
        bad=dict(q);bad[k]="wrong";r=m._audit(m.MODEL,bad,p,e);assert r["status"]=="STOP"
        runs.append(dict(id="selector:"+k,record_id=record,request=bad,parameters=p,result=r))
    for label,bad in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        r=m._audit(m.MODEL,bad,p,e);assert r["status"]=="STOP";runs.append(dict(id="selector:"+label,record_id=record,request=bad,parameters=p,result=r))
    r=m._audit("GPU",q,p,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",record_id=record,request=q,parameters=p,result=r))
    for label in("extra","missing","schema","context","reference","target_bool","units","auth","zero","negative","radius_negative","radius_bool","overflow","cap_raised","cap_bool"):
        bad=deepcopy(p)
        if label=="extra":bad["extra"]=0
        elif label=="missing":bad.pop("wavelength_BU")
        elif label=="schema":bad["schema"]="MEASURED"
        elif label=="context":bad["source_context"]=dict(bad["source_context"],other_source="S1")
        elif label=="reference":bad["reference_point"]=0
        elif label=="target_bool":bad["target_point"]=True
        elif label=="units":bad["units"]["wavelength"]="m"
        elif label=="auth":bad["authentication"]="AUTHENTICATED"
        elif label=="zero":bad["wavelength_BU"]=[0,1]
        elif label=="negative":bad["wavelength_BU"]=[-1,1]
        elif label=="radius_negative":bad["wavelength_radius_BU"]=[-1,1]
        elif label=="radius_bool":bad["wavelength_radius_BU"]=[True,1]
        elif label=="overflow":bad["wavelength_BU"]=[1,2**128]
        elif label=="cap_raised":bad["cap_rad"]=[1,1]
        else:bad["cap_rad"]=[True,10000]
        r=run("malformed:"+label,record,bad,False);assert r["HOST_cost"]["exact_divisions"]==0
    public=m.audit(m.MODEL,q,p);assert public==runs[0]["result"];saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q,p);m.retained=saved;assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    flags=("GPU_launch_allowed","GPU_executed","CPU_native_executed","scene_authenticated","uncertainty_authenticated","wavelength_authenticated","total_phase_certified","full_visibility_certified","phase_certified","physical_field_certified","optical_reference_certified","correlation_assumed","periodic_wrapping_used")
    for x in runs+[dict(result=public),dict(result=missing)]:
        r=x["result"];assert all(r[k]is False for k in flags)
        assert r["root_calls"]==r["RN64_operations"]==r["producer_replays"]==0 and r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if r["status"]=="STOP":assert r["rows"]==[]and r["turns_interval"]is None and not r["geometric_budget_conditional"]
    assert list(inspect.signature(m.audit).parameters)==["model","request","declared_source"]
    assert len(runs)==91 and sum(x["result"]["geometric_budget_conditional"]for x in runs)==13
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,public=public,missing=missing,pins=len(pins),
        census=dict(main=91,HOST=13,STOP=78,parent_records=53,parent_STOP=43,new_lambda_cases=12,selector_model=11,malformed=15),
        GPU_executed=False,root_calls=0,producer_replays=0)),sort_keys=True))
if __name__=="__main__":main()
