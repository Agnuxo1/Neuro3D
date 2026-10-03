"""Lossless baseline+patch evidence, HOST only; all retained STOP inputs tested."""
import inspect,json,sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_reference_unit_budget_HOST_v1 as m

def main():
    e,pins=m.retained();runs=[];angles=[];base=m.baseline()
    def packed(out):
        # Lossless exact typed template encoding, not an omitted trace or guard summary.
        changes={k:v for k,v in out.items()if type(v)is not type(base[k])or v!=base[k]}
        reconstructed=dict(base,**changes);assert reconstructed==out and set(reconstructed)==set(out)
        return changes
    def run(ID,record,raw,q=None,model=m.MODEL):
        q=m.selector(record,e)if q is None else q;r=m._audit(model,q,raw,e)
        runs.append(dict(id=ID,record_id=record,request=q,model=model,raw_hex=raw.hex()if type(raw)is bytes else None,
            wire_type=type(raw).__name__,baseline_changes=packed(r)));return r
    for record,x in e.items():
        positive=x["result"]["angle_conditional"]
        raw=bytes.fromhex("".join(x["result"]["pair_words_LE"]))if positive else b""
        r=run("parent:"+record,record,raw)
        if positive:angles.append((record,raw,r))
        else:assert r["reason"]=="parent_STOP_not_rescued"
    assert len(angles)==39
    accepted=[x for x in angles if x[2]["conditional_unit"]]
    domain=[x for x in angles if x[2]["reason"]=="angle_enclosure_outside_fixed_1rad_NO_WRAP"]
    assert(len(accepted),len(domain))==(15,24)
    record,raw,_=accepted[0];q=m.selector(record,e)
    for bit in range(128):
        bad=bytearray(raw);bad[bit//8]^=1<<(bit%8)
        assert run("bit:"+str(bit),record,bytes(bad))["reason"]=="ALL16bytes_before_decode"
    for label,bad in(("short",raw[:-1]),("long",raw+b"x"),("bytearray",bytearray(raw)),("text",raw.hex()),("none",None)):
        assert run("wire:"+label,record,bad)["reason"]=="ALL16bytes_before_decode"
    for k in q:
        b=dict(q);b[k]="wrong";assert run("selector:"+k,record,raw,b)["status"]=="STOP"
    for label,b in(("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),
                  ("bool",dict(q,unit_budget_rule=True))):
        assert run("selector:"+label,record,raw,b)["status"]=="STOP"
    assert run("wrong_model",record,raw,q,"GPU")["reason"]=="explicit_model"
    public=m.audit(m.MODEL,q,raw);assert public==accepted[0][2]
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent
    try:missing=m.audit(m.MODEL,q,raw)
    finally:m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    helpers=[]
    pairs=(("zero","0000000000000000"*2,F(0),"PASS"),
        ("signed_zero","0000000000000080"*2,F(0),"PASS"),
        ("hi_lo_half","000000000000e03f"+"000000000000303c",F(0),"PASS"),
        ("negative_half","000000000000e0bf"+"00000000000030bc",F(0),"PASS"),
        ("fixed_cap_no_slack","000000000000e03f"+"0000000000000000",m.PHASE_CAP,"STOP"),
        ("domain_radius","000000000000f03f"+"0000000000000000",F(1,100000),"STOP"),
        ("subnormal","0100000000000000"+"0000000000000000",F(0),"STOP"),
        ("phase_cap_over","0000000000000000"*2,m.PHASE_CAP+F(1,10**10),"STOP"))
    for label,h,err,want in pairs:
        out=m.baseline();verdict="STOP";reason=None
        try:m.compute(bytes.fromhex(h),err,out);verdict="PASS"
        except ValueError as ex:reason=str(ex)
        assert verdict==want,(label,reason)
        helpers.append(dict(label=label,scope="UNBOUND_NUMERICAL_HELPER_NOT_SCENE",raw_hex=h,
            error_rad=m.pair(err),verdict=verdict,reason=reason,baseline_changes=packed(out)))
    assert helpers[2]["baseline_changes"]["diagnostics"][0]["nominal_rad_HOST"]!=[1,2]
    assert helpers[4]["reason"]=="unit_budget_exhausted_BEFORE_polynomial"
    assert helpers[4]["baseline_changes"].get("HOST_polynomial_operations",0)==0
    falseflags=("GPU_executed","GPU_launch_allowed","scene_authenticated","uncertainty_authenticated",
        "material_authenticated","wavelength_authenticated","total_phase_certified","phase_certified",
        "physical_field_certified","full_visibility_certified","optical_reference_certified","correlation_assumed",
        "shared_phase_cancellation_assumed","periodic_wrapping_used","native_scalar_phase_output",
        "native_unit_output","rounding_into_scalar_used","CPU_native_executed")
    results=[dict(base,**x["baseline_changes"])for x in runs]+[public,missing]
    for r in results:
        assert all(r[k]is False for k in falseflags)
        assert r["root_calls"]==r["producer_replays"]==r["compiler_calls"]==r["RN64_conversions"]==r["RN64_operations"]==0
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert r["field"]is r["amplitude"]is r["power"]is None
        if r["status"]=="STOP":assert r["rows"]==[]and r["unit_pair_HOST"]is None and not r["conditional_unit"]
        else:assert(r["HOST_polynomial_operations"],r["HOST_factorials"],r["HOST_word_decodes"])==(26,16,4)
    assert list(inspect.signature(m.audit).parameters)==["model","request","raw_frame"]
    census=dict(main=len(runs),HOST_units=15,STOP=len(runs)-15,parent_STOP=591,domain_STOP=24,
        bit_corruptions=128,bad_wire=5,selector_model=len(q)+4,
        HOST_polynomial_operations=sum(dict(base,**x["baseline_changes"])["HOST_polynomial_operations"]for x in runs),
        HOST_word_decodes=sum(dict(base,**x["baseline_changes"])["HOST_word_decodes"]for x in runs),
        HOST_factorials=sum(dict(base,**x["baseline_changes"])["HOST_factorials"]for x in runs),
        helpers=8,RN64_operations=0,GPU_calls=0)
    assert(census["main"],census["HOST_polynomial_operations"],census["HOST_word_decodes"],census["HOST_factorials"])==(777,390,156,240)
    print(json.dumps(dict(status="PASS",data=dict(baseline_template=base,runs=runs,public=public,missing=missing,
        helpers=helpers,census=census,pins=len(pins),storage="LOSSLESS_TYPED_BASELINE_PLUS_EXACT_KEY_REPLACEMENTS")),sort_keys=True))
if __name__=="__main__":main()
