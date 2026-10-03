"""Opt-in HOST audit of retained HOST/native CPU units. No backend execution."""
from pathlib import Path
from fractions import Fraction as F
import json,math
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-reference-unit-join-HOST-v1"
CPU="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-UNIT-NATIVE-CPU-001-CODEX.json"
CSHA="57d05f94e42493c5f3dfd1e544f859e2a64d6d34caab1952055ff2579b795c7f"
HOST="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-UNIT-BUDGET-HOST-001-CODEX.json"
HSHA="f83bd046776cafcf3fd7db70aa11978ce6e1e7119fe80fc79c513fbf912d6002"
REP="HOST_JOIN_RETAINED_CPU_WORDS_TO_HOST_POLYNOMIAL_NOT_EQUAL_WORK"
INTENT="SAME_ORIGINAL_REFERENCE_CAPS_ALL16_OUTPUT_BYTES_NO_REPLAY"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/CPU).read_bytes();need(sha(raw)==CSHA and len(raw)==555386,"CPU_parent_identity");cr=json.loads(raw)
    pins=dict(cr["code_doc_sha256"])
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"frozen_pin:"+p)
    need(c.capture(cr["independent_pre"])["pins"]==232 and c.capture(cr["independent_pre"])["status"]=="PASS","CPU_parent_oracle")
    cd=c.capture(cr["test_run"])["data"];cb=cd["baseline_template"]
    ce={x["id"]:dict(record=x,result=dict(cb,**x["baseline_changes"]))for x in cd["runs"]}
    need(len(ce)==924 and sum(x["result"]["conditional_unit"]is True for x in ce.values())==15,"CPU_closed_grid")
    raw=(ROOT/HOST).read_bytes();need(sha(raw)==HSHA and len(raw)==388070,"HOST_parent_identity");hr=json.loads(raw)
    need(pins[HOST]==HSHA and cr["parent_receipt_sha256"]==HSHA,"same_parent_receipt")
    need(c.capture(hr["independent_pre"])["status"]=="PASS","HOST_parent_oracle")
    hd=c.capture(hr["test_run"])["data"];hb=hd["baseline_template"]
    he={x["id"]:dict(record=x,result=dict(hb,**x["baseline_changes"]))for x in hd["runs"]}
    need(len(he)==777 and sum(x["result"]["conditional_unit"]is True for x in he.values())==15,"HOST_closed_grid")
    need(all(x["record"]["record_id"]in he for x in ce.values()),"all_HOST_links")
    pins[CPU]=CSHA;return ce,he,pins

def selector(case,ce,he):
    x=ce[case];hid=x["record"]["record_id"];h=he[hid];q=h["record"]["request"]
    return dict(native_record_id=case,host_record_id=hid,native_receipt_sha256=CSHA,native_record_sha256=digest(x),
        host_receipt_sha256=HSHA,host_record_sha256=digest(h),source_context_sha256=q["source_context_sha256"],
        original_geometry_sha256=q["original_geometry_sha256"],overlay_sha256=q["overlay_sha256"],representation=REP,intent=INTENT)

def baseline():
    out=c.baseline();out.update(model=MODEL,representation=REP,root_calls=0,CPU_native_executed=False,
        RN64_conversions=0,HOST_word_decodes=0,HOST_derivative_terms=0,join_conditional=False,
        same_nominal_context=False,native_unit_output=False,work_equivalence_certified=False,
        time_efficiency_comparison_valid=False,physical_phase_cancellation_assumed=False,
        reduced_parent_bounds_adopted=False,retained_CPU_nodes_observed=0,retained_CPU_conversions_observed=0,
        backend_executions=0)
    return out

def frac(v):
    need(type(v)is list and len(v)==2 and all(type(a)is int for a in v)and v[1]>0,"typed_rational")
    need(max(abs(v[0]).bit_length(),v[1].bit_length())<=16384,"bounded_derived_HOST_rational")
    return F(*v)
def decode(w):
    need(type(w)is str and len(w)==16,"word_LE")
    b=int.from_bytes(bytes.fromhex(w),"little");ex=(b>>52)&2047;m=b&((1<<52)-1)
    need(ex!=2047 and(ex!=0 or m==0),"normal_zero_only")
    if ex==0:return F(0)
    v=F((1<<52)+m)*F(2)**(ex-1075);return -v if b>>63 else v

def lipschitz(x,y):
    """Positive coefficient derivative envelope; no sin/cos derivative alias."""
    need(type(x)is F and type(y)is F,"typed_HOST_arguments")
    m=max(abs(x),abs(y));need(m<=1,"fixed_parent_1rad_domain")
    cos=sum((m**(2*k-1)/math.factorial(2*k-1)for k in range(1,7)),F(0))
    sin=sum((m**(2*k)/math.factorial(2*k)for k in range(7)),F(0))
    return [cos,sin]

