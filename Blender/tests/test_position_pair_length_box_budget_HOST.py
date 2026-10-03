"""SOURCE, vertex and end boxes charged; conditional only, fixed96 untouched."""
import inspect,json,sys
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_pair_length_box_budget_HOST_v1 as m
def main():
    e,pins=m.retained();runs=[]
    for record,x in e.items():
        boxes=m.zero_boxes();q=m.selector(record,e,boxes);r=m._audit(m.MODEL,q,boxes,e)
        blocked=x["nominal"]["result"]["status"]=="STOP";negative=":tilted:0:outside_2m60"in record
        assert r["status"]==("STOP"if blocked or negative else"HOST_CONDITIONAL_DECLARED_BOX_POSITIVE_DIFFERENCE_ONLY"),(record,r)
        if blocked:assert r["reason"]=="parent_STOP_not_rescued"and all(v==0 for v in r["HOST_cost"].values())
        runs.append(dict(id="zero:"+record,record_id=record,request=q,boxes=boxes,result=r))
    for plane,(xcoord,ycoord)in {"xy":(0,1),"xz":(0,2),"yz":(1,2)}.items():
        record=next(k for k in e if ":HOST_HILO32:synthetic:"+plane+":0:outside_2m60"in k)
        for label,point,coord,rad,positive in(("source_y_half_gap",0,ycoord,F(1,2**61),False),("vertex_y_gap",3,ycoord,F(1,2**60),False),
            ("end_x_2m122",1,xcoord,F(1,2**122),False),("end_x_2m125",1,xcoord,F(1,2**125),True)):
            boxes=m.zero_boxes();boxes["points_BU"][point][coord]=m.pair(rad);q=m.selector(record,e,boxes);r=m._audit(m.MODEL,q,boxes,e)
            assert r["conditional_difference_certified"]is positive,(label,plane,r)
            if not positive:assert r["reason"]=="declared_boxes_do_not_certify_strict_positive_difference"and F(*r["diagnostics"][0]["numerator_interval_BU2"][0])<=0
            if point==0:
                d=r["diagnostics"][0];assert F(*d["target_delta_radii_BU"][coord])==F(*d["reference_delta_radii_BU"][coord])==rad
            runs.append(dict(id=plane+":"+label,record_id=record,request=q,boxes=boxes,result=r))
    record=next(iter(e));boxes=m.zero_boxes();q=m.selector(record,e,boxes)
    for k in q:
        bad=dict(q);bad[k]="wrong";r=m._audit(m.MODEL,bad,boxes,e);assert r["status"]=="STOP"
        runs.append(dict(id="selector:"+k,record_id=record,request=bad,boxes=boxes,result=r))
    for label,bad in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        r=m._audit(m.MODEL,bad,boxes,e);assert r["status"]=="STOP";runs.append(dict(id="selector:"+label,record_id=record,request=bad,boxes=boxes,result=r))
    r=m._audit("GPU",q,boxes,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",record_id=record,request=q,boxes=boxes,result=r))
    for label in("extra","missing","schema","negative_tail","bool_tail","string_tail","overflow_tail","wrongshape"):
        bad=deepcopy(boxes)
        if label=="extra":bad["extra"]=0
        elif label=="missing":bad.pop("points_BU")
        elif label=="schema":bad["schema"]="MEASURED_AUTHENTICATED"
        elif label=="negative_tail":bad["points_BU"][-1][-1]=[-1,1]
        elif label=="bool_tail":bad["points_BU"][-1][-1]=[True,1]
        elif label=="string_tail":bad["points_BU"][-1][-1]="0"
        elif label=="overflow_tail":bad["points_BU"][-1][-1]=[1,2**128]
        else:bad["points_BU"][-1].pop()
        qq=m.selector(record,e,bad);r=m._audit(m.MODEL,qq,bad,e);assert r["status"]=="STOP"and r["HOST_cost"]["squared_box_bounds"]==0
        runs.append(dict(id="malformed:"+label,record_id=record,request=qq,boxes=bad,result=r))
    bad=m.zero_boxes();bad["points_BU"][0][0]=[4,1];qq=m.selector(record,e,bad);r=m._audit(m.MODEL,qq,bad,e)
    assert r["reason"]=="nonpositive_denominator_lower_NO_EPSILON"and r["HOST_cost"]["ratio_corner_divisions"]==0
    runs.append(dict(id="denominator_exhausted",record_id=record,request=qq,boxes=bad,result=r))
    public=m.audit(m.MODEL,q,boxes);assert public==runs[0]["result"];saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q,boxes);m.retained=saved;assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    assert list(inspect.signature(m.audit).parameters)==["model","request","declared_boxes"]
    for x in runs+[dict(result=public),dict(result=missing)]:
        r=x["result"]
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","CPU_native_executed","scene_authenticated","uncertainty_authenticated","full_visibility_certified","phase_certified","physical_field_certified","optical_reference_certified","correlation_assumed"))
        assert r["declared_uncertainty_only"]and r["parent_branches_unchanged"]and r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"and r["root_calls"]==r["RN64_operations"]==0
        if r["status"]=="STOP":assert r["rows"]==[]and r["difference_interval_BU"]is None and not r["conditional_difference_certified"]
    assert len(runs)==53 and sum(v["result"]["conditional_difference_certified"]for v in runs)==10
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,public=public,missing=missing,pins=len(pins),
        census=dict(main=53,HOST=10,STOP=43,zero_parent=20,uncertainty_scenarios=12,selector_model=12,malformed=8,denominator_exhausted=1),
        GPU_executed=False,root_calls=0,native_replays=0)),sort_keys=True))
if __name__=="__main__":main()
