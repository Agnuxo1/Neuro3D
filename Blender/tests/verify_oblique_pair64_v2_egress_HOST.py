"""Independent sealed V2 egress verifier. No producer, compiler or core imports."""
from pathlib import Path
from fractions import Fraction
import ast, base64, copy, hashlib, json, struct, zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-V2-EGRESS-HOST-001-CODEX.json"
CASES=("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60")
MODEL="precision-oblique-pair64-v2-egress-HOST-v1"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def cap(r):
    t=r["test_run"];b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert sha(b)==t["stdout_sha256"] and len(b)==t["stdout_bytes"] and t["rc"]==0 and not t["timed_out"]
    v=json.loads(b);assert v["status"]=="PASS";return v
def f(q):assert len(q)==2 and all(type(v)is int for v in q) and q[1]>0;return Fraction(q[0],q[1])
def packed(q):return [q.numerator,q.denominator]
def number(b):
    # Independent big-endian bit string extraction, no floating conversion or RN.
    bits=format(int.from_bytes(b,"little"),"064b");e=int(bits[1:12],2)
    if e==2047:raise ValueError("nonfinite_raw")
    frac=int(bits[12:],2)
    value=Fraction(frac+(2**52 if e else 0))*Fraction(2)**(e-1075 if e else -1074)
    return -value if bits[0]=="1" else value
def sel(case,e):
    p=e[case]["packet"]
    return dict(case=case,packet_sha256=digest(p),original_scene_sha256=p["scene_sha256"],
                literal_request_sha256=p["literal_sha256"],shader_sha256=p["shader_sha256"],intent="HOST_V2_EGRESS_ONLY")
def expected(q,e):
    case=q["case"];raw=bytes.fromhex(q["raw_hex"]);p=e[case]["packet"];rows=e[case]["rows"]
    if q["model"]!=MODEL:return "model",None
    if q["origin"]!="CPU_UNATTESTED_BYTES":return "unattested_origin_only",None
    request=q["request"]
    if set(request)!={"case","packet_sha256","original_scene_sha256","literal_request_sha256","shader_sha256","intent"}:return "closed_selector",None
    if len(raw)!=32:return "output_extent",None
    if request["case"]not in CASES:return "case",None
    if request!=sel(case,e):return "selector_identity",None
    if raw[:16]!=bytes.fromhex("3246444f040000000200000001000000"):return "output_header",None
    if len(rows)!=3 or [r["record_id"]for r in rows]!=["S0","S1","S0-minus-S1"]:return "source_completeness",None
    incoming=bytes.fromhex(p["input_hex"]);vv=[];rr=[];bounds=[];rounding=Fraction(0)
    for j,row in enumerate(rows[:2]):
        if row["original_scene_sha256"]!=p["scene_sha256"]or row["literal_request_sha256"]!=p["literal_sha256"]:return "source_identity",None
        h=incoming[16+j*16:24+j*16];l=incoming[24+j*16:32+j*16]
        if h.hex()!=row["hi"]["word_le_hex"]or l.hex()!=row["lo"]["word_le_hex"]:return "source_bits",None
        v=number(h)+number(l);a,b=map(f,row["interval"])
        sc=f(row["literal_cap_rad"]);assert sc==f(p["source_literal_caps"][j])
        error=max(abs(v-a),abs(v-b))*8
        if error>sc:return "source_cap",None
        bounds.append(packed(error));vv.append(v);rr.append((a,b));rounding+=abs(v-(a+b)/2)
    row=rows[2]
    if row["original_scene_sha256"]!=p["scene_sha256"]or row["literal_request_sha256"]!=p["literal_sha256"]:return "relative_identity",None
    a=rr[0][0]-rr[1][1];b=rr[0][1]-rr[1][0]
    if [packed(a),packed(b)]!=row["parent_relative_CONTROL_ONLY"]["interval"]:return "relative_interval",None
    rc=f(row["literal_cap_rad"]);assert rc==f(p["retained_CPU_budget"]["literal_cap_rad"])
    try:v=number(raw[16:24])+number(raw[24:])
    except ValueError:return "nonfinite_raw",None
    ae=abs(v-vv[0]+vv[1]);radius=(b-a)/2
    cb=8*(radius+rounding+ae);db=8*max(abs(v-a),abs(v-b))
    if db>cb or cb>rc:return "relative_cap",None
    if raw[16:].hex()!=row["hi_word"]+row["lo_word"]:return "native_bits_mismatch",None
    assert raw.hex()==p["expected_CONTROL_ONLY_hex"]
    return None,dict(source_bounds_rad=bounds,arithmetic_error_cycles=packed(ae),
            source_rounding_budget_cycles=packed(rounding),interval_radius_cycles=packed(radius),
            direct_error_bound_rad=packed(db),conservative_error_bound_rad=packed(cb),
            literal_cap_rad=packed(rc),relative_value=packed(v))
