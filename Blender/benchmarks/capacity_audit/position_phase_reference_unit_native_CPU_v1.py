"""Opt-in partial native CPU relative unit from retained scene-bound hi-lo radians.
Internal RN64 collapse is explicit, charged and never labeled lossless transport.
"""
from pathlib import Path
from fractions import Fraction as F
import json,math,struct,sys
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-reference-unit-native-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-UNIT-BUDGET-HOST-001-CODEX.json"
PSHA="f83bd046776cafcf3fd7db70aa11978ce6e1e7119fe80fc79c513fbf912d6002"
REP="PARTIAL_CPU_RN64_RELATIVE_UNIT_EXPLICIT_CHARGED_SCALAR_NOT_PHYSICAL"
INTENT="ALL16_BYTES_THEN_CHARGED_SUM_COEFFICIENTS_HORNER26_NO_FMA"
CAP=F(1,10000);UC=2*CAP;MIN=F(2)**-1022
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes()
    need(sha(raw)==PSHA and len(raw)==388070,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"frozen_pin:"+p)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS"and v["pins"]==228,"parent_oracle")
    d=c.capture(r["test_run"]);need(d["status"]=="PASS","parent_capture");data=d["data"]
    base=data["baseline_template"];runs=data["runs"]
    e={x["id"]:dict(record=x,result=dict(base,**x["baseline_changes"]))for x in runs}
    need(len(e)==len(runs)==777 and sum(x["result"]["conditional_unit"]is True for x in e.values())==15,"closed_parent_grid")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins

def selector(record,e):
    x=e[record];q=x["record"]["request"]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        parent_request_sha256=digest(q),source_context_sha256=q["source_context_sha256"],
        original_geometry_sha256=q["original_geometry_sha256"],overlay_sha256=q["overlay_sha256"],
        representation=REP,intent=INTENT,unit_budget_rule="TWO_TIMES_SAME_ORIGINAL_PHASE_CAP")

def baseline():
    out=c.baseline();out.update(model=MODEL,representation=REP,root_calls=0,
        trace=[],coefficient_trace=[],stages=[],RN64_conversions=0,decoded_words=0,
        CPU_native_executed=False,CPU_binary64_conversion_executed=False,
        rounding_into_scalar_used=False,lossless_hi_lo_transport_claim=False,
        conditional_unit=False,native_unit_output=False,native_scalar_phase_output=False,
        unit_words_LE=None,periodic_wrapping_used=False,total_phase_certified=False,
        material_authenticated=False,wavelength_authenticated=False,optical_reference_certified=False,
        correlation_assumed=False,shared_phase_cancellation_assumed=False,
        declared_uncertainty_only=True,parent_branches_unchanged=True)
    return out

def word(x):return struct.pack("<d",x).hex()
def normal(w):
    b=int.from_bytes(bytes.fromhex(w),"little");ex=(b>>52)&2047
    need(ex!=2047 and(ex!=0 or b&((1<<63)-1)==0),"normal_zero_only")
def Q(x):return F.from_float(x)
def checked(x):
    normal(word(x));need(abs(Q(x))<=10**6,"unchanged_numeric_domain_1e6")
def node(a,b,op,label,out):
    exact=Q(a)*Q(b)if op=="mul"else Q(a)+Q(b)
    y=a*b if op=="mul"else a+b
    row=dict(label=label,op=op,a=word(a),b=word(b),y=word(y))
    out["trace"].append(row)
    # Even an underflow STOP preserves the executed node and actual words.
    checked(a);checked(b);checked(y)
    need(exact==0 or abs(exact)>=MIN,"subnormal_exact_result_AFTER_node")
    row["delta"]=pair(Q(y)-exact)
    return y,abs(Q(y)-exact)

