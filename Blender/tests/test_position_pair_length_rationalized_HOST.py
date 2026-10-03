"""Identity branch, signs, fail-closed denominator; old fixed96 branch retained."""
import inspect,json,sys
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_pair_length_rationalized_HOST_v1 as m
def main():
    e,pins=m.retained();runs=[];tight=[];non_nested=[]
    for record,x in e.items():
        q=m.selector(record,e);r=m._audit(m.MODEL,q,e);blocked=x["result"]["status"]=="STOP"
        assert r["status"]==("STOP"if blocked else"HOST_RATIONALIZED_LENGTH_DIFFERENCE_ONLY"),(record,r)
        if blocked:assert r["reason"]=="parent_STOP_not_rescued"and all(v==0 for v in r["HOST_cost"].values())
        else:
            assert r["HOST_cost"]==dict(original_squared_norms=4,parent_roots_checked=4,rationalized_differences=4,helper_roots_checked=8,exact_divisions=6,algebraic_zero_cases=1)
            assert r["differences"][0]["interval_BU"]==[[0,1],[0,1]]
            for z in r["differences"]:
                lo,hi=map(lambda v:F(*v),z["interval_BU"]);oldlo,oldhi=map(lambda v:F(*v),z["old_interval_retained"]["difference_interval_BU"])
                # Both enclosures contain the same root difference; nesting is NOT universal.
                assert max(oldlo,lo)<=min(oldhi,hi)
                if not oldlo<=lo<=hi<=oldhi:
                    non_nested.append(dict(record_id=record,point=z["point"],new_interval_BU=z["interval_BU"],old_interval_BU=z["old_interval_retained"]["difference_interval_BU"],status="NON_NESTING_COUNTEREXAMPLE_RETAINED"))
                if ":outside_2m60"in record and F(*z["squared_BU2"])==4+F(1,2**120):
                    assert oldlo==0 and 0<lo<=hi==F(1,2**122) and hi-lo<F(1,2**220)
                    tight.append(dict(record_id=record,point=z["point"],old_interval_BU=z["old_interval_retained"]["difference_interval_BU"],new_interval_BU=z["interval_BU"],
                        status="POSITIVE_EXTENSION_HOST_IDENTITY_ONLY_OLD_BRANCH_UNCHANGED",phase_admission=False))
        runs.append(dict(id=record,request=q,result=r))
    record=next(iter(e));q=m.selector(record,e)
    for k in q:
        bad=dict(q);bad[k]="wrong";r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP";runs.append(dict(id="selector:"+k,request=bad,result=r))
    for label,bad in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP";runs.append(dict(id="selector:"+label,request=bad,result=r))
    r=m._audit("GPU",q,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",request=q,result=r))
    mutations=[]
    for label in("last_squared","last_root","last_order","last_bits","source_context","optical_reference","last_delta"):
        ee=deepcopy(e);r=ee[record]["result"];z=r["lengths"][-1]
        if label=="last_squared":z["squared_BU2"]=[1,1]
        elif label=="last_root":z["length_interval_BU"][0]=[0,1]
        elif label=="last_order":z["point"]=True
        elif label=="last_bits":z["fractional_bits"]=128
        elif label=="source_context":r["rows"][0]["source_context"]["provenance"]="WRONG"
        elif label=="optical_reference":r["optical_reference_certified"]=True
        else:z["delta_BU"][0]=[0,1]
        # Keep redundant capture views coherent so each targeted guard is reached.
        r["rows"][0]["lengths"]=r["lengths"];r["rows"][0]["relative_lengths"]=r["relative_lengths"]
        r["diagnostics"]=r["rows"]
        qq=m.selector(record,ee);out=m._audit(m.MODEL,qq,ee);assert out["status"]=="STOP"and out["HOST_cost"]["rationalized_differences"]==0 and out["differences"]==[]
        mutations.append(dict(id=label,request=qq,result=out))
    step=F(1,2**96)
    cases=[
        ("positive",[[4,1],[1,1],[[2,1],[2,1]],[[1,1],[1,1]]],"HOST_RATIONALIZED_DIFFERENCE_ONLY","POSITIVE"),
        ("negative",[[1,1],[4,1],[[1,1],[1,1]],[[2,1],[2,1]]],"HOST_RATIONALIZED_DIFFERENCE_ONLY","NEGATIVE"),
        ("bothzero",[[0,1],[0,1],[[0,1],[0,1]],[[0,1],[0,1]]],"HOST_RATIONALIZED_DIFFERENCE_ONLY","ZERO_IDENTICAL_SQUARED_NORMS"),
        ("sameirrational",[[2,1],[2,1],e[record]["result"]["lengths"][0]["length_interval_BU"],e[record]["result"]["lengths"][0]["length_interval_BU"]],"STOP",None)]
    # Explicit sqrt2 fixed96 cell from its sealed parent control, not root execution.
    from coplanar_clearance_CPU_v1 import capture
    parent=json.loads((m.ROOT/m.PARENT).read_bytes());iv=capture(parent["test_run"])["data"]["controls"][2]["interval_BU"]
    cases[-1]=("sameirrational",[[2,1],[2,1],iv,iv],"HOST_RATIONALIZED_DIFFERENCE_ONLY","ZERO_IDENTICAL_SQUARED_NORMS")
    cases += [
        ("tiny_denominator",[[1,2**240],[0,1],[[0,1],m.pair(step)],[[0,1],[0,1]]],"STOP",None),
        ("typedbool",[[True,1],[1,1],[[1,1],[1,1]],[[1,1],[1,1]]],"STOP",None),
        ("negative_squared",[[-1,1],[1,1],[[0,1],[0,1]],[[1,1],[1,1]]],"STOP",None),
        ("bad_root",[[4,1],[1,1],[[1,1],[2,1]],[[1,1],[1,1]]],"STOP",None),
        ("overflowdomain",[[1,2**256],[0,1],[[0,1],[0,1]],[[0,1],[0,1]]],"STOP",None)]
    helpers=[]
    for label,args,status,sign in cases:
        v=m.rationalized(*args);assert v["status"]==status and v["sign"]==sign,(label,v)
        if label=="tiny_denominator":assert v["reason"]=="nonpositive_denominator_lower_NO_EPSILON"and v["exact_divisions"]==0
        helpers.append(dict(id=label,args=args,result=v))
    public=m.audit(m.MODEL,q);assert public==runs[0]["result"];saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q);m.retained=saved;assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    assert list(inspect.signature(m.audit).parameters)==["model","request"]and len(tight)==3
    for r in [v["result"]for v in runs+mutations]+[public,missing]:
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","CPU_native_executed","scene_authenticated","uncertainty_authenticated","full_visibility_certified","phase_certified","physical_field_certified","optical_reference_certified"))
        assert r["promotion"]=="STOP"and r["RN64_operations"]==r["root_calls"]==0 and r["parent_interval_branch_unchanged"]is True and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if r["status"]=="STOP":assert r["rows"]==r["differences"]==[]and not r["difference_enclosure_verified"]
    assert len(runs)==31
    assert non_nested
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,mutations=mutations,helpers=helpers,tight=tight,non_nested=non_nested,public=public,missing=missing,pins=len(pins),
        census=dict(main=31,HOST=8,STOP=23,mutation_STOP=7,helper_HOST=4,helper_STOP=5,positive_tight=3),GPU_executed=False,root_calls=0,native_replays=0)),sort_keys=True))
if __name__=="__main__":main()
