"""Opt-in TOTALphase readback HOST validator. Byte copies remain unauthenticated."""
from pathlib import Path
from fractions import Fraction as F
import base64,hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-total-phase-readback-HOST-v1"
ORIGIN="HOST_UNATTESTED_TOTAL_PHASE_BYTES"
TAG=0x54504731
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-SHADERC-001-CODEX.json"
PSHA="6316b24df16dfb9080c5aee9d8563c4644541ef500029546e822dcf626723606"
NATIVE="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001-CODEX.json"
NSHA="acc107cb584dba1d7845584ac1040569fa3a2dd4be7d2f9c39d702d2ce06b6c3"
def need(v,why):
    if not v:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def frac(q):return F(*q)
def inflate(s,limit):
    z=zlib.decompressobj();b=z.decompress(base64.b64decode(s,validate=True),limit+1)
    need(len(b)<=limit and z.eof and not z.unused_data and not z.unconsumed_tail,"compressed_extent")
    return b
def capture(t):
    b=inflate(t["stdout_zlib_base64"],2097152)
    need(t["rc"]==0 and t["timed_out"]is False and len(b)==t["stdout_bytes"] and sha(b)==t["stdout_sha256"],"capture_identity")
    return json.loads(b)
def packed_bytes(q):
    b=inflate(q["zlib_base64"],4096);need(len(b)==q["bytes"] and sha(b)==q["sha256"],"packet_identity");return b
def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA,"candidate_receipt_identity");r=json.loads(raw)
    for path,h in r["code_doc_sha256"].items():
        p=Path(path);need(sha((p if p.is_absolute()else ROOT/p).read_bytes())==h,"ancestral_pin:"+path)
    raw=(ROOT/NATIVE).read_bytes();need(sha(raw)==NSHA,"native_receipt_identity");n=json.loads(raw)
    c=capture(r["test_run"])["data"];d=capture(n["test_run"])["data"]
    need(c["status"]=="HOST_COMPILE_TOPOLOGY_PREFIX_ONLY" and c["GPU_executed"]is False and c["new_RN_operations"]==0,"sealed_candidate_scope")
    native={x["id"]:x for x in d["runs"]};entries={}
    for item in c["preparations"]:
        case=item["id"];prep=item["result"];parent=native[case]["result"]
        entry=dict(prepared=prep,native=parent,SPIRV_sha256=c["valid_compile"]["spirv"]["sha256"],
            shader_sha256=c["valid_compile"]["source"]["sha256"],selector_binding=digest(native[case]["request"]))
        if prep["status"]=="HOST_PREPARED_UNATTESTED":
            entry["input"]=packed_bytes(prep["input"]);entry["output"]=packed_bytes(prep["expected_output"])
            need(parent["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY" and len(parent["rows"])==3,"native_rows")
            expected=struct.pack("<4I",TAG,6,2,1)+b"".join(bytes.fromhex(rr[k])for rr in parent["rows"]for k in("hi","lo"))
            need(entry["output"]==expected,"explicit_retagged_CONTROL")
            registry=d["registry"][case];rq=registry["request"]
            entry.update(original_scene_sha256=rq["original_scene_sha256"],literal_request_sha256=rq["literal_request_sha256"],
                phase_request_sha256=digest(rq))
            fixture=registry["fixture"];encoded=[rr[k]["word_le_hex"]for rr in fixture["rows"][:2]for k in("hi","lo")]
            need([x["name"]for x in parent["encodings"]]==["gamma0","gamma1","mu"],"material_SOURCE_order")
            encoded += [x[k]for x in parent["encodings"]for k in("hi","lo")]
            need(entry["input"]==struct.pack("<4I",TAG,10,2,1)+b"".join(bytes.fromhex(h)for h in encoded),"sealed_scene_parameter_input")
        else:
            need(prep["status"]=="STOP" and parent["status"]=="STOP" and prep["input"]is None and prep["expected_output"]is None,"parent_STOP_retained")
            entry.update(input=None,output=None,original_scene_sha256=None,literal_request_sha256=None,phase_request_sha256=None)
        entries[case]=entry
    need(len(entries)==46 and sum(v["input"]is not None for v in entries.values())==11,"sealed_census")
    return entries,r["code_doc_sha256"]
def selector(case,e):
    a=e[case]
    return dict(case=case,compiler_receipt_sha256=PSHA,input_sha256=sha(a["input"])if a["input"]is not None else None,
        SPIRV_sha256=a["SPIRV_sha256"],original_scene_sha256=a["original_scene_sha256"],
        literal_request_sha256=a["literal_request_sha256"],phase_request_sha256=a["phase_request_sha256"],
        native_selector_sha256=a["selector_binding"],abi_tag=TAG,intent="HOST_TOTAL_PHASE_READBACK_NUMERIC_ONLY")
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,rows=[],diagnostics=[],decoded_components=0,
        raw_input_checked=0,raw_output_checked=0,verified_rows=0,output_sha256=None,promotion="STOP",
        GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,device_egress_authenticated=False,
        fence_readback_authenticated=False,scene_authenticated=False,material_authenticated=False,
        native_promotion_allowed=False,physical_field_certified=False,amplitude=None,field=None,power=None,
        full_costs="UNMEASURED_NOT_ZERO",RN64_operations=0,producer_replays=0,compiler_calls=0)
