"""New hi-lo wire tests; independent word decoder, no geometry producer replays."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,copy,struct
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_trace_output_hilo32_HOST_v1 as m
def scope(r):
 assert all(r[k]is False for k in ("computed_hilo_collapse_allowed","native_IEEE_RN_graph_certified","GPU_used","Bpy_used","RT_used",
  "scene_authenticated","phase_certified","physical_field_certified","SOURCE_merged"))
 assert r["phase_error_bound"]is None and r["full_costs"]=="UNKNOWN_NOT_ZERO"
 assert all(r[k]==0 for k in ("new_intersections","new_guard_calls","new_root_calls","old_numeric_replays"))
def word_value(w):return F(*struct.unpack("<f",struct.pack("<I",w))[0].as_integer_ratio())
def reseal(p):
 b=bytes.fromhex(p["buffer_hex"]);p["manifest"].update(buffer_sha256=m.hashlib.sha256(b).hexdigest(),buffer_bytes=len(b));p["manifest_sha256"]=m.digest(p["manifest"]);return p
def suite():
 e,a,pins=m.retained();positive=[];up=[];radii=[];losses=[]
 for k,c in e.items():
  r=m.evaluate(k,m.selector(k,e),e,a);scope(r)
  if k not in a:
   assert r["status"]=="STOP_UPSTREAM"and r["cast_attempts"]==r["integer_word_decodes"]==0
   up.append(dict(id=k,result=r));continue
  assert r["transport_verified"],(k,r)
  parser=r["parser"];scope(parser);assert parser["transport_verified"]and parser["cast_attempts"]==0
  p=r["packet"];b=bytes.fromhex(p["buffer_hex"]);assert len(b)==368
  assert m.HEADER.unpack_from(b)==(b"N3OH32V1",1,2,21,42,84,0)
  assert r["cast_attempts"]==r["integer_word_decodes"]==parser["integer_word_decodes"]==84
  for i,f in enumerate(p["manifest"]["fields"]):
   wh,wl=struct.unpack_from("<2I",b,32+8*i);hi=word_value(wh);lo=word_value(wl);q=F(*f["original_rational"])
   assert hi+lo-q==F(*f["signed_error"])and abs(hi+lo-q)==F(*f["radius"])
   assert hi-q==F(*f["drop_lo_signed_error"])and wh==f["word_pair"][0]and wl==f["word_pair"][1]
   assert hi+lo-F(*f["radius"])<=q<=hi+lo+F(*f["radius"])
   assert parser["decoded_fields"][i]==f
   if f["radius"]!=[0,1]:radii.append(dict(case=k,path=f["path"],radius=f["radius"]))
   if wl!=0:losses.append(dict(case=k,path=f["path"],hi_word=wh,lo_word=wl,paired_error=f["signed_error"],drop_lo_error=f["drop_lo_signed_error"]))
  assert r["exact_contact_allowed"]is False and parser["exact_contact_allowed"]is False
  assert r["exact_contact_status"]==parser["exact_contact_status"]=="STOP_NONEXACT_TRACE_OUTPUT"
  positive.append(dict(id=k,request=m.selector(k,e),result=r))
 assert len(positive)==6 and len(up)==38 and len(radii)>0 and len(losses)>0
 orig=next(z for z in positive if z["id"]=="oblique");ref=orig["result"]["packet"];c=e["oblique"];neg=[]
 def n(name,p):
  assert m.digest(p)!=m.digest(ref),(name,"negative_control_must_change_packet")
  r=m.parse(p,"oblique",c,ref);scope(r);assert not r["transport_verified"]and not r["exact_contact_allowed"],(name,r)
  assert r["cast_attempts"]==0;neg.append(dict(name=name,packet=p,result=r))
 for name,change in (
  ("SOURCE_order",lambda p:p["manifest"].update(source_ids=["S1","S0"])),
  ("trace_hash",lambda p:p["manifest"].update(trace_result_sha256="0"*64)),
  ("scene_hash",lambda p:p["manifest"].update(scene_sha256="0"*64)),
  ("input_buffer_hash",lambda p:p["manifest"].update(input_buffer_sha256="0"*64)),
  ("coverage_drop",lambda p:p["manifest"]["SOURCE_coverage"][0]["primary_ids"].pop()),
  ("field_order",lambda p:p["manifest"]["fields"].reverse()),
  ("unit",lambda p:p["manifest"]["fields"][0].update(unit="BU")),
  ("zero_budget_relaxed",lambda p:p["manifest"].update(zero_exact_contact_budget=[1,100])),
  ("exact_gate_forged",lambda p:p["manifest"].update(exact_contact_allowed=True,source_exact_contact_allowed=[True,True])),
  ("radius_forged",lambda p:next(f for f in p["manifest"]["fields"]if f["radius"]!=[0,1]).update(radius=[0,1])),
  ("word_bool",lambda p:p["manifest"]["fields"][0]["word_pair"].__setitem__(0,True)),
  ("extra_phase_bound",lambda p:p["manifest"].update(phase_error_bound=[0,1]))):
  p=copy.deepcopy(ref);change(p);p["manifest_sha256"]=m.digest(p["manifest"]);n(name,p)
 for name,offset,v in (("drop_lo",32+8*4+4,0),("NaN",32,0x7fc00000),("inf",32,0x7f800000),
      ("subnormal",32,1),("negzero",32,0x80000000),("header_reserved",28,1)):
  p=copy.deepcopy(ref);b=bytearray.fromhex(p["buffer_hex"]);struct.pack_into("<I",b,offset,v);p["buffer_hex"]=b.hex();n(name,reseal(p))
 for name,change in (("truncated",lambda h:h[:-2]),("extra_bytes",lambda h:h+"00000000"),("pair_order",lambda h:h[:64]+h[72:80]+h[64:72]+h[80:])):
  p=copy.deepcopy(ref);p["buffer_hex"]=change(p["buffer_hex"]);n(name,reseal(p))
 p=copy.deepcopy(ref);p["extra"]=1;n("extra_packet_key",p)
 # Public-context validation builds its own reference, no caller reference argument.
 bad=copy.deepcopy(ref);bb=bytearray.fromhex(bad["buffer_hex"]);struct.pack_into("<I",bb,32+8*4+4,0);bad["buffer_hex"]=bb.hex();reseal(bad)
 r=m.evaluate("oblique",m.selector("oblique",e),e,a,received=bad);scope(r)
 assert r["status"]=="STOP_RECEIVED_PACKET"and r["packet"]is None and r["cast_attempts"]==84
 public_negative=dict(label="NEW_RECEIVED_PACKET_CONTEXT_CHECK_REFERENCE_BUILT_FROM_PINNED_TRACE",result=r)
 inputs=[]
 for name,value in (("subnormal_hi",[1,2**127]),("subnormal_lo",[(2**127)+1,2**127]),
    ("noncanonical",[2,8]),("boolean",[True,4]),("too_large",[1000001,1])):
  cc=copy.deepcopy(c);cc["source_results"][0]["primary_hit"]["parameter"]=value
  r=m.emit("synthetic_field_only",cc);scope(r);assert not r["transport_verified"]and r["packet"]is None
  inputs.append(dict(name=name,label="NEW_SYNTHETIC_OUTPUT_FIELD_ONLY_NOT_TRACE_ADMISSION",field=value,result=r))
 selectors=[];q=m.selector("oblique",e)
 for key,val in (("source_ids",["S1","S0"]),("case",True),("epsilon",[1,2**60]),("model","IEEE32"),("trace_result_sha256",["nested"]),("parent_receipt_sha256","0"*64)):
  qq=copy.deepcopy(q);qq[key]=val;r=m.evaluate("oblique",qq,e,a);scope(r);assert r["status"]=="STOP_INPUT"and r["cast_attempts"]==0
  selectors.append(dict(field=key,result=r))
 api=[];reader=m.retained
 try:
  def missing():raise OSError("SIMULATED_MISSING_DEPENDENCY")
  def drift():raise ValueError("SIMULATED_SHA_DRIFT")
  for fn in (missing,drift):
   m.retained=fn;r=m.run("oblique",q);scope(r);assert r["status"]=="STOP_DEPENDENCY";api.append(r)
 finally:m.retained=reader
 summary=dict(original_trace_packets=6,original_SOURCE=12,original_fields=252,original_word_count=504,
  original_bytes=2208,upstream_stops=38,exact_contact_admitted=0,exact_contact_stops=6,nonexact_fields=len(radii),
  nonzero_lo_fields=len(losses),negative_packets=len(neg),synthetic_output_field_stops=5,selectors=6,API_simulated=2,
  dependency_pins=len(pins),new_intersections=0,new_guard_calls=0,new_root_calls=0,old_numeric_replays=0,
  GPU_used=False,phase_certified=False,full_costs="UNKNOWN_NOT_ZERO",QA_seconds_not_benchmark=True)
 return dict(status="PASS",summary=summary,evidence=dict(positive=positive,upstream=up,radii=radii,drop_lo_losses=losses,
   negative_packets=neg,public_context_negative=public_negative,synthetic_fields=inputs,selectors=selectors,API_negative=api))
if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
