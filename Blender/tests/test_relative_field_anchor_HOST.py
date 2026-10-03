"""Anchor missing is UNKNOWN, not zero; controls do not certify actual scene sources."""
import sys,json,inspect,copy
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import relative_field_anchor_HOST_v1 as m

def main():
    records,pins,stops=m.retained();runs=[]
    def run(ID,cid,anchor,raw,q=None,model=m.MODEL):
        q=m.selector(cid,records,anchor)if q is None else q
        r=m._audit(model,q,anchor,raw,records)
        runs.append(dict(id=ID,record_id=cid,anchor=anchor,request=q,model=model,
            raw_hex=raw.hex()if type(raw)is bytes else None,wire_type=type(raw).__name__,result=r))
        return r
    for cid,x in records.items():
        raw=bytes.fromhex("".join(x["result"]["rows"][0]["CPU_words_LE"]))
        r=run("missing:"+cid,cid,None,raw)
        assert r["reason"]=="SOURCE_complex_reference_anchor_missing_NOT_ZERO"and r["HOST_word_decodes"]==0
    cid=next(iter(records));raw=bytes.fromhex("".join(records[cid]["result"]["rows"][0]["CPU_words_LE"]))
    controls=[]
    for label,a,ba in(("one_plus_i",[F(1),F(1)],F(1,10000)),("zero_known",[F(0),F(0)],F(0)),
        ("zero_uncertain",[F(0),F(0)],F(1,10000))):
        anchor=m.anchor_control(cid,records,a,ba,F(1))
        r=run("control:"+label,cid,anchor,raw);assert r["conditional_control_product"];controls.append(r)
    anchor=m.anchor_control(cid,records,[F(1),F(1)],F(1,10000),F(1));q=m.selector(cid,records,anchor)
    b=copy.deepcopy(anchor);b["output_budget_L1"]=[0,1]
    r=run("budget_exhausted",cid,b,raw)
    assert r["reason"]=="declared_control_product_budget_exceeded"and r["diagnostics"]and r["relative_field_HOST"]is None
    for bit in(0,127):
        b=bytearray(raw);b[bit//8]^=1<<(bit%8)
        assert run("bit:"+str(bit),cid,anchor,bytes(b))["reason"]=="ALL16_unit_bytes_before_decode"
    for label,b in(("short",raw[:-1]),("long",raw+b"x"),("text",raw.hex()),("bytearray",bytearray(raw)),("none",None)):
        assert run("wire:"+label,cid,anchor,b)["reason"]=="ALL16_unit_bytes_before_decode"
    for key,value in(("origin","ORIGINAL_AUTHENTICATED_SOURCE"),("reference_point",2),("reference_point",True),
        ("source_context_sha256","wrong"),("original_geometry_sha256","wrong"),("source_component","SOURCE_POINT_1"),
        ("units","W"),("error_L1",None),("error_L1",[True,1]),("error_L1",[0.0,1]),("error_L1",[-1,1000]),
        ("output_budget_L1",[1,2**200])):
        b=copy.deepcopy(anchor);b[key]=value
        assert run("anchor:"+key+":"+str(value),cid,b,raw)["status"]=="STOP"
    for label,b in(("extra",dict(anchor,authenticated=True)),("missing",{k:v for k,v in anchor.items()if k!="error_L1"})):
        assert run("anchor:"+label,cid,b,raw)["reason"]=="closed_anchor_control"
    for k in q:
        b=dict(q);b[k]="wrong";assert run("selector:"+k,cid,anchor,raw,b)["status"]=="STOP"
    assert run("wrong_model",cid,anchor,raw,q,"GPU")["reason"]=="explicit_model"
    # Same control but a different sealed fixture is not a common-detector/source aggregate.
    other=list(records)[1]
    assert run("cross_fixture",other,anchor,bytes.fromhex("".join(records[other]["result"]["rows"][0]["CPU_words_LE"])))["status"]=="STOP"
    public=m.audit(m.MODEL,q,anchor,raw);assert public==controls[0]
    saved=m.retained
    def absent():raise ValueError("simulated_absent")
    m.retained=absent
    try:missing=m.audit(m.MODEL,q,anchor,raw)
    finally:m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_absent"
    # Independent algebraic corner check for GENERAL complex products, not unit/scene evidence.
    a=[F(1,2),F(-1,4)];v=[F(1,3),F(2,5)];ba=F(1,1024);bu=F(1,2048)
    probe=m.product(a,v,ba,bu);helpers=[]
    def mul(a,v):return[a[0]*v[0]-a[1]*v[1],a[0]*v[1]+a[1]*v[0]]
    for da in([ba,F(0)],[-ba,F(0)],[F(0),ba],[F(0),-ba]):
        for du in([bu,F(0)],[-bu,F(0)],[F(0),bu],[F(0),-bu]):
            truth=mul([x+y for x,y in zip(a,da)],[x+y for x,y in zip(v,du)])
            delta=sum((abs(x-y)for x,y in zip(truth,map(m.frac,probe["value"]))),F(0))
            assert delta<=m.frac(probe["bound_L1"])
            helpers.append(dict(da=[m.pair(x)for x in da],du=[m.pair(x)for x in du],difference_L1=m.pair(delta)))
    for row in runs:
        r=row["result"]
        assert r["SOURCE_complex_reference"]is None and r["SOURCE_anchor_error"]is None
        assert all(r[k]is False for k in("SOURCE_anchor_authenticated","original_scene_source_amplitude_used",
            "physical_field_certified","optical_power_certified","source_coherence_certified","reference_calibrated",
            "scene_authenticated","normalization_performed","full_visibility_certified","reduced_parent_bounds_adopted",
            "physical_phase_cancellation_assumed","work_equivalence_certified","time_efficiency_comparison_valid",
            "GPU_executed","GPU_launch_allowed","native_field_output"))
        assert r["backend_executions"]==r["producer_replays"]==r["RN64_operations"]==0
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if not r["conditional_control_product"]:assert r["relative_field_HOST"]is None
    assert list(inspect.signature(m.audit).parameters)==["model","request","declared_anchor","unit_frame"]
    census=dict(main=len(runs),declared_controls=3,STOP=len(runs)-3,actual_missing_anchors=15,
        parent_STOP_manifest=stops,parent_census_replays=0,main_word_decodes=sum(x["result"]["HOST_word_decodes"]for x in runs),
        main_product_evaluations=sum(x["result"]["HOST_product_evaluations"]for x in runs),pins=len(pins),
        helpers=16,GPU_calls=0,new_RN64_operations=0,backend_replays=0)
    print(json.dumps(dict(status="PASS",data=dict(runs=runs,public=public,missing=missing,
        unbound_bilinear_probe=probe,helpers=helpers,census=census)),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
