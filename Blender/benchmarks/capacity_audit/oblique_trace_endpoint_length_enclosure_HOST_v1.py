"""Opt-in HOST enclosure of two declared segments from sealed hi-lo endpoint boxes.
New rational interval arithmetic and integer sqrt certificates, no geometry/encoder replay.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,struct,base64,zlib,math
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-trace-endpoint-length-enclosure-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TRACE-OUTPUT-HILO32-HOST-001-CODEX.json"
PSHA="b62ddeca67ae4c9c8f37d50db1fbe9d53ca62e1fcae3bf0fc6e7a015aa092bfd"
BITS=96
def need(ok,s):
 if not ok:raise ValueError(s)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def pair(v):return [v.numerator,v.denominator]
def rat(v):
 need(type(v)is list and len(v)==2 and all(type(x)is int for x in v),"typed_rational")
 need(v[1]>0 and math.gcd(v[0],v[1])==1 and max(abs(v[0]).bit_length(),v[1].bit_length())<=128,"canonical_bounded_rational")
 return F(*v)
def capture(w):
 need(w["rc"]==0 and w["timed_out"]is False,"capture_complete")
 b=zlib.decompress(base64.b64decode(w["stdout_zlib_base64"]));need(hashlib.sha256(b).hexdigest()==w["stdout_sha256"]and len(b)==w["stdout_bytes"],"capture_seal")
 return json.loads(b)
def retained():
 b=(ROOT/PARENT).read_bytes();need(len(b)==112485 and hashlib.sha256(b).hexdigest()==PSHA,"parent_seal")
 p=json.loads(b);pins=dict(p["code_doc_sha256"]);need(len(pins)==351,"pins351")
 for s,h in pins.items():need(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h,"dependency:"+s)
 need(capture(p["independent_verification"])["status"]=="PASS","parent_oracle")
 d=capture(p["test_run"]);need(d["status"]=="PASS","parent_suite")
 e={z["id"]:z["result"]for z in d["evidence"]["positive"]+d["evidence"]["upstream"]}
 a={z["id"]for z in d["evidence"]["positive"]};need(len(e)==44 and len(a)==6,"closed_cases")
 pins[PARENT]=PSHA;return e,a,pins
def selector(k,e):
 r=e[k];return dict(model=MODEL,case=k,source_ids=["S0","S1"],parent_receipt_sha256=PSHA,captured_result_sha256=digest(r))
def base():
 return dict(model=MODEL,status="STOP_INPUT",reason=None,SOURCE_results=[],HOST_length_enclosure_verified=False,
  new_integer_word_decodes=0,new_integer_root_certificates=0,new_interval_segment_norms=0,
  old_numeric_replays=0,old_encoder_replays=0,old_geometry_replays=0,old_guard_replays=0,old_root_replays=0,
  native_IEEE_RN_graph_certified=False,GPU_used=False,Bpy_used=False,RT_used=False,scene_authenticated=False,
  exact_contact_allowed=False,phase_certified=False,physical_field_certified=False,length_accuracy_budget_admitted=False,
  computed_hilo_collapse_allowed=False,SOURCE_merged=False,phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO")
def decode(w):
 need(type(w)is int and 0<=w<2**32,"word_integer")
 exp=(w>>23)&255;mant=w&((1<<23)-1)
 need(w==0 or exp not in (0,255),"normal_or_positive_zero_only")
 return F(0)if w==0 else (-1 if w>>31 else 1)*F((1<<23)+mant)*F(2)**(exp-150)
def sqrt_certificate(q,r):
 need(type(q)is F and q>=0 and max(q.numerator.bit_length(),q.denominator.bit_length())<=512 and q<=2**64,"root_capacity")
 r["new_integer_root_certificates"]+=1
 scaled=q.numerator<<(2*BITS);n=scaled//q.denominator;k=math.isqrt(n)
 need(k*k*q.denominator<=scaled<(k+1)*(k+1)*q.denominator,"integer_sqrt_certificate")
 lo=F(k,2**BITS);hi=lo if k*k*q.denominator==scaled else F(k+1,2**BITS)
 need(lo*lo<=q<=hi*hi,"root_enclosure")
 return dict(squared=pair(q),lower_BU=pair(lo),upper_BU=pair(hi),fraction_bits=BITS,
  floor_scaled_root=k,scaled_numerator=scaled,scaled_denominator=q.denominator,exact=lo==hi)
def square_interval(lo,hi):
 need(type(lo)is F and type(hi)is F and lo<=hi,"ordered_interval")
 return (F(0)if lo<=0<=hi else min(lo*lo,hi*hi),max(lo*lo,hi*hi))
def segment(a,b,r):
 need(type(a)is list and type(b)is list and len(a)==len(b)==3,"point_box3")
 components=[];sqlo=F(0);sqhi=F(0)
 for x,y in zip(a,b):
  need(type(x)is tuple and type(y)is tuple and len(x)==len(y)==2 and all(type(v)is F for v in x+y),"typed_box")
  need(x[0]<=x[1] and y[0]<=y[1],"ordered_box")
  lo=y[0]-x[1];hi=y[1]-x[0];sl,sh=square_interval(lo,hi);sqlo+=sl;sqhi+=sh
  components.append(dict(difference_BU=[pair(lo),pair(hi)],squared_BU2=[pair(sl),pair(sh)]))
 r["new_interval_segment_norms"]+=1;low=sqrt_certificate(sqlo,r);high=sqrt_certificate(sqhi,r)
 return dict(components=components,squared_BU2=[pair(sqlo),pair(sqhi)],root_lower_certificate=low,root_upper_certificate=high,
  length_BU=[low["lower_BU"],high["upper_BU"]])
def packet_boxes(packet,reference,r):
 need(type(packet)is dict and set(packet)=={"manifest","manifest_sha256","buffer_hex"},"closed_packet")
 need(digest(packet)==digest(reference),"sealed_original_packet")
 m=packet["manifest"];need(m["source_ids"]==["S0","S1"]and m["zero_exact_contact_budget"]==[0,1],"source_gate")
 need(m["exact_contact_allowed"]is False and m["source_exact_contact_allowed"]==[False,False],"retain_contact_STOP")
 need(type(packet["buffer_hex"])is str and len(packet["buffer_hex"])==736,"wire_size")
 b=bytes.fromhex(packet["buffer_hex"]);need(struct.unpack_from("<8s6I",b)==(b"N3OH32V1",1,2,21,42,84,0),"header")
 need(len(b)==368 and hashlib.sha256(b).hexdigest()==m["buffer_sha256"]and digest(m)==packet["manifest_sha256"],"wire_seal")
 need(len(m["fields"])==42,"closed_fields")
 all_fields={};boxes=[];decoded=[]
 for i,f in enumerate(m["fields"]):
  wh,wl=struct.unpack_from("<2I",b,32+8*i);r["new_integer_word_decodes"]+=1;hi=decode(wh);r["new_integer_word_decodes"]+=1;lo=decode(wl)
  q=rat(f["original_rational"]);error=hi+lo-q;radius=rat(f["radius"])
  need(radius==abs(error)and rat(f["signed_error"])==error and rat(f["decoded_pair_value"])==hi+lo and rat(f["drop_lo_signed_error"])==hi-q,"exact_residual")
  need(f["word_pair"]==[wh,wl]and f["path"]not in all_fields,"words_unique_path")
  all_fields[f["path"]]=(hi+lo-radius,hi+lo+radius)
  decoded.append(dict(path=f["path"],unit=f["unit"],hi_rational=pair(hi),lo_rational=pair(lo),radius=pair(radius),box=[pair(hi+lo-radius),pair(hi+lo+radius)]))
 for sid in ("S0","S1"):
  points=[]
  for j in range(3):
   point=[]
   for n in range(3):
    path=sid+"/segment_endpoints_BU/"+str(j)+"/"+str(n)
    matches=[f for f in m["fields"]if f["path"]==path];need(len(matches)==1 and matches[0]["unit"]=="BU","endpoint_unit")
    point.append(all_fields[path])
   points.append(point)
  boxes.append(points)
 return boxes,decoded
def evaluate(k,q,e,a,received=None):
 r=base()
 try:
  need(type(k)is str and k in e,"known_case");expected=selector(k,e)
  need(type(q)is dict and set(q)==set(expected),"closed_selector")
  for key,val in expected.items():
   need(type(q[key])is type(val),"typed_selector")
   if type(val)is str:need(len(q[key])<=512,"bounded_selector")
   else:need(q[key]==["S0","S1"],"literal_SOURCE")
  need(digest(q)==digest(expected),"sealed_selector")
  if k not in a:r.update(status="STOP_UPSTREAM",retained_status=e[k]["retained_status"]);return r
  old=e[k];need(old["transport_verified"]is True and old["exact_contact_allowed"]is False,"retained_wire_not_contact")
  ref=old["packet"];packet=ref if received is None else received;boxes,decoded=packet_boxes(packet,ref,r)
  m=packet["manifest"];sources=[]
  for i,sid in enumerate(("S0","S1")):
   segments=[segment(boxes[i][j],boxes[i][j+1],r)for j in range(2)]
   lo=sum((F(*z["length_BU"][0])for z in segments),F(0));hi=sum((F(*z["length_BU"][1])for z in segments),F(0))
   # Received squared outputs are diagnostic contrasts, never norm inputs.
   for j,z in enumerate(segments):
    f=next(f for f in m["fields"]if f["path"]==sid+"/segment_squared_BU2/"+str(j))
    need(f["unit"]=="BU2"and F(*z["squared_BU2"][0])<=rat(f["original_rational"])<=F(*z["squared_BU2"][1]),"retained_squared_contrast")
   sources.append(dict(source_id=sid,endpoint_boxes=[[[pair(x)for x in v]for v in pt]for pt in boxes[i]],
    segments=segments,total_length_BU=[pair(lo),pair(hi)],interval_width_BU=pair(hi-lo),coverage=m["SOURCE_coverage"][i],
    exact_contact_allowed=False,length_accuracy_budget_admitted=False))
  r.update(status="HOST_DECLARED_LENGTH_ENCLOSURE_ONLY",HOST_length_enclosure_verified=True,SOURCE_results=sources,
   endpoint_descriptor_count=18,decoded_fields=decoded,scene_sha256=m["scene_sha256"],query_sha256=m["query_sha256"],
   input_buffer_sha256=m["input_buffer_sha256"],output_buffer_sha256=m["buffer_sha256"],
   trace_result_sha256=m["trace_result_sha256"],packet_sha256=digest(packet),parent_receipt_sha256=PSHA,
   sqrt_fraction_bits=BITS,original_squares_used_as_inputs=False)
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error,RecursionError)as ex:
  r.update(status="STOP_INPUT",reason=str(ex),HOST_length_enclosure_verified=False,SOURCE_results=[])
 return r
def run(k,q,received=None):
 try:e,a,pins=retained();return evaluate(k,q,e,a,received)
 except(OSError,ValueError,KeyError,TypeError,RecursionError)as ex:
  r=base();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
