"""Focused native CPU graph/error ledger; immutable HOST parents never replayed."""
import inspect,json,sys,math
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_reference_unit_native_CPU_v1 as m

def main():
    e,pins=m.retained();runs=[];base=m.baseline();units=[]
    def packed(r):
        v={k:x for k,x in r.items()if type(x)is not type(base[k])or x!=base[k]}
        assert dict(base,**v)==r and set(r)==set(base);return v
    def run(ID,record,raw,q=None,model=m.MODEL):
        q=m.selector(record,e)if q is None else q;r=m._audit(model,q,raw,e)
        runs.append(dict(id=ID,record_id=record,request=q,model=model,raw_hex=raw.hex()if type(raw)is bytes else None,
            wire_type=type(raw).__name__,baseline_changes=packed(r)));return r
    for record,x in e.items():
        positive=x["result"]["conditional_unit"]
        raw=bytes.fromhex("".join(x["result"]["rows"][0]["input_words_LE"]))if positive else b""
        r=run("parent:"+record,record,raw)
        if positive:units.append((record,raw,r))
        else:assert r["reason"]=="parent_STOP_not_rescued"
    assert len(units)==15 and all(r["conditional_unit"]for _,_,r in units)
    record,raw,_=units[0];q=m.selector(record,e)
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
    public=m.audit(m.MODEL,q,raw);assert public==units[0][2]
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent
    try:missing=m.audit(m.MODEL,q,raw)
    finally:m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    tiny=F(1,10**22);halfremainder=F(1,2)**14/math.factorial(14)+F(1,2)**15/math.factorial(15)
    tests=(("zero","0000000000000000"*2,F(0),"PASS"),
        ("signed_zero","0000000000000080"*2,F(0),"PASS"),
        ("hi_lo_half","000000000000e03f"+"000000000000303c",F(0),"PASS"),
        ("negative_half","000000000000e0bf"+"00000000000030bc",F(0),"PASS"),
        ("fixed_cap_no_slack","000000000000e03f"+"0000000000000000",m.CAP,"STOP"),
        ("domain_radius","000000000000f03f"+"0000000000000000",F(1,100000),"STOP"),
        ("subnormal_input","0100000000000000"+"0000000000000000",F(0),"STOP"),
        ("underflow_square",(423<<52).to_bytes(8,"little").hex()+"0000000000000000",F(0),"STOP"),
        ("phase_cap_over","0000000000000000"*2,m.CAP+F(1,10**10),"STOP"),
        ("post_budget","000000000000e03f"+"0000000000000000",m.CAP-halfremainder/2-tiny,"STOP"))
    helpers=[]
    for label,h,err,want in tests:
        r=m.baseline();verdict="STOP";reason=None
        try:m.compute(bytes.fromhex(h),err,r);verdict="PASS"
        except ValueError as ex:reason=str(ex)
        r["RN64_operations"]=len(r["trace"]);r["RN64_conversions"]=len(r["coefficient_trace"])
        r["CPU_native_executed"]=bool(r["trace"]);r["CPU_binary64_conversion_executed"]=bool(r["coefficient_trace"])
        assert verdict==want,(label,reason)
        helpers.append(dict(label=label,scope="UNBOUND_NUMERICAL_HELPER_NOT_SCENE",raw_hex=h,error_rad=m.pair(err),
            verdict=verdict,reason=reason,baseline_changes=packed(r)))
    assert helpers[2]["baseline_changes"]["diagnostics"][0]["collapse_error_rad"]==[1,2**60]
    assert helpers[4]["reason"]=="unit_budget_exhausted_BEFORE_polynomial"and helpers[4]["baseline_changes"]["RN64_operations"]==1
    assert helpers[7]["reason"]=="subnormal_exact_result_AFTER_node"and helpers[7]["baseline_changes"]["RN64_operations"]==2
    assert helpers[9]["reason"]=="native_unit_budget_exhausted_AFTER_polynomial"and helpers[9]["baseline_changes"]["RN64_operations"]==27
    allresults=[dict(base,**x["baseline_changes"])for x in runs]+[public,missing]
    for r in allresults:
        assert all(r[k]is False for k in("GPU_executed","GPU_launch_allowed","scene_authenticated","uncertainty_authenticated",
            "physical_field_certified","full_visibility_certified","phase_certified","total_phase_certified",
            "material_authenticated","wavelength_authenticated","optical_reference_certified","correlation_assumed",
            "shared_phase_cancellation_assumed","periodic_wrapping_used","native_scalar_phase_output","lossless_hi_lo_transport_claim"))
        assert r["root_calls"]==r["producer_replays"]==r["compiler_calls"]==0
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert r["field"]is r["amplitude"]is r["power"]is None
        assert r["RN64_operations"]==len(r["trace"])and r["RN64_conversions"]==len(r["coefficient_trace"])
        if r["conditional_unit"]:assert(r["RN64_operations"],r["RN64_conversions"],r["decoded_words"])==(27,14,2)
        else:assert r["rows"]==[]and r["unit_words_LE"]is None
    assert list(inspect.signature(m.audit).parameters)==["model","request","raw_frame"]
    census=dict(main=len(runs),CPU_units=15,STOP=len(runs)-15,parent_STOP=762,bit_corruptions=128,bad_wire=5,selector_model=len(q)+4,
        RN64_operations=sum(dict(base,**x["baseline_changes"])["RN64_operations"]for x in runs),
        RN64_conversions=sum(dict(base,**x["baseline_changes"])["RN64_conversions"]for x in runs),
        public_duplicate_nodes=27,helpers_nodes=sum(dict(base,**x["baseline_changes"])["RN64_operations"]for x in helpers),
        helpers=10,GPU_calls=0)
    assert(census["main"],census["RN64_operations"],census["RN64_conversions"],census["helpers_nodes"])==(924,405,210,138)
    print(json.dumps(dict(status="PASS",data=dict(baseline_template=base,runs=runs,public=public,missing=missing,helpers=helpers,
        census=census,pins=len(pins),storage="LOSSLESS_TYPED_BASELINE_PLUS_EXACT_KEY_REPLACEMENTS")),sort_keys=True))
if __name__=="__main__":main()