def compute(raw,error_rad,out):
    """Unbound numerical helper; NOT authentication or fresh scene inference."""
    need(type(raw)is bytes and len(raw)==16,"typed_16_byte_frame")
    need(type(error_rad)is F and 0<=error_rad<=CAP,"same_original_phase_budget")
    need((sys.float_info.radix,sys.float_info.mant_dig,sys.float_info.max_exp)==(2,53,1024),"binary64_runtime")
    a,b=struct.unpack("<dd",raw);out["decoded_words"]=2;checked(a);checked(b)
    x=Q(a)+Q(b);need(abs(x)+error_rad<=1,"parent_domain_NO_WRAP")
    y,collapse=node(a,b,"add","argument.sum_hi_lo",out);out["rounding_into_scalar_used"]=True
    yr=Q(y)
    d=dict(input_words_LE=[word(a),word(b)],input_pair_exact_rad_HOST=pair(x),
        scalar_argument_word_LE=word(y),scalar_argument_exact_rad_HOST=pair(yr),
        collapse_error_rad=pair(collapse),inherited_angle_error_rad=pair(error_rad),
        original_phase_cap_rad=pair(CAP),derived_unit_cap_L1=pair(UC),
        absolute_argument_upper_rad=pair(abs(yr)+error_rad+collapse),
        reference_scope="CPU_SYNTHETIC_DECLARED_RELATIVE_UNIT_NOT_PHYSICAL_FIELD",
        internal_scalar_rounding_is_EXPLICIT_NOT_LOSSLESS=True)
    out["diagnostics"]=[d]
    need(abs(yr)+error_rad+collapse<=1,"native_domain_NO_WRAP")
    rem=[abs(yr)**n/F(math.factorial(n))for n in(14,15)]
    pre=2*error_rad+2*collapse+sum(rem,F(0))
    d.update(component_remainders_L1=list(map(pair,rem)),pre_polynomial_unit_bound_L1=pair(pre))
    need(pre<=UC,"unit_budget_exhausted_BEFORE_polynomial")
    coeff=[];ec=[]
    for odd in(0,1):
        cv=[];ce=[]
        for k in range(7):
            ref=F((-1)**k,math.factorial(2*k+odd));v=float(ref)
            out["coefficient_trace"].append(dict(odd=odd,k=k,exact_coefficient=pair(ref),word_LE=word(v),
                delta=pair(Q(v)-ref)))
            checked(v);cv.append(v);ce.append(abs(Q(v)-ref))
        coeff.append(cv);ec.append(ce)
    z,ez=node(y,y,"mul","square",out);zt=yr*yr;values=[];roundcharges=[];coefcharges=[]
    for odd in(0,1):
        h=coeff[odd][6];eh=F(0);ch=ec[odd][6]
        for k in range(5,-1,-1):
            prod,delta=node(h,z,"mul",str(odd)+".mul"+str(k),out)
            eh=abs(Q(h))*ez+abs(zt)*eh+delta;ch=abs(zt)*ch
            h,delta=node(prod,coeff[odd][k],"add",str(odd)+".add"+str(k),out)
            eh+=delta;ch+=ec[odd][k]
            out["stages"].append(dict(odd=odd,k=k,word_LE=word(h),round_error_L1=pair(eh),coefficient_error_L1=pair(ch)))
        if odd:
            h,delta=node(h,y,"mul","sin.final",out);eh=abs(yr)*eh+delta;ch=abs(yr)*ch
        values.append(h);roundcharges.append(eh);coefcharges.append(ch)
    bound=pre+sum(roundcharges,F(0))+sum(coefcharges,F(0))
    components=[error_rad+collapse+rem[i]+roundcharges[i]+coefcharges[i]for i in(0,1)]
    d.update(output_words_LE=list(map(word,values)),component_RN_error_L1=list(map(pair,roundcharges)),
        component_coefficient_error_L1=list(map(pair,coefcharges)),error_unit_L1_upper=pair(bound),
        component_enclosures_HOST=[[pair(Q(v)-err),pair(Q(v)+err)]for v,err in zip(values,components)])
    need(len(out["trace"])==27 and len(out["coefficient_trace"])==14,"closed_native_graph")
    need(bound<=UC,"native_unit_budget_exhausted_AFTER_polynomial")
    return d

def _audit(model,q,raw,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"]
        need(r["status"]=="HOST_DECLARED_RELATIVE_UNIT_ONLY"and r["conditional_unit"]is True,"parent_STOP_not_rescued")
        d=r["rows"][0];want=bytes.fromhex("".join(d["input_words_LE"]))
        need(type(raw)is bytes and len(raw)==16 and raw==want,"ALL16bytes_before_decode")
        need(d["original_phase_cap_rad"]==[1,10000]and d["derived_unit_cap_L1"]==[1,5000],"same_original_caps")
        need(type(d["reference_point"])is int and d["reference_point"]==1 and type(d["target_point"])is int and d["target_point"]==3,"same_reference_target")
        err=F(*d["inherited_angle_error_rad"])
        need(2*err==F(*d["inherited_unit_L1_charge"]),"all_inherited_angle_charge")
        diag=compute(raw,err,out)
        diag.update(parent_record_sha256=digest(x),input_frame_sha256=sha(raw),reference_point=1,target_point=3)
        out.update(status="CPU_RN64_RELATIVE_UNIT_PARTIAL_ONLY",rows=[diag],conditional_unit=True,
            native_unit_output=True,unit_words_LE=diag["output_words_LE"])
    except(ValueError,TypeError,KeyError,IndexError,OverflowError,struct.error)as ex:out["reason"]=str(ex)
    finally:
        out["RN64_operations"]=len(out["trace"]);out["RN64_conversions"]=len(out["coefficient_trace"])
        out["CPU_native_executed"]=out["RN64_operations"]>0
        out["CPU_binary64_conversion_executed"]=out["RN64_conversions"]>0
    return out

def audit(model,request,raw_frame):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,raw_frame,e)
