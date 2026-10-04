"""Opt-in HOST hi-lo32 wire for retained new CPU trace outputs.
Exact rational residuals are HOST descriptors, not IEEE32 arithmetic or phase bounds.
"""
from pathlib import Path
from fractions import Fraction as F
import struct,json,hashlib
import oblique_scene_geometry32_ingress_HOST_v1 as ingress
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-trace-output-hilo32-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-GEOMETRY32-TRACE-RATIONAL-CPU-001-CODEX.json"
PSHA="509f6a032fc3391a6027f8b6a62fefd3a7eb8b7d81bfcdd091b493bdb32aab23"
HEADER=struct.Struct("<8s6I")
MAGIC=b"N3OH32V1"
SCOPE="HOST_WIRE_ONLY_EXACT_CONTACT_GATE_ZERO_LOSS_NO_PHASE"
def need(ok,msg):
 if not ok:raise ValueError(msg)
def pair(v):return [v.numerator,v.denominator]
def digest(x):return ingress.digest(x)
def retained():
 raw=(ROOT/PARENT).read_bytes();need(hashlib.sha256(raw).hexdigest()==PSHA and len(raw)==102298,"parent_seal")
 p=json.loads(raw);pins=dict(p["code_doc_sha256"]);need(len(pins)==347,"pins347")
 for s,h in pins.items():need(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h,"dependency:"+s)
 need(ingress.capture(p["independent_after_format_repair"])["status"]=="PASS","parent_final_oracle")
 d=ingress.capture(p["test_run"]);need(d["status"]=="PASS","parent_suite")
 e={a["id"]:a["result"]for a in d["evidence"]["positive"]+d["evidence"]["upstream"]}
 admitted={a["id"]for a in d["evidence"]["positive"]};need(len(e)==44 and len(admitted)==6,"closed_original_selection")
 pins[PARENT]=PSHA;return e,admitted,pins
def selector(k,e):
 c=e[k];return dict(model=MODEL,case=k,source_ids=["S0","S1"],trace_result_sha256=digest(c),parent_receipt_sha256=PSHA)
def base():
 return dict(model=MODEL,status="STOP_INPUT",reason=None,packet=None,transport_verified=False,
  exact_contact_allowed=False,source_exact_contact_allowed=[False,False],
  cast_attempts=0,HOST_float64_conversion_attempts=0,HOST_struct_float32_cast_attempts=0,integer_word_decodes=0,
  new_intersections=0,new_guard_calls=0,new_root_calls=0,old_numeric_replays=0,
  computed_hilo_collapse_allowed=False,native_IEEE_RN_graph_certified=False,GPU_used=False,Bpy_used=False,RT_used=False,
  scene_authenticated=False,phase_certified=False,physical_field_certified=False,phase_error_bound=None,
  SOURCE_merged=False,full_costs="UNKNOWN_NOT_ZERO")
def layout(c):
 need(c["status"]=="CPU_RATIONAL_DECLARED_TWO_SEGMENT_TRACE_ONLY"and c["declared_two_segment_trace_certified"]is True,"admitted_CPU_trace")
 need([s["source_id"]for s in c["source_results"]]==["S0","S1"],"literal_SOURCE_order")
 out=[]
 def field(sid,path,unit,v):
  ingress.rat(v);out.append(dict(path=sid+"/"+path,unit=unit,original_rational=v))
 for s in c["source_results"]:
  sid=s["source_id"];need(s["status"]=="CPU_DECLARED_TERMINAL_CLEAR_ONLY","SOURCE_trace_clear")
  h=s["primary_hit"];field(sid,"primary_hit/parameter","original_primary_direction_parameter",h["parameter"])
  for key,unit in (("point_BU","BU"),("barycentric","dimensionless")):
   need(type(h[key])is list and len(h[key])==3,"hit_vector3")
   for j,v in enumerate(h[key]):field(sid,"primary_hit/"+key+"/"+str(j),unit,v)
  for j,v in enumerate(s["reflected_direction"]):field(sid,"reflected_direction/"+str(j),"original_direction_parameter",v)
  need(len(s["reflected_direction"])==3 and len(s["segment_endpoints_BU"])==3,"closed_ray_vectors")
  for i,point in enumerate(s["segment_endpoints_BU"]):
   need(len(point)==3,"point3")
   for j,v in enumerate(point):field(sid,"segment_endpoints_BU/"+str(i)+"/"+str(j),"BU",v)
  need(len(s["segment_squared_BU2"])==2,"segments2")
  for j,v in enumerate(s["segment_squared_BU2"]):field(sid,"segment_squared_BU2/"+str(j),"BU2",v)
 need(len(out)==42,"closed42_fields");return out
