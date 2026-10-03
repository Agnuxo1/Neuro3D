"""Explicit four-term reference phase overlay. HOST intervals only, no inferred cancellation."""
from pathlib import Path
from fractions import Fraction as F
import json
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-reference-overlay-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-PAIR64-NORMALIZE-NATIVE-CPU-001-CODEX.json"
PSHA="0ada58247e69c73306eeb037787346a4561ce28bc28e5664816fa05985d94a34"
REP="HOST_DECLARED_FOUR_TERM_REFERENCE_CONTRAST_NOT_NATIVE_TOTAL_PHASE"
INTENT="CHARGE_ALL_FOUR_RADII_NO_CONTEXT_CROSSJOIN_NO_CANCELLATION"
CAP=F(1,10000)
ORDER=(("SOURCE_POINT_0","target",3,1),("SOURCE_POINT_0","reference",1,-1),
       ("MATERIAL_OFFSET","target",3,1),("MATERIAL_OFFSET","reference",1,-1))
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==110327,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS"and v["pins"]==212 and r["root_calls"]==r["producer_replays"]==0,"parent_oracle")
    d=c.capture(r["test_run"]);need(d["status"]=="PASS"and len(d["data"]["runs"])==258,"closed_parent_capture")
    e={x["id"]:x for x in d["data"]["runs"]};need(len(e)==258,"unique_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA;return e,pins

def packet(record,e):
    d=e[record]["result"]["diagnostics"];enc=d[0]["parent_encoding"]if d else {}
    return dict(schema="NEW_DECLARED_FOUR_TERM_REFERENCE_OVERLAY",source_context=enc.get("source_context"),
        original_geometry_sha256=enc.get("original_geometry_sha256"),reference_point=1,target_point=3,
        frame="DECLARED_COMMON_TURNS_FRAME_NOT_CALIBRATED",authentication="DECLARED_NOT_PHYSICALLY_AUTHENTICATED",
        units=dict(phase="turns",cap="rad"),cap_rad=[1,10000],
        components=[dict(kind=k,endpoint=end,point=point,phase_interval_turns=[[0,1],[0,1]])for k,end,point,sign in ORDER])

def selector(record,e,p):
    x=e[record];template=packet(record,e)
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        parent_parameters_sha256=digest(x["request"]),source_context_sha256=digest(template["source_context"]),
        original_geometry_sha256=template["original_geometry_sha256"]or digest(None),
        overlay_sha256=digest(p),representation=REP,intent=INTENT)

def baseline():
    r=c.baseline();r.update(model=MODEL,representation=REP,CPU_native_executed=False,
        CPU_binary64_conversion_executed=False,root_calls=0,producer_replays=0,compiler_calls=0,
        RN64_conversions=0,RN64_operations=0,total_phase_certified=False,material_authenticated=False,
        wavelength_authenticated=False,optical_reference_certified=False,correlation_assumed=False,
        shared_phase_cancellation_assumed=False,periodic_wrapping_used=False,declared_uncertainty_only=True,
        parent_branches_unchanged=True,reference_overlay_conditional=False,
        HOST_cost=dict(terms_validated=0,midpoints=0,radii=0,interval_component_addsubs=0,nominal_component_addsubs=0,rad_upper_products=0))
    return r

def _audit(model,q,p,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e,p)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"]
        need(r["status"]=="CPU_NATIVE_PAIR_GEOMETRIC_BUDGET_ONLY"and r["geometric_normalization_budget_conditional"]is True,"parent_STOP_not_rescued")
        d=r["rows"][0];enc=d["parent_encoding"];template=packet(q["record_id"],e)
        ctx=template["source_context"]
        need(type(ctx)is dict and set(ctx)=={"provenance","synthetic_scene_sha256"}and ctx["provenance"]=="CPU_SYNTHETIC_ONLY_NOT_SEALED_SCENE",
            "unbound_helper_or_non_synthetic_context_NO_OVERLAY")
        need(type(p)is dict and set(p)==set(template),"closed_packet")
        for k in template:
            if k!="components":need(p[k]==template[k]and type(p[k])is type(template[k]),"closed_context_reference_frame:"+k)
        need(type(p["reference_point"])is int and type(p["target_point"])is int,"typed_endpoints")
        need(type(p["components"])is list and len(p["components"])==4,"ALL_FOUR_TERMS_NO_OMISSION")
        center,radius=F(*d["center_turns"]),F(*d["radius_turns"])
        enc_error,arith_error=F(*d["encoding_error_turns"]),F(*d["arithmetic_error_turns"])
        value=F(*d["decoded_output_exact_HOST"])
        need(abs(value-center)<=enc_error+arith_error and F(*r["error_rad_upper"])==8*(radius+enc_error+arith_error)<=CAP,
            "pinned_geometric_budget")
        low,high=center-radius,center+radius;nominal=value;phase_radius=F(0);terms=[]
        for term,(kind,end,point,sign)in zip(p["components"],ORDER):
            need(type(term)is dict and set(term)=={"kind","endpoint","point","phase_interval_turns"}and term["kind"]==kind
                and term["endpoint"]==end and type(term["point"])is int and term["point"]==point,"closed_component_order_identity")
            interval=term["phase_interval_turns"];need(type(interval)is list and len(interval)==2,"closed_interval")
            a,b=map(c.frac,interval);need(a<=b,"ordered_phase_interval")
            mid=(a+b)/2;rad=(b-a)/2;phase_radius+=rad
            low+=a if sign==1 else -b;high+=b if sign==1 else -a;nominal+=sign*mid
            terms.append(dict(kind=kind,endpoint=end,point=point,sign=sign,interval_turns=interval,midpoint_turns=pair(mid),radius_turns=pair(rad),standalone_error_rad_upper=pair(8*rad),standalone_fits=8*rad<=CAP))
            cost=out["HOST_cost"];cost["terms_validated"]+=1;cost["midpoints"]+=1;cost["radii"]+=1
            cost["interval_component_addsubs"]+=2;cost["nominal_component_addsubs"]+=1
        bound=8*(radius+enc_error+arith_error+phase_radius);direct=8*max(abs(nominal-low),abs(nominal-high))
        out["HOST_cost"]["rad_upper_products"]=2
        need(direct<=bound,"conservative_bound_dominates")
        diag=dict(selector=q,declared_packet=p,parent_record_sha256=digest(x),parent_normalized_geometry=d,
            terms=terms,nominal_contrast_turns=pair(nominal),interval_contrast_turns=[pair(low),pair(high)],
            geometric_radius_turns=pair(radius),encoding_error_turns=pair(enc_error),normalization_error_turns=pair(arith_error),
            all_four_phase_radius_turns=pair(phase_radius),error_rad_upper=pair(bound),direct_error_rad_upper=pair(direct),
            cap_rad=pair(CAP),all_terms_individually_fit=all(t["standalone_fits"]for t in terms),
            reference_scope="DECLARED_TARGET3_MINUS_END1_NOT_CALIBRATED_OPTICAL_REFERENCE",
            scope="CPU_SYNTHETIC_HOST_CONTRAST_NOT_PHYSICAL_TOTAL_PHASE_NOT_NATIVE_BACKEND")
        out["diagnostics"]=[diag];need(bound<=CAP,"cumulative_reference_phase_budget_exhausted")
        out.update(status="HOST_DECLARED_REFERENCE_CONTRAST_ONLY",rows=[diag],reference_overlay_conditional=True)
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request,declared_overlay):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,declared_overlay,e)
