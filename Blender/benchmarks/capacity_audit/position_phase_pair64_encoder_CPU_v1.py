"""CPU binary64 word conversion with exact HOST residual; NOT native phase arithmetic."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-pair64-encoder-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-BOX-WAVELENGTH-BUDGET-HOST-001-CODEX.json"
PSHA="3018979f9ea16607babcffe69231f710fe0635670d170c458b4f2c7a27d57011"
REP="CPU_BINARY64_PAIR_WORDS_NO_NATIVE_SCALAR_SUM"
INTENT="ENCODING_ERROR_CHARGED_GEOMETRIC_ONLY_NOT_TOTAL_PHASE"
CAP=F(1,10000);MIN=F(1,2**1022)
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==81588,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS"and v["pins"]==204 and r["root_calls"]==r["producer_replays"]==0,"parent_oracle")
    d=c.capture(r["test_run"]);need(d["status"]=="PASS"and len(d["data"]["runs"])==91,"closed_parent_capture")
    e={x["id"]:x for x in d["data"]["runs"]};need(len(e)==91,"unique_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA;return e,pins

def selector(record,e):
    x=e[record];diag=x["result"]["diagnostics"]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),parent_parameters_sha256=digest(x["parameters"]),
        source_context_sha256=digest(diag[0]["source_context"])if diag else digest(None),
        original_geometry_sha256=diag[0]["original_geometry_sha256"]if diag else digest(None),representation=REP,intent=INTENT)

def internal(v):
    need(type(v)is list and len(v)==2 and all(type(n)is int for n in v)and v[1]>0,"typed_internal_rational")
    need(max(abs(v[0]).bit_length(),v[1].bit_length())<=2048,"bounded_internal_2048")
    q=F(*v);need(abs(q)<=1000000,"internal_magnitude");return q

def baseline():
    out=c.baseline();out.update(model=MODEL,representation=REP,CPU_native_executed=False,CPU_binary64_conversion_executed=False,
        root_calls=0,producer_replays=0,compiler_calls=0,RN64_conversions=0,conversion_trace=[],geometric_encoding_budget_conditional=False,total_phase_certified=False,
        wavelength_authenticated=False,optical_reference_certified=False,correlation_assumed=False,periodic_wrapping_used=False,
        native_scalar_sum_executed=False,declared_uncertainty_only=True,parent_branches_unchanged=True,pair_words_LE=None,encoding_error_turns=None,error_rad_upper=None)
    return out

def convert(value,out):
    v=float(value);out["RN64_conversions"]+=1;out["CPU_binary64_conversion_executed"]=True
    word=struct.pack("<d",v).hex();bits=int.from_bytes(bytes.fromhex(word),"little");exp=(bits>>52)&2047
    out["conversion_trace"].append(dict(input_exact_HOST=pair(value),word_LE=word,value_exact_HOST=pair(F.from_float(v))))
    need(exp!=2047 and (exp!=0 or bits&((1<<63)-1)==0),"normal_zero_word_only")
    return v,word

def encode(center_turns,radius_turns):
    out=baseline()
    try:
        center,radius=map(internal,(center_turns,radius_turns));need(radius>=0,"nonnegative_radius")
        need(center==0 or abs(center)>=MIN,"subnormal_center_NO_CONVERSION")
        hi,hw=convert(center,out);residual=center-F.from_float(hi)
        need(residual==0 or abs(residual)>=MIN,"subnormal_residual_STOP_AFTER_HIGH")
        lo,lw=convert(residual,out);value=F.from_float(hi)+F.from_float(lo);err=abs(value-center)
        bound=8*(radius+err);high_bound=8*(radius+abs(F.from_float(hi)-center))
        diag=dict(center_turns=pair(center),radius_turns=pair(radius),hi_word_LE=hw,lo_word_LE=lw,
            high_value_turns=pair(F.from_float(hi)),residual_exact_HOST=pair(residual),low_value_turns=pair(F.from_float(lo)),
            decoded_pair_exact_HOST=pair(value),encoding_error_turns=pair(err),error_rad_upper=pair(bound),
            hi_only_error_rad_upper=pair(high_bound),hi_only_budget_passes=high_bound<=CAP,cap_rad=pair(CAP),
            scope="CPU_CONVERSION_WORDS_HOST_RESIDUAL_GEOMETRIC_ONLY_NO_NATIVE_SUM_NO_PHASE_TOTAL")
        out["diagnostics"]=[diag];need(bound<=CAP,"pair_encoding_geometric_budget_exhausted")
        out.update(status="CPU_BINARY64_PAIR_GEOMETRIC_BUDGET_ONLY",rows=[diag],pair_words_LE=[hw,lw],
            geometric_encoding_budget_conditional=True,encoding_error_turns=pair(err),error_rad_upper=pair(bound))
    except(ValueError,TypeError,KeyError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def _audit(model,q,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e);need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"];need(r["status"]=="HOST_CONDITIONAL_GEOMETRIC_WAVELENGTH_BUDGET_ONLY"and r["geometric_budget_conditional"]is True,"parent_STOP_not_rescued")
        d=r["rows"][0];need(d["source_context"]==x["parameters"]["source_context"]and digest(d["source_context"])==q["source_context_sha256"],"same_SOURCE_context")
        out=encode(r["center_turns"],r["error_turns"])
        for diag in out["diagnostics"]:diag.update(selector=q,source_context=d["source_context"],original_geometry_sha256=d["original_geometry_sha256"],
            parent_record_sha256=digest(x),parent_turns_interval=r["turns_interval"],reference_point=1,target_point=3)
    except(ValueError,TypeError,KeyError,IndexError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,e)
