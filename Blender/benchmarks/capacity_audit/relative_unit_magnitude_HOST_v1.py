"""Opt-in HOST squared-magnitude certificates; no normalization or backend replay."""
from pathlib import Path
from fractions import Fraction as F
import json
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-relative-unit-magnitude-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-UNIT-JOIN-HOST-001-CODEX.json"
PSHA="9068bcf3e4093957901616c37e5362da283b9dc5936ff94039e46f80084b4a44"
CAP=F(1,5000)
INTENT="SQUARED_MAGNITUDE_ONLY_NO_RENORMALIZATION_NO_OPTICAL_POWER"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def frac(v):
    need(type(v)is list and len(v)==2 and all(type(x)is int for x in v)and v[1]>0,"typed_rational")
    need(max(abs(v[0]).bit_length(),v[1].bit_length())<=16384,"bounded_rational")
    return F(*v)

def decode(w):
    need(type(w)is str and len(w)==16,"word_LE")
    b=int.from_bytes(bytes.fromhex(w),"little");e=(b>>52)&2047;n=b&((1<<52)-1)
    need(e!=2047 and(e!=0 or n==0),"normal_zero_only")
    if e==0:return F(0)
    v=F((1<<52)+n)*F(2)**(e-1075)
    return -v if b>>63 else v

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==1044941,"parent_identity")
    r=json.loads(raw);pins=dict(r["code_doc_sha256"])
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"frozen_pin:"+p)
    need(c.capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    d=c.capture(r["test_run"])["data"];base=d["baseline_template"]
    records={x["id"]:dict(record=x,result=dict(base,**x["baseline_changes"]))for x in d["runs"]}
    need(len(records)==1282 and sum(x["result"]["join_conditional"]is True for x in records.values())==15,"closed_parent_grid")
    need(all(x["result"]["promotion"]=="STOP"and x["result"]["work_equivalence_certified"]is False for x in records.values()),"parent_scope")
    pins[PARENT]=PSHA;return records,pins

def selector(case,records):
    x=records[case];d=x["result"]["rows"][0]if x["result"]["join_conditional"]else {}
    return dict(join_record_id=case,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        source_context_sha256=d.get("source_context_sha256","STOP"),
        original_geometry_sha256=d.get("original_geometry_sha256","STOP"),overlay_sha256=d.get("overlay_sha256","STOP"),
        intent=INTENT,representation="HOST_EXACT_SQUARED_NORM_OF_RETAINED_REPRESENTATIONS")

def baseline():
    return dict(model=MODEL,status="STOP",reason=None,rows=[],conditional_squared_magnitude=False,
        exact_unit_norm_claimed=False,renormalization_performed=False,physical_field_certified=False,
        optical_power_certified=False,scene_authenticated=False,reference_calibrated=False,
        GPU_executed=False,GPU_launch_allowed=False,backend_executions=0,producer_replays=0,
        RN64_operations=0,HOST_word_decodes=0,HOST_norm_evaluations=0,
        reduced_parent_bounds_adopted=False,physical_phase_cancellation_assumed=False,
        work_equivalence_certified=False,time_efficiency_comparison_valid=False,
        promotion="STOP",full_costs="UNMEASURED_NOT_ZERO")

def certificate(v,b):
    """If ||v-u||_1 <= b and ||u||_2=1, squared norm defect <= 2*b+b*b."""
    need(type(v)is list and len(v)==2 and all(type(x)is F for x in v),"typed_HOST_pair")
    need(type(b)is F and 0<=b<=CAP,"fixed_full_unit_cap")
    norm=sum((x*x for x in v),F(0));defect=abs(norm-1);bound=2*b+b*b
    need(defect<=bound,"squared_norm_defect_exceeds_inherited_bound")
    return dict(squared_magnitude=pair(norm),absolute_defect_from_one=pair(defect),
        inherited_full_unit_L1_bound=pair(b),linear_charge=pair(2*b),quadratic_charge=pair(b*b),
        squared_magnitude_defect_bound=pair(bound),fixed_squared_cap=pair(2*CAP+CAP*CAP),
        units="DIMENSIONLESS_SQUARED_RELATIVE_FACTOR_NOT_OPTICAL_POWER",
        guarantee="CONDITIONAL_ON_RETAINED_UNIT_ERROR_CERTIFICATE",
        exact_unit_norm=norm==1)

def _audit(model,q,raw,records):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("join_record_id"))is str and q["join_record_id"]in records,"closed_parent_record")
        need(q==selector(q["join_record_id"],records)and all(type(v)is str for v in q.values()),"closed_selector")
        x=records[q["join_record_id"]];r=x["result"]
        need(r["join_conditional"]is True and r["status"]=="HOST_RETAINED_OUTPUT_JOIN_BOUND_ONLY","parent_STOP_not_rescued")
        d=r["rows"][0]
        need(type(d["reference_point"])is int and type(d["target_point"])is int and(d["reference_point"],d["target_point"])==(1,3),"same_reference")
        words=d["output_CPU_words_LE"]
        need(type(raw)is bytes and len(raw)==16 and raw==bytes.fromhex("".join(words)),"ALL16_output_bytes_before_decode")
        v=list(map(decode,words));out["HOST_word_decodes"]=2
        need(list(map(pair,v))==d["output_CPU_exact_HOST"],"retained_CPU_values")
        hp=list(map(frac,d["output_HOST_polynomial"]))
        bCPU=frac(d["CPU_full_unit_bound"]);bHOST=frac(d["HOST_full_unit_bound"])
        a=certificate(v,bCPU);b=certificate(hp,bHOST);out["HOST_norm_evaluations"]=2
        diag=dict(join_record_sha256=digest(x),source_context_sha256=q["source_context_sha256"],
            original_geometry_sha256=q["original_geometry_sha256"],overlay_sha256=q["overlay_sha256"],
            reference_point=1,target_point=3,CPU_words_LE=words,CPU_values=list(map(pair,v)),
            HOST_values=d["output_HOST_polynomial"],CPU=a,HOST=b,
            CPU_original_enclosures=d["CPU_enclosures"],HOST_original_enclosures=d["HOST_enclosures"],
            angular_caps_preserved_rad=[1,10000],unit_cap_preserved_L1=pair(CAP),
            scope="CONDITIONAL_RELATIVE_FACTOR_INVARIANT_NOT_FIELD_TRANSPORT")
        out.update(status="HOST_CONDITIONAL_SQUARED_MAGNITUDE_ONLY",conditional_squared_magnitude=True,rows=[diag])
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request,raw_frame):
    try:records,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,raw_frame,records)
