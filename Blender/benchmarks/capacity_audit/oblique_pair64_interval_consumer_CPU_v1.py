"""Sealed native pair64 scene -> actual CPU64 intervals; no transport replay/GPU."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,base64,zlib,copy
import oblique_finite_interval_HOST_v1 as host
import oblique_finite_interval_CPU64_v1 as cpu
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-pair64-interval-consumer-CPU-v1"
POLICY="EXACT_BOTH_LIMBS_THEN_OUTWARD_BOX_CAST_KEEP_ALL_RADII"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-CPU-001-CODEX.json"
PSHA="813fd728006a90adb40f99d1eb49aa3523f8f63bf61edca7775e332dc57106ea"
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def capture(c):
    require(c["rc"]==0 and c["timed_out"]is False,"capture_PASS")
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),2*1024*1024+1)
    require(z.eof and not z.unused_data and not z.unconsumed_tail,"bounded_closed_capture")
    require(len(raw)==c["stdout_bytes"]<=2*1024*1024 and sha(raw)==c["stdout_sha256"],"capture_identity")
    return json.loads(raw)
def retained():
    raw=(ROOT/PARENT).read_bytes();require(len(raw)==84149 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw)
    require(len(r["code_doc_sha256"])==260,"parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","sealed_parent_oracle")
    d=capture(r["test_run"])["evidence"]
    e={"scene:"+x["name"]:x for x in d["records"]}
    e["native_inexact"]=d["inexact"]
    e.update({"input:"+x["name"]:x for x in d["invalid"]})
    require(len(e)==16,"closed_six_plus_ten_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins
def selector(record,e):
    x=e[record];f=x["result"]["frame"]
    packet=f["output_packet_hex"]if f else ""
    query=x.get("scene_query",x["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,parent_receipt_sha256=PSHA,record_id=record,
        parent_record_sha256=host.digest(x),original_snapshot_sha256=host.digest(x["scene"]),
        original_query_sha256=host.digest(query),input_request_sha256=host.digest(x["request"]),
        output_packet_hex=packet,output_packet_sha256=sha(bytes.fromhex(packet)))
def decode_word(word):
    require(type(word)is str and len(word)==16 and bytes.fromhex(word).hex()==word,"canonical_binary64_word")
    b=int.from_bytes(bytes.fromhex(word),"little");exp=(b>>52)&2047;mant=b&((1<<52)-1)
    require(exp!=2047 and (exp!=0 or mant==0),"normal_zero_word")
    if exp==0:return F(0)
    return (-1 if b>>63 else 1)*F((1<<52)+mant)*F(2)**(exp-1075)
def decode_pair(hi,lo):
    return decode_word(hi)+decode_word(lo) # EXACT HOST decode, NOT RN limb collapse
def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,frame=None,native_result=None,
        packet_bytes=0,word_decodes=0,exact_pair_decodes=0,predicate_calls=0,
        new_transport_graph_calls=0,retained_suite_replays=0,scalar_RN_limb_collapse=False,
        physical_visibility_certified=False,phase_certified=False,scene_authenticated=False,
        GPU_used=False,source_uncertainty_cancelled=False,full_costs="UNKNOWN_NOT_ZERO",
        promotion="STOP_PHYSICAL_GPU",decode_scope="HOST_EXACT_WORD_DECODE_PLUS_NATIVE_CPU64_INTERVALS")
def _consume(q,e):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        require(set(q)==set(expected)and all(type(v)is str for v in q.values())and q==expected,"closed_selector")
        x=e[q["record_id"]];prior=x["result"]
        out.update(parent_record_sha256=host.digest(x),parent_receipt_sha256=PSHA,
            original_snapshot_sha256=q["original_snapshot_sha256"],request_sha256=host.digest(q),
            upstream_status=prior["status"],upstream_reason=prior["reason"])
        if prior["status"]!="CPU_NATIVE_PAIR64_RECENTER_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_upstream_STOP_not_rescued");return out
        require(prior["source_uncertainty_cancelled"]is False and prior["phase_certified"]is False
            and prior["HOST_recenter_substitution"]is False and prior["native_hi_lo_recenter_executed"]is True,"upstream_scope")
        s=x["scene"];host.validate(s,x["scene_query"])
        f=prior["frame"];raw=bytes.fromhex(q["output_packet_hex"])
        require(len(raw)==240 and sha(raw)==q["output_packet_sha256"],"ALL_output_packet_bytes")
        received=copy.deepcopy(f["scene"]);ledger=[]
        for i in range(15):
            n=host.POINTS[i//3];axis=i%3
            hi=raw[16*i:16*i+8].hex();lo=raw[16*i+8:16*i+16].hex()
            value=decode_pair(hi,lo);out["word_decodes"]+=2;out["exact_pair_decodes"]+=1
            require([value.numerator,value.denominator]==f["scene"]["points"][n]["nominal"][axis],"pair_frame_identity")
            target=F(*s["points"][n]["nominal"][axis])-F(*s["points"]["origin"]["nominal"][axis])
            require(value==target,"common_reference_geometry")
            radius=s["points"][n]["radius"][axis]
            require(f["scene"]["points"][n]["radius"][axis]==radius,"ALL_original_radii")
            received["points"][n]["nominal"][axis]=[value.numerator,value.denominator]
            ledger.append(dict(point=n,axis=axis,hi_word=hi,lo_word=lo,decoded=[value.numerator,value.denominator],radius=radius))
        require(host.digest(received)==f["snapshot_sha256"],"received_frame_snapshot")
        host.validate(received,f["scene_query"])
        nq=dict(backend=cpu.MODEL,scene_query=f["scene_query"],snapshot_sha256=host.digest(received))
        out.update(packet_bytes=240,frame=dict(scene=received,scene_query=f["scene_query"],snapshot_sha256=host.digest(received),
            native_request=nq,decode_ledger=ledger,reference=f["reference"]),predicate_calls=1)
        result=cpu.classify(received,nq)
        out.update(status=result["status"],reason="sealed_native_packet_outward_predicate",native_result=result)
    except (ValueError,TypeError,KeyError,IndexError,OverflowError,OSError)as ex:
        out["reason"]=str(ex)
    return out
def classify(q):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError,zlib.error)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _consume(q,e)
