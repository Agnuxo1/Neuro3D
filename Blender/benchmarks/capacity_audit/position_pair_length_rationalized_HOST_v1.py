"""Separate HOST identity for root differences; sealed fixed96 roots unchanged."""
from pathlib import Path
from fractions import Fraction as F
import json
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-pair-length-rationalized-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PAIR-LENGTH-HOST-001-CODEX.json"
PSHA="14018465082053924e3b0dc572304fb782ffffeb31387e81570339bf86efa20a"
REP="EXACT_HOST_RATIONALIZED_LENGTH_DIFFERENCE_FIXED96"
INTENT="SAME_GEOMETRY_END_DIFFERENCE_NOT_OPTICAL_REFERENCE"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def rational(v):
    need(type(v)is list and len(v)==2 and all(type(x)is int for x in v),"typed_rational")
    need(v[1]>0 and max(abs(v[0]).bit_length(),v[1].bit_length())<=256,"bounded_rational_256")
    return F(*v)

def check_root(s,v):
    need(s>=0 and type(v)is list and len(v)==2,"root_interval")
    a,b=map(rational,v);step=F(1,2**96)
    need(a>=0 and(a*2**96).denominator==1 and a*a<=s and(a+step)**2>s,"minimal_fixed96_root_lower")
    need(b==(a if a*a==s else a+step),"minimal_fixed96_root_upper")
    return a,b

