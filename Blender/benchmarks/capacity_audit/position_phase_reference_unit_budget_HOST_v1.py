"""Opt-in HOST-only relative reference unit budget from retained native angle pair."""
from fractions import Fraction as F
from pathlib import Path
import json,math
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-reference-unit-budget-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-ANGLE-NATIVE-CPU-001-CODEX.json"
PSHA="1e84ec39940f7accb09f584b92ae24e10fd13443e9ee77017d381aa876c46cb9"
REP="HOST_EXACT_PAIR_RELATIVE_UNIT_NOT_NATIVE_NOT_PHYSICAL_FIELD"
INTENT="ALL16_BYTES_EXACT_HILO_HOST_NO_WRAP_TWO_TIMES_ORIGINAL_PHASE_CAP"
RULE="L1_UNIT_CAP_EQUALS_TWO_TIMES_SAME_ORIGINAL_PHASE_CAP_RAD"
PHASE_CAP=F(1,10000)
UNIT_CAP=2*PHASE_CAP
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==383219,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"frozen_pin:"+p)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS"and v["pins"]==224,"parent_oracle")
    d=c.capture(r["test_run"]);need(d["status"]=="PASS","parent_capture")
    runs=d["data"]["runs"];e={x["id"]:x for x in runs}
    need(len(e)==len(runs)==630 and sum(x["result"]["angle_conditional"]is True for x in runs)==39,"closed_parent_grid")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins

def selector(record,e):
    x=e[record];q=x["request"]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        parent_request_sha256=digest(q),source_context_sha256=q["source_context_sha256"],
        original_geometry_sha256=q["original_geometry_sha256"],overlay_sha256=q["overlay_sha256"],
        representation=REP,intent=INTENT,unit_budget_rule=RULE)

def baseline():
    out=c.baseline()
    out.update(model=MODEL,representation=REP,root_calls=0,CPU_native_executed=False,RN64_conversions=0,
        HOST_word_decodes=0,HOST_pair_exact_sums=0,HOST_polynomial_operations=0,HOST_factorials=0,
        HOST_remainder_powers=0,HOST_unit_evaluated=False,conditional_unit=False,unit_pair_HOST=None,
        total_phase_certified=False,material_authenticated=False,wavelength_authenticated=False,
        optical_reference_certified=False,correlation_assumed=False,shared_phase_cancellation_assumed=False,
        periodic_wrapping_used=False,native_scalar_phase_output=False,native_unit_output=False,
        declared_uncertainty_only=True,parent_branches_unchanged=True,rounding_into_scalar_used=False,
        exact_HOST_pair_interpretation=True,unit_budget_rule=RULE,derived_unit_cap_L1=pair(UNIT_CAP))
    return out

def component(word):
    need(type(word)is str and len(word)==16,"binary64_word")
    b=int.from_bytes(bytes.fromhex(word),"little");ex=(b>>52)&2047;mant=b&((1<<52)-1)
    need(ex!=2047 and(ex!=0 or mant==0),"normal_zero_only")
    if ex==0:return F(0)
    v=F((1<<52)+mant)*F(2)**(ex-1075)
    need(abs(v)<=10**6,"unchanged_numeric_domain_1e6")
    return -v if b>>63 else v

def bounded(v):
    v=F(v);need(max(abs(v.numerator).bit_length(),v.denominator.bit_length())<=16384,"bounded_derived_HOST_rational")
    return v

def polynomial(x,out):
    z=bounded(x*x);out["HOST_polynomial_operations"]+=1;vals=[]
    for odd in(0,1):
        cs=[]
        for k in range(7):
            cs.append(F((-1)**k,math.factorial(2*k+odd)));out["HOST_factorials"]+=1
        h=cs[-1]
        for k in range(5,-1,-1):
            h=bounded(h*z);out["HOST_polynomial_operations"]+=1
            h=bounded(h+cs[k]);out["HOST_polynomial_operations"]+=1
        if odd:h=bounded(h*x);out["HOST_polynomial_operations"]+=1
        vals.append(h)
    return vals

