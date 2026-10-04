"""Focused stdlib tests; all synthetic stages labelled, never physical admission."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_signed_cycle_branch_HOST_v1 as m
def safe(r):
 assert all(r[k]is False for k in m.FALSE_FLAGS)and r["phase_error_bound"]is None
 assert r["old_numeric_replays"]==r["old_geometry_replays"]==r["old_root_replays"]==r["old_encoder_replays"]==r["old_guard_replays"]==r["new_input_word_decodes"]==0
 assert r["RAD_conversion_performed"]is False and r["pi_trig_used"]is False
def zero(r):
 safe(r);assert r["new_integer_floor_evaluations"]==r["new_endpoint_translations"]==0
def main():
 e,a,pins=m.retained();ev={x:[]for x in ["positive","upstream","mutations","selectors","stages","capacities","synthetic_contexts","synthetic_cross_case","public_API","API_negative"]}
 for k in sorted(e):
  q=m.selector(k,e);r=m.evaluate(k,q,e,a);safe(r)
  if k in a:
   assert r["HOST_branch_verified"]is True and r["new_integer_floor_evaluations"]==4 and r["new_endpoint_translations"]==4
   for i,s in enumerate(r["SOURCE_results"]):
    assert s["coverage"]==e[k]["SOURCE_results"][i]["coverage"]and s["original_cap_rad_HOST_only"]==e[k]["SOURCE_results"][i]["original_cap_rad_HOST_only"]
   ev["positive"].append(dict(id=k,request=q,result=r))
  else:
   zero(r);assert r["status"]=="STOP_UPSTREAM";ev["upstream"].append(dict(id=k,result=r))
 k="oblique";q=m.selector(k,e);ref=e[k]
 mutations=[]
 def mutation(label,change):
  x=copy.deepcopy(ref);change(x);assert m.digest(x)!=m.digest(ref)
  r=m.evaluate(k,q,e,a,x);zero(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="sealed_same_signed_result"
  ev["mutations"].append(dict(id=label,result=r,received_sha256=m.digest(x)))
 mutation("other_query_ref1000",lambda x:x.update(query_sha256=e["shared_ref1000"]["query_sha256"]))
 mutation("same_scene_other_result",lambda x:x.update(SOURCE_results=e["shared_ref1000"]["SOURCE_results"]))
 mutation("SOURCE_reverse",lambda x:x["SOURCE_results"].reverse())
 mutation("coverage_cross_SOURCE",lambda x:x["SOURCE_results"][0].update(coverage=x["SOURCE_results"][1]["coverage"]))
 mutation("endpoint_bool",lambda x:x["SOURCE_results"][0]["argument"]["signed_cycles"][0].__setitem__(0,True))
 mutation("endpoint_float",lambda x:x["SOURCE_results"][0]["argument"]["signed_cycles"][0].__setitem__(0,1.0))
 mutation("phase_error_from_width",lambda x:x.update(phase_error_bound=x["SOURCE_results"][0]["argument"]["interval_width_cycles"]))
 mutation("RAD_cap_relax",lambda x:x["SOURCE_results"][0].update(original_cap_rad_HOST_only=[1,1]))
 mutation("reference_truth_claim",lambda x:x.update(reference_truth_verified=True))
 mutation("phase_claim",lambda x:x.update(phase_certified=True))
 mutation("inputbytes_drift",lambda x:x.update(input_buffer_sha256="0"*64))
 mutation("extra_reduced_field",lambda x:x.update(reduced_phase_RAD=[0,1]))
 for label,edit in [
  ("extra",lambda z:z.update(unit="RAD")),("model",lambda z:z.update(model="other")),
  ("SOURCE_reverse",lambda z:z.update(source_ids=["S1","S0"])),
  ("hash_type",lambda z:z.update(signed_result_sha256=True)),("hash",lambda z:z.update(signed_result_sha256="0"*64)),
  ("oversize",lambda z:z.update(case="x"*513))]:
  z=copy.deepcopy(q);edit(z);r=m.evaluate(k,z,e,a);zero(r);assert r["status"]=="STOP_INPUT";ev["selectors"].append(dict(id=label,result=r))
 stages=[
  ("positive",F(7,3),F(5,2),True,2),("negative",F(-5,2),F(-7,3),True,-3),
  ("zero_singleton",F(0),F(0),True,0),("negative_integer_singleton",F(-2),F(-2),True,-2),
  ("tiny_straddle_zero",F(-1,2**100),F(1,2**100),False,None),
  ("upper_positive_integer",F(1)-F(1,2**100),F(1),False,None),
  ("upper_negative_integer",F(-2)-F(1,2**100),F(-2),False,None),
  ("lower_integer",F(1),F(1)+F(1,2**100),True,1),
  ("multi_turn",F(-5,2),F(5,2),False,None),
  ("tiny_stable_negative",F(-1)+F(1,2**100),F(-1)+F(2,2**100),True,-1)]
 for label,lo,hi,unique,integer in stages:
  packet=dict(unit="CYCLES",closed_interval=[m.pair(lo),m.pair(hi)]);r=m.base();z=m.branch(packet,r);safe(r)
  assert z["branch_unique"]is unique and z["branch_integer"]==integer
  assert r["new_integer_floor_evaluations"]==2 and r["new_endpoint_translations"]==(2 if unique else 0)
  ev["stages"].append(dict(id=label,label="SYNTHETIC_BRANCH_STAGE_ONLY_NOT_SCENE_OR_PHASE_ADMISSION",packet=packet,result=z,counters=r))
 for label,p in [
  ("RAD_unit",dict(unit="RAD",closed_interval=[[0,1],[0,1]])),
  ("bool_rational",dict(unit="CYCLES",closed_interval=[[False,1],[0,1]])),
  ("float_rational",dict(unit="CYCLES",closed_interval=[[0.0,1],[0,1]])),
  ("zero_den",dict(unit="CYCLES",closed_interval=[[0,0],[0,1]])),
  ("unreduced",dict(unit="CYCLES",closed_interval=[[0,2],[0,1]])),
  ("reversed",dict(unit="CYCLES",closed_interval=[[1,1],[0,1]])),
  ("bits129",dict(unit="CYCLES",closed_interval=[[1,2**128],[1,1]])),
  ("magnitude",dict(unit="CYCLES",closed_interval=[[2**64+1,1],[2**64+1,1]])),
  ("extra_phase",dict(unit="CYCLES",closed_interval=[[0,1],[0,1]],phase_error_bound=[0,1]))]:
  r=m.base()
  try:m.branch(p,r)
  except(ValueError,TypeError)as ex:reason=str(ex)
  else:raise AssertionError("expected STOP "+label)
  zero(r);ev["capacities"].append(dict(id=label,packet=p,status="STOP_INPUT",reason=reason,counters=r))
 for label,change in [
  ("physical_claim",lambda x:x.update(phase_certified=True)),
  ("SOURCE_coverage",lambda x:x["SOURCE_results"][0]["coverage"].update(source_id="S1")),
  ("SOURCE_order",lambda x:x["SOURCE_results"].reverse()),
  ("reference_not_shared",lambda x:x.update(reference_is_shared_declared_scalar=False))]:
  x=copy.deepcopy(ref);change(x);context=copy.deepcopy(e);context[k]=x
  r=m.evaluate(k,m.selector(k,context),context,a);zero(r);assert r["status"]=="STOP_INPUT"
  ev["synthetic_contexts"].append(dict(id=label,label="SYNTHETIC_TRUSTED_HELPER_CONTEXT_ONLY_NOT_PUBLIC_SCENE_ADMISSION",result=r))
 x=copy.deepcopy(ref);x["SOURCE_results"][1]["argument"]["signed_cycles"]=[[-1,2**100],[1,2**100]]
 context=copy.deepcopy(e);context[k]=x;r=m.evaluate(k,m.selector(k,context),context,a);safe(r)
 assert r["status"]=="STOP_BRANCH_CROSSING"and r["HOST_branch_verified"]is False and r["new_integer_floor_evaluations"]==4 and r["new_endpoint_translations"]==2
 assert r["SOURCE_results"][0]["branch"]["branch_unique"]is True and r["SOURCE_results"][1]["branch"]["closed_residual_interval"]is None
 ev["synthetic_cross_case"].append(dict(id="S1_cross_S0_unique",label="SYNTHETIC_TRUSTED_HELPER_CONTEXT_ONLY_NOT_PUBLIC_SCENE_ADMISSION",result=r))
 pk="shared_ref1000";pq=m.selector(pk,e);r=m.run(pk,pq);safe(r)
 assert r==m.evaluate(pk,pq,e,a)and r["HOST_branch_verified"]is True
 ev["public_API"].append(dict(id="original_shared_ref1000",result=r))
 r=m.run(pk,pq,ref);zero(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="sealed_same_signed_result"
 ev["public_API"].append(dict(id="other_query_result_STOP",result=r))
 saved=m.retained
 for label in ("missing","drift"):
  def fail():raise OSError("SIMULATED_"+label)
  m.retained=fail
  try:r=m.run(k,q)
  finally:m.retained=saved
  zero(r);assert r["status"]=="STOP_DEPENDENCY";ev["API_negative"].append(dict(id=label,result=r))
 summary={key:len(v)for key,v in ev.items()};summary.update(dependency_pins=len(pins),SOURCE_results=12,new_original_floor_evaluations=24,new_original_translations=24,new_stage_floor_evaluations=20,new_stage_translations=12,new_cross_case_floor_evaluations=4,new_cross_case_translations=2,new_public_API_floor_evaluations=4,new_public_API_translations=4,new_public_contrast_floor_evaluations=4,new_public_contrast_translations=4,full_costs="UNKNOWN_NOT_ZERO")
 print(json.dumps(dict(status="PASS",summary=summary,evidence=ev),sort_keys=True,separators=(",",":"),allow_nan=False))
if __name__=="__main__":main()
