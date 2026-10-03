"""Focused HOST tests, retained parent manifest, no old census or backend replay."""
import json,sys,inspect
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import relative_unit_magnitude_HOST_v1 as m

def main():
    records,pins=m.retained();runs=[]
    def run(ID,cid,raw,q=None,model=m.MODEL):
        q=m.selector(cid,records)if q is None else q
        r=m._audit(model,q,raw,records)
        runs.append(dict(id=ID,parent_id=cid,request=q,model=model,raw_hex=raw.hex()if type(raw)is bytes else None,
            wire_type=type(raw).__name__,result=r))
        return r
    positive=[k for k,x in records.items()if x["result"]["join_conditional"]]
    stops=[dict(id=k,sha256=m.digest(x))for k,x in records.items()if not x["result"]["join_conditional"]]
    assert len(positive)==15 and len(stops)==1267
    norm_nonunit=0
    for cid in positive:
        raw=bytes.fromhex("".join(records[cid]["result"]["rows"][0]["output_CPU_words_LE"]))
        r=run("retained:"+cid,cid,raw);assert r["conditional_squared_magnitude"]
        norm_nonunit+=sum(not r["rows"][0][k]["exact_unit_norm"]for k in("CPU","HOST"))
    cid=positive[0];raw=bytes.fromhex("".join(records[cid]["result"]["rows"][0]["output_CPU_words_LE"]));q=m.selector(cid,records)
    for i in(0,127):
        v=bytearray(raw);v[i//8]^=1<<(i%8)
        assert run("bit:"+str(i),cid,bytes(v))["reason"]=="ALL16_output_bytes_before_decode"
    for label,v in(("short",raw[:-1]),("long",raw+b"x"),("text",raw.hex()),("bytearray",bytearray(raw)),("none",None)):
        assert run("wire:"+label,cid,v)["reason"]=="ALL16_output_bytes_before_decode"
    for k in q:
        v=dict(q);v[k]="wrong";assert run("selector:"+k,cid,raw,v)["status"]=="STOP"
    for label,v in(("missing",{k:x for k,x in q.items()if k!="intent"}),("extra",dict(q,extra=True)),("bool",dict(q,intent=True))):
        assert run("selector:"+label,cid,raw,v)["status"]=="STOP"
    v=dict(q);v["source_context_sha256"]=m.selector(positive[1],records)["source_context_sha256"]
    v["parent_record_sha256"]=m.selector(positive[1],records)["parent_record_sha256"]
    assert run("cross_context",cid,raw,v)["reason"]=="closed_selector"
    assert run("wrong_model",cid,raw,q,"GPU")["reason"]=="explicit_model"
    sid=stops[0]["id"];assert run("old_STOP_sample",sid,b"")["reason"]=="parent_STOP_not_rescued"
    assert run("unknown",cid,raw,dict(q,join_record_id="absent"))["reason"]=="closed_parent_record"
    public=m.audit(m.MODEL,q,raw);assert public==runs[0]["result"]
    saved=m.retained
    def absent():raise ValueError("simulated_absent")
    m.retained=absent
    try:missing=m.audit(m.MODEL,q,raw)
    finally:m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_absent"
    helpers=[]
    for sign in(-1,1):
        for u in([F(1),F(0)],[F(3,5),F(4,5)]):
            for err in([m.CAP,F(0)],[F(0),-m.CAP],[m.CAP/2,-m.CAP/2]):
                v=[sign*u[i]+err[i]for i in(0,1)];b=sum(map(abs,err),F(0))
                cert=m.certificate(v,b);helpers.append(dict(unit=list(map(m.pair,[sign*x for x in u])),error=list(map(m.pair,err)),certificate=cert))
    negatives=[]
    for label,v,b,reason in(("omit_quadratic",[F(1)+m.CAP,F(0)],F(0),"squared_norm_defect_exceeds_inherited_bound"),
        ("over_cap",[F(1),F(0)],m.CAP+F(1,10**10),"fixed_full_unit_cap"),
        ("negative",[F(1),F(0)],-m.CAP,"fixed_full_unit_cap"),
        ("float_cap",[F(1),F(0)],0.0002,"fixed_full_unit_cap"),
        ("bool_cap",[F(1),F(0)],True,"fixed_full_unit_cap"),
        ("float_vector",[1.0,F(0)],m.CAP,"typed_HOST_pair")):
        got=None
        try:m.certificate(v,b)
        except ValueError as ex:got=str(ex)
        assert got==reason;negatives.append(dict(label=label,reason=got))
    # Sharp cap: v=(1+cap,0) reaches 2*cap+cap^2, not 2*cap alone.
    sharp=m.certificate([F(1)+m.CAP,F(0)],m.CAP)
    assert sharp["absolute_defect_from_one"]==sharp["squared_magnitude_defect_bound"]
    assert m.frac(sharp["absolute_defect_from_one"])>2*m.CAP
    for row in runs:
        r=row["result"]
        assert all(r[k]is False for k in("exact_unit_norm_claimed","renormalization_performed","physical_field_certified",
            "optical_power_certified","scene_authenticated","reference_calibrated","GPU_executed","GPU_launch_allowed",
            "reduced_parent_bounds_adopted","physical_phase_cancellation_assumed","work_equivalence_certified","time_efficiency_comparison_valid"))
        assert r["backend_executions"]==r["producer_replays"]==r["RN64_operations"]==0 and r["promotion"]=="STOP"
        assert r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if not r["conditional_squared_magnitude"]:assert r["rows"]==[] and r["HOST_norm_evaluations"]==0
    assert list(inspect.signature(m.audit).parameters)==["model","request","raw_frame"]
    census=dict(own_main=len(runs),certified_records=15,main_STOP=len(runs)-15,
        retained_STOP_manifest_count=len(stops),retained_STOP_manifest_sha256=m.digest(stops),
        parent_census_replays=0,backend_executions=0,new_RN64_operations=0,GPU_calls=0,
        main_word_decodes=30,main_norm_evaluations=30,nonunit_representations=norm_nonunit,
        helpers=len(helpers),negative_helpers=len(negatives),pins=len(pins))
    print(json.dumps(dict(status="PASS",data=dict(runs=runs,public=public,missing=missing,helpers=helpers,
        negative_helpers=negatives,sharp=sharp,census=census)),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
