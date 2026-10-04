"""Typed scene join and signed cycles; no retained numerical computation replays."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import sys,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_scene_reference_argument_interval_HOST_v1 as m
def scope(r):
 assert all(r[k]is False for k in ("exact_contact_allowed","phase_certified","phase_accuracy_budget_admitted","reference_truth_verified","gauge_provenance_verified","material_phase_verified","scene_authenticated","native_IEEE_RN_graph_certified","GPU_used","Bpy_used","RT_used","physical_field_certified","computed_hilo_collapse_allowed","SOURCE_merged"))
 assert r["phase_error_bound"]is None and r["full_costs"]=="UNKNOWN_NOT_ZERO"
 assert all(r[k]==0 for k in ("old_numeric_replays","old_encoder_replays","old_geometry_replays","old_guard_replays","old_root_replays"))
def verify(z):
 l=tuple(F(*x)for x in z["length_BU"]);ref=tuple(F(*x)for x in z["reference_BU"]);lam=F(*z["lambda_BU"]);c=tuple(F(*x)for x in z["signed_cycles"])
 for x,y in product(l,ref):assert c[0]<=(x-y)/lam<=c[1]
 assert c[1]-c[0]==F(*z["interval_width_cycles"])
 assert c[1]-c[0]==F(*z["contributions"]["length_interval_width_cycles"])+F(*z["contributions"]["reference_interval_width_cycles"])
 assert z["phase_error_bound"]is None and z["phase_accuracy_budget_admitted"]is False
def reseal(p):
 p["manifest"]["buffer_sha256"]=m.hashlib.sha256(bytes.fromhex(p["buffer_hex"])).hexdigest();p["manifest_sha256"]=m.digest(p["manifest"])
def suite():
 e,a,g,pins=m.retained();positive=[];up=[]
 for k in e:
  r=m.evaluate(k,m.selector(k,e,g),e,a,g);scope(r)
  if k not in a:assert r["status"]=="STOP_UPSTREAM"and r["new_input_word_decodes"]==r["new_rational_endpoint_subtractions"]==r["new_rational_endpoint_divisions"]==0;up.append(dict(id=k,result=r));continue
  assert r["argument_interval_enclosure_verified"],(k,r)
  assert (r["new_input_word_decodes"],r["new_rational_endpoint_subtractions"],r["new_rational_endpoint_divisions"])==(2,4,4)
  assert r["cap_used_for_cycles_or_phase"]is False and r["modulo_or_pi_or_trig_used"]is False
  for s in r["SOURCE_results"]:verify(s["argument"]);assert s["cap_used_for_cycles_or_phase"]is False
  if k=="shared_ref1000":assert all(F(*s["argument"]["signed_cycles"][1])<0 for s in r["SOURCE_results"])
  positive.append(dict(id=k,request=m.selector(k,e,g),result=r))
 assert len(positive)==6 and len(up)==38
 ref=dict(length=e["oblique"],geometry=g["oblique"]);neg=[]
 for name,change in (
  ("other_reference_same_scene",lambda b:b.update(geometry=g["shared_ref1000"])),
  ("other_direction_case",lambda b:b.update(length=e["direction_scaled"])),
  ("input_hash",lambda b:b["length"].update(input_buffer_sha256="0"*64)),
  ("scene_hash",lambda b:b["length"].update(scene_sha256="0"*64)),
  ("SOURCE_order",lambda b:b["length"]["SOURCE_results"].reverse()),
  ("length_lower",lambda b:b["length"]["SOURCE_results"][0]["total_length_BU"].__setitem__(0,[0,1])),
  ("fake_reference_radius",lambda b:b["geometry"]["manifest"].update(reference_radius_BU=[1,2**80])),
  ("gauge_assertion",lambda b:b["geometry"]["manifest"].update(gauge_verified=True)),
  ("rad_cap_relaxed",lambda b:b["geometry"]["manifest"].update(relative_width_cap_rad_HOST_only=[1,1])),
  ("unit_alias",lambda b:next(f for f in b["geometry"]["manifest"]["fields"]if f["path"]=="query/lambda_BU").update(unit="mm")),
  ("lambda_metadata",lambda b:next(f for f in b["geometry"]["manifest"]["fields"]if f["path"]=="query/lambda_BU").update(original_rational=[1,4])),
  ("lambda_word",lambda b:b["geometry"].update(buffer_hex=b["geometry"]["buffer_hex"][:-16]+"0000803e"+b["geometry"]["buffer_hex"][-8:])),
  ("phase_claim",lambda b:b["length"].update(phase_certified=True)),
  ("extra_bundle",lambda b:b.update(reference=0))):
  b=copy.deepcopy(ref);change(b);reseal(b["geometry"]);assert m.digest(b)!=m.digest(ref),(name,"must_change")
  r=m.evaluate("oblique",m.selector("oblique",e,g),e,a,g,b);scope(r)
  assert r["status"]=="STOP_INPUT"and not r["SOURCE_results"]and r["new_input_word_decodes"]==r["new_rational_endpoint_subtractions"]==r["new_rational_endpoint_divisions"]==0
  neg.append(dict(name=name,bundle=b,result=r))
 contexts=[]
 # Corrupt trusted helper contexts only to exercise join predicates independently
 # of the outer byte seal. These are synthetic internal stages, NOT public admission.
 for name,change,reason,decodes in (
  ("scene",lambda ee,gg:gg["oblique"]["manifest"].update(scene_sha256="0"*64),"join:scene_sha256",0),
  ("query",lambda ee,gg:gg["oblique"]["manifest"].update(query_sha256="0"*64),"join:query_sha256",0),
  ("input",lambda ee,gg:ee["oblique"].update(input_buffer_sha256="0"*64),"join:original_input_bytes",0),
  ("SOURCE",lambda ee,gg:gg["oblique"]["manifest"].update(source_ids=["S1","S0"]),"case_SOURCE_join",0),
  ("unit",lambda ee,gg:next(f for f in gg["oblique"]["manifest"]["fields"]if f["path"]=="query/lambda_BU").update(unit="mm"),"original_BU_units",0),
  ("lambda_zero",lambda ee,gg:gg["oblique"].update(buffer_hex=gg["oblique"]["buffer_hex"][:-16]+"00000000"+gg["oblique"]["buffer_hex"][-8:]),"zero_input_conversion_error",1)):
  ee=copy.deepcopy(e);gg=copy.deepcopy(g);change(ee,gg);reseal(gg["oblique"])
  if name=="lambda_zero":
   # Isolated input decoder stage: the public/full join already rejects changed
   # bytes earlier. No rebinding of the original input hash or scene admission.
   r=m.base()
   try:m.optical_inputs(gg["oblique"],r);raise AssertionError("lambda_decoder_accepted")
   except ValueError as ex:r.update(status="STOP_INPUT",reason=str(ex))
  else:r=m.evaluate("oblique",m.selector("oblique",ee,gg),ee,a,gg)
  scope(r)
  assert r["status"]=="STOP_INPUT"and r["reason"]==reason and r["new_input_word_decodes"]==decodes and r["new_rational_endpoint_subtractions"]==r["new_rational_endpoint_divisions"]==0,(name,r)
  contexts.append(dict(name=name,label="SYNTHETIC_TRUSTED_HELPER_CONTEXT_ONLY_NOT_PUBLIC_SCENE_ADMISSION",expected_reason=reason,result=r))
 stages=[]
 for name,L,R,lam in (("shared1000",(F(2),F(3)),(F(1000),F(1000)),F(1,8)),
  ("reference_uncertainty",(F(2),F(3)),(F(1),F(3,2)),F(1,8)),
  ("tiny_signed",(F(0),F(1,2**60)),(F(1,2**61),F(1,2**61)),F(1,8)),
  ("nonbinary",(F(1,3),F(2,3)),(F(-1,3),F(1,7)),F(3,5))):
  r=m.base();z=m.argument(L,R,lam,r);scope(r);verify(z)
  stages.append(dict(name=name,label="SYNTHETIC_ARGUMENT_STAGE_ONLY_NOT_SCENE_OR_PHASE_ADMISSION",result=z,counters=r))
 capacity=[]
 for name,L,R,lam in (("negative_lambda",(F(1),F(2)),(F(0),F(0)),F(-1)),
  ("zero_lambda",(F(1),F(2)),(F(0),F(0)),F(0)),("lambda_interval",(F(1),F(2)),(F(0),F(0)),(F(1),F(2))),
  ("reversed_L",(F(2),F(1)),(F(0),F(0)),F(1)),("negative_length",(F(-1),F(1)),(F(0),F(0)),F(1)),
  ("reversed_reference",(F(1),F(2)),(F(1),F(0)),F(1)),("huge",(F(2**513),F(2**513+1)),(F(0),F(0)),F(1))):
  r=m.base()
  try:m.argument(L,R,lam,r);raise AssertionError("accepted:"+name)
  except ValueError as ex:capacity.append(dict(name=name,reason=str(ex),counters=r))
 selectors=[];q=m.selector("oblique",e,g)
 for key,val in (("source_ids",["S1","S0"]),("case",True),("lambda",[1,4]),("geometry_packet_sha256","0"*64),("parent_receipt_sha256","0"*64),("phase_cap",1)):
  qq=copy.deepcopy(q);qq[key]=val;r=m.evaluate("oblique",qq,e,a,g);scope(r);assert r["status"]=="STOP_INPUT"and r["new_input_word_decodes"]==0;selectors.append(dict(field=key,result=r))
 api=[];reader=m.retained
 try:
  for message in ("SIMULATED_MISSING_DEPENDENCY","SIMULATED_SHA_DRIFT"):
   def fail():raise ValueError(message)
   m.retained=fail;r=m.run("oblique",q);scope(r);assert r["status"]=="STOP_DEPENDENCY";api.append(r)
 finally:m.retained=reader
 return dict(status="PASS",summary=dict(original_cases=6,SOURCE=12,input_word_decodes=12,new_rational_endpoint_subtractions=24,new_rational_endpoint_divisions=24,upstream_STOP=38,negative_bundles=len(neg),synthetic_argument_stages=4,stage_capacity_STOP=7,selectors=6,API_simulated=2,dependency_pins=len(pins),phase_budget_admitted=0,physical_phase_certified=False,GPU_used=False,full_costs="UNKNOWN_NOT_ZERO",QA_seconds_not_benchmark=True),
  evidence=dict(positive=positive,upstream=up,negative_bundles=neg,synthetic_join_contexts=contexts,synthetic_stages=stages,stage_capacity=capacity,selectors=selectors,API_negative=api))
if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
