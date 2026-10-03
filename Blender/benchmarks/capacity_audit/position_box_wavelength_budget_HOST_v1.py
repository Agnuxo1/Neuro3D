"""Conditional geometric turns from retained position boxes and declared SOURCE lambda."""
from pathlib import Path
from fractions import Fraction as F
import json
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-box-wavelength-budget-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PAIR-LENGTH-BOX-BUDGET-HOST-001-CODEX.json"
PSHA="0682fb6c82dcf1d6a20fedcd077c704be8b4d3f9c87881b710a3430c7f235022"
REP="CONDITIONAL_GEOMETRIC_TURNS_DECLARED_SOURCE_WAVELENGTH"
INTENT="VERTEX3_MINUS_END_GEOMETRIC_ONLY_NO_TOTAL_PHASE"
CAP=F(1,10000)
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==83121,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS"and v["pins"]==200 and r["root_bits"]==96 and r["root_calls"]==0,"parent_oracle")
    d=c.capture(r["test_run"]);need(d["status"]=="PASS"and len(d["data"]["runs"])==53,"closed_parent_capture")
    e={x["id"]:x for x in d["data"]["runs"]};need(len(e)==53,"unique_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA;return e,pins

def parameters(record,e):
    out=e[record]["result"];context=out["diagnostics"][0]["source_context"]if out["diagnostics"]else None
    return dict(schema="DECLARED_SOURCE_WAVELENGTH_GEOMETRIC_ONLY",source_context=context,reference_point=1,target_point=3,
        wavelength_BU=[1,1],wavelength_radius_BU=[0,1],cap_rad=[1,10000],
        units=dict(wavelength="BU",quotient="turns",cap="rad"),authentication="DECLARED_NOT_SCENE_METROLOGY")

def selector(record,e,p):
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(e[record]),parameters_sha256=digest(p),
        source_context_sha256=digest(p.get("source_context"))if type(p)is dict else digest(None),
        representation=REP,intent=INTENT)

def baseline():
    out=c.baseline();out.update(model=MODEL,representation=REP,CPU_native_executed=False,root_calls=0,
        geometric_budget_conditional=False,total_phase_certified=False,wavelength_authenticated=False,optical_reference_certified=False,
        correlation_assumed=False,periodic_wrapping_used=False,producer_replays=0,turns_interval=None,center_turns=None,error_turns=None,error_rad_upper=None,
        declared_uncertainty_only=True,parent_branches_unchanged=True,HOST_cost=dict(parameters_validated=0,exact_divisions=0,centers=0,rad_upper_products=0))
    return out

def _audit(model,q,p,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e,p);need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"];need(r["status"]=="HOST_CONDITIONAL_DECLARED_BOX_POSITIVE_DIFFERENCE_ONLY"and r["conditional_difference_certified"]is True,"parent_STOP_not_rescued")
        d=r["rows"][0];template=parameters(q["record_id"],e)
        need(type(p)is dict and set(p)==set(template),"closed_parameters")
        for k in("schema","source_context","reference_point","target_point","units","authentication"):
            need(p[k]==template[k]and type(p[k])is type(template[k]),"closed_SOURCE_reference_units:"+k)
        need(type(p["reference_point"])is int and type(p["target_point"])is int,"typed_point_indices")
        need(d["source_context"]==d["original_geometry"]["context"]and digest(d["source_context"])==q["source_context_sha256"],"ORIGINAL_SOURCE_context")
        lam,err,cap=map(c.frac,(p["wavelength_BU"],p["wavelength_radius_BU"],p["cap_rad"]))
        need(lam>0 and err>=0 and cap==CAP and p["cap_rad"]==[1,10000],"closed_fixed_rad_cap_positive_lambda")
        out["HOST_cost"]["parameters_validated"]=3
        a,b=lam-err,lam+err;need(a>0,"nonpositive_lambda_lower_NO_EPSILON")
        lo,hi=map(lambda v:F(*v),r["difference_interval_BU"]);need(0<lo<=hi,"retained_positive_difference")
        qlo,qhi=lo/b,hi/a;out["HOST_cost"]["exact_divisions"]=2
        center=(qlo+qhi)/2;radius=(qhi-qlo)/2;out["HOST_cost"]["centers"]=1
        rad=8*radius;out["HOST_cost"]["rad_upper_products"]=1
        diag=dict(selector=q,parameters=p,source_context=d["source_context"],original_geometry_sha256=digest(d["original_geometry"]),
            reference_point=1,target_point=3,difference_interval_BU=r["difference_interval_BU"],wavelength_interval_BU=[pair(a),pair(b)],
            turns_interval=[pair(qlo),pair(qhi)],center_turns=pair(center),error_turns=pair(radius),error_rad_upper=pair(rad),cap_rad=pair(cap),
            two_pi_upper=[8,1],proof="2pi<8_AND_interval_midpoint_Chebyshev_radius_GEOMETRIC_ONLY",
            parent_record_sha256=digest(x),scope="CONDITIONAL_UNWRAPPED_GEOMETRIC_PHASE_NOT_TOTAL_PHASE_NOT_AUTHENTICATED")
        out["diagnostics"]=[diag];need(rad<=cap,"declared_geometric_wavelength_budget_exhausted")
        out.update(status="HOST_CONDITIONAL_GEOMETRIC_WAVELENGTH_BUDGET_ONLY",rows=[diag],verified_queries=1,geometric_budget_conditional=True,
            turns_interval=diag["turns_interval"],center_turns=pair(center),error_turns=pair(radius),error_rad_upper=pair(rad))
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request,declared_source):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,declared_source,e)
