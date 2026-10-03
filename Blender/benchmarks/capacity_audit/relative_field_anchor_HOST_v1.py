"""Explicit declared reference-anchor control times sealed relative unit; HOST only."""
from pathlib import Path
from fractions import Fraction as F
import json
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-relative-field-anchor-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-RELATIVE-UNIT-MAGNITUDE-HOST-001-CODEX.json"
PSHA="1a83104a6840f589b86f7cfb7074a7795eb35255d6ab51fe0d9fd6342df95249"
ORIGIN="NEW_DECLARED_ANCHOR_CONTROL_NOT_ORIGINAL_SOURCE_AMPLITUDE"
INTENT="ALL_ANCHOR_AND_UNIT_ERRORS_NOT_MISSING_AS_ZERO"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def frac(v,limit=16384):
    need(type(v)is list and len(v)==2 and all(type(x)is int for x in v)and v[1]>0,"typed_rational")
    q=F(*v);need(pair(q)==v and max(abs(v[0]).bit_length(),v[1].bit_length())<=limit,"canonical_bounded_rational")
    return q

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==491104,"parent_identity")
    r=json.loads(raw);pins=dict(r["code_doc_sha256"])
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"frozen_pin:"+p)
    need(c.capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    data=c.capture(r["test_run"])["data"]
    records={x["id"]:x for x in data["runs"]if x["result"]["conditional_squared_magnitude"]is True}
    need(len(records)==15,"closed_retained15")
    manifest=dict(count=1267,sha256=data["census"]["retained_STOP_manifest_sha256"])
    need(data["census"]["retained_STOP_manifest_count"]==manifest["count"],"old_STOP_manifest")
    pins[PARENT]=PSHA;return records,pins,manifest

def anchor_control(case,records,nominal,error,budget):
    d=records[case]["result"]["rows"][0]
    return dict(schema="DECLARED_REFERENCE_COMPLEX_ANCHOR_CONTROL_v1",origin=ORIGIN,
        source_component="SOURCE_POINT_0",source_context_sha256=d["source_context_sha256"],
        original_geometry_sha256=d["original_geometry_sha256"],overlay_sha256=d["overlay_sha256"],
        reference_point=1,target_point=3,units="DECLARED_RELATIVE_FIELD_L1_UNIT_NOT_WATTS",
        nominal_complex=[pair(x)for x in nominal],error_L1=pair(error),output_budget_L1=pair(budget))

def selector(case,records,anchor):
    d=records[case]["result"]["rows"][0]
    return dict(record_id=case,parent_receipt_sha256=PSHA,parent_record_sha256=digest(records[case]),
        source_context_sha256=d["source_context_sha256"],original_geometry_sha256=d["original_geometry_sha256"],
        overlay_sha256=d["overlay_sha256"],anchor_sha256=digest(anchor),intent=INTENT)

def baseline():
    return dict(model=MODEL,status="STOP",reason=None,diagnostics=[],relative_field_HOST=None,
        conditional_control_product=False,SOURCE_complex_reference=None,SOURCE_anchor_error=None,
        SOURCE_anchor_authenticated=False,original_scene_source_amplitude_used=False,
        physical_field_certified=False,optical_power_certified=False,source_coherence_certified=False,
        reference_calibrated=False,scene_authenticated=False,normalization_performed=False,
        full_visibility_certified=False,reduced_parent_bounds_adopted=False,physical_phase_cancellation_assumed=False,
        work_equivalence_certified=False,time_efficiency_comparison_valid=False,
        GPU_executed=False,GPU_launch_allowed=False,native_field_output=False,
        backend_executions=0,producer_replays=0,RN64_operations=0,HOST_word_decodes=0,HOST_product_evaluations=0,
        promotion="STOP",full_costs="UNMEASURED_NOT_ZERO")

def product(a,v,ba,bu):
    need(type(a)is list and type(v)is list and len(a)==len(v)==2 and all(type(x)is F for x in a+v),"typed_HOST_complex")
    need(type(ba)is F and type(bu)is F and ba>=0 and bu>=0,"nonnegative_declared_bounds")
    na=sum(map(abs,a),F(0));nv=sum(map(abs,v),F(0))
    value=[a[0]*v[0]-a[1]*v[1],a[0]*v[1]+a[1]*v[0]]
    charges=dict(anchor_error=nv*ba,unit_error=na*bu,mixed_error=ba*bu)
    return dict(value=[pair(x)for x in value],anchor_L1=pair(na),unit_represented_L1=pair(nv),
        charges={k:pair(x)for k,x in charges.items()},bound_L1=pair(sum(charges.values(),F(0))),
        HOST_arithmetic_error_L1=[0,1],units="DECLARED_RELATIVE_FIELD_L1_UNIT_NOT_WATTS",
        guarantee="CONDITIONAL_BILINEAR_BOUND_NOT_SOURCE_AUTHENTICATION")

def decode(w):
    b=int.from_bytes(bytes.fromhex(w),"little");e=(b>>52)&2047;n=b&((1<<52)-1)
    need(len(w)==16 and e!=2047 and(e!=0 or n==0),"normal_zero_word")
    if e==0:return F(0)
    x=F((1<<52)+n)*F(2)**(e-1075)
    return -x if b>>63 else x

def _audit(model,q,anchor,raw,records):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in records,"closed_retained_record")
        need(q==selector(q["record_id"],records,anchor)and all(type(v)is str for v in q.values()),"closed_selector")
        need(anchor is not None,"SOURCE_complex_reference_anchor_missing_NOT_ZERO")
        d=records[q["record_id"]]["result"]["rows"][0]
        expected=anchor_control(q["record_id"],records,[F(0),F(0)],F(0),F(0))
        need(type(anchor)is dict and set(anchor)==set(expected),"closed_anchor_control")
        for k in expected:
            if k not in("nominal_complex","error_L1","output_budget_L1"):
                need(type(anchor[k])is type(expected[k])and anchor[k]==expected[k],"anchor_context_scope:"+k)
        need(type(anchor["nominal_complex"])is list and len(anchor["nominal_complex"])==2,"complex_anchor_pair")
        a=[frac(x,128)for x in anchor["nominal_complex"]];ba=frac(anchor["error_L1"],128);cap=frac(anchor["output_budget_L1"],128)
        need(all(abs(x)<=10**6 for x in a)and 0<=ba<=10**6 and 0<=cap<=10**6,"declared_anchor_control_domain")
        words=d["CPU_words_LE"]
        need(type(raw)is bytes and len(raw)==16 and raw==bytes.fromhex("".join(words)),"ALL16_unit_bytes_before_decode")
        v=list(map(decode,words));out["HOST_word_decodes"]=2
        need([pair(x)for x in v]==d["CPU_values"],"same_retained_unit")
        bu=frac(d["CPU"]["inherited_full_unit_L1_bound"]);need(bu<=F(1,5000),"original_unit_cap")
        z=product(a,v,ba,bu);out["HOST_product_evaluations"]=1
        diag=dict(declared_anchor=anchor,CPU_values=d["CPU_values"],CPU_original_enclosures=d["CPU_original_enclosures"],
            inherited_full_unit_L1_bound=pair(bu),original_unit_cap_L1=[1,5000],product=z,control_output_budget_L1=pair(cap),
            context_kind="SEALED_CPU_SYNTHETIC_RELATIVE_UNIT_PLUS_NEW_DECLARED_ANCHOR_CONTROL",
            actual_SOURCE_anchor_missing=True,scope="NOT_ORIGINAL_SOURCE_FIELD_NOT_COHERENT_SUM")
        out["diagnostics"]=[diag]
        need(frac(z["bound_L1"])<=cap,"declared_control_product_budget_exceeded")
        out.update(status="HOST_DECLARED_ANCHOR_PRODUCT_CONTROL_ONLY",conditional_control_product=True,relative_field_HOST=z["value"])
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request,declared_anchor,unit_frame):
    try:records,_,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,declared_anchor,unit_frame,records)