def raw_guard(raw,count,extent):
    need(type(raw)is bytes and len(raw)==extent,"raw_extent_"+str(extent))
    need(struct.unpack("<4I",raw[:16])==(TAG,count,2,1),"new_TOTAL_phase_header_"+str(count))
    words=[raw[16+8*i:24+8*i]for i in range(count)]
    need(all(((int.from_bytes(w,"little")>>52)&2047)!=2047 for w in words),"raw_nonfinite_"+str(count))
    need(all((int.from_bytes(w,"little")&((1<<63)-1))<=0x4270000000000000 for w in words),"raw_domain_"+str(count))
    return words
def number(word):
    bits=int.from_bytes(word,"little");ex=(bits>>52)&2047;need(ex!=2047,"number_raw_nonfinite")
    mant=bits&((1<<52)-1);mant|=(1<<52)if ex else 0;exp=ex-1075 if ex else -1074
    val=F(mant<<exp)if exp>=0 else F(mant,1<<-exp)
    return -val if bits>>63 else val
def _compare(model,request,input_bytes,output_bytes,origin,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(origin)is str and origin==ORIGIN,"only_unattested_HOST_origin")
        need(type(request)is dict and type(request.get("case"))is str and request["case"]in e,"closed_case")
        expected=selector(request["case"],e)
        need(set(request)==set(expected) and all(type(request[k])is type(expected[k])for k in expected) and request==expected,"closed_selector_identity")
        a=e[request["case"]];parent=a["native"]
        need(a["prepared"]["status"]=="HOST_PREPARED_UNATTESTED","parent_STOP:"+str(parent["reason"]))
        need([r["record_id"]for r in parent["rows"]]==["S0","S1","S0-minus-S1"]and all(r["fits"]is True for r in parent["rows"]),"ALL_parent_rows_caps")
        raw_guard(input_bytes,10,96);out["raw_input_checked"]=10
        words=raw_guard(output_bytes,6,64);out["raw_output_checked"]=6
        need(input_bytes==a["input"],"sealed_input_bits_before_decode")
        values=[number(w)for w in words];out["decoded_components"]=6
        sums=[values[i]+values[i+1]for i in(0,2,4)];pending=[];deltas=[]
        for i in range(2):
            r=parent["rows"][i];lo,hi=map(frac,r["interval_cycles"])
            delta=abs(sums[i]-frac(r["value_cycles"]));conservative=frac(r["conservative_error_rad"])+8*delta
            direct=8*max(abs(sums[i]-lo),abs(sums[i]-hi));cap=frac(r["literal_cap_rad"])
            need(direct<=conservative,"SOURCE_bound_dominates")
            pending.append(dict(record_id=r["record_id"],hi=words[2*i].hex(),lo=words[2*i+1].hex(),
                value_cycles=pair(sums[i]),egress_delta_cycles=pair(delta),direct_error_rad=pair(direct),
                conservative_error_rad=pair(conservative),literal_cap_rad=pair(cap),fits=conservative<=cap))
            deltas.append(delta)
        r=parent["rows"][2];lo,hi=map(frac,r["interval_cycles"]);arith=abs(sums[2]-(sums[0]-sums[1]))
        conservative=8*(frac(r["geometric_error_cycles"])+frac(r["gamma_radius_cycles"])+frac(r["gamma_encoding_error_cycles"])+
            frac(r["SOURCE_add_error_cycles"])+sum(deltas)+arith)
        direct=8*max(abs(sums[2]-lo),abs(sums[2]-hi));cap=frac(r["literal_cap_rad"])
        need(direct<=conservative,"relative_bound_dominates")
        pending.append(dict(record_id=r["record_id"],hi=words[4].hex(),lo=words[5].hex(),value_cycles=pair(sums[2]),
            SOURCE_egress_delta_cycles=pair(sum(deltas)),relative_arithmetic_error_cycles=pair(arith),
            direct_error_rad=pair(direct),conservative_error_rad=pair(conservative),literal_cap_rad=pair(cap),fits=conservative<=cap))
        out["diagnostics"]=pending
        need(all(v["fits"]for v in pending[:2]),"ALL_SOURCE_readback_cap")
        need(pending[2]["fits"],"relative_readback_cap")
        need(output_bytes==a["output"],"native_TOTAL_phase_bits")
        out.update(status="HOST_UNATTESTED_TOTAL_PHASE_MATCH",rows=pending,verified_rows=3,output_sha256=sha(output_bytes))
    except (ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error)as ex:out["reason"]=str(ex)
    return out
def compare(model,request,input_bytes,output_bytes,origin):
    try:e,_=retained()
    except (ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _compare(model,request,input_bytes,output_bytes,origin,e)
