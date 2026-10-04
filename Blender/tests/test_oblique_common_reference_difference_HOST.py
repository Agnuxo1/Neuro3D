"""Original captured cases vs separately labelled synthetic common-R stages."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_common_reference_difference_HOST_v1 as m
def safe(r):
 assert all(r[k]is False for k in m.FLAGS)and r["phase_error_bound"]is None
 assert all(r[k]==0 for k in ("old_numeric_replays","old_encoder_replays","old_geometry_replays","old_guard_replays","old_root_replays","new_input_word_decodes"))
 assert r["RAD_conversion_performed"]is False and r["pi_trig_used"]is False
def zero(r):
 safe(r);assert r["new_length_endpoint_subtractions"]==r["new_relative_endpoint_divisions"]==r["new_signed_cycle_contrast_subtractions"]==0
def main():
 e,a,j,pins=m.retained();ev={k:[]for k in ("positive","upstream","mutations","synthetic_contexts","selectors","stages","capacities","public_API","API_negative")}
 for k in sorted(e):
  q=m.selector(k,e,j);r=m.evaluate(k,q,e,a,j);safe(r)
  if k in a:
   assert r["HOST_relative_interval_verified"]is True and r["new_length_endpoint_subtractions"]==r["new_relative_endpoint_divisions"]==r["new_signed_cycle_contrast_subtractions"]==2
   assert [v["source_id"]for v in r["SOURCE_inputs"]]==["S0","S1"]
   ev["positive"].append(dict(id=k,request=q,result=r))
  else:zero(r);assert r["status"]=="STOP_UPSTREAM";ev["upstream"].append(dict(id=k,result=r))
 results={x["id"]:x["result"]for x in ev["positive"]}
 assert results["oblique"]["relative"]["closed_signed_relative_cycles"]==results["shared_ref1000"]["relative"]["closed_signed_relative_cycles"]
 assert results["oblique"]["query_sha256"]!=results["shared_ref1000"]["query_sha256"]
 k="oblique";q=m.selector(k,e,j);ref=dict(branch=e[k],signed=j[k])
 def mutation(label,change):
  x=copy.deepcopy(ref);change(x);assert m.digest(x)!=m.digest(ref)
  r=m.evaluate(k,q,e,a,j,x);zero(r);assert r["reason"]=="sealed_same_original_bundle"
  ev["mutations"].append(dict(id=label,result=r,received_sha256=m.digest(x)))
 mutation("other_query_signed",lambda x:x.update(signed=j["shared_ref1000"]))
 mutation("other_query_branch",lambda x:x.update(branch=e["shared_ref1000"]))
 mutation("S1_reference",lambda x:x["signed"]["SOURCE_results"][1]["argument"].update(reference_BU=[[1,1],[1,1]]))
 mutation("S1_lambda",lambda x:x["signed"]["SOURCE_results"][1]["argument"].update(lambda_BU=[1,4]))
 mutation("reverse_SOURCE",lambda x:x["signed"]["SOURCE_results"].reverse())
 mutation("inputbytes",lambda x:x["signed"].update(input_buffer_sha256="0"*64))
 mutation("RAD_width_promote",lambda x:x["signed"].update(phase_error_bound=x["signed"]["SOURCE_results"][0]["argument"]["interval_width_cycles"]))
 mutation("reference_truth",lambda x:x["signed"].update(reference_truth_verified=True))
 mutation("cap_relax",lambda x:x["signed"].update(original_relative_cap_rad_HOST_only=[1,1]))
 mutation("branch_drift",lambda x:x["branch"]["SOURCE_results"][0]["branch"].update(branch_integer=0))
 mutation("length_bool",lambda x:x["signed"]["SOURCE_results"][0]["argument"]["length_BU"][0].__setitem__(0,True))
 mutation("extra_phase",lambda x:x.update(relative_phase_RAD=[0,1]))
 for label,edit in (
  ("extra",lambda x:x.update(unit="RAD")),("reverse_SOURCE",lambda x:x.update(source_ids=["S1","S0"])),
  ("hash_bool",lambda x:x.update(branch_result_sha256=True)),("hash",lambda x:x.update(signed_result_sha256="0"*64)),
  ("long",lambda x:x.update(case="x"*513)),("parent",lambda x:x.update(parent_receipt_sha256="0"*64))):
  qq=copy.deepcopy(q);edit(qq);r=m.evaluate(k,qq,e,a,j);zero(r);assert r["status"]=="STOP_INPUT"
  ev["selectors"].append(dict(id=label,result=r))
 contexts=[
  ("different_reference","same_SOURCE_lambda_reference",lambda s,b:s["SOURCE_results"][1]["argument"].update(reference_BU=[[1,1],[1,1]])),
  ("different_lambda","same_SOURCE_lambda_reference",lambda s,b:s["SOURCE_results"][1]["argument"].update(lambda_BU=[1,4])),
  ("reference_not_shared","common_declared_reference_only",lambda s,b:s.update(reference_is_shared_declared_scalar=False)),
  ("descriptor_unit_RAD","exact_original_scalar_BU",lambda s,b:s["original_input_descriptors"][0].update(unit="RAD")),
  ("coverage_SOURCE","SOURCE_coverage_caps",lambda s,b:s["SOURCE_results"][0]["coverage"].update(source_id="S1")),
  ("original_scalar_drift","exact_original_scalar_BU",lambda s,b:s["original_input_descriptors"][1].update(original_rational=[1,1]))]
 for label,reason,change in contexts:
  ss=copy.deepcopy(j);bb=copy.deepcopy(e);change(ss[k],bb[k]);bb[k]["signed_result_sha256"]=m.digest(ss[k])
  if label.startswith("descriptor")or label=="original_scalar_drift":bb[k]["original_input_descriptors"]=copy.deepcopy(ss[k]["original_input_descriptors"])
  if label=="coverage_SOURCE":bb[k]["SOURCE_results"][0]["coverage"]=copy.deepcopy(ss[k]["SOURCE_results"][0]["coverage"])
  r=m.evaluate(k,m.selector(k,bb,ss),bb,a,ss);zero(r);assert r["reason"]==reason,(label,r["reason"])
  ev["synthetic_contexts"].append(dict(id=label,label="SYNTHETIC_TRUSTED_HELPER_CONTEXT_ONLY_NOT_PUBLIC_SCENE_ADMISSION",result=r))
 stages=[
  ("positive_ref0",((F(2),F(3)),(F(1),F(3,2))),(F(0),F(0)),F(1,8)),
  ("positive_ref1000",((F(2),F(3)),(F(1),F(3,2))),(F(1000),F(1000)),F(1,8)),
  ("common_uncertain_R",((F(2),F(3)),(F(1),F(3,2))),(F(-1000),F(1000)),F(1,8)),
  ("negative",((F(1),F(3,2)),(F(2),F(3))),(F(3),F(7)),F(2)),
  ("zero",((F(1),F(1)),(F(1),F(1))),(F(0),F(1000)),F(1)),
  ("tiny",((F(1,2**60),F(2,2**60)),(F(3,2**60),F(4,2**60))),(F(-1,2**100),F(1,2**100)),F(1,8))]
 for label,lengths,refR,lam in stages:
  r=m.base();z=m.relative(lengths,refR,lam,r);safe(r)
  assert r["new_length_endpoint_subtractions"]==r["new_relative_endpoint_divisions"]==2 and r["new_signed_cycle_contrast_subtractions"]==0
  assert z["reference_contribution_cycles"]==[0,1]and z["phase_error_bound"]is None
  ev["stages"].append(dict(id=label,label="SYNTHETIC_COMMON_R_STAGE_ONLY_NOT_SCENE_OR_PHASE_ADMISSION",lengths_BU=[[m.pair(v)for v in row]for row in lengths],reference_BU=[m.pair(v)for v in refR],lambda_BU=m.pair(lam),result=z,counters=r))
 assert ev["stages"][0]["result"]["closed_signed_relative_cycles"]==ev["stages"][1]["result"]["closed_signed_relative_cycles"]==ev["stages"][2]["result"]["closed_signed_relative_cycles"]
 defaults=(((F(1),F(1)),(F(2),F(2))),(F(0),F(0)),F(1),"DECLARED_SAME_R")
 bad=[
  ("uncorrelated",defaults[:3]+("INDEPENDENT_R",)),
  ("lambda_zero",(defaults[0],defaults[1],F(0),defaults[3])),
  ("lambda_negative",(defaults[0],defaults[1],F(-1),defaults[3])),
  ("length_negative",(((F(-1),F(1)),defaults[0][1]),defaults[1],defaults[2],defaults[3])),
  ("length_reversed",(((F(2),F(1)),defaults[0][1]),defaults[1],defaults[2],defaults[3])),
  ("reference_reversed",(defaults[0],(F(1),F(0)),defaults[2],defaults[3])),
  ("float_length",(((1.0,F(1)),defaults[0][1]),defaults[1],defaults[2],defaults[3])),
  ("capacity",(((F(1,2**513),F(1)),defaults[0][1]),defaults[1],defaults[2],defaults[3]))]
 for label,params in bad:
  r=m.base()
  try:m.relative(*params[:3],r,correlation=params[3])
  except(ValueError,TypeError)as ex:reason=str(ex)
  else:raise AssertionError("STOP required "+label)
  zero(r);ev["capacities"].append(dict(id=label,status="STOP_INPUT",reason=reason,counters=r))
 pk="shared_ref1000";pq=m.selector(pk,e,j);r=m.run(pk,pq);safe(r);assert r==results[pk];ev["public_API"].append(dict(id="original_shared_ref1000",result=r))
 r=m.run(pk,pq,ref);zero(r);assert r["reason"]=="sealed_same_original_bundle";ev["public_API"].append(dict(id="other_query_bundle_STOP",result=r))
 saved=m.retained
 for label in ("missing","drift"):
  def fail():raise OSError("SIMULATED_"+label)
  m.retained=fail
  try:r=m.run(pk,pq)
  finally:m.retained=saved
  zero(r);assert r["status"]=="STOP_DEPENDENCY";ev["API_negative"].append(dict(id=label,result=r))
 summary={key:len(v)for key,v in ev.items()};summary.update(dependency_pins=len(pins),original_SOURCE_inputs=12,new_length_subtractions=26,new_relative_divisions=26,new_signed_contrast_subtractions=14,full_costs="UNKNOWN_NOT_ZERO")
 print(json.dumps(dict(status="PASS",summary=summary,evidence=ev),sort_keys=True,separators=(",",":"),allow_nan=False))
if __name__=="__main__":main()
