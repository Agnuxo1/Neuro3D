"""Opt-in CPU RN64 two-limb normalization; geometric budget only, never total phase."""
from pathlib import Path
from fractions import Fraction as F
import json,struct,math
import coplanar_clearance_CPU_v1 as c
import oblique_pair64_difference_CPU_v1 as arithmetic
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-pair64-normalize-native-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-PAIR64-ENCODER-CPU-001-CODEX.json"
PSHA="e6e07a6c765db82382ea49d8165f9a1ee2fec16b33d8be4505f9a9621cd0d52f"
REP="CPU_RN64_TWO_SUM_PAIR_NOT_SCALAR_PHASE"
INTENT="NORMALIZATION_ERROR_CHARGED_GEOMETRIC_ONLY_NOT_TOTAL_PHASE"
CAP=F(1,10000)
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==117621,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS"and v["pins"]==208 and r["root_calls"]==r["producer_replays"]==0,"parent_oracle")
    d=c.capture(r["test_run"]);need(d["status"]=="PASS"and len(d["data"]["runs"])==103 and len(d["data"]["helpers"])==10,"closed_parent_capture")
    e={x["id"]:x for x in d["data"]["runs"]+d["data"]["helpers"]};need(len(e)==113,"unique_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA;return e,pins

def selector(record,e):
    x=e[record];d=x["result"]["diagnostics"]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        parent_parameters_sha256=digest(x.get("request",dict(center=x.get("center"),radius=x.get("radius")))),
        source_context_sha256=digest(d[0].get("source_context"))if d else digest(None),
        original_geometry_sha256=d[0].get("original_geometry_sha256",digest(None))if d else digest(None),
        representation=REP,intent=INTENT)

def baseline():
    r=c.baseline();r.update(model=MODEL,representation=REP,CPU_native_executed=False,
        CPU_binary64_conversion_executed=False,root_calls=0,producer_replays=0,compiler_calls=0,
        RN64_conversions=0,decoded_words=0,RN64_operations=0,trace=dict(nodes=[],eft=[]),
        geometric_normalization_budget_conditional=False,total_phase_certified=False,
        wavelength_authenticated=False,optical_reference_certified=False,correlation_assumed=False,
        periodic_wrapping_used=False,declared_uncertainty_only=True,parent_branches_unchanged=True,
        native_scalar_phase_output=False,pair_words_LE=None,arithmetic_error_turns=None,error_rad_upper=None)
    return r

def decode(raw,r):
    # Caller must already have checked ALL 16 bytes against the pinned parent's pair.
    v=struct.unpack("<dd",raw);r["decoded_words"]=2
    for x in v:
        b=int.from_bytes(struct.pack("<d",x),"little");exp=(b>>52)&2047
        need(exp!=2047 and (exp!=0 or b&((1<<63)-1)==0),"normal_zero_input")
        need(math.isfinite(x)and abs(x)<=1000000,"bounded_native_input")
    return v

def _audit(model,q,raw,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];p=x["result"]
        need(p["status"]=="CPU_BINARY64_PAIR_GEOMETRIC_BUDGET_ONLY"and p["geometric_encoding_budget_conditional"]is True,"parent_STOP_not_rescued")
        d=p["rows"][0];center=F(*d["center_turns"]);radius=F(*d["radius_turns"])
        need(F(*d["cap_rad"])==CAP and radius>=0,"fixed_parent_budget")
        words=p["pair_words_LE"];want=bytes.fromhex("".join(words))
        need(type(raw)is bytes and len(raw)==16 and raw==want,"ALL16bytes_before_decode")
        hi,lo=decode(raw,out);decoded=F.from_float(hi)+F.from_float(lo)
        need(decoded==F(*d["decoded_pair_exact_HOST"]),"pinned_pair_value")
        before=abs(decoded-center)
        need(before==F(*d["encoding_error_turns"])and 8*(radius+before)==F(*p["error_rad_upper"])and 8*(radius+before)<=CAP,"pinned_encoded_budget")
        # Reuse only the frozen pure six-node two_sum, NOT its producer/audit.
        h,l=arithmetic.two_sum(hi,lo,"normalize",out["trace"])
        out["RN64_operations"]=len(out["trace"]["nodes"]);out["CPU_native_executed"]=out["RN64_operations"]>0
        value=F.from_float(h)+F.from_float(l);err=abs(value-decoded);bound=8*(radius+before+err)
        diag=dict(selector=q,parent_record_sha256=digest(x),parent_encoding=d,
            input_words_LE=words,input_frame_sha256=sha(raw),output_words_LE=[arithmetic.word(h),arithmetic.word(l)],
            decoded_input_exact_HOST=pair(decoded),decoded_output_exact_HOST=pair(value),
            center_turns=pair(center),radius_turns=pair(radius),encoding_error_turns=pair(before),
            arithmetic_error_turns=pair(err),error_rad_upper=pair(bound),cap_rad=pair(CAP),
            scope="CPU_NATIVE_TWO_LIMBS_GEOMETRIC_ONLY_UNATTESTED_NOT_TOTAL_PHASE")
        out["diagnostics"]=[diag]
        for xword in (h,l):
            b=int.from_bytes(struct.pack("<d",xword),"little");exp=(b>>52)&2047
            need(exp!=2047 and (exp!=0 or b&((1<<63)-1)==0),"normal_zero_output")
        need(len(out["trace"]["nodes"])==6 and len(out["trace"]["eft"])==1,"six_node_graph")
        need(value==decoded,"measured_two_sum_identity")
        need(bound<=CAP,"normalization_geometric_budget_exhausted")
        out.update(status="CPU_NATIVE_PAIR_GEOMETRIC_BUDGET_ONLY",rows=[diag],pair_words_LE=diag["output_words_LE"],
            geometric_normalization_budget_conditional=True,arithmetic_error_turns=pair(err),error_rad_upper=pair(bound))
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    finally:
        out["RN64_operations"]=len(out["trace"]["nodes"]);out["CPU_native_executed"]=out["RN64_operations"]>0
    return out

def audit(model,request,raw_frame):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,raw_frame,e)
