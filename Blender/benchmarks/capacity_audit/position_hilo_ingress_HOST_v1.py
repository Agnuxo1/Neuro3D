"""Opt-in sealed-position frame receiver; HOST exact sums, never GPU ingress."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-hilo-ingress-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-HILO-ENCODING-CPU-001-CODEX.json"
PSHA="db093b5430ce3ec6e43e748e2d5cf839b0bfaea6369a9d8528fbe7dfd3a41b33"
MAGIC=b"N3DPHI01"
HEADER_BYTES=112
MODES={"HOST_SINGLE32":(1,15),"HOST_HILO32":(2,30)}
INTENT="SEALED_POSITION_PACKET_HOST_RECEIVE_ONLY"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(c.capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    runs=c.capture(r["test_run"])["data"]["runs"];e={}
    for x in runs:
        if x["id"].startswith(tuple(mode+":" for mode in MODES)):
            need(x["request"]["mode"]in MODES,"parent_mode")
            need(x["result"]["status"]in("HOST_POSITION_ENCODING_SEPARATION_ONLY","STOP"),"parent_status")
            need(x["id"]not in e,"parent_unique");e[x["id"]]=x
    need(len(e)==160 and sum(x["result"]["status"]!="STOP"for x in e.values())==120,"closed_retained_grid")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins

def selector(record,e):
    x=e[record];q=x["request"]
    return dict(record_id=record,mode=q["mode"],parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        geometry_sha256=q["geometry_sha256"],intent=INTENT)

def header(q):
    mode,count=MODES[q["mode"]]
    return MAGIC+struct.pack("<II",mode,count)+b"".join(bytes.fromhex(q[k])for k in
        ("parent_receipt_sha256","parent_record_sha256","geometry_sha256"))

def frame(record,e):
    x=e[record];r=x["result"];need(r["status"]=="HOST_POSITION_ENCODING_SEPARATION_ONLY","parent_STOP_no_frame")
    q=selector(record,e);w=r["packet_words"];need(len(w)==MODES[q["mode"]][1],"sealed_extent")
    return header(q)+struct.pack("<"+"I"*len(w),*w)

def word_value(w):
    ex=(w>>23)&255;mant=w&0x7fffff
    need(ex!=255 and(ex!=0 or mant==0),"normal_or_zero_word")
    if ex==0:return F(0)
    n=(1<<23)+mant;power=ex-150
    return (-1 if w>>31 else 1)*F(n*(2**power)if power>=0 else n,1 if power>=0 else 2**(-power))

def baseline():
    r=c.baseline();r.update(model=MODEL,frame_verified=False,received_geometry=None,radii_BU=None,
        frame_sha256=None,packet_sha256=None,HOST_cost=dict(exact_word_decodes=0,exact_reconstructions=0,
            original_error_differences=0,frame_matches=0,certificate_reuses=0))
    return r

def _receive(model,q,raw,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e);need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];parent=x["result"]
        need(parent["status"]=="HOST_POSITION_ENCODING_SEPARATION_ONLY","parent_STOP_not_rescued")
        mode,count=MODES[q["mode"]]
        need(type(raw)is bytes and len(raw)==HEADER_BYTES+4*count,"strict_frame_type_extent")
        need(raw[:HEADER_BYTES]==header(q),"explicit_header_original_record_mode")
        words=list(struct.unpack("<"+"I"*count,raw[HEADER_BYTES:]))
        # Check all finite/normal-or-zero word classifications and all byte identities BEFORE scalar decode.
        need(all(((w>>23)&255)!=255 and(((w>>23)&255)!=0 or(w&0x7fffff)==0)for w in words),"all_normal_or_zero_words")
        need(raw==frame(q["record_id"],e),"sealed_payload_bytes")
        out["HOST_cost"]["frame_matches"]+=1
        diag=parent["rows"][0];g=diag["original_geometry"]
        original=[g["origin_BU"],g["end_BU"]]+g["triangle_BU"];centers=[];errors=[];decoded=[]
        stride=1 if mode==1 else 2
        for i in range(15):
            hi=word_value(words[stride*i]);out["HOST_cost"]["exact_word_decodes"]+=1;value=hi
            if stride==2:
                lo=word_value(words[2*i+1]);out["HOST_cost"]["exact_word_decodes"]+=1
                value+=lo;out["HOST_cost"]["exact_reconstructions"]+=1
            error=abs(value-c.frac(original[i//3][i%3]));out["HOST_cost"]["original_error_differences"]+=1
            decoded.append(dict(point=i//3,coordinate=i%3,center_BU=pair(value),error_abs_BU=pair(error)))
            centers.append(pair(value));errors.append(pair(error))
        points=[centers[i:i+3]for i in range(0,15,3)];radii=[errors[i:i+3]for i in range(0,15,3)]
        received=dict(origin_BU=points[0],end_BU=points[1],triangle_BU=points[2:],context=g["context"])
        need(digest(g)==q["geometry_sha256"] and received==diag["encoded_geometry"]and radii==diag["radii_BU"],"decoded_original_error_identity")
        cert=diag["separator"]
        need(cert["geometry"]==received and cert["radii_BU"]==radii and F(*cert["signed_best_gap_BU"])>0,"sealed_separator_identity")
        out["HOST_cost"]["certificate_reuses"]+=1
        out.update(status="HOST_POSITION_FRAME_MATCH_UNATTESTED",rows=[dict(selector=q,decoded_coordinates=decoded,
            separator_sha256=digest(cert))],verified_queries=1,clearance_lower_BU=cert["clearance_lower_BU"],
            frame_verified=True,received_geometry=received,radii_BU=radii,frame_sha256=sha(raw),packet_sha256=sha(raw[HEADER_BYTES:]))
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError,struct.error)as ex:out["reason"]=str(ex)
    return out

def receive(model,request,raw_frame):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _receive(model,request,raw_frame,e)
