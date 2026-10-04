"""Fresh enclosure QA; parent outputs read as data, no producer or geometry replays."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import sys,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_trace_endpoint_length_enclosure_HOST_v1 as m
def scope(r):
 assert all(r[k]is False for k in ("native_IEEE_RN_graph_certified","GPU_used","Bpy_used","RT_used","scene_authenticated","exact_contact_allowed","phase_certified","physical_field_certified","length_accuracy_budget_admitted","computed_hilo_collapse_allowed","SOURCE_merged"))
 assert r["phase_error_bound"]is None and r["full_costs"]=="UNKNOWN_NOT_ZERO"
 assert all(r[k]==0 for k in ("old_numeric_replays","old_encoder_replays","old_geometry_replays","old_guard_replays","old_root_replays"))
def verify(z):
 low=F(*z["squared_BU2"][0]);high=F(*z["squared_BU2"][1]);l=F(*z["length_BU"][0]);h=F(*z["length_BU"][1])
 assert l*l<=low<=high<=h*h
 for c in (z["root_lower_certificate"],z["root_upper_certificate"]):
  q=F(*c["squared"]);a=F(*c["lower_BU"]);b=F(*c["upper_BU"]);k=c["floor_scaled_root"]
  assert a*a<=q<=b*b and b-a<=F(1,2**96)
  assert k*k*c["scaled_denominator"]<=c["scaled_numerator"]<(k+1)**2*c["scaled_denominator"]
def suite():
 e,a,pins=m.retained();positive=[];upstream=[]
 for k,old in e.items():
  r=m.evaluate(k,m.selector(k,e),e,a);scope(r)
  if k not in a:assert r["status"]=="STOP_UPSTREAM"and r["new_integer_word_decodes"]==r["new_integer_root_certificates"]==0;upstream.append(dict(id=k,result=r));continue
  assert r["HOST_length_enclosure_verified"],(k,r)
  assert r["new_integer_word_decodes"]==84 and r["new_integer_root_certificates"]==8 and r["new_interval_segment_norms"]==4
  assert [s["source_id"]for s in r["SOURCE_results"]]==["S0","S1"]
  for s in r["SOURCE_results"]:
   for z in s["segments"]:verify(z)
   assert F(*s["total_length_BU"][0])<=F(*s["total_length_BU"][1]) and F(*s["interval_width_BU"])>=0
  positive.append(dict(id=k,request=m.selector(k,e),result=r))
 assert len(positive)==6 and len(upstream)==38
 ref=e["oblique"]["packet"];neg=[]
 for name,change in (
  ("drop_lo",lambda p:p.update(buffer_hex=p["buffer_hex"][:136]+"00000000"+p["buffer_hex"][144:])),
  ("field_radius",lambda p:p["manifest"]["fields"][10].update(radius=[1,2**80])),
  ("endpoint_unit",lambda p:p["manifest"]["fields"][10].update(unit="mm")),
  ("SOURCE_order",lambda p:p["manifest"].update(source_ids=["S1","S0"])),
  ("coverage_drop",lambda p:p["manifest"]["SOURCE_coverage"][0]["secondary_ids"].pop()),
  ("scene_hash",lambda p:p["manifest"].update(scene_sha256="0"*64)),
  ("query_hash",lambda p:p["manifest"].update(query_sha256="0"*64)),
  ("reference_swap",lambda p:p.update(buffer_hex=e["direction_scaled"]["packet"]["buffer_hex"])),
  ("zero_contact_promoted",lambda p:p["manifest"].update(exact_contact_allowed=True)),
  ("extra_phase",lambda p:p["manifest"].update(phase_error_bound=[0,1])),
  ("extra_key",lambda p:p.update(expected_packet=ref)),
  ("truncated",lambda p:p.update(buffer_hex=p["buffer_hex"][:-2]))):
  p=copy.deepcopy(ref);change(p);p["manifest"]["buffer_sha256"]=m.hashlib.sha256(bytes.fromhex(p["buffer_hex"])).hexdigest();p["manifest_sha256"]=m.digest(p["manifest"])
  assert m.digest(p)!=m.digest(ref),(name,"control_must_change")
  r=m.evaluate("oblique",m.selector("oblique",e),e,a,p);scope(r)
  assert not r["HOST_length_enclosure_verified"]and not r["SOURCE_results"]and r["new_integer_word_decodes"]==r["new_integer_root_certificates"]==0,(name,r)
  neg.append(dict(name=name,packet=p,result=r))
 # New interval stage controls; not replacements of sealed scene or promotion.
 controls=[]
 for name,aa,bb in (("point_exact",[(0,0)]*3,[(3,3),(4,4),(0,0)]),
  ("cross_zero",[(-1,1)]*3,[(-1,1)]*3),
  ("signed_box",[(1,2),(-4,-3),(0,1)],[(5,6),(1,2),(-2,-1)]),
  ("tiny_gap",[(0,0)]*3,[(F(1,2**60),F(1,2**60))]*3),
  ("nonbinary_radius",[(F(1,3),F(2,3))]*3,[(F(4,3),F(5,3))]*3)):
  aa=[tuple(F(x)for x in v)for v in aa];bb=[tuple(F(x)for x in v)for v in bb];r=m.base();z=m.segment(aa,bb,r);verify(z);scope(r)
  for av in product(*aa):
   for bv in product(*bb):
    sq=sum(((x-y)**2 for x,y in zip(av,bv)),F(0));assert F(*z["squared_BU2"][0])<=sq<=F(*z["squared_BU2"][1])
  controls.append(dict(name=name,label="SYNTHETIC_INTERVAL_STAGE_ONLY_NOT_SCENE_ADMISSION",a=[[m.pair(x)for x in v]for v in aa],b=[[m.pair(x)for x in v]for v in bb],segment=z,counters=r,corner_checks=64))
 errors=[]
 for name,q in (("negative",F(-1)),("too_many_bits",F(1,2**513)),("too_large",F(2**65)),("boolean",True)):
  r=m.base()
  try:m.sqrt_certificate(q,r);raise AssertionError("accepted:"+name)
  except ValueError as ex:errors.append(dict(name=name,reason=str(ex),counters=r))
 selectors=[];q=m.selector("oblique",e)
 for key,val in (("source_ids",["S1","S0"]),("case",True),("fraction_bits",192),("captured_result_sha256","0"*64),("parent_receipt_sha256","0"*64),("model","GPU")):
  qq=copy.deepcopy(q);qq[key]=val;r=m.evaluate("oblique",qq,e,a);scope(r);assert r["status"]=="STOP_INPUT"and r["new_integer_word_decodes"]==r["new_integer_root_certificates"]==0
  selectors.append(dict(field=key,result=r))
 api=[];reader=m.retained
 try:
  for message in ("SIMULATED_MISSING_DEPENDENCY","SIMULATED_SHA_DRIFT"):
   def fail():raise ValueError(message)
   m.retained=fail;r=m.run("oblique",q);scope(r);assert r["status"]=="STOP_DEPENDENCY";api.append(r)
 finally:m.retained=reader
 return dict(status="PASS",summary=dict(original_cases=6,SOURCE=12,endpoint_descriptors=108,word_decodes=504,new_interval_segment_norms=24,new_integer_root_certificates=48,upstream_STOP=38,negative_packets=len(neg),synthetic_interval_stages=5,synthetic_corner_checks=320,root_capacity_STOP=4,selectors=6,API_simulated=2,dependency_pins=len(pins),exact_contact_admitted=0,phase_certified=False,GPU_used=False,full_costs="UNKNOWN_NOT_ZERO",QA_seconds_not_benchmark=True),
  evidence=dict(positive=positive,upstream=upstream,negative_packets=neg,synthetic_controls=controls,root_capacity=errors,selectors=selectors,API_negative=api))
if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
