"""CPU-only total-phase egress contract; raw integer/rational validation, no GPU ABI."""
from pathlib import Path
from fractions import Fraction as F
import base64,hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-total-phase-pair64-egress-HOST-v1"
ORIGIN="CPU_UNATTESTED_BYTES"
TAG=0x43545031
INTENT="HOST_CPU_TOTAL_PHASE_EGRESS_ONLY"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001-CODEX.json"
PSHA="acc107cb584dba1d7845584ac1040569fa3a2dd4be7d2f9c39d702d2ce06b6c3"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def f(q):return F(*q)
def p(q):return [q.numerator,q.denominator]
def need(v,msg):
    if not v:raise ValueError(msg)
def capture(t):
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    need(t["rc"]==0 and not t["timed_out"]and len(b)==t["stdout_bytes"]and sha(b)==t["stdout_sha256"],"capture_integrity")
    return json.loads(b)
def load_evidence():
    b=(ROOT/PARENT).read_bytes();need(sha(b)==PSHA,"parent_identity");r=json.loads(b)
    for path,h in r["code_doc_sha256"].items():need(sha((ROOT/path).read_bytes())==h,"ancestral_pin")
    need(capture(r["independent_pre_after_whitespace"])["status"]=="PASS","parent_independent_capture")
    d=capture(r["test_run"])["data"]
    return {v["id"]:dict(native_request=v["request"],native_model=v["model"],native_result=v["result"],
        registry_entry=d["registry"].get(v["id"]))for v in d["runs"]}
def selector(case,e):
    a=e[case];q=a["native_request"]
    return dict(case=case,native_request_sha256=digest(q),phase_request_sha256=q["phase_request_sha256"],
        original_scene_sha256=q["original_scene_sha256"],literal_request_sha256=q["literal_request_sha256"],
        abi_tag=TAG,intent=INTENT)
def validate(model,request,e):
    need(model==MODEL,"model")
    need(type(request)is dict and set(request)=={"case","native_request_sha256","phase_request_sha256",
        "original_scene_sha256","literal_request_sha256","abi_tag","intent"},"closed_selector")
    need(type(request["case"])is str and request["case"]in e,"case")
    need(type(request["abi_tag"])is int and request==selector(request["case"],e),"selector_identity")
    a=e[request["case"]];r=a["native_result"]
    need(r["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY","parent_STOP:"+str(r["reason"]))
    need(len(r["rows"])==3 and [v["record_id"]for v in r["rows"]]==["S0","S1","S0-minus-S1"],"sealed_completeness")
    return a
def number(b):
    n=int.from_bytes(b,"little");ex=(n>>52)&2047
    need(ex!=2047,"raw_nonfinite")
    mant=n&((1<<52)-1)
    if ex:mant|=1<<52
    power=ex-1075 if ex else -1074
    val=F(mant<<power)if power>=0 else F(mant,1<<-power)
    return -val if n>>63 else val
def _packet(a):
    rows=a["native_result"]["rows"]
    return struct.pack("<4I",TAG,6,2,1)+b"".join(bytes.fromhex(r[k])for r in rows for k in("hi","lo"))
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,rows=[],diagnostics=[],raw_hex=None,
        promotion="STOP",GPU_launch_allowed=False,GPU_executed=False,GPU_guard_certified=False,
        V2_total_phase_backend_bound=False,native_promotion_allowed=False,scene_authenticated=False,
        material_authenticated=False,fence_readback_authenticated=False,physical_field_certified=False,
        amplitude=None,field=None,power=None,full_costs="UNMEASURED_NOT_ZERO",
        RN64_operations=0,producer_replays=0,compiler_calls=0,output_extent_bytes=64,
        semantic_order=["SOURCE0_TOTAL","SOURCE1_TOTAL","SOURCE0_MINUS_SOURCE1_TOTAL"])
def _compare(model,request,raw,origin,e):
    out=baseline()
    try:
        need(origin==ORIGIN,"unattested_origin_only");a=validate(model,request,e)
        need(type(raw)is bytes,"raw_type");need(len(raw)==64,"output_extent")
        need(struct.unpack("<4I",raw[:16])==(TAG,6,2,1),"CPU_total_phase_header")
        # Inspect ALL raw exponent words before budget or equality, no float conversion.
        words=[raw[16+8*j:24+8*j]for j in range(6)]
        need(all((int.from_bytes(v,"little")>>52)&2047!=2047 for v in words),"raw_nonfinite")
        decoded=[number(v)for v in words]
        vals=[decoded[2*j]+decoded[2*j+1]for j in range(3)]
        parent=a["native_result"]["rows"];pending=[];deltas=[]
        for j in range(2):
            r=parent[j];lo,hi=map(f,r["interval_cycles"]);delta=abs(vals[j]-f(r["value_cycles"]))
            conservative=f(r["conservative_error_rad"])+8*delta
            direct=8*max(abs(vals[j]-lo),abs(vals[j]-hi));cap=f(r["literal_cap_rad"])
            need(direct<=conservative,"SOURCE_bound_dominates")
            pending.append(dict(record_id=r["record_id"],hi=words[2*j].hex(),lo=words[2*j+1].hex(),
                value_cycles=p(vals[j]),interval_cycles=[p(lo),p(hi)],egress_delta_cycles=p(delta),
                direct_error_rad=p(direct),conservative_error_rad=p(conservative),literal_cap_rad=p(cap),fits=conservative<=cap))
            deltas.append(delta)
        r=parent[2];lo,hi=map(f,r["interval_cycles"])
        arith=abs(vals[2]-(vals[0]-vals[1]))
        conservative=8*(f(r["geometric_error_cycles"])+f(r["gamma_radius_cycles"])+f(r["gamma_encoding_error_cycles"])+
            f(r["SOURCE_add_error_cycles"])+sum(deltas)+arith)
        direct=8*max(abs(vals[2]-lo),abs(vals[2]-hi));cap=f(r["literal_cap_rad"])
        need(direct<=conservative,"relative_bound_dominates")
        pending.append(dict(record_id=r["record_id"],hi=words[4].hex(),lo=words[5].hex(),value_cycles=p(vals[2]),
            interval_cycles=[p(lo),p(hi)],SOURCE_egress_delta_cycles=p(sum(deltas)),relative_arithmetic_error_cycles=p(arith),
            direct_error_rad=p(direct),conservative_error_rad=p(conservative),literal_cap_rad=p(cap),fits=conservative<=cap))
        out["diagnostics"]=pending
        need(all(v["fits"]for v in pending[:2]),"ALL_SOURCE_egress_cap")
        need(pending[2]["fits"],"relative_egress_cap")
        need(raw==_packet(a),"native_total_phase_bits")
        out.update(status="HOST_CPU_TOTAL_PHASE_UNATTESTED_MATCH",rows=pending,raw_hex=raw.hex())
    except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error)as ex:out["reason"]=str(ex)
    return out
def compare(model,request,raw,origin):
    try:e=load_evidence()
    except(ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _compare(model,request,raw,origin,e)
def export(model,request):
    # Pure serialization of sealed captured words, NOT inference/replay or authentication.
    try:
        e=load_evidence();a=validate(model,request,e);raw=_packet(a)
    except(ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]=str(ex);return out
    return _compare(model,request,raw,ORIGIN,e)
