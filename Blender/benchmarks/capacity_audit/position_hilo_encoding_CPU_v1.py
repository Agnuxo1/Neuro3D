"""HOST position encoding proof, not a GPU hit ABI or scene inference."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-hilo-encoding-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-COPLANAR-CLEARANCE-CPU-001-CODEX.json"
PSHA="7b17d4f38db66357ff6c8589325283e1b5a85e041304d4233179a93a6013c9e1"
MODES=("HOST_SINGLE32","HOST_HILO32")
INTENT="DERIVED_POSITION_ENCODING_ERROR_ONLY"
def need(v,s):
    if not v:raise ValueError(s)
def power(e):return F(2**e)if e>=0 else F(1,2**(-e))
def rn32(value):
    need(type(value)is F,"exact_HOST_fraction")
    if value==0:return 0
    sign=0x80000000 if value<0 else 0;q=abs(value)
    e=q.numerator.bit_length()-q.denominator.bit_length()
    if q<power(e):e-=1
    need(-126<=e<=127,"normal_RNE32_domain")
    scaled=q*power(23-e);m,rem=divmod(scaled.numerator,scaled.denominator)
    if 2*rem>scaled.denominator or(2*rem==scaled.denominator and m%2):m+=1
    if m==2**24:m//=2;e+=1
    need(e<=127,"RNE32_overflow")
    return sign|((e+127)<<23)|(m-2**23)
def decode(word):
    need(type(word)is int and 0<=word<2**32,"word32")
    exp=(word>>23)&255;mant=word&0x7fffff
    need(exp!=255 and(exp!=0 or mant==0),"normal_or_zero_word")
    if exp==0:return F(0)
    return (-1 if word>>31 else 1)*F(2**23+mant)*power(exp-127-23)
def encode(value,mode,cost):
    need(type(mode)is str and mode in MODES,"explicit_mode")
    cost["RN32_rounds"]+=1;hi=rn32(value);hh=decode(hi);cost["exact_decodes"]+=1
    lo=None;center=hh
    if mode=="HOST_HILO32":
        cost["exact_residuals"]+=1;residual=value-hh;cost["RN32_rounds"]+=1
        lo=rn32(residual);ll=decode(lo);cost["exact_decodes"]+=1;cost["exact_reconstructions"]+=1;center=hh+ll
    return dict(original_BU=c.pair(value),hi_bits=hi,lo_bits=lo,center_BU=c.pair(center),error_abs_BU=c.pair(abs(center-value)))
def retained():
    raw=(ROOT/PARENT).read_bytes();need(c.sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(c.sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(c.capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    finite=(ROOT/r["parent_receipt"]).read_bytes();need(c.sha(finite)==r["parent_sha256"],"finite_parent_identity")
    fr=json.loads(finite);data=c.capture(fr["test_run"])["data"]
    original={x["id"]:x for x in data["runs"]if x["result"]["status"]=="CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY"or x["id"].startswith("sealed:")}
    zero={x["request"]["case"]:x for x in c.capture(r["test_run"])["data"]["runs"]if x["id"].startswith(("zero:","contact_zero:"))}
    need(len(original)==len(zero)==80 and set(original)==set(zero),"closed_retained_grid")
    e={}
    for case,x in original.items():
        z=zero[case];need(z["request"]["parent_record_sha256"]==c.digest(x)and z["request"]["geometry_sha256"]==c.digest(c.geometry(x)),"sealed_parent_binding")
        need(all(F(*v)==0 for point in z["uncertainty"]["points_BU"]for v in point),"sealed_zero_boxes")
        need(z["result"]["status"]in("CPU_CONDITIONAL_DECLARED_BOX_SEPARATION_ONLY","STOP"),"sealed_zero_status")
        e[case]=dict(original=x,zero=z)
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins
def selector(case,mode,e):
    return dict(case=case,mode=mode,parent_receipt_sha256=PSHA,parent_record_sha256=c.digest(e[case]),
        geometry_sha256=c.digest(c.geometry(e[case]["original"])),intent=INTENT)
def cost():
    return dict(RN32_rounds=0,exact_decodes=0,exact_residuals=0,exact_reconstructions=0,new_separator_evaluations=0,cached_separator_reuses=0)
def baseline():
    out=c.baseline();out.update(model=MODEL,packet_words=[],packet_sha256=None,encoding_error_derived=False,HOST_cost=cost());return out
def _audit(model,q,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("case"))is str and q["case"]in e,"closed_case")
        need(type(q.get("mode"))is str and q["mode"]in MODES,"explicit_mode")
        expected=selector(q["case"],q["mode"],e);need(q==expected and set(q)==set(expected)and all(type(q[k])is str for k in q),"closed_selector_identity")
        x=e[q["case"]];need(x["original"]["result"]["status"]=="CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY","parent_contact_STOP")
        g=c.geometry(x["original"]);points=[g["origin_BU"],g["end_BU"]]+g["triangle_BU"]
        encoded=[];centers=[];errors=[];words=[]
        for i,point in enumerate(points):
            pp=[];rr=[]
            for j,value in enumerate(point):
                item=encode(c.frac(value),q["mode"],out["HOST_cost"]);item.update(point=i,coordinate=j);encoded.append(item)
                pp.append(item["center_BU"]);rr.append(item["error_abs_BU"]);words.append(item["hi_bits"])
                if item["lo_bits"]is not None:words.append(item["lo_bits"])
            centers.append(pp);errors.append(rr)
        encoded_g=dict(origin_BU=centers[0],end_BU=centers[1],triangle_BU=centers[2:],context=g["context"])
        packet=struct.pack("<"+"I"*len(words),*words)
        diagnostic=dict(selector=q,original_geometry=g,encoded_geometry=encoded_g,coordinates=encoded,radii_BU=errors,
            packet_words=words,packet_sha256=c.sha(packet),packet_bytes=len(packet),HOST_cost=out["HOST_cost"],
            guarantee="HOST_ENCODING_OF_DECLARED_ORIGINAL_ONLY",physical_uncertainty_authenticated=False)
        out["diagnostics"]=[diagnostic]
        if encoded_g==g and all(F(*v)==0 for point in errors for v in point):
            zero=x["zero"]["result"];need(zero["status"]=="CPU_CONDITIONAL_DECLARED_BOX_SEPARATION_ONLY"and len(zero["rows"])==1,"cached_zero_admission")
            cert=zero["rows"][0];need(cert["geometry"]==g and cert["radii_BU"]==errors,"exact_cache_identity")
            out["HOST_cost"]["cached_separator_reuses"]+=1;diagnostic["separator_source"]="SEALED_ZERO_CAPTURE"
        else:
            out["HOST_cost"]["new_separator_evaluations"]+=1
            cert=c._bound(encoded_g,[tuple(F(*v)for v in rr)for rr in errors]);diagnostic["separator_source"]="NEW_ENCODED_GEOMETRY_BOUND"
        diagnostic["separator"]=cert
        need(F(*cert["signed_best_gap_BU"])>0,"encoding_exhausts_separator")
        out.update(status="HOST_POSITION_ENCODING_SEPARATION_ONLY",rows=[diagnostic],verified_queries=1,
            clearance_lower_BU=cert["clearance_lower_BU"],packet_words=words,packet_sha256=c.sha(packet),encoding_error_derived=True)
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError,struct.error)as ex:out["reason"]=str(ex)
    return out
def audit(model,request):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _audit(model,request,e)