def main():
    receipt=json.loads((ROOT/RECEIPT).read_bytes())
    for p,h in receipt["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
    r=cap(receipt);assert r["groups"]==5;d=r["data"];e=d["evidence"]
    v2path="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-RAW-GUARD-SHADERC-001-CODEX.json"
    cpupath="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json"
    assert sha((ROOT/v2path).read_bytes())=="3fd747841aaea192619df18add3a701a69cc0f20beed598497125d8202f252cf"
    assert sha((ROOT/cpupath).read_bytes())=="bb67a76885010c9485415007b1f1b5e7fbe03689812216d464baf21dcf4a9dfb"
    vd=cap(json.loads((ROOT/v2path).read_bytes()))["data"];cd=cap(json.loads((ROOT/cpupath).read_bytes()))["data"]
    assert set(e)==set(CASES)
    for c in CASES:assert e[c]==dict(packet=vd["results"][c]["packet"],rows=cd["results"][c]["rows"])
    # Public API must not expose caller-supplied evidence/caps. Test-only private fixture hook.
    tree=ast.parse((ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_v2_egress_HOST_v1.py").read_text())
    public=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=="compare")
    assert [a.arg for a in public.args.args]==["model","request","raw","origin"] and public.args.kwarg is None
    assert any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=="load_evidence"for n in ast.walk(public))
    ids=set();matches=0;stops=0;faults=set()
    for q in d["runs"]:
        assert q["id"]not in ids;ids.add(q["id"]);ev=copy.deepcopy(e);c=q["case"];fault=q["fault"]
        if fault:faults.add(fault)
        if fault=="missing_source":ev[c]["rows"].pop(0)
        elif fault=="source_identity":ev[c]["rows"][0]["original_scene_sha256"]="0"*64
        elif fault=="source_bits":ev[c]["rows"][0]["lo"]["word_le_hex"]="0000000000000000"
        elif fault=="source_cap":ev[c]["rows"][0]["literal_cap_rad"]=[1,1<<120];ev[c]["packet"]["source_literal_caps"][0]=[1,1<<120]
        elif fault=="relative_identity":ev[c]["rows"][2]["literal_request_sha256"]="0"*64
        elif fault=="relative_interval":ev[c]["rows"][2]["parent_relative_CONTROL_ONLY"]["interval"]=[[0,1],[0,1]]
        elif fault=="relative_cap":ev[c]["rows"][2]["literal_cap_rad"]=[1,1<<120];ev[c]["packet"]["retained_CPU_budget"]["literal_cap_rad"]=[1,1<<120]
        reason,b=expected(q,ev);out=q["result"]
        assert out["reason"]==reason and out["status"]==("HOST_UNATTESTED_BYTES_MATCH"if reason is None else "STOP"),q["id"]
        assert out["promotion"]=="STOP"and out["full_costs"]=="UNMEASURED_NOT_ZERO"
        for k in("GPU_executed","GPU_launch_allowed","GPU_guard_certified","scene_authenticated",
                 "fence_readback_authenticated","physical_field_certified","native_promotion_allowed"):assert out[k]is False
        assert out["compiler_calls"]==out["new_RN_operations"]==out["frozen_producer_replays"]==0
        if b is None:stops+=1;assert "budget"not in out
        else:
            matches+=1;assert out["budget"]==b
            assert out["output_sha256"]==sha(bytes.fromhex(q["raw_hex"]))and out["packet_sha256"]==digest(ev[c]["packet"])
            assert out["completeness"]=="SEALED_2_SOURCE_1_RELATIVE_ONLY"
            assert out["costs"]==dict(input_SSBO_bytes=48,output_SSBO_bytes=32,total_SSBO_bytes=80,
                source_records=2,relative_records=1,scene_build="UNMEASURED_NOT_ZERO",upload="UNMEASURED_NOT_ZERO",
                dispatch="UNMEASURED_NOT_ZERO",fence_readback="UNMEASURED_NOT_ZERO",geometry_material_field="UNMEASURED_NOT_ZERO")
    required=set(CASES)|{"hi_only","within_cap_wrong_bits","wrong_model","same_bytes_shared_reference_unattested","same_bytes_wrong_identity",
       "selector_extra","selector_missing","selector_unknown_case"}
    for c in CASES:
        required|={c+s for s in("_short","_long","_marker_only","_nonfinite16","_nonfinite24")}
        required|={c+"_header"+str(j)for j in range(4)}
    required|={"selector_"+k for k in("packet_sha256","original_scene_sha256","literal_request_sha256","shader_sha256","intent")}
    required|={"origin_"+k for k in("GPU_READBACK","GPU_ATTESTED","CPU_AUTHENTICATED")}
    required|={"fault_"+k for k in("missing_source","source_identity","source_bits","source_cap","relative_identity","relative_interval","relative_cap")}
    assert ids==required and matches==5 and stops==len(ids)-5
    witness=d["equal_payload_witness"];assert witness["establishes_provenance"]is False and witness["measured_GPU_execution"]is False
    assert witness["cases"]==list(CASES[:3])
    for c in witness["cases"]:assert e[c]["packet"]["expected_CONTROL_ONLY_hex"]==witness["bytes_hex"]
    assert len({e[c]["packet"]["literal_sha256"]for c in witness["cases"]})==3
    assert receipt["GPU_launch_allowed"]is False and receipt["promotion"]=="STOP"
    print(json.dumps(dict(status="PASS",independent_cases=len(ids),matches=matches,stops=stops,pins=len(receipt["code_doc_sha256"]),
             public_evidence_override=False,GPU_launch_allowed=False,compiler_calls=0,new_RN_operations=0)))
if __name__=="__main__":main()