def compute(raw,error_rad,out):
    """Numerical HOST helper. NOT scene/auth/backend admission."""
    need(type(raw)is bytes and len(raw)==16,"typed_16_byte_frame")
    need(type(error_rad)is F and 0<=error_rad<=PHASE_CAP,"same_original_phase_budget")
    iw=[raw[:8].hex(),raw[8:].hex()];v=[component(w)for w in iw];out["HOST_word_decodes"]+=2
    x=bounded(v[0]+v[1]);out["HOST_pair_exact_sums"]=1
    d=dict(input_words_LE=iw,decoded_pair_rad_HOST=list(map(pair,v)),nominal_rad_HOST=pair(x),
        inherited_angle_error_rad=pair(error_rad),angle_radius_enclosure_rad_HOST=[pair(x-error_rad),pair(x+error_rad)],
        magnitude_domain_rad=[1,1],absolute_argument_upper_rad=pair(abs(x)+error_rad),
        original_phase_cap_rad=pair(PHASE_CAP),derived_unit_cap_L1=pair(UNIT_CAP),unit_budget_rule=RULE,
        inherited_unit_L1_charge=pair(2*error_rad),HOST_pair_sum_is_NOT_native_scalar=True,
        scope="CPU_SYNTHETIC_HOST_RELATIVE_REFERENCE_UNIT_NOT_PHYSICAL_FIELD")
    out["diagnostics"]=[d]
    need(abs(x)+error_rad<=1,"angle_enclosure_outside_fixed_1rad_NO_WRAP")
    # Proven |d(sin)/dx|,|d(cos)/dx|<=1; propagate TWO times same parent angle bound.
    rem=[bounded(abs(x)**n/F(math.factorial(n)))for n in(14,15)]
    out["HOST_factorials"]+=2;out["HOST_remainder_powers"]+=2
    d.update(Taylor_remainder_L1=pair(sum(rem,F(0))),component_remainders_L1=list(map(pair,rem)),
        unit_error_L1_upper=pair(2*error_rad+sum(rem,F(0))))
    need(F(*d["unit_error_L1_upper"])<=UNIT_CAP,"unit_budget_exhausted_BEFORE_polynomial")
    vals=polynomial(x,out);out["HOST_unit_evaluated"]=True
    d.update(exact_polynomial_unit_HOST=list(map(pair,vals)),
        component_enclosures_HOST=[[pair(val-(error_rad+rr)),pair(val+(error_rad+rr))]for val,rr in zip(vals,rem)],
        polynomial_degree=[12,13],HOST_exact_polynomial_error_L1=[0,1],
        native_polynomial_error_L1="UNMEASURED_NOT_ZERO_NO_NATIVE_BACKEND")
    need(out["HOST_polynomial_operations"]==26 and out["HOST_factorials"]==16,"closed_HOST_graph")
    return d

def _audit(model,q,raw,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"]
        need(r["status"]=="CPU_NATIVE_PAIR_DECLARED_REFERENCE_ANGLE_ONLY"and r["angle_conditional"]is True,"parent_STOP_not_rescued")
        d=r["rows"][0]
        need(d["reference_point"]==1 and type(d["reference_point"])is int
            and d["target_point"]==3 and type(d["target_point"])is int,"same_declared_reference_target")
        need(d["cap_rad"]==[1,10000]and d["scope"]=="CPU_SYNTHETIC_DECLARED_REFERENCE_ANGLE_NOT_PHYSICAL_TOTAL","same_original_phase_cap_scope")
        expected_raw=bytes.fromhex("".join(r["pair_words_LE"]))
        need(type(raw)is bytes and len(raw)==16 and raw==expected_raw,"ALL16bytes_before_decode")
        err=F(*d["error_rad_upper"]);need(err==sum(F(*v)for v in d["charges_rad"].values()),"all_angle_charges_retained")
        low,high=map(lambda v:F(*v),d["interval_angle_rad_HOST"])
        nominal=sum((component(w)for w in r["pair_words_LE"]),F(0))
        out["HOST_word_decodes"]+=2 # Parent interval check is explicit additional HOST work.
        need(max(abs(nominal-low),abs(nominal-high))<=err,"parent_interval_within_retained_bound")
        diag=compute(raw,err,out)
        diag.update(parent_record_sha256=digest(x),input_frame_sha256=sha(raw),reference_point=1,target_point=3,
            parent_interval_angle_rad_HOST=d["interval_angle_rad_HOST"])
        out.update(status="HOST_DECLARED_RELATIVE_UNIT_ONLY",rows=[diag],conditional_unit=True,
            unit_pair_HOST=diag["exact_polynomial_unit_HOST"])
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request,raw_frame):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,raw_frame,e)
