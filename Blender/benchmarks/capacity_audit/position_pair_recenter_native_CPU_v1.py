"""CPU-native pair64 position differences; translated HOST certificate only."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import json,base64,struct,sys
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-pair-recenter-native-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-HILO-RECONSTRUCT-CPU-001-CODEX.json"
PSHA="58fa525be63ff825e708d31fad11b28582076420a6eefa69b3fff1394386ef54"
OPS="Blender/benchmarks/capacity_audit/oblique_pair64_difference_CPU_v1.py"
OSHA="902dfb1030a41bc6594806d0cef6d00729bbc11b4eade0adb96a23b3f688774e"
REP="NATIVE_CPU_PAIR64_POINT_MINUS_SOURCE_ORIGIN_KEEP_LIMBS"
INTENT="EXACT_PAIR_RECENTER_TRANSLATION_ONLY"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def subtract(a,b):
    need(sha((ROOT/OPS).read_bytes())==OSHA,"pinned_native_graph")
    need((sys.float_info.radix,sys.float_info.mant_dig,sys.float_info.max_exp,sys.float_info.min_exp)==(2,53,1024,-1021),"binary64_CPU_format")
    import oblique_pair64_difference_CPU_v1 as ops
    trace=dict(nodes=[],eft=[])
    try:h,l=ops.native_difference(a,b,trace)
    except(ValueError,TypeError)as ex:
        return dict(status="STOP",reason=str(ex),trace=trace,native_RN64_operations=len(trace["nodes"]),
            exact_pair_difference=False,CPU_native_executed=bool(trace["nodes"]),GPU_executed=False)
    need(len(trace["nodes"])==26 and ops.word(h)==trace["nodes"][-6]["y"]and ops.word(l)==trace["nodes"][-1]["y"],"graph_output_not_residual_reencoding")
    target=F.from_float(a[0])+F.from_float(a[1])-F.from_float(b[0])-F.from_float(b[1])
    decoded=F.from_float(h)+F.from_float(l);error=abs(decoded-target)
    return dict(status="CONTROL_ONLY",reason=None,hi_word_le_hex=ops.word(h),lo_word_le_hex=ops.word(l),decoded_debug_BU=pair(decoded),target_debug_BU=pair(target),
        error_abs_BU=pair(error),trace=trace,native_RN64_operations=26,exact_pair_difference=error==0,CPU_native_executed=True,GPU_executed=False)

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(r["code_doc_sha256"][OPS]==OSHA and c.capture(r["independent_pre"])["status"]=="PASS","parent_oracle_graph")
    scalar={x["id"]:x for x in c.capture(r["test_run"])["data"]["runs"]}
    p=r["parent_receipt"];raw=(ROOT/p).read_bytes();need(sha(raw)==r["parent_sha256"],"ingress_identity");ig=json.loads(raw)
    rows={x["id"]:x for x in c.capture(ig["test_run"])["data"]["runs"]if x["id"].startswith("retained:")}
    p=ig["parent_receipt"];raw=(ROOT/p).read_bytes();need(sha(raw)==ig["parent_sha256"],"encoding_identity");enc=json.loads(raw)
    encrows={x["id"]:x for x in c.capture(enc["test_run"])["data"]["runs"]}
    names=[]
    for plane in("xy","xz","yz","tilted"):
        names+=["retained:"+mode+":synthetic:"+plane+":0:"+case for mode,case in
            (("HOST_HILO32","outside_2m60"),("HOST_SINGLE32","outside_2m60"),("HOST_HILO32","before"))]
    names+=sorted(k for k in rows if k.startswith("retained:HOST_HILO32:sealed:"))
    need(len(names)==20 and len(set(names))==20,"closed_twenty_records")
    e={}
    for name in names:
        x=rows[name];certificate=None
        if x["result"]["status"]=="HOST_POSITION_FRAME_MATCH_UNATTESTED":
            d=encrows[x["request"]["record_id"]]["result"]["rows"][0]
            need(d["original_geometry"]==x["result"]["received_geometry"]and all(v==[0,1]for p in d["radii_BU"]for v in p),"exact_original_encoding_only")
            certificate=d["separator"];need(digest(certificate)==x["result"]["rows"][0]["separator_sha256"],"cached_certificate_identity")
        e[name]=dict(ingress=x,scalar_RNE64=scalar["ANALYTICAL_RNE64:"+name],certificate=certificate)
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins

def selector(record,e):
    x=e[record]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        geometry_sha256=x["ingress"]["request"]["geometry_sha256"],native_graph_sha256=OSHA,representation=REP,intent=INTENT)

def word32(w):
    ex=(w>>23)&255;mant=w&0x7fffff;need(ex!=255 and(ex!=0 or mant==0),"normal_or_zero_word")
    if ex==0:return F(0)
    return(-1 if w>>31 else 1)*F((1<<23)+mant)*F(2)**(ex-150)

def translate(cert,g,origin):
    z=deepcopy(cert);z["geometry"]=g
    for row in z["axes"]:
        shift=sum((F(*a)*F(*b)for a,b in zip(row["axis_L1"],origin)),F(0))
        row["centers"]=[pair(F(*v)-shift)for v in row["centers"]]
        for key in("segment_projection","triangle_projection"):row[key]=[pair(F(*v)-shift)for v in row[key]]
    return z

def baseline():
    r=c.baseline();r.update(model=MODEL,CPU_native_executed=False,exact_pair_recenter_verified=False,relative_geometry=None,
        output_pairs=[],HOST_cost=dict(word32_widens=0,pair_differences=0,translated_certificates=0),scalar_RNE64_branch_preserved=True)
    return r

def _audit(model,q,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e);need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];ig=x["ingress"];r=ig["result"]
        need(r["status"]=="HOST_POSITION_FRAME_MATCH_UNATTESTED"and r["frame_verified"]is True,"ingress_STOP_not_rescued")
        need(ig["request"]["mode"]=="HOST_HILO32","explicit_hilo_input")
        g=r["received_geometry"];need(digest(g)==q["geometry_sha256"],"original_geometry_identity")
        packet=base64.b64decode(ig["frame_base64"],validate=True)
        need(len(packet)==232 and sha(packet)==r["frame_sha256"]and sha(packet[112:])==r["packet_sha256"],"sealed_frame_bytes")
        words=struct.unpack("<30I",packet[112:]);exact=list(map(word32,words))
        points=[g["origin_BU"],g["end_BU"]]+g["triangle_BU"]
        need(all(exact[2*i]+exact[2*i+1]==F(*points[i//3][i%3])for i in range(15)),"all_original_limbs_before_native")
        values=[]
        for w,v in zip(words,exact):
            f=struct.unpack("<f",struct.pack("<I",w))[0];need(F.from_float(f)==v,"exact_widen32_to_CPU64");values.append(f)
        out["HOST_cost"]["word32_widens"]=30
        origin=g["origin_BU"];records=[];relative=[]
        diag=dict(selector=q,original_geometry=g,frame_origin_BU=origin,coordinates=records,
            scalar_RNE64_retained_status=x["scalar_RNE64"]["result"]["status"],
            scalar_RNE64_retained_record_sha256=digest(x["scalar_RNE64"]),input_frame_sha256=r["frame_sha256"])
        out["diagnostics"]=[diag]
        for i in range(15):
            d=subtract(tuple(values[2*i:2*i+2]),tuple(values[2*(i%3):2*(i%3)+2]))
            out["RN64_operations"]+=d["native_RN64_operations"];out["HOST_cost"]["pair_differences"]+=1;out["CPU_native_executed"]=out["CPU_native_executed"]or d["CPU_native_executed"]
            d.update(point=i//3,coordinate=i%3);records.append(d)
            need(d["status"]!="STOP","native_graph_STOP:"+str(d["reason"]))
            target=F(*points[i//3][i%3])-F(*origin[i%3]);need(F(*d["target_debug_BU"])==target,"original_frame_difference")
            need(d["exact_pair_difference"]is True,"inexact_difference_cannot_use_translation_cache")
            relative.append(d["decoded_debug_BU"])
        pp=[relative[i:i+3]for i in range(0,15,3)]
        relg=dict(origin_BU=pp[0],end_BU=pp[1],triangle_BU=pp[2:],context=dict(original_context=g["context"],
            coordinate_frame=REP,frame_origin_BU=origin,original_geometry_sha256=digest(g)))
        cert=x["certificate"];need(cert["geometry"]==g and all(v==[0,1]for p in cert["radii_BU"]for v in p),"zero_boxes_only")
        local=translate(cert,relg,origin);need(F(*local["signed_best_gap_BU"])>0,"positive_translation_separator")
        out["HOST_cost"]["translated_certificates"]+=1;diag.update(relative_geometry=relg,translated_separator=local,
            original_certificate_sha256=digest(cert),all_original_error_radii_zero=True)
        pairs=[dict(point=d["point"],coordinate=d["coordinate"],hi_word_le_hex=d["hi_word_le_hex"],lo_word_le_hex=d["lo_word_le_hex"])for d in records]
        out.update(status="CPU_POSITION_PAIR_RECENTER_ONLY",rows=[diag],verified_queries=1,clearance_lower_BU=local["clearance_lower_BU"],
            exact_pair_recenter_verified=True,relative_geometry=relg,output_pairs=pairs)
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError,struct.error)as ex:out["reason"]=str(ex)
    return out

def audit(model,request):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,e)
