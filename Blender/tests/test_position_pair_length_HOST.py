"""Sealed pair words -> fixed96 HOST norms; resolution limits stay visible."""
import json,inspect,sys
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_pair_length_HOST_v1 as m

def main():
    e,pins=m.retained();runs=[]
    for record,x in e.items():
        q=m.selector(record,e);r=m._audit(m.MODEL,q,e);blocked=x["result"]["status"]=="STOP"
        assert r["status"]==("STOP" if blocked else "HOST_PAIR_LENGTH_ENCLOSURE_ONLY"),(record,r)
        if blocked:assert r["reason"]=="parent_STOP_not_rescued" and all(v==0 for v in r["HOST_cost"].values())
        else:
            assert r["HOST_cost"]==dict(pair_words_decoded=30,exact_pair_sums=15,squared_norms=4,sqrt_brackets=4,reference_subtractions=6)
            assert r["relative_lengths"][0]["difference_interval_BU"]==[[0,1],[0,1]]
            for z in r["lengths"]:
                s=F(*z["squared_BU2"]);a,b=map(lambda v:F(*v),z["length_interval_BU"])
                assert 0<=a and a*a<=s<=b*b and b-a<=F(1,2**96)
        runs.append(dict(id=record,request=q,result=r))
    record=next(iter(e));q=m.selector(record,e)
    for k in q:
        bad=dict(q);bad[k]="wrong";r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP"
        runs.append(dict(id="selector:"+k,request=bad,result=r))
    for label,bad in (("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP";runs.append(dict(id="selector:"+label,request=bad,result=r))
    r=m._audit("GPU",q,e);assert r["reason"]=="explicit_model";runs.append(dict(id="wrong_model",request=q,result=r))
    mutations=[]
    for label in ("last_word_bad","last_nonfinite","last_subnormal","last_word_vs_ORIGINAL","duplicate_coordinate","false_exact","wrong_context","wrong_geometry"):
        ee=deepcopy(e);p=ee[record]["result"]["output_pairs"][-1];t=ee[record]["result"]["diagnostics"][0]["coordinates"][-1]
        if label=="last_word_bad":p["lo_word_le_hex"]=t["lo_word_le_hex"]="z"*16
        elif label=="last_nonfinite":p["lo_word_le_hex"]=t["lo_word_le_hex"]="000000000000f07f"
        elif label=="last_subnormal":p["lo_word_le_hex"]=t["lo_word_le_hex"]="0100000000000000"
        elif label=="last_word_vs_ORIGINAL":p["lo_word_le_hex"]=t["lo_word_le_hex"]="000000000000f03f"
        elif label=="duplicate_coordinate":p["point"]=0
        elif label=="false_exact":t["exact_pair_difference"]=False
        elif label=="wrong_context":ee[record]["result"]["relative_geometry"]["context"]["coordinate_frame"]="OTHER"
        else:ee[record]["result"]["diagnostics"][0]["original_geometry"]["end_BU"][0]=[3,1]
        qq=m.selector(record,ee);r=m._audit(m.MODEL,qq,ee)
        assert r["status"]=="STOP" and r["lengths"]==[]and r["HOST_cost"]["sqrt_brackets"]==0,(label,r)
        mutations.append(dict(id=label,request=qq,result=r))
    controls=[]
    for label,s in (("zero",F(0)),("square",F(4)),("irrational",F(2)),("tangential_2m60_gap",F(4)+F(1,2**120)),("tiny",F(1,2**240))):
        a,b=m.root(s);controls.append(dict(id=label,squared_BU2=m.pair(s),interval_BU=[m.pair(a),m.pair(b)],fractional_bits=96))
    tangent=controls[3];a,b=map(lambda v:F(*v),tangent["interval_BU"])
    assert a==2 and b==2+F(1,2**96) and F(*tangent["squared_BU2"])>4
    limit=[]
    for x in runs:
        if ":outside_2m60" in x["id"]and x["result"]["status"]!="STOP":
            for z in x["result"]["lengths"]:
                if F(*z["squared_BU2"])==4+F(1,2**120):
                    a,b=map(lambda v:F(*v),z["length_interval_BU"]);assert a==2 and b>2
                    limit.append(dict(record_id=x["id"],point=z["point"],status="UNRESOLVED_EXTENSION_AT_FIXED96BITS",squared_BU2=z["squared_BU2"],
                        length_interval_BU=z["length_interval_BU"],scalar_length_control_BU=[2,1],phase_admission=False))
    assert len(limit)==3
    public=m.audit(m.MODEL,q);assert public==runs[0]["result"]
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q);m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    assert list(inspect.signature(m.audit).parameters)==["model","request"]
    for r in [x["result"]for x in runs+mutations]+[public,missing]:
        assert all(r[k]is False for k in ("GPU_launch_allowed","GPU_executed","CPU_native_executed","scene_authenticated","uncertainty_authenticated",
            "full_visibility_certified","phase_certified","physical_field_certified","optical_reference_certified","parent_native_execution_replayed"))
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"and r["RN64_operations"]==0
        if r["status"]=="STOP":assert r["rows"]==[]and r["lengths"]==[]and r["relative_lengths"]==[]and not r["length_enclosure_verified"]
    assert len(runs)==31 and sum(x["result"]["HOST_cost"]["sqrt_brackets"]for x in runs)==32
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,mutations=mutations,controls=controls,limit=limit,public=public,missing=missing,
        pins=len(pins),census=dict(main=31,HOST=8,STOP=23,mutation_STOP=8,root_helpers=5,fixed96_unresolved=3),GPU_executed=False,native_replays=0)),sort_keys=True))
if __name__=="__main__":main()
