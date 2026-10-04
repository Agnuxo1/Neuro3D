"""New opt-in HOST geometry32 ingress from retained ORIGINAL S0/S1 inputs.
No impacts, path lengths, launch certificates or phase results in this input ABI.
"""
from pathlib import Path
from fractions import Fraction as F
import struct,json,hashlib,zlib,base64
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-scene-geometry32-ingress-HOST-v1"
POLICY="EXACT_ORIGINAL_INPUTS_ONLY_CLOSED_SOURCE_PRIMITIVE_ORDER_NO_COMPUTED_OUTPUTS"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SEALED-TERMINAL-LEDGER-CPU-001-CODEX.json"
PSHA="4985f70e2658a7d500e0608bec9dafb2b7b995aca65ff2e670abe77379512fd9"
VIS="coordinacion/respuestas/PRECISION-OBLIQUE-SEGMENT-VISIBILITY-CPU-001-CODEX.json"
VSHA="caeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5"
MAGIC=b"N3DG32V1"
HEADER=struct.Struct("<8s8I")
WORD=struct.Struct("<I")
SCOPE="HOST_DECLARED_ORIGINAL_GEOMETRY_INPUT_BYTES_ONLY"
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def rat(p):
 need(type(p)is list and len(p)==2 and all(type(v)is int for v in p)and p[1]>0,"typed_rational")
 need(max(abs(v).bit_length()for v in p)<=128,"bounded_rational")
 v=F(*p);need(pair(v)==p and abs(v)<=10**6,"canonical_bounded_rational");return v
def pow2(e):return F(2**e)if e>=0 else F(1,2**(-e))
def decode_word(w):
 need(type(w)is int and 0<=w<2**32,"typed_word32")
 sign=w>>31;exp=(w>>23)&255;frac=w&((1<<23)-1)
 need(exp!=255,"nonfinite_word");need(exp!=0 or frac==0,"subnormal_word")
 need(not(sign and exp==frac==0),"negative_zero_word")
 return F(0)if exp==0 else (-1 if sign else 1)*F((1<<23)+frac)*pow2(exp-127-23)
def capture(c):
 need(c["rc"]==0 and c["timed_out"]is False,"successful_capture")
 z=zlib.decompressobj();b=z.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),4194305)
 need(len(b)<=4194304 and z.eof and not z.unconsumed_tail and not z.unused_data,"bounded_capture")
 need(sha(b)==c["stdout_sha256"]and len(b)==c["stdout_bytes"],"capture_seal");return json.loads(b)
def retained():
 b=(ROOT/PARENT).read_bytes();need(sha(b)==PSHA and len(b)==210904,"parent_seal")
 p=json.loads(b);pins=dict(p["code_doc_sha256"]);need(len(pins)==339,"parent_pins339")
 for path,h in pins.items():need(sha((ROOT/path).read_bytes())==h,"dependency:"+path)
 need(capture(p["independent_final_after_doc_pins"])["status"]=="PASS","parent_oracle")
 d=capture(p["test_run"]);need(d["status"]=="PASS","parent_suite")
 admitted={r["id"]:r for r in d["evidence"]["positive"]};need(len(admitted)==6,"closed_positive6")
 need(pins[VIS]==VSHA,"visibility_pin")
 v=json.loads((ROOT/VIS).read_bytes());x=capture(v["test_run"])
 e={r["id"]:r for r in x["runs"]};need(len(e)==len(x["runs"])==44,"closed44")
 for k,r in admitted.items():
  need(r["result"]["status"]=="CPU_DECLARED_BOTH_SOURCE_TERMINAL_CLEAR_ONLY","terminal_status")
  need([a["source_id"]for a in r["result"]["source_decisions"]]==["S0","S1"],"terminal_SOURCE")
  need(all(a["plan"]["record_sha256"]==digest(e[k])for a in r["result"]["source_decisions"]),"same_original_record")
 pins[PARENT]=PSHA;return e,set(admitted),pins
