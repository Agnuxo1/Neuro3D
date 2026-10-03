"""Own CPU-only retained-parent, corruption and selector regressions; no producer replay."""
import inspect,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_reference_native_CPU_v1 as m

def main():
    e,pins=m.retained();runs=[];admitted=[]
    def run(ID,record,raw,q=None,model=m.MODEL):
        q=m.selector(record,e)if q is None else q
        r=m._audit(model,q,raw,e);runs.append(dict(id=ID,record_id=record,request=q,model=model,
            raw_hex=raw.hex()if type(raw)is bytes else None,wire_type=type(raw).__name__,result=r));return r
    for record,x in e.items():
        positive=x["result"]["reference_overlay_conditional"]
        raw=bytes.fromhex("".join(x["result"]["rows"][0]["parent_normalized_geometry"]["output_words_LE"]))if positive else b""
        r=run("parent:"+record,record,raw)
        assert r["reference_contrast_conditional"]is positive,(record,r)
        if positive:admitted.append((record,raw))
        else:assert r["reason"]=="parent_STOP_not_rescued"
    assert len(admitted)==39
    record,raw=admitted[0];q=m.selector(record,e)
    for bit in range(128):
        bad=bytearray(raw);bad[bit//8]^=1<<(bit%8)
        assert run("bit:"+str(bit),record,bytes(bad))["reason"]=="ALL16bytes_before_decode"
    for label,bad in(("short",raw[:-1]),("long",raw+b"x"),("bytearray",bytearray(raw)),("text",raw.hex()),("none",None)):
        assert run("wire:"+label,record,bad)["reason"]=="ALL16bytes_before_decode"
    for k in q:
        b=dict(q);b[k]="wrong";assert run("selector:"+k,record,raw,b)["status"]=="STOP"
    for label,b in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):
        assert run("selector:"+label,record,raw,b)["status"]=="STOP"
    assert run("wrong_model",record,raw,q,"GPU")["reason"]=="explicit_model"
    public=m.audit(m.MODEL,q,raw);assert public==runs[0]["result"]
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q,raw);m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    false_flags=("GPU_executed","GPU_launch_allowed","scene_authenticated","uncertainty_authenticated",
        "material_authenticated","wavelength_authenticated","total_phase_certified","phase_certified",
        "physical_field_certified","full_visibility_certified","optical_reference_certified","correlation_assumed",
        "shared_phase_cancellation_assumed","periodic_wrapping_used","native_scalar_phase_output")
    for x in runs+[dict(result=public),dict(result=missing)]:
        r=x["result"];assert all(r[k]is False for k in false_flags)
        assert r["root_calls"]==r["producer_replays"]==r["compiler_calls"]==0 and r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert r["field"]is r["amplitude"]is r["power"]is None
        if r["status"]=="STOP":
            assert r["rows"]==[]and r["pair_words_LE"]is None and not r["reference_contrast_conditional"]
            assert r["decoded_words"]==r["decoded_term_words"]==r["RN64_conversions"]==r["RN64_operations"]==r["sign_bit_flips"]==0
        else:assert r["decoded_words"]==2 and r["decoded_term_words"]==8
    assert list(inspect.signature(m.audit).parameters)==["model","request","raw_frame"]
    assert len(runs)==482
    counts=dict(main=len(runs),CPU_contrasts=len(admitted),STOP=len(runs)-len(admitted),parent_STOP=297,
        bit_corruptions=128,bad_wire=5,selector_model=13,RN64_operations=sum(x["result"]["RN64_operations"]for x in runs),
        RN64_conversions=sum(x["result"]["RN64_conversions"]for x in runs),sign_bit_flips=sum(x["result"]["sign_bit_flips"]for x in runs))
    assert(counts["RN64_operations"],counts["RN64_conversions"],counts["sign_bit_flips"])==(4056,312,156)
    print(json.dumps(dict(status="PASS",data=dict(runs=runs,public=public,missing=missing,census=counts,pins=len(pins))),sort_keys=True))
if __name__=="__main__":main()
