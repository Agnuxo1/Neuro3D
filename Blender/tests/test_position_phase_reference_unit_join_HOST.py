"""Lossless selector and result templates; no native backend or old producer replay."""
import inspect,json,sys,math
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_reference_unit_join_HOST_v1 as m

def main():
    ce,he,pins=m.retained();base=m.baseline();selectors={k:m.selector(k,ce,he)for k in ce};runs=[];positive=[]
    def changes(v,b):
        assert set(v)==set(b)
        return{k:x for k,x in v.items()if type(x)is not type(b[k])or x!=b[k]}
    def run(ID,cid,raw,q=None,model=m.MODEL):
        q=selectors[cid]if q is None else q;r=m._audit(model,q,raw,ce,he)
        patch=changes(r,base);qpatch={k:v for k,v in q.items()if k not in selectors[cid]or type(v)is not type(selectors[cid][k])or v!=selectors[cid][k]}
        missing=[k for k in selectors[cid]if k not in q]
        reconstructed={k:v for k,v in dict(selectors[cid],**qpatch).items()if k not in missing}
        assert reconstructed==q and set(reconstructed)==set(q)
        assert dict(base,**patch)==r
        runs.append(dict(id=ID,native_record_id=cid,model=model,raw_hex=raw.hex()if type(raw)is bytes else None,
            wire_type=type(raw).__name__,selector_changes=qpatch,selector_missing=missing,baseline_changes=patch));return r
    for cid,x in ce.items():
        raw=bytes.fromhex("".join(x["result"]["unit_words_LE"]))if x["result"]["conditional_unit"]else b""
        r=run("retained:"+cid,cid,raw)
        if x["result"]["conditional_unit"]:
            assert r["join_conditional"];positive.append((cid,raw,r))
        else:assert r["reason"]=="CPU_parent_STOP_not_rescued"
    assert len(positive)==15
    for cid,raw,r in positive:
        for other,_,_ in positive:
            if other==cid:continue
            q=dict(selectors[cid]);b=selectors[other]
            for k in("host_record_id","host_record_sha256","source_context_sha256","original_geometry_sha256","overlay_sha256"):q[k]=b[k]
            assert run("cross:"+cid+"->"+other,cid,raw,q)["reason"]=="closed_join_selector"
    cid,raw,r=positive[0];q=selectors[cid]
    for bit in range(128):
        b=bytearray(raw);b[bit//8]^=1<<(bit%8)
        assert run("bit:"+str(bit),cid,bytes(b))["reason"]=="ALL16_output_bytes_before_decode"
    for label,b in(("short",raw[:-1]),("long",raw+b"x"),("bytearray",bytearray(raw)),("text",raw.hex()),("none",None)):
        assert run("wire:"+label,cid,b)["reason"]=="ALL16_output_bytes_before_decode"
    for k in q:
        b=dict(q);b[k]="wrong";assert run("selector:"+k,cid,raw,b)["status"]=="STOP"
    for label,b in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,intent=True))):
        assert run("selector:"+label,cid,raw,b)["status"]=="STOP"
    assert run("wrong_model",cid,raw,q,"GPU")["reason"]=="explicit_model"
    public=m.audit(m.MODEL,q,raw);assert public==r
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent
    try:missing=m.audit(m.MODEL,q,raw)
    finally:m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    helpers=[]
    for label,x,y,want in(("zero",F(0),F(0),"PASS"),("hi_lo_half",F(1,2)+F(1,2**60),F(1,2),"PASS"),
        ("negative_half",-F(1,2)-F(1,2**60),-F(1,2),"PASS"),("full_domain",F(-1),F(1),"PASS"),
        ("over_domain",F(1),F(1)+F(1,2**60),"STOP"),("float_argument",0.5,F(1,2),"STOP"),("bool_argument",True,F(0),"STOP")):
        vals=None;verdict="STOP";reason=None
        try:vals=m.lipschitz(x,y);verdict="PASS"
        except ValueError as ex:reason=str(ex)
        assert verdict==want
        if vals is not None:
            delta=abs(y-x)
            for odd,LP in enumerate(vals):
                px=sum((F((-1)**k,math.factorial(2*k+odd))*x**(2*k+odd)for k in range(7)),F(0))
                py=sum((F((-1)**k,math.factorial(2*k+odd))*y**(2*k+odd)for k in range(7)),F(0))
                assert abs(py-px)<=LP*delta
        helpers.append(dict(label=label,x=m.pair(x)if type(x)is F else x,y=m.pair(y),x_type=type(x).__name__,
            verdict=verdict,reason=reason,derivative_bound=list(map(m.pair,vals))if vals is not None else None,
            scope="UNBOUND_POLYNOMIAL_THEOREM_NOT_SCENE"))
    for x in runs:
        r=dict(base,**x["baseline_changes"])
        assert r["CPU_native_executed"]is False and r["RN64_operations"]==r["RN64_conversions"]==r["backend_executions"]==r["producer_replays"]==r["root_calls"]==0
        assert all(r[k]is False for k in("GPU_executed","GPU_launch_allowed","physical_field_certified","phase_certified",
            "scene_authenticated","uncertainty_authenticated","full_visibility_certified","native_unit_output",
            "work_equivalence_certified","time_efficiency_comparison_valid","physical_phase_cancellation_assumed","reduced_parent_bounds_adopted"))
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if not r["join_conditional"]:assert r["rows"]==[]
    census=dict(main=len(runs),HOST_joins=15,STOP=len(runs)-15,parent_STOP=909,cross_join_STOP=210,bit_corruptions=128,
        bad_wire=5,selector_model=len(q)+4,HOST_word_decodes=30,HOST_derivative_terms=195,retained_CPU_nodes_observed=405,
        retained_CPU_conversions_observed=210,new_RN64_operations=0,backend_replays=0,helpers=7,GPU_calls=0)
    assert census["main"]==1282 and census["selector_model"]==15
    assert list(inspect.signature(m.audit).parameters)==["model","request","raw_frame"]
    print(json.dumps(dict(status="PASS",data=dict(baseline_template=base,selectors_by_native_id=selectors,runs=runs,
        public=public,missing=missing,helpers=helpers,census=census,pins=len(pins),
        storage="LOSSLESS_TYPED_RESULT_AND_SELECTOR_TEMPLATES_WITH_EXACT_DELETIONS")),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
