"""Analytical RNE32/RNE64 position consumer; not hardware or optical evidence."""
from pathlib import Path
from fractions import Fraction as F
import json
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-hilo-reconstruct-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-HILO-INGRESS-HOST-001-CODEX.json"
PSHA="03dbb47ddec84ffec2ffbbac02f4f0467a9cefd8063b787a727bdfed8ebe7ec9"
CONSUMERS={"ANALYTICAL_RNE32":(32,24,-126,127,8),"ANALYTICAL_RNE64":(64,53,-1022,1023,11)}
INTENT="ROUNDED_POSITION_CONSUMER_ERROR_ONLY"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def power(e):return F(2)**e

def rounded(value,consumer):
    need(type(value)is F,"exact_fraction")
    need(type(consumer)is str and consumer in CONSUMERS,"explicit_consumer")
    bits,p,emin,emax,exbits=CONSUMERS[consumer]
    if value==0:return dict(word=0,center_BU=[0,1])
    sign=int(value<0);v=abs(value);e=v.numerator.bit_length()-v.denominator.bit_length()
    if v<power(e):e-=1
    need(emin<=e<=emax,"normal_RNE_domain")
    u=v*power(p-1-e);n,rem=divmod(u.numerator,u.denominator)
    if 2*rem>u.denominator or(2*rem==u.denominator and n%2):n+=1
    if n==2**p:n//=2;e+=1
    need(e<=emax,"RNE_overflow")
    center=(-1 if sign else 1)*F(n)*power(e-(p-1))
    word=(sign<<(bits-1))|((e+(2**(exbits-1)-1))<<(p-1))|(n-2**(p-1))
    return dict(word=word,center_BU=pair(center))

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(c.capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    e={x["id"]:x for x in c.capture(r["test_run"])["data"]["runs"]if x["id"].startswith("retained:")}
    need(len(e)==160 and sum(x["result"]["status"]=="HOST_POSITION_FRAME_MATCH_UNATTESTED"for x in e.values())==120,"closed_retained_grid")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins

def selector(record,consumer,e):
    x=e[record]
    return dict(record_id=record,consumer=consumer,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        geometry_sha256=x["request"]["geometry_sha256"],intent=INTENT)

def baseline():
    r=c.baseline();r.update(model=MODEL,consumer_error_derived=False,rounded_geometry=None,radii_BU=None,
        consumer_words=[],HOST_cost=dict(RNE_rounds=0,original_error_differences=0,new_separator_evaluations=0,cached_separator_reuses=0))
    return r

def _audit(model,q,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e and q["record_id"]!="__certificates__","closed_record")
        need(type(q.get("consumer"))is str and q["consumer"]in CONSUMERS,"explicit_consumer")
        expected=selector(q["record_id"],q["consumer"],e)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];parent=x["result"]
        need(parent["status"]=="HOST_POSITION_FRAME_MATCH_UNATTESTED"and parent["frame_verified"]is True,"parent_STOP_not_rescued")
        g=parent["received_geometry"];need(digest(g)==q["geometry_sha256"],"exact_received_original_identity")
        points=[g["origin_BU"],g["end_BU"]]+g["triangle_BU"];rr=[];pp=[];records=[]
        for i,point in enumerate(points):
            radii=[];centers=[]
            for j,value in enumerate(point):
                original=c.frac(value);r=rounded(original,q["consumer"]);out["HOST_cost"]["RNE_rounds"]+=1
                center=c.frac(r["center_BU"]);error=abs(center-original);out["HOST_cost"]["original_error_differences"]+=1
                r.update(point=i,coordinate=j,original_BU=value,error_abs_BU=pair(error));records.append(r)
                radii.append(pair(error));centers.append(r["center_BU"])
            pp.append(centers);rr.append(radii)
        geometry=dict(origin_BU=pp[0],end_BU=pp[1],triangle_BU=pp[2:],context=g["context"])
        diag=dict(selector=q,parent_frame_sha256=parent["frame_sha256"],original_geometry=g,
            rounded_geometry=geometry,coordinates=records,radii_BU=rr,arithmetic="ANALYTICAL_RNE_NORMAL_OR_ZERO_NO_FTZ_NO_HARDWARE")
        out["diagnostics"]=[diag]
        if geometry==g and all(F(*v)==0 for point in rr for v in point):
            # Retained receiver row has only certificate SHA; read its sealed encoding ancestor, never rerun it.
            cert=e["__certificates__"][q["record_id"]]
            need(cert["geometry"]==g and cert["radii_BU"]==rr and digest(cert)==parent["rows"][0]["separator_sha256"],"cached_certificate_identity")
            out["HOST_cost"]["cached_separator_reuses"]+=1;diag["separator_source"]="SEALED_PARENT_CERTIFICATE"
        else:
            out["HOST_cost"]["new_separator_evaluations"]+=1
            cert=c._bound(geometry,[tuple(F(*v)for v in point)for point in rr]);diag["separator_source"]="NEW_CONSUMER_ROUNDED_GEOMETRY"
        diag["separator"]=cert
        need(F(*cert["signed_best_gap_BU"])>0,"consumer_rounding_exhausts_separator")
        out.update(status="CPU_ROUNDED_POSITION_SEPARATION_ONLY",rows=[diag],verified_queries=1,
            clearance_lower_BU=cert["clearance_lower_BU"],consumer_error_derived=True,rounded_geometry=geometry,radii_BU=rr,
            consumer_words=[r["word"]for r in records])
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out

def evidence():
    e,pins=retained()
    # Verify ancestor through the already pinned parent receipt. No producer import/call.
    parent=json.loads((ROOT/PARENT).read_bytes());path=parent["parent_receipt"];raw=(ROOT/path).read_bytes()
    need(sha(raw)==parent["parent_sha256"]and pins[path]==parent["parent_sha256"],"encoding_ancestor_identity")
    r=json.loads(raw);records={x["id"]:x for x in c.capture(r["test_run"])["data"]["runs"]}
    certs={}
    for record,x in e.items():
        if x["result"]["status"]=="HOST_POSITION_FRAME_MATCH_UNATTESTED":
            original=records[x["request"]["record_id"]];d=original["result"]["rows"][0]
            need(digest(d["separator"])==x["result"]["rows"][0]["separator_sha256"],"sealed_ancestor_certificate")
            need(d["original_geometry"]==x["result"]["received_geometry"]and d["radii_BU"]==x["result"]["radii_BU"],"zero_original_error_cache")
            certs[record]=d["separator"]
    e["__certificates__"]=certs
    return e,pins

def audit(model,request):
    try:e,_=evidence()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,e)
