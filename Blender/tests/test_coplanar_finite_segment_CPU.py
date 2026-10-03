"""Finite-domain geometry controls, sealed coplanar scenes and strict selectors."""
import copy,inspect,itertools,json,sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import coplanar_finite_segment_CPU_v1 as m
def point(v):return [m.p(F(x))for x in v]
def main():
    e,pins=m.retained();runs=[]
    base=[(2,-1),(2,1),(4,0)];g=F(1,2**60)
    queries=[("before",(0,0),(1,0),None),("enter",(0,0),(3,0),[F(2,3),F(1)]),
        ("cross",(0,0),(5,0),[F(2,5),F(4,5)]),("after",(5,0),(6,0),None),
        ("terminal_vertex",(0,1),(2,1),[F(1),F(1)]),("departure_vertex",(2,1),(0,1),[F(0),F(0)]),
        ("closed_edge",(2,-1),(2,1),[F(0),F(1)]),("outside_2m60",(0,1+g),(2,1+g),None),
        ("terminal_inside_2m60",(0,1-g),(2,1-g),[F(1),F(1)])]
    for plane in("xy","xz","yz","tilted"):
        def lift(v):
            x,y=v
            return point((x,y,0)if plane=="xy"else ((x,0,y)if plane=="xz"else ((0,x,y)if plane=="yz"else (x,y,x+y))))
        for order,vs in enumerate(itertools.permutations(base)):
            triangle=[lift(v)for v in vs]
            for label,o,end,interval in queries:
                origin=lift(o);last=lift(end)
                scene=dict(schema="CPU_SYNTHETIC_FINITE_SEGMENT_CONTROL",source_position_BU=origin,segment_end_BU=last,triangle_BU=triangle)
                context=dict(provenance="CPU_SYNTHETIC_ONLY_NOT_SEALED_SCENE",synthetic_scene_sha256=m.digest(scene))
                r=m._classify(origin,last,triangle,context);expected=None if interval is None else list(map(m.p,interval))
                cert=r["diagnostics"][0];assert cert["contact_interval_t"]==expected
                assert cert["empty"]is (interval is None)
                assert r["status"]==("CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY"if interval is None else "STOP")
                if interval is not None:assert r["reason"]=="actual_coplanar_contact"
                runs.append(dict(id="synthetic:"+plane+":"+str(order)+":"+label,scope="CPU_SYNTHETIC_ONLY",
                    origin_BU=origin,end_BU=last,triangle_BU=triangle,expected_interval_t=expected,result=r))
    for case in e:
        for sid in("S0","S1"):
            for j in(0,1):
                q=m.selector(case,sid,j,2,e);r=m._audit(m.MODEL,q,e)
                assert r["reason"]=="actual_coplanar_contact" and r["status"]=="STOP"
                assert r["diagnostics"][0]["contact_interval_t"]==[[0,1],[1,1]]
                assert r["diagnostics"][0]["context"]["parent_STOP_preserved"]is True
                runs.append(dict(id="sealed:"+case+":"+sid+":"+str(j),scope="SEALED_DECLARED_CPU",request=q,result=r))
                for pid in(0,1):
                    bad=m.selector(case,sid,j,pid,e);rr=m._audit(m.MODEL,bad,e)
                    assert rr["status"]=="STOP" and rr["reason"]=="coplanar_only" and rr["diagnostics"]==[]
                    runs.append(dict(id="noncoplanar:"+case+":"+sid+":"+str(j)+":"+str(pid),scope="SEALED_DECLARED_CPU",request=bad,result=rr))
    case="oblique/coplanar";q=m.selector(case,"S0",0,2,e)
    for key in q:
        bad=copy.deepcopy(q);bad[key]="wrong";r=m._audit(m.MODEL,bad,e)
        assert r["status"]=="STOP" and r["diagnostics"]==[]
        runs.append(dict(id="selector:"+key,scope="SELECTOR_NEGATIVE",request=bad,result=r))
    variants=[("extra",dict(q,extra=True)),("segment_bool",dict(q,segment=False)),
        ("primitive_bool",dict(q,primitive_id=True)),("source_swap",dict(q,source_id="S2")),
        ("primitive_unknown",m.selector(case,"S0",0,9,e)),("missing",dict(q))]
    del variants[-1][1]["paths_sha256"]
    for label,bad in variants:
        r=m._audit(m.MODEL,bad,e);assert r["status"]=="STOP" and r["diagnostics"]==[]
        runs.append(dict(id="selector:"+label,scope="SELECTOR_NEGATIVE",request=bad,result=r))
    r=m._audit("GPU",q,e);assert r["reason"]=="explicit_model"
    runs.append(dict(id="wrong_model",scope="MODEL_NEGATIVE",request=q,result=r))
    triangle=list(map(point,[(2,-1,0),(2,1,0),(4,0,0)]));o=point((0,0,0));end=point((1,0,0))
    malformed=[]
    for label in("zero_segment","degenerate","noncoplanar","denominator_zero","bool_rational","too_many_bits","coordinate_bound","float_nan"):
        a=copy.deepcopy(o);b=copy.deepcopy(end);t=copy.deepcopy(triangle)
        if label=="zero_segment":b=copy.deepcopy(a)
        elif label=="degenerate":t=[copy.deepcopy(t[0])for i in range(3)]
        elif label=="noncoplanar":a[2]=[1,1]
        elif label=="denominator_zero":a[0]=[1,0]
        elif label=="bool_rational":a[0]=[True,1]
        elif label=="too_many_bits":a[0]=[1,2**129]
        elif label=="coordinate_bound":a[0]=[1000001,1]
        else:a[0]=[float("nan"),1]
        result=m._classify(a,b,t,dict(provenance="MALFORMED_SYNTHETIC"))
        assert result["status"]=="STOP" and result["diagnostics"]==[]
        malformed.append(dict(id=label,result=result))
    assert list(inspect.signature(m.audit).parameters)==["model","request"]
    public=m.audit(m.MODEL,q);assert public["reason"]=="actual_coplanar_contact"
    saved=m.retained
    def missing():raise ValueError("simulated_missing_receipt")
    m.retained=missing;unavailable=m.audit(m.MODEL,q);m.retained=saved
    assert unavailable["reason"]=="evidence_integrity:simulated_missing_receipt"
    for r in [x["result"]for x in runs]+[x["result"]for x in malformed]+[public,unavailable]:
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","scene_authenticated","full_visibility_certified",
            "native_hit_coverage_certified","physical_field_certified","phase_certified","object_wide_skip","previous_zero_exemption"))
        assert r["promotion"]=="STOP" and r["epsilon_BU"]==[0,1] and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert (r["RN64_operations"],r["compiler_calls"],r["producer_replays"])==(0,0,0)
        if r["status"]=="STOP":assert r["rows"]==[] and r["verified_queries"]==0
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,malformed_controls=malformed,
        public_contact_STOP=public,missing_receipt_STOP=unavailable,
        census=dict(runs=len(runs),synthetic_queries=216,synthetic_disjoint=72,synthetic_contact_STOP=144,
            sealed_contact_STOP=8,noncoplanar_STOP=16,malformed_STOP=8),
        GPU_launch_allowed=False,GPU_executed=False,compiler_calls=0,RN64_operations=0,producer_replays=0)),sort_keys=True))
if __name__=="__main__":main()
