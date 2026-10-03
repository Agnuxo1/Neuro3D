"""Pinned input, 128 single-bit corruptions rejected predecode, native limbs/error budget."""
import inspect,json,sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_pair64_normalize_native_CPU_v1 as m
def main():
    e,pins=m.retained();runs=[]
    def run(ID,record,q,raw,model=m.MODEL):
        r=m._audit(model,q,raw,e)
        runs.append(dict(id=ID,record_id=record,request=q,raw_hex=raw.hex()if type(raw)is bytes else None,raw_type=type(raw).__name__,model=model,result=r))
        return r
    for record,x in e.items():
        p=x["result"];positive=p["geometric_encoding_budget_conditional"]
        raw=bytes.fromhex("".join(p["pair_words_LE"]))if positive else b""
        r=run("parent:"+record,record,m.selector(record,e),raw)
        assert r["geometric_normalization_budget_conditional"]is positive,(record,r)
        assert r["RN64_operations"]==(6 if positive else 0)and r["decoded_words"]==(2 if positive else 0)
        if positive:assert r["pair_words_LE"]==p["pair_words_LE"]and r["arithmetic_error_turns"]==[0,1]and r["error_rad_upper"]==p["error_rad_upper"]
    record="tiny_signal_pair_needed";q=m.selector(record,e);raw=bytes.fromhex("".join(e[record]["result"]["pair_words_LE"]))
    for bit in range(128):
        bad=bytearray(raw);bad[bit//8]^=1<<(bit%8)
        r=run("bit:"+str(bit),record,q,bytes(bad));assert r["reason"]=="ALL16bytes_before_decode"and r["decoded_words"]==r["RN64_operations"]==0
    for label,bad in (("short",raw[:-1]),("long",raw+b"\x00"),("bytearray",bytearray(raw)),("string",raw.hex()),("absent",None)):
        r=run("wire:"+label,record,q,bad);assert r["reason"]=="ALL16bytes_before_decode"
    for k in q:
        bad=dict(q);bad[k]="wrong";r=run("selector:"+k,record,bad,raw);assert r["status"]=="STOP"
    for label,bad in (("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        assert run("selector:"+label,record,bad,raw)["status"]=="STOP"
    assert run("model",record,q,raw,"GPU")["reason"]=="explicit_model"
    public=m.audit(m.MODEL,q,raw);assert public==runs[103]["result"] # first helper after the 103 main parents
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q,raw);m.retained=saved;assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    tiny=public["rows"][0];assert F(*tiny["decoded_output_exact_HOST"])==1+F(1,2**60)and not e[record]["result"]["rows"][0]["hi_only_budget_passes"]
    flags=("GPU_launch_allowed","GPU_executed","scene_authenticated","uncertainty_authenticated","wavelength_authenticated","total_phase_certified","full_visibility_certified","phase_certified","physical_field_certified","optical_reference_certified","correlation_assumed","periodic_wrapping_used","native_scalar_phase_output","CPU_binary64_conversion_executed")
    for x in runs+[dict(result=public),dict(result=missing)]:
        r=x["result"];assert all(r[k]is False for k in flags)
        assert r["root_calls"]==r["producer_replays"]==r["compiler_calls"]==r["RN64_conversions"]==0 and r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert r["CPU_native_executed"]is(r["RN64_operations"]>0)
        if r["status"]=="STOP":assert r["rows"]==[]and r["pair_words_LE"]is None
    assert list(inspect.signature(m.audit).parameters)==["model","request","raw_frame"]
    assert len(runs)==258 and sum(x["result"]["geometric_normalization_budget_conditional"]for x in runs)==17
    print(json.dumps(dict(status="PASS",data=dict(runs=runs,public=public,missing=missing,pins=len(pins),
        census=dict(main=258,CPU_native_pairs=17,STOP=241,parent_records=113,parent_STOP=96,bit_mutations=128,wire=5,selector_model=12),
        main_RN64_operations=102,public_duplicate_RN64_operations=6,root_calls=0,producer_replays=0,GPU_executed=False)),sort_keys=True))
if __name__=="__main__":main()