def _audit(model,q,raw,ce,he):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("native_record_id"))is str and q["native_record_id"]in ce,"closed_native_record")
        expected=selector(q["native_record_id"],ce,he)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_join_selector")
        nr=ce[q["native_record_id"]];cr=nr["result"];hr=he[q["host_record_id"]];h=hr["result"]
        need(cr["status"]=="CPU_RN64_RELATIVE_UNIT_PARTIAL_ONLY"and cr["conditional_unit"]is True,"CPU_parent_STOP_not_rescued")
        need(h["status"]=="HOST_DECLARED_RELATIVE_UNIT_ONLY"and h["conditional_unit"]is True,"HOST_parent_STOP_not_rescued")
        need(nr["record"]["id"]=="parent:"+q["host_record_id"],"canonical_same_record")
        cq=nr["record"]["request"];hq=hr["record"]["request"]
        need(cq["parent_record_sha256"]==digest(hr)and cq["parent_request_sha256"]==digest(hq),"CPU_bound_to_same_HOST")
        for key in("source_context_sha256","original_geometry_sha256","overlay_sha256"):need(cq[key]==hq[key]==q[key],"same_context:"+key)
        cd=cr["rows"][0];hd=h["rows"][0]
        for d in(cd,hd):
            need(type(d["reference_point"])is int and type(d["target_point"])is int and(d["reference_point"],d["target_point"])==(1,3),"same_reference_target")
            need(d["original_phase_cap_rad"]==[1,10000]and d["derived_unit_cap_L1"]==[1,5000],"same_original_caps")
        need(cd["input_words_LE"]==hd["input_words_LE"],"same_original_angle_words")
        need(type(raw)is bytes and len(raw)==16 and raw==bytes.fromhex("".join(cd["output_words_LE"])),"ALL16_output_bytes_before_decode")
        need(cr["unit_words_LE"]==cd["output_words_LE"],"same_CPU_output_words")
        x=frac(hd["nominal_rad_HOST"]);y=frac(cd["scalar_argument_exact_rad_HOST"])
        need(x==frac(cd["input_pair_exact_rad_HOST"]),"same_original_nominal")
        loss=abs(y-x);need(loss==frac(cd["collapse_error_rad"]),"explicit_collapse_ledger")
        ang=frac(hd["inherited_angle_error_rad"]);need(ang==frac(cd["inherited_angle_error_rad"])and 2*ang==frac(hd["inherited_unit_L1_charge"]),"same_original_angle_charge")
        LP=lipschitz(x,y);out["HOST_derivative_terms"]=13
        native=list(map(decode,cd["output_words_LE"]));out["HOST_word_decodes"]=2
        hp=list(map(frac,hd["exact_polynomial_unit_HOST"]))
        rr=list(map(frac,cd["component_RN_error_L1"]));cf=list(map(frac,cd["component_coefficient_error_L1"]))
        rh=list(map(frac,hd["component_remainders_L1"]));rc=list(map(frac,cd["component_remainders_L1"]))
        need(all(v>=0 for v in [ang,loss]+rr+cf+rh+rc),"all_positive_charges")
        need(frac(hd["unit_error_L1_upper"])==2*ang+sum(rh,F(0))<=F(1,5000),"HOST_budget_preserved")
        need(frac(cd["error_unit_L1_upper"])==2*ang+2*loss+sum(rr+cf+rc,F(0))<=F(1,5000),"CPU_budget_preserved")
        delta=[abs(a-b)for a,b in zip(native,hp)]
        bounds=[rr[i]+cf[i]+LP[i]*loss for i in(0,1)]
        need(all(a<=b for a,b in zip(delta,bounds)),"nominal_output_difference_dominated")
        hi=hd["component_enclosures_HOST"];ci=cd["component_enclosures_HOST"]
        for i in(0,1):
            hb=ang+rh[i];cb=ang+loss+rr[i]+cf[i]+rc[i]
            need(list(map(frac,hi[i]))==[hp[i]-hb,hp[i]+hb],"HOST_enclosure_preserved")
            need(list(map(frac,ci[i]))==[native[i]-cb,native[i]+cb],"CPU_enclosure_preserved")
            need(max(frac(hi[i][0]),frac(ci[i][0]))<=min(frac(hi[i][1]),frac(ci[i][1])),"same_declared_component_intervals_overlap")
        diag=dict(host_record_sha256=digest(hr),CPU_record_sha256=digest(nr),source_context_sha256=q["source_context_sha256"],
            original_geometry_sha256=q["original_geometry_sha256"],overlay_sha256=q["overlay_sha256"],
            reference_point=1,target_point=3,input_original_words_LE=hd["input_words_LE"],output_CPU_words_LE=cd["output_words_LE"],
            output_CPU_exact_HOST=list(map(pair,native)),output_HOST_polynomial=hd["exact_polynomial_unit_HOST"],
            nominal_x_rad_HOST=pair(x),native_argument_y_rad_HOST=pair(y),collapse_error_rad=pair(loss),
            polynomial_derivative_bound=list(map(pair,LP)),nominal_difference_L1_components=list(map(pair,delta)),
            nominal_difference_bound_components=list(map(pair,bounds)),nominal_difference_L1=pair(sum(delta,F(0))),
            nominal_difference_bound_L1=pair(sum(bounds,F(0))),RN_charge_components=cd["component_RN_error_L1"],
            coefficient_charge_components=cd["component_coefficient_error_L1"],HOST_full_unit_bound=hd["unit_error_L1_upper"],
            CPU_full_unit_bound=cd["error_unit_L1_upper"],HOST_enclosures=hi,CPU_enclosures=ci,
            scope="HOST_NOMINAL_OUTPUT_JOIN_NOT_PHYSICAL_CANCELLATION_NOT_EQUAL_WORK")
        out.update(status="HOST_RETAINED_OUTPUT_JOIN_BOUND_ONLY",rows=[diag],join_conditional=True,same_nominal_context=True,
            retained_CPU_nodes_observed=27,retained_CPU_conversions_observed=14)
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request,raw_frame):
    try:ce,he,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,raw_frame,ce,he)