def selector(k,e):
 x=e[k];return dict(model=MODEL,policy=POLICY,case=k,source_ids=["S0","S1"],
  scene_sha256=digest(x["scene"]),query_sha256=digest(x["request"]),
  record_sha256=digest(x),parent_receipt_sha256=PSHA,visibility_receipt_sha256=VSHA)
def baseline():
 return dict(model=MODEL,status="STOP_INPUT",reason=None,packet=None,loss=None,cast_attempts=0,
  HOST_float64_conversion_attempts=0,HOST_struct_float32_cast_attempts=0,integer_word_decodes=0,
  native_IEEE_RN_graph_certified=False,geometry_input_bytes_verified=False,
  hit_arithmetic_certified=False,computed_hilo_collapse_allowed=False,scene_authenticated=False,
  phase_certified=False,physical_field_certified=False,full_path_visibility_certified=False,
  GPU_used=False,Bpy_used=False,phase_error_bound=None,new_intersections=0,new_guard_calls=0,
  new_root_calls=0,old_numeric_replays=0,full_costs="UNKNOWN_NOT_ZERO",SOURCE_merged=False)
def fields(x):
 scene=x["scene"];q=x["request"]
 need(set(scene)=={"schema","units","sources","triangles"}and scene["schema"]=="precision-oblique-declared-scene-v1"
      and scene["units"]=="BU","original_scene_schema")
 need(set(q)=={"detector_point_BU","detector_primitive_id","lambda_BU","original_scene_sha256",
     "reference_BU","relative_width_cap_rad","root_primitive_id","source_ids","source_width_caps_rad"},"closed_original_query")
 need(digest(scene)==q["original_scene_sha256"],"original_scene_hash")
 need(q["source_ids"]==[s["id"]for s in scene["sources"]]==["S0","S1"],"literal_SOURCE_order")
 triangles=scene["triangles"];need(type(triangles)is list and 1<=len(triangles)<=64,"triangle_count")
 ids=[t["primitive_id"]for t in triangles]
 need(all(type(i)is int and 0<=i<2**31 for i in ids)and len(set(ids))==len(ids),"unique_primitive_ids")
 need(all(type(q[k])is int and q[k]in ids for k in ("root_primitive_id","detector_primitive_id")),"query_primitive_ids")
 need(q["root_primitive_id"]!=q["detector_primitive_id"],"distinct_terminal_primitives")
 need(rat(q["lambda_BU"])>0,"positive_declared_lambda")
 # Caps kept verbatim as HOST metadata, not uploaded or interpreted as a phase bound.
 need(len(q["source_width_caps_rad"])==2 and rat(q["relative_width_cap_rad"])>=0
      and all(rat(c)>=0 for c in q["source_width_caps_rad"]),"original_caps")
 out=[]
 def vector(v,path,unit):
  need(type(v)is list and len(v)==3,"vector3")
  for j,value in enumerate(v):
   rat(value);out.append(dict(path=path+"/"+str(j),unit=unit,original_rational=value))
 for s in scene["sources"]:
  need(set(s)=={"id","position_BU","direction"},"closed_source")
  vector(s["position_BU"],"sources/"+s["id"]+"/position_BU","BU")
  vector(s["direction"],"sources/"+s["id"]+"/direction","unscaled_original_direction_parameter")
 for index,t in enumerate(triangles):
  need(set(t)=={"primitive_id","object_id","vertices_BU"}and type(t["object_id"])is str and 0<len(t["object_id"])<=64,"closed_triangle")
  need(type(t["vertices_BU"])is list and len(t["vertices_BU"])==3,"triangle3")
  for j,v in enumerate(t["vertices_BU"]):vector(v,"triangles/"+str(index)+"/vertices_BU/"+str(j),"BU")
 vector(q["detector_point_BU"],"query/detector_point_BU","BU")
 for k in ("lambda_BU","reference_BU"):out.append(dict(path="query/"+k,unit="BU",original_rational=q[k]))
 return out,ids
