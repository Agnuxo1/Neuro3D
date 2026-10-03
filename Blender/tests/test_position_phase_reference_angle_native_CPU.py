"""Focused angle regressions consuming retained pairs, no producer/suite replay."""
import inspect,json,struct,sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_reference_angle_native_CPU_v1 as m

def main():
    e,h,pins=m.retained();runs=[];admitted=[]
    def run(ID,record,raw,q=None,model=m.MODEL):
        q=m.selector(record,e)if q is None else q
        r=m._audit(model,q,raw,e,h)
        runs.append(dict(id=ID,record_id=record,request=q,model=model,raw_hex=raw.hex()if type(raw)is bytes else None,
            wire_type=type(raw).__name__,result=r));return r
    for record,x in e.items():
        positive=x["result"]["reference_contrast_conditional"]
        raw=bytes.fromhex("".join(x["result"]["pair_words_LE"]))if positive else b""
        r=run("parent:"+record,record,raw)
        assert r["angle_conditional"]is positive,(record,r)
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
    for label,b in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),
                  ("bool",dict(q,tau_word_LE=True))):
        assert run("selector:"+label,record,raw,b)["status"]=="STOP"
    assert run("wrong_model",record,raw,q,"GPU")["reason"]=="explicit_model"
    public=m.audit(m.MODEL,q,raw);assert public==runs[0]["result"]
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent
    try:missing=m.audit(m.MODEL,q,raw)
    finally:m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    helpers=[]
    for label,vals,budget,expected in (
        ("positive_zero",(0.0,0.0),F(0),"PASS"),
        ("negative_zero",(-0.0,-0.0),F(0),"PASS"),
        ("mixed_zero",(-0.0,0.0),F(0),"PASS"),
        ("low_word",(1.0,2.0**-60),F(0),"PASS"),
        ("negative_pair",(-1.0,-2.0**-60),F(0),"PASS"),
        ("fixed_cap_no_slack",(1.0,2.0**-60),m.CAP/8,"STOP"),
        ("subnormal",(2.0**-1074,0.0),F(0),"STOP"),
        ("domain",(1000001.0,0.0),F(0),"STOP")):
        rawh=struct.pack("<dd",*vals);out=m.baseline();diag=None;reason=None;verdict="STOP"
        try:
            diag=m.compute_pair(rawh,budget,out)
            if F(*diag["error_rad_upper"])<=m.CAP:verdict="PASS"
            else:reason="angle_budget_exhausted"
        except ValueError as ex:reason=str(ex)
        assert verdict==expected,(label,diag,reason)
        helpers.append(dict(label=label,scope="UNBOUND_NUMERICAL_HELPER_NOT_SCENE",raw_hex=rawh.hex(),
            budget_turns=m.pair(budget),verdict=verdict,reason=reason,diagnostic=diag,trace=out["trace"],
            decoded_phase_words=out["decoded_phase_words"],decoded_constant_words=out["decoded_constant_words"]))
    assert helpers[3]["diagnostic"]["output_words_LE"][1]!="0000000000000000"
    assert len(helpers[5]["trace"])==8 and helpers[5]["diagnostic"]["error_rad_upper"]!=[1,10000]
    assert helpers[6]["trace"]==helpers[7]["trace"]==[]
    # Cancellation at the normal/subnormal boundary: preserve all eight native nodes,
    # no diagnostic/PASS admission, and no historical 'error_cycles' metadata leak.
    raw_partial=bytes.fromhex("0000000000001000"+"0100000000001080")
    partial_out=m.baseline();partial_diag=None;partial_reason=None
    try:partial_diag=m.compute_pair(raw_partial,F(0),partial_out)
    except ValueError as ex:partial_reason=str(ex)
    assert partial_reason=="normal_zero_only"and partial_diag is None and len(partial_out["trace"])==8
    assert all(set(t)=={"name","op","a","b","y","error_rad"}for t in partial_out["trace"])
    partial=dict(scope="UNBOUND_NUMERICAL_HELPER_NOT_SCENE",raw_hex=raw_partial.hex(),budget_turns=[0,1],
        verdict="STOP",reason=partial_reason,diagnostic=None,trace=partial_out["trace"],
        decoded_phase_words=partial_out["decoded_phase_words"],decoded_constant_words=partial_out["decoded_constant_words"])
    falseflags=("GPU_executed","GPU_launch_allowed","scene_authenticated","uncertainty_authenticated",
        "material_authenticated","wavelength_authenticated","total_phase_certified","phase_certified",
        "physical_field_certified","full_visibility_certified","optical_reference_certified","correlation_assumed",
        "shared_phase_cancellation_assumed","periodic_wrapping_used","native_scalar_phase_output")
    for x in runs+[dict(result=public),dict(result=missing)]:
        r=x["result"];assert all(r[k]is False for k in falseflags)
        assert r["root_calls"]==r["producer_replays"]==r["compiler_calls"]==r["RN64_conversions"]==0
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"and r["trace_unit"]=="rad"
        assert r["field"]is r["amplitude"]is r["power"]is None
        if r["status"]=="STOP":
            assert r["rows"]==[]and r["pair_words_LE"]is None and not r["angle_conditional"]
            assert r["RN64_operations"]==r["decoded_phase_words"]==r["decoded_constant_words"]==0
        else:assert (r["RN64_operations"],r["decoded_phase_words"],r["decoded_constant_words"])==(8,2,1)
    assert list(inspect.signature(m.audit).parameters)==["model","request","raw_frame"]
    census=dict(main=len(runs),CPU_angles=39,STOP=len(runs)-39,parent_STOP=443,bit_corruptions=128,bad_wire=5,
        selector_model=len(q)+4,RN64_operations=sum(x["result"]["RN64_operations"]for x in runs),
        decoded_phase_words=sum(x["result"]["decoded_phase_words"]for x in runs),
        decoded_constant_words=sum(x["result"]["decoded_constant_words"]for x in runs),RN64_conversions=0,
        helpers=len(helpers),helper_operations=sum(len(x["trace"])for x in helpers),public_duplicate_operations=8)
    assert(census["main"],census["RN64_operations"],census["decoded_phase_words"],census["decoded_constant_words"])==(630,312,78,39)
    print(json.dumps(dict(status="PASS",data=dict(runs=runs,public=public,missing=missing,helpers=helpers,
        certificate=m.CERT,certificate_sha256=m.CERT_SHA,census=census,pins=len(pins),partial_stop=partial)),sort_keys=True))
if __name__=="__main__":main()