def provenance(k,c):
 return dict(model=MODEL,scope=SCOPE,case=k,parent_receipt_sha256=PSHA,trace_result_sha256=digest(c),
  scene_sha256=c["scene_sha256"],query_sha256=c["query_sha256"],input_buffer_sha256=c["input_buffer_sha256"],
  source_ids=["S0","S1"],SOURCE_coverage=[dict(source_id=s["source_id"],primary_primitive_id=s["primary_hit"]["primitive_id"],
    primary_ids=[v["primitive_id"]for v in s["primary_rows"]],secondary_ids=[v["primitive_id"]for v in s["secondary_rows"]],
    coverage_sha256=digest(dict(primary=s["primary_rows"],secondary=s["secondary_rows"],decisions=s["terminal_decisions"])))for s in c["source_results"]],
  endian="little",header_bytes=32,pair_field_count=42,source_field_count=21,word_count=84,
  normal_or_positive_zero_only=True,zero_exact_contact_budget=[0,1],
  computed_hilo_collapse_allowed=False,phase_bound_in_packet=False,scene_authentication=False)
def cast(q,r):
 r["cast_attempts"]+=1;r["HOST_float64_conversion_attempts"]+=1;v=float(q)
 r["HOST_struct_float32_cast_attempts"]+=1;w=struct.unpack("<I",struct.pack("<f",v))[0]
 r["integer_word_decodes"]+=1;return w,ingress.decode_word(w)
def descriptor(f,words,hi,lo):
 original=ingress.rat(f["original_rational"]);value=hi+lo;err=value-original
 return dict(**f,word_pair=words,decoded_pair_value=pair(value),signed_error=pair(err),radius=pair(abs(err)),drop_lo_signed_error=pair(hi-original))
def emit(k,c):
 r=base()
 try:
  fs=layout(c);words=[];desc=[]
  for f in fs:
   q=ingress.rat(f["original_rational"]);wh,hi=cast(q,r);wl,lo=cast(q-hi,r)
   words.extend((wh,wl));desc.append(descriptor(f,[wh,wl],hi,lo))
  source_exact=[all(d["radius"]==[0,1]for d in desc[i:i+21])for i in (0,21)]
  b=HEADER.pack(MAGIC,1,2,21,42,84,0)+struct.pack("<84I",*words)
  meta=provenance(k,c);meta.update(fields=desc,source_exact_contact_allowed=source_exact,exact_contact_allowed=all(source_exact),
    buffer_sha256=hashlib.sha256(b).hexdigest(),buffer_bytes=len(b))
  packet=dict(manifest=meta,manifest_sha256=digest(meta),buffer_hex=b.hex())
  r.update(status="HOST_TRACE_OUTPUT_HILO32_WIRE_ONLY",transport_verified=True,packet=packet,
   exact_contact_allowed=all(source_exact),source_exact_contact_allowed=source_exact,
   exact_contact_status="EXACT_OUTPUT_FIELDS_ONLY"if all(source_exact)else "STOP_NONEXACT_TRACE_OUTPUT",
   nonexact_fields=[dict(path=d["path"],radius=d["radius"])for d in desc if d["radius"]!=[0,1]])
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error,RecursionError)as ex:r["reason"]=str(ex)
 return r
