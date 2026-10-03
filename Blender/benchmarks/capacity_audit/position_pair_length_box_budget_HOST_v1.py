"""Conditional HOST uncertainty boxes for a selected vertex-minus-end length."""
from pathlib import Path
from fractions import Fraction as F
import json
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-pair-length-box-budget-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PAIR-LENGTH-RATIONALIZED-HOST-001-CODEX.json"
PSHA="63ee2a87c4609b89a07d1d75a4ba5eff33f92ab094ea42a0d705b98aabb93f61"
REP="CONDITIONAL_HOST_DECLARED_POSITION_BOXES_FIXED96_LENGTH_DIFFERENCE"
INTENT="STRICT_POSITIVE_VERTEX_INDEX3_MINUS_END_DECLARED_ONLY"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==88107,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(c.capture(r["independent_pre"])["status"]=="PASS"and r["root_bits"]==96 and r["root_calls"]==0,"parent_oracle_fixed96")
    a={v["id"]:v for v in c.capture(r["test_run"])["data"]["runs"]if v["id"].startswith("retained:")}
    raw=(ROOT/r["parent_receipt"]).read_bytes();need(sha(raw)==r["parent_sha256"],"length_parent_identity");lr=json.loads(raw)
    b={v["id"]:v for v in c.capture(lr["test_run"])["data"]["runs"]if v["id"].startswith("retained:")}
    need(set(a)==set(b)and len(a)==20,"closed_twenty_records")
    e={}
    for k in a:
        need(a[k]["request"]["parent_record_sha256"]==digest(b[k]),"same_length_parent_record")
        e[k]=dict(nominal=a[k],length=b[k])
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA;return e,pins

def zero_boxes():return dict(schema="DECLARED_INDEPENDENT_COORDINATE_BOXES_ONLY",points_BU=[[[0,1]for k in range(3)]for p in range(5)])

def selector(record,e,boxes):
    x=e[record]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        original_geometry_sha256=x["nominal"]["request"]["original_geometry_sha256"],
        relative_geometry_sha256=x["nominal"]["request"]["relative_geometry_sha256"],
        declared_boxes_sha256=digest(boxes),representation=REP,intent=INTENT)

def squared_box(delta,radii):
    intervals=[];lo=hi=F(0)
    for d,r in zip(delta,radii):
        a,b=d-r,d+r;lower=F(0)if a<=0<=b else min(a*a,b*b);upper=max(a*a,b*b)
        lo+=lower;hi+=upper;intervals.append(dict(delta_interval_BU=[pair(a),pair(b)],squared_interval_BU2=[pair(lower),pair(upper)]))
    return dict(coordinates=intervals,squared_interval_BU2=[pair(lo),pair(hi)])

def baseline():
    out=c.baseline();out.update(model=MODEL,representation=REP,CPU_native_executed=False,root_calls=0,conditional_difference_certified=False,
        optical_reference_certified=False,reference_scope="VERTEX_INDEX3_MINUS_END_SAME_GEOMETRY_NOT_OPTICAL_REFERENCE",difference_interval_BU=None,
        declared_uncertainty_only=True,correlation_assumed=False,parent_branches_unchanged=True,
        HOST_cost=dict(radii_validated=0,squared_box_bounds=0,L1_error_bounds=0,ratio_corner_divisions=0))
    return out

def _audit(model,q,declared_boxes,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e,declared_boxes)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];nr=x["nominal"]["result"];lr=x["length"]["result"]
        need(nr["status"]=="HOST_RATIONALIZED_LENGTH_DIFFERENCE_ONLY"and nr["difference_enclosure_verified"]is True and
            lr["status"]=="HOST_PAIR_LENGTH_ENCLOSURE_ONLY"and lr["length_enclosure_verified"]is True,"parent_STOP_not_rescued")
        rr=c.boxes(declared_boxes);out["HOST_cost"]["radii_validated"]=15
        g=lr["rows"][0]["original_geometry"];local=lr["rows"][0]["relative_geometry"]
        need(digest(g)==q["original_geometry_sha256"] and digest(local)==q["relative_geometry_sha256"],"geometry_identity")
        need(nr["rows"][0]["source_context"]==g["context"] and lr["rows"][0]["source_context"]==g["context"],"source_context_identity")
        pts=list(map(c.vector,[g["origin_BU"],g["end_BU"]]+g["triangle_BU"]))
        selected=nr["differences"][2];need(selected["point"]==3 and selected["reference_point"]==1,"closed_selected_vertex_end")
        target=tuple(pts[3][k]-pts[0][k]for k in range(3));ref=tuple(pts[1][k]-pts[0][k]for k in range(3))
        need(sum(v*v for v in target)==F(*selected["squared_BU2"])and sum(v*v for v in ref)==F(*selected["reference_squared_BU2"]),"ORIGINAL_squared_identity")
        tr=tuple(rr[0][k]+rr[3][k]for k in range(3));er=tuple(rr[0][k]+rr[1][k]for k in range(3))
        s=squared_box(target,tr);t=squared_box(ref,er);out["HOST_cost"]["squared_box_bounds"]=2
        ell,eref=sum(tr),sum(er);out["HOST_cost"]["L1_error_bounds"]=2
        nlo=F(*s["squared_interval_BU2"][0])-F(*t["squared_interval_BU2"][1])
        nhi=F(*s["squared_interval_BU2"][1])-F(*t["squared_interval_BU2"][0])
        A,B=map(lambda v:F(*v),selected["denominator_interval_BU"]);dlo=max(F(0),A-ell-eref);dhi=B+ell+eref
        diag=dict(selector=q,original_geometry=g,source_context=g["context"],declared_boxes=declared_boxes,target_point=3,reference_point=1,
            source_radius_BU=list(map(pair,rr[0])),target_delta_radii_BU=list(map(pair,tr)),reference_delta_radii_BU=list(map(pair,er)),
            target_square_box=s,reference_square_box=t,target_L1_error_BU=pair(ell),reference_L1_error_BU=pair(eref),
            numerator_interval_BU2=[pair(nlo),pair(nhi)],nominal_denominator_interval_BU=selected["denominator_interval_BU"],
            denominator_interval_BU=[pair(dlo),pair(dhi)],parent_record_sha256=digest(x),nominal_selected_record_sha256=digest(selected),
            scope="CONDITIONAL_ON_DECLARED_COORDINATE_BOXES_NO_AUTHENTICATION",SOURCE_error_charged_to_both_norms=True)
        out["diagnostics"]=[diag];need(dlo>0,"nonpositive_denominator_lower_NO_EPSILON")
        corners=[a/b for a in(nlo,nhi)for b in(dlo,dhi)];out["HOST_cost"]["ratio_corner_divisions"]=4
        lo,hi=min(corners),max(corners);diag.update(ratio_corners_BU=list(map(pair,corners)),conditional_difference_interval_BU=[pair(lo),pair(hi)])
        need(lo>0,"declared_boxes_do_not_certify_strict_positive_difference")
        out.update(status="HOST_CONDITIONAL_DECLARED_BOX_POSITIVE_DIFFERENCE_ONLY",rows=[diag],verified_queries=1,
            conditional_difference_certified=True,difference_interval_BU=[pair(lo),pair(hi)])
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request,declared_boxes):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,declared_boxes,e)