def metadata(x,layout,ids):
 q=x["request"];return dict(model=MODEL,policy=POLICY,scope=SCOPE,case=x["id"],
  scene_sha256=digest(x["scene"]),query_sha256=digest(q),record_sha256=digest(x),
  parent_receipt_sha256=PSHA,source_ids=["S0","S1"],primitive_ids=ids,
  primitive_object_ids=[t["object_id"]for t in x["scene"]["triangles"]],
  root_primitive_id=q["root_primitive_id"],detector_primitive_id=q["detector_primitive_id"],
  endian="little",header_bytes=HEADER.size,primitive_table_offset=HEADER.size,
  scalar_payload_offset=HEADER.size+len(ids)*WORD.size,scalar_count=len(layout),
  fields=layout,source_width_caps_rad_HOST_only=q["source_width_caps_rad"],
  relative_width_cap_rad_HOST_only=q["relative_width_cap_rad"],
  float32_zero_policy="positive_zero_only",normal_or_zero_only=True,
  computed_outputs_in_buffer=False,scene_authentication=False,phase_bound_in_buffer=False)
def expected_header(x,layout,ids):
 q=x["request"];return (MAGIC,1,2,len(ids),len(layout),len(ids),q["root_primitive_id"],q["detector_primitive_id"],0)
def emit(x):
 """Internal producer from a trusted retained ORIGINAL record; no calculated hit inputs."""
 r=baseline()
 try:
  layout,ids=fields(x);words=[]
  for f in layout:
   q=rat(f["original_rational"]);r["cast_attempts"]+=1;r["HOST_float64_conversion_attempts"]+=1
   v=float(q);r["HOST_struct_float32_cast_attempts"]+=1
   w=WORD.unpack(struct.pack("<f",v))[0];r["integer_word_decodes"]+=1;decoded=decode_word(w)
   if decoded!=q:
    r.update(status="STOP_INPUT_CONVERSION_LOSS",reason="exact_zero_input_loss_required",
       loss=dict(field=f["path"],original_rational=pair(q),decoded32=pair(decoded),signed_error=pair(decoded-q),candidate_word=w));return r
   words.append(w)
  b=HEADER.pack(*expected_header(x,layout,ids))+b"".join(WORD.pack(i)for i in ids+words)
  meta=metadata(x,layout,ids);meta.update(buffer_sha256=sha(b),buffer_bytes=len(b))
  packet=dict(manifest=meta,manifest_sha256=digest(meta),buffer_hex=b.hex())
  r.update(status="HOST_ORIGINAL_GEOMETRY32_INPUT_BYTES_ONLY",reason="ALL_original_input_scalars_exact",
     packet=packet,geometry_input_bytes_verified=True)
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error)as ex:r["reason"]=str(ex)
 return r