def rationalized(squared,reference_squared,root_interval,reference_interval):
    out=dict(status="STOP",reason=None,interval_BU=None,numerator_BU2=None,denominator_interval_BU=None,
        exact_divisions=0,algebraic_zero_cases=0,root_certificates_checked=0,sign=None,GPU_executed=False)
    try:
        s,t=rational(squared),rational(reference_squared)
        a,b=check_root(s,root_interval);out["root_certificates_checked"]+=1
        x,y=check_root(t,reference_interval);out["root_certificates_checked"]+=1
        n=s-t;A,B=a+x,b+y
        out.update(numerator_BU2=pair(n),denominator_interval_BU=[pair(A),pair(B)])
        if n==0:
            lo=hi=F(0);out["algebraic_zero_cases"]=1;out["sign"]="ZERO_IDENTICAL_SQUARED_NORMS"
        else:
            need(A>0,"nonpositive_denominator_lower_NO_EPSILON")
            if n>0:lo,hi=n/B,n/A;sign="POSITIVE"
            else:lo,hi=n/A,n/B;sign="NEGATIVE"
            out["exact_divisions"]=2;out["sign"]=sign
            need(lo<=hi and(lo>0 if n>0 else hi<0),"rationalized_sign")
        out.update(status="HOST_RATIONALIZED_DIFFERENCE_ONLY",interval_BU=[pair(lo),pair(hi)])
    except(ValueError,TypeError,IndexError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==68322,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(c.capture(r["independent_pre"])["status"]=="PASS" and r["fixed96_unresolved"]==3 and r["root_bits"]==96,"parent_oracle_fixed96")
    runs=c.capture(r["test_run"])["data"]["runs"];e={x["id"]:x for x in runs if x["id"].startswith("retained:")}
    need(len(e)==20 and sum(x["result"]["status"]=="HOST_PAIR_LENGTH_ENCLOSURE_ONLY"for x in e.values())==8,"closed_twenty_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA;return e,pins

def selector(record,e):
    x=e[record]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        original_geometry_sha256=x["request"]["original_geometry_sha256"],relative_geometry_sha256=x["request"]["relative_geometry_sha256"],
        representation=REP,intent=INTENT)

def baseline():
    r=c.baseline();r.update(model=MODEL,representation=REP,CPU_native_executed=False,root_calls=0,
        difference_enclosure_verified=False,optical_reference_certified=False,reference_scope="SAME_GEOMETRY_END_NOT_OPTICAL_REFERENCE",
        differences=[],parent_interval_branch_unchanged=True,
        HOST_cost=dict(original_squared_norms=0,parent_roots_checked=0,rationalized_differences=0,helper_roots_checked=0,exact_divisions=0,algebraic_zero_cases=0))
    return r

def _audit(model,q,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"]
        need(r["status"]=="HOST_PAIR_LENGTH_ENCLOSURE_ONLY" and r["length_enclosure_verified"]is True,"parent_STOP_not_rescued")
        need(r["reference_scope"]=="SAME_GEOMETRY_END_LENGTH_NOT_OPTICAL_REFERENCE" and r["optical_reference_certified"]is False,"reference_scope")
        need(len(r["rows"])==len(r["diagnostics"])==1 and r["rows"]==r["diagnostics"],"one_parent_diagnostic")
        d=r["rows"][0];g=d["original_geometry"];local=d["relative_geometry"]
        need(digest(g)==q["original_geometry_sha256"] and digest(local)==q["relative_geometry_sha256"],"geometry_identity")
        points=list(map(c.vector,[g["origin_BU"],g["end_BU"]]+g["triangle_BU"]));o=points[0]
        vv=[[pair(p[k]-o[k])for k in range(3)]for p in points]
        context=dict(original_context=g["context"],coordinate_frame="NATIVE_CPU_PAIR64_POINT_MINUS_SOURCE_ORIGIN_KEEP_LIMBS",
            frame_origin_BU=g["origin_BU"],original_geometry_sha256=digest(g))
        need(local==dict(origin_BU=vv[0],end_BU=vv[1],triangle_BU=vv[2:],context=context)and d["source_context"]==g["context"],"explicit_source_context_translation")
        need(len(r["lengths"])==len(r["relative_lengths"])==4 and d["lengths"]==r["lengths"]and d["relative_lengths"]==r["relative_lengths"],"all_four_lengths")
        for i,z in enumerate(r["lengths"],1):
            need(type(z["point"])is int and z["point"]==i and type(z["from_point"])is int and z["from_point"]==0
                and type(z["fractional_bits"])is int and z["fractional_bits"]==96,"closed_length_order_fixed96")
            delta=[points[i][k]-o[k]for k in range(3)];s=sum(v*v for v in delta);out["HOST_cost"]["original_squared_norms"]+=1
            need([rational(v)for v in z["delta_BU"]]==delta and rational(z["squared_BU2"])==s,"squared_norm_against_ORIGINAL")
            a,b=check_root(s,z["length_interval_BU"]);out["HOST_cost"]["parent_roots_checked"]+=1
            need(rational(z["width_BU"])==b-a,"root_width")
        reference=r["lengths"][0];rows=[]
        for z in r["lengths"]:
            v=rationalized(z["squared_BU2"],reference["squared_BU2"],z["length_interval_BU"],reference["length_interval_BU"])
            out["HOST_cost"]["rationalized_differences"]+=1
            for dst,src in(("helper_roots_checked","root_certificates_checked"),("exact_divisions","exact_divisions"),("algebraic_zero_cases","algebraic_zero_cases")):out["HOST_cost"][dst]+=v[src]
            need(v["status"]=="HOST_RATIONALIZED_DIFFERENCE_ONLY","rationalized_STOP:"+str(v["reason"]))
            v.update(point=z["point"],reference_point=1,old_interval_retained=r["relative_lengths"][z["point"]-1],
                squared_BU2=z["squared_BU2"],reference_squared_BU2=reference["squared_BU2"])
            rows.append(v)
        diag=dict(selector=q,source_context=g["context"],original_geometry_sha256=digest(g),relative_geometry_sha256=digest(local),
            parent_record_sha256=digest(x),differences=rows,old_length_branch_record_sha256=digest(x))
        out.update(status="HOST_RATIONALIZED_LENGTH_DIFFERENCE_ONLY",rows=[diag],diagnostics=[diag],verified_queries=1,
            difference_enclosure_verified=True,differences=rows)
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,e)