def parse(packet,k,c,reference):
 """Internal receiver; reference must be freshly emitted from pinned trace context.
Public validate_received builds that reference itself; no caller-supplied reference API.
"""
 r=base()
 try:
  fs=layout(c);need(type(packet)is dict and set(packet)=={"manifest","manifest_sha256","buffer_hex"},"closed_packet")
  need(type(packet["buffer_hex"])is str and len(packet["buffer_hex"])==736 and all(v in "0123456789abcdef"for v in packet["buffer_hex"]),"closed_wire_hex")
  need(packet["buffer_hex"]==reference["buffer_hex"],"sealed_reference_bytes")
  meta=packet["manifest"];ref=reference["manifest"];need(type(meta)is dict and set(meta)==set(ref),"closed_manifest")
  need(type(meta["fields"])is list and len(meta["fields"])==42,"bounded_fields")
  for f in meta["fields"]:
   need(type(f)is dict and set(f)=={"path","unit","original_rational","word_pair","decoded_pair_value","signed_error","radius","drop_lo_signed_error"},"closed_descriptor")
   need(type(f["path"])is str and len(f["path"])<=160 and type(f["unit"])is str and len(f["unit"])<=64,"bounded_descriptor_strings")
   for key in ("original_rational","decoded_pair_value","signed_error","radius","drop_lo_signed_error"):ingress.rat(f[key])
   need(type(f["word_pair"])is list and len(f["word_pair"])==2 and all(type(w)is int and 0<=w<2**32 for w in f["word_pair"]),"typed_pair_words")
  # Trusted reference derived from the original captured trace, not supplied by public caller.
  p=provenance(k,c)
  for key,val in p.items():need(digest(ref[key])==digest(val),"original_provenance:"+key)
  need(digest(meta)==packet["manifest_sha256"]==reference["manifest_sha256"]==digest(ref),"sealed_original_manifest")
  b=bytes.fromhex(packet["buffer_hex"]);need(HEADER.unpack_from(b)==(MAGIC,1,2,21,42,84,0),"header")
  need(hashlib.sha256(b).hexdigest()==meta["buffer_sha256"]and len(b)==meta["buffer_bytes"]==368,"wire_seal")
  actual=[];source_exact=[True,True]
  for i,f in enumerate(fs):
   wh,wl=struct.unpack_from("<2I",b,32+8*i);r["integer_word_decodes"]+=1;hi=ingress.decode_word(wh)
   r["integer_word_decodes"]+=1;lo=ingress.decode_word(wl);d=descriptor(f,[wh,wl],hi,lo)
   need(digest(d)==digest(meta["fields"][i]),"pair_error_or_original_field")
   if d["radius"]!=[0,1]:source_exact[i//21]=False
   actual.append(d)
  need(source_exact==meta["source_exact_contact_allowed"]and all(source_exact)is meta["exact_contact_allowed"],"derived_exact_contact_gate")
  r.update(status="HOST_RECEIVED_TRACE_HILO32_WIRE_VERIFIED_ONLY",transport_verified=True,
   exact_contact_allowed=all(source_exact),source_exact_contact_allowed=source_exact,
   exact_contact_status="EXACT_OUTPUT_FIELDS_ONLY"if all(source_exact)else "STOP_NONEXACT_TRACE_OUTPUT",
   decoded_fields=actual,buffer_sha256=meta["buffer_sha256"])
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error,RecursionError)as ex:r["reason"]=str(ex)
 return r
def evaluate(k,q,e,a,received=None):
 r=base()
 try:
  need(k in e,"known_case");expected=selector(k,e)
  need(type(q)is dict and set(q)==set(expected),"closed_selector")
  for key,val in expected.items():
   need(type(q[key])is type(val),"typed_selector")
   if type(val)is str:need(len(q[key])<=512,"bounded_selector")
   else:need(type(q[key])is list and q[key]==["S0","S1"],"SOURCE_selector")
  need(digest(q)==digest(expected),"original_selector")
  if k not in a:r.update(status="STOP_UPSTREAM",retained_status=e[k]["retained_status"],reason=e[k].get("reason"));return r
  r=emit(k,e[k]);need(r["transport_verified"]is True,"producer_STOP")
  r["parser"]=parse(r["packet"]if received is None else received,k,e[k],r["packet"])
  if not r["parser"]["transport_verified"]:r.update(status="STOP_RECEIVED_PACKET",transport_verified=False,packet=None,exact_contact_allowed=False,source_exact_contact_allowed=[False,False])
 except(ValueError,KeyError,TypeError,IndexError,RecursionError)as ex:r.update(status="STOP_INPUT",transport_verified=False,packet=None,reason=str(ex))
 return r
def run(k,q):
 try:e,a,pins=retained();return evaluate(k,q,e,a)
 except(OSError,ValueError,KeyError,TypeError,RecursionError)as ex:
  r=base();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
def validate_received(k,q,packet):
 try:e,a,pins=retained();return evaluate(k,q,e,a,received=packet)
 except(OSError,ValueError,KeyError,TypeError,RecursionError)as ex:
  r=base();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