def parse(packet,x):
 """Validate received bytes against ORIGINAL input, even if caller rehashes mutations.
Integer decoding only; no encoder, hit/guard/phase computation or HOST output injection.
"""
 r=baseline()
 try:
  need(type(packet)is dict and set(packet)=={"manifest","manifest_sha256","buffer_hex"},"closed_packet")
  need(type(packet["buffer_hex"])is str and len(packet["buffer_hex"])<=10000
       and len(packet["buffer_hex"])%2==0 and all(c in "0123456789abcdef"for c in packet["buffer_hex"]),"canonical_bounded_hex")
  b=bytes.fromhex(packet["buffer_hex"]);layout,ids=fields(x)
  expected=metadata(x,layout,ids);expected.update(buffer_sha256=sha(b),buffer_bytes=len(b))
  meta=packet["manifest"]
  need(type(meta)is dict and set(meta)==set(expected),"closed_manifest_shape")
  need(type(meta["fields"])is list and len(meta["fields"])==len(layout),"bounded_field_count")
  for f in meta["fields"]:
   need(type(f)is dict and set(f)=={"path","unit","original_rational"},"closed_field_descriptor")
   need(type(f["path"])is str and len(f["path"])<=128 and type(f["unit"])is str and len(f["unit"])<=80,"bounded_field_strings")
   rat(f["original_rational"])
  for key in ("model","policy","scope","case","scene_sha256","query_sha256","record_sha256",
     "parent_receipt_sha256","endian","float32_zero_policy","buffer_sha256"):
   need(type(meta[key])is str and len(meta[key])<=512,"bounded_manifest_string")
  for key in ("root_primitive_id","detector_primitive_id","header_bytes","primitive_table_offset",
     "scalar_payload_offset","scalar_count","buffer_bytes"):
   need(type(meta[key])is int and 0<=meta[key]<2**31,"typed_manifest_integer")
  need(type(meta["source_ids"])is list and meta["source_ids"]==["S0","S1"],"manifest_SOURCE")
  need(type(meta["primitive_ids"])is list and len(meta["primitive_ids"])==len(ids)
       and all(type(i)is int for i in meta["primitive_ids"]),"typed_manifest_ids")
  need(type(meta["primitive_object_ids"])is list and len(meta["primitive_object_ids"])==len(ids)
       and all(type(o)is str and len(o)<=64 for o in meta["primitive_object_ids"]),"bounded_objects")
  need(type(meta["source_width_caps_rad_HOST_only"])is list and len(meta["source_width_caps_rad_HOST_only"])==2,"HOST_caps2")
  for c in meta["source_width_caps_rad_HOST_only"]:rat(c)
  rat(meta["relative_width_cap_rad_HOST_only"])
  for key in ("normal_or_zero_only","computed_outputs_in_buffer","scene_authentication","phase_bound_in_buffer"):
   need(type(meta[key])is bool,"typed_manifest_boolean")
  need(digest(packet["manifest"])==packet["manifest_sha256"]==digest(expected),"closed_original_manifest")
  need(len(b)==HEADER.size+4*(len(ids)+len(layout)),"exact_buffer_length")
  need(HEADER.unpack_from(b)==expected_header(x,layout,ids),"typed_header")
  actual_ids=[WORD.unpack_from(b,HEADER.size+4*j)[0]for j in range(len(ids))]
  need(actual_ids==ids,"original_primitive_order")
  start=HEADER.size+4*len(ids);decoded=[]
  for j,f in enumerate(layout):
   w=WORD.unpack_from(b,start+4*j)[0];r["integer_word_decodes"]+=1;v=decode_word(w)
   need(v==rat(f["original_rational"]),"word_not_original:"+f["path"])
   decoded.append(dict(path=f["path"],unit=f["unit"],value=pair(v),word=w))
  r.update(status="HOST_RECEIVED_GEOMETRY32_INPUT_VERIFIED_ONLY",reason="exact_original_bytes_by_word",
    geometry_input_bytes_verified=True,decoded_fields=decoded,buffer_sha256=sha(b),buffer_bytes=len(b))
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error,RecursionError)as ex:r["reason"]=str(ex)
 return r
def evaluate(k,q,e,admitted):
 r=baseline()
 try:
  need(k in e and type(q)is dict and digest(q)==digest(selector(k,e)),"closed_selector")
  if k not in admitted:
   r.update(status="STOP_UPSTREAM",reason=e[k]["result"].get("reason"),retained_status=e[k]["result"]["status"]);return r
  r=emit(e[k])
  if r["geometry_input_bytes_verified"]:
   validation=parse(r["packet"],e[k]);r["parser"]=validation
   need(validation["geometry_input_bytes_verified"]is True,"self_parse")
 except(ValueError,KeyError,TypeError,IndexError)as ex:r.update(status="STOP_INPUT",reason=str(ex),geometry_input_bytes_verified=False)
 return r
def run(k,q):
 try:e,a,pins=retained();return evaluate(k,q,e,a)
 except(OSError,ValueError,KeyError,TypeError,zlib.error)as ex:
  r=baseline();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
