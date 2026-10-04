"""Geometry input adapter tests; independent float.as_integer_ratio decoder."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,copy,struct
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_scene_geometry32_ingress_HOST_v1 as m
def check(r):
 assert all(r[k]is False for k in ("hit_arithmetic_certified","computed_hilo_collapse_allowed",
  "scene_authenticated","phase_certified","physical_field_certified","full_path_visibility_certified",
  "GPU_used","Bpy_used","SOURCE_merged","native_IEEE_RN_graph_certified"))
 assert r["phase_error_bound"]is None and r["full_costs"]=="UNKNOWN_NOT_ZERO"
 assert all(r[k]==0 for k in ("new_intersections","new_guard_calls","new_root_calls","old_numeric_replays"))
def reseal(p):
 b=bytes.fromhex(p["buffer_hex"]);p["manifest"].update(buffer_sha256=m.sha(b),buffer_bytes=len(b))
 p["manifest_sha256"]=m.digest(p["manifest"])
 return p
def suite():
 e,a,pins=m.retained();positive=[];upstream=[]
 for k,x in e.items():
  r=m.evaluate(k,m.selector(k,e),e,a);check(r)
  if k not in a:
   assert r["status"]=="STOP_UPSTREAM"and r["cast_attempts"]==0
   upstream.append(dict(id=k,result=r));continue
  assert r["status"]=="HOST_ORIGINAL_GEOMETRY32_INPUT_BYTES_ONLY"and r["geometry_input_bytes_verified"]
  parser=r["parser"];check(parser);assert parser["geometry_input_bytes_verified"]and parser["cast_attempts"]==0
  p=r["packet"];b=bytes.fromhex(p["buffer_hex"]);meta=p["manifest"]
  assert b[:8]==b"N3DG32V1"and len(b)==40+4*(len(meta["primitive_ids"])+meta["scalar_count"])
  off=meta["scalar_payload_offset"]
  for j,f in enumerate(meta["fields"]):
   vv=struct.unpack_from("<f",b,off+4*j)[0];q=F(*vv.as_integer_ratio())
   assert q==F(*f["original_rational"])==F(*parser["decoded_fields"][j]["value"])
   assert parser["decoded_fields"][j]["word"]==struct.unpack_from("<I",b,off+4*j)[0]
  assert meta["source_ids"]==["S0","S1"]and r["cast_attempts"]==meta["scalar_count"]
  assert meta["computed_outputs_in_buffer"]is False and meta["phase_bound_in_buffer"]is False
  assert meta["source_width_caps_rad_HOST_only"]==x["request"]["source_width_caps_rad"]
  positive.append(dict(id=k,request=m.selector(k,e),result=r))
 assert len(positive)==6 and len(upstream)==38
 assert sum(v["result"]["cast_attempts"]for v in positive)==228
 assert sum(v["result"]["packet"]["manifest"]["buffer_bytes"]for v in positive)==1208
 base=next(v["result"]["packet"]for v in positive if v["id"]=="oblique");x=e["oblique"]
 neg=[]
 def n(name,p):
  r=m.parse(p,x);check(r);assert not r["geometry_input_bytes_verified"],(name,r)
  assert r["cast_attempts"]==0
  neg.append(dict(name=name,label="IN_MEMORY_RECEIVED_PACKET_NEGATIVE_NOT_ORIGINAL_MUTATION",packet=p,result=r))
 for name,mutation in (
  ("SOURCE_order",lambda p:p["manifest"].update(source_ids=["S1","S0"])),
  ("bool_version_metadata",lambda p:p["manifest"].update(header_bytes=True)),
  ("scene_hash",lambda p:p["manifest"].update(scene_sha256="0"*64)),
  ("record_hash",lambda p:p["manifest"].update(record_sha256="0"*64)),
  ("primitive_object",lambda p:p["manifest"]["primitive_object_ids"].__setitem__(0,"other")),
  ("phase_cap",lambda p:p["manifest"].update(relative_width_cap_rad_HOST_only=[1,1])),
  ("extra_hit_output",lambda p:p["manifest"].update(hit_points_BU=[])),
  ("field_order",lambda p:p["manifest"]["fields"].reverse()),
  ("field_unit",lambda p:p["manifest"]["fields"][0].update(unit="scene_length")),
  ("rational_bool",lambda p:p["manifest"]["fields"][0]["original_rational"].__setitem__(0,True))):
  p=copy.deepcopy(base);mutation(p);p["manifest_sha256"]=m.digest(p["manifest"]);n(name,p)
 # Payload controls are rehashed: matching metadata SHA cannot hide wrong original words.
 for name,offset,word in (
  ("SOURCE_position_word",base["manifest"]["scalar_payload_offset"],0x3f800000),
  ("NaN",base["manifest"]["scalar_payload_offset"],0x7fc00000),
  ("infinity",base["manifest"]["scalar_payload_offset"],0x7f800000),
  ("subnormal",base["manifest"]["scalar_payload_offset"],1),
  ("negative_zero",base["manifest"]["scalar_payload_offset"]+20,0x80000000),
  ("primitive_id_order",40,1),
  ("header_version",8,2),
  ("header_count",20,34),
  ("header_reserved",36,1)):
  p=copy.deepcopy(base);b=bytearray.fromhex(p["buffer_hex"]);struct.pack_into("<I",b,offset,word)
  p["buffer_hex"]=b.hex();n(name,reseal(p))
 for name,transform in (
  ("truncated",lambda h:h[:-2]),("trailing_bytes",lambda h:h+"00000000"),
  ("endianness_swapped",lambda h: b"".join(bytes.fromhex(h)[j:j+4][::-1]for j in range(0,len(bytes.fromhex(h)),4)).hex())):
  p=copy.deepcopy(base);p["buffer_hex"]=transform(p["buffer_hex"]);n(name,reseal(p))
 p=copy.deepcopy(base);p["buffer_hex"]="ZZ";n("invalid_hex",p)
 p=copy.deepcopy(base);p["extra"]="ignored";n("extra_packet_key",p)
 # Shape validation precedes hash serialization; don't serialize the malformed input.
 nested=0
 for j in range(1200):nested=[nested]
 p=copy.deepcopy(base);p["manifest"]["fields"]=nested
 r=m.parse(p,x);assert r["status"]=="STOP_INPUT"and r["reason"]=="bounded_field_count"
 neg.append(dict(name="deep_fields",label="NEW_MALFORMED_DESCRIPTOR_ONLY",depth=1200,result=r))
 p=copy.deepcopy(base);p["manifest"]["extra_loop"]=p["manifest"]
 r=m.parse(p,x);assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_manifest_shape"
 neg.append(dict(name="cyclic_extra_key",label="NEW_MALFORMED_DESCRIPTOR_ONLY",result=r))
 # New explicit non-original inputs; no changed retained fixtures or thresholds.
 controls=[]
 for name,v in (("third_not_exact32",[1,3]),("near_one_not_exact32",[33554433,33554432]),
      ("subnormal_input",[1,2**127]),("bool_rational",[True,4]),("noncanonical",[2,8])):
  xx=copy.deepcopy(x);xx["scene"]["sources"][0]["position_BU"][0]=v
  xx["request"]["original_scene_sha256"]=m.digest(xx["scene"])
  r=m.emit(xx);check(r);assert not r["geometry_input_bytes_verified"]and r["packet"]is None
  if name in ("third_not_exact32","near_one_not_exact32"):
   assert r["status"]=="STOP_INPUT_CONVERSION_LOSS"and F(*r["loss"]["signed_error"])!=0
  controls.append(dict(name=name,label="NEW_SYNTHETIC_INPUT_NOT_RETAINED_SCENE",input=v,result=r))
 # Separate synthetic ABI control: IDs are 31-bit, not a count/byte-size limit.
 xx=copy.deepcopy(x);xx["scene"]["triangles"][1]["primitive_id"]=2**31-1
 xx["request"]["root_primitive_id"]=2**31-1
 xx["request"]["original_scene_sha256"]=m.digest(xx["scene"])
 encoded=m.emit(xx);assert encoded["geometry_input_bytes_verified"]
 parsed=m.parse(encoded["packet"],xx);assert parsed["geometry_input_bytes_verified"]
 abi_control=dict(label="NEW_SYNTHETIC_ID_BOUNDARY_NOT_RETAINED_OR_PROMOTED",
   primitive_id=2**31-1,producer=encoded,parser=parsed)
 selectors=[]
 q=m.selector("oblique",e)
 for key,val in (("source_ids",["S1","S0"]),("case",True),("model","binary64"),("record_sha256","0"*64),
    ("epsilon_BU",[1,2**60]),("computed_outputs_in_buffer",True)):
  qq=copy.deepcopy(q);qq[key]=val;r=m.evaluate("oblique",qq,e,a);assert r["status"]=="STOP_INPUT"and r["cast_attempts"]==0
  selectors.append(dict(field=key,result=r))
 api=[];reader=m.retained
 try:
  def missing():raise OSError("SIMULATED_MISSING_DEPENDENCY")
  def drift():raise ValueError("SIMULATED_SHA_DRIFT")
  for fn in (missing,drift):
   m.retained=fn;r=m.run("oblique",q);assert r["status"]=="STOP_DEPENDENCY";api.append(r)
 finally:m.retained=reader
 summary=dict(retained_records=44,positive_packets=6,upstream_stops_preserved=38,original_scalar_inputs=228,
  original_buffer_bytes=1208,negative_received_packets=len(neg),synthetic_input_rejections=len(controls),
  selector_negatives=len(selectors),API_negative=len(api),dependency_pins=len(pins),
  producer_original_cast_attempts=228,parser_original_integer_decodes=228,
  new_intersections=0,new_guard_calls=0,new_root_calls=0,old_numeric_replays=0,full_costs="UNKNOWN_NOT_ZERO",
  QA_seconds_not_benchmark=True,GPU_used=False,phase_certified=False)
 return dict(status="PASS",summary=summary,evidence=dict(positive=positive,upstream=upstream,
  negative_packets=neg,synthetic_inputs=controls,synthetic_ABI_control=abi_control,selector_negatives=selectors,API_negative=api))
if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
