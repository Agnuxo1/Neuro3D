"""New ledger decision tests; consume old sealed results, never call old numeric code."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_sealed_terminal_ledger_CPU_v1 as m

def f(x):return F(*x)
def oracle(plan):
 # Independent decision: ignore the single certified previous zero; require retained
 # set to be exactly the target point at 1. No sorting or intersection computation.
 remaining=[];zero=0
 for row in plan["rows"]:
  r=row["result"]
  if r["status"]not in (m.EXCLUDE,m.KEEP,m.MISS):return "STOP"
  if r["status"]==m.EXCLUDE:
   assert r["contact"]["primitive_id"]==plan["token"]["previous_primitive_id"]
   assert f(r["contact"]["t"])==0;zero+=1
  elif r["status"]==m.KEEP:remaining.append(r["contact"])
 if zero!=1:return "STOP"
 if len(remaining)!=1:return "STOP"
 c=remaining[0]
 return "CLEAR"if c["primitive_id"]==plan["target_primitive_id"]and f(c["t"])==1 and c["point_BU"]==plan["to_BU"]else"STOP"

def check(r):
 assert all(r[k]is False for k in ("full_path_visibility_certified","scene_authenticated",
   "native_hit_coverage_certified","phase_certified","physical_field_certified","GPU_used",
   "Bpy_used","object_wide_skip","SOURCE_merged"))
 assert r["phase_error_bound"]is None
 assert all(r[k]==0 for k in ("new_intersections","new_guard_calls","new_root_calls","new_native_RN","old_numeric_replays"))
 assert r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["epsilon_BU"]==r["t_min"]==[0,1]

def suite():
 e,rows,controls,pins=m.retained();positive=[];upstream=[]
 for k,x in e.items():
  q=m.selector(k,e);r=m.evaluate(k,q,e,rows);check(r)
  if x["result"]["status"]!="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY":
   assert r["status"]=="STOP_UPSTREAM"and r["ledger_rows_audited"]==0
   upstream.append(dict(id=k,result=r));continue
  assert r["status"]=="CPU_DECLARED_BOTH_SOURCE_TERMINAL_CLEAR_ONLY"
  assert [v["source_id"]for v in r["source_decisions"]]==["S0","S1"]
  for v in r["source_decisions"]:
   assert oracle(v["plan"])=="CLEAR";check(v["result"])
   assert v["result"]["ledger_rows_audited"]==len(x["scene"]["triangles"])
  assert r["source_decisions"][0]["plan"]["token"]!=r["source_decisions"][1]["plan"]["token"]
  positive.append(dict(id=k,request=q,result=r))
 assert len(positive)==6 and len(upstream)==38
 base=positive[[p["id"]for p in positive].index("oblique")]["result"]["source_decisions"][0]["plan"]
 negatives=[]
 def neg(name,plan,expected=None,unsealed=False):
  r=m.consume(plan,m.digest(base)if unsealed else m.digest(plan));check(r)
  assert r["declared_terminal_clear"]is False
  if expected:assert r["status"]==expected,(name,r)
  negatives.append(dict(name=name,scope="IN_MEMORY_NEGATIVE_NOT_ORIGINAL_SNAPSHOT",plan=plan,
       expected_seal="ORIGINAL"if unsealed else"NEW_EXPLICIT_TEST_CONTEXT",result=r))
 # Strong exact seal refuses every drift, even when a altered value is mathematically equivalent.
 for name,mut in (
  ("lost_target",lambda p:p["rows"].pop(0)),
  ("duplicate_previous",lambda p:p["rows"].append(copy.deepcopy(p["rows"][-1]))),
  ("source_replay",lambda p:p["token"].update(source_id="S1")),
  ("target_alias",lambda p:p.update(target_primitive_id=True)),
  ("bool_launch",lambda p:p["token"]["launch_point_BU"][0].__setitem__(0,True)),
  ("missing_no_contact",lambda p:p.update(rows=[])),
  ("stale_scene",lambda p:p.update(scene_sha256="0"*64)),
  ("shifted_origin",lambda p:p["from_BU"][0].__setitem__(1,2)),
  ("extra_epsilon",lambda p:p.update(epsilon_BU=[1,2**60]))):
  p=copy.deepcopy(base);mut(p);neg("sealed_"+name,p,"STOP_INPUT",True)
 # Separate test scope reseals mutations to test semantic validation beyond SHA.
 for name,mut in (
  ("lost_target",lambda p:p["rows"].pop(0)),
  ("duplicate_primitive",lambda p:p["rows"][0].update(primitive_id=1)),
  ("bool_t",lambda p:p["rows"][0]["result"]["contact"]["t"].__setitem__(0,True)),
  ("noncanonical_t",lambda p:p["rows"][0]["result"]["contact"].update(t=[2,2])),
  ("bool_token_version",lambda p:p["token"].update(version=True)),
  ("bool_token_point",lambda p:p["token"]["launch_point_BU"][0].__setitem__(0,True)),
  ("source_token",lambda p:p["token"].update(source_id="S1")),
  ("row_source",lambda p:p["rows"][0].update(source_id="S1")),
  ("off_primitive",lambda p:p["rows"][0]["result"]["contact"]["barycentric"].__setitem__(0,[1,1])),
  ("exclude_target",lambda p:p["rows"][0]["result"].update(status=m.EXCLUDE,action="EXCLUDE_THIS_ZERO_POINT_ONLY",exclusion_allowed=True))):
  p=copy.deepcopy(base);p["scope"]="NEW_SYNTHETIC_DECISION_CONTROL_ONLY";mut(p);neg("semantic_"+name,p,"STOP_INPUT")
 # Lost target reported as NO_CONTACT must STOP, never accept launch exclusion alone.
 p=copy.deepcopy(base);p["scope"]="NEW_SYNTHETIC_DECISION_CONTROL_ONLY"
 p["rows"][0]["result"].update(status=m.MISS,action="NO_CONTACT",contact=None,exclusion_allowed=False)
 neg("target_reported_miss",p,"STOP_TARGET_MISSING")
 # Preserve the focused REAL failure as a permanent typed captured-token regression.
 for field,mutation in (
  ("bool_result_token",lambda p:p["rows"][0]["result"]["launch_credential"]["launch_point_BU"][0].__setitem__(0,True)),
  ("guard_selector_bool_segment",lambda p:p["rows"][0]["request"].update(segment=True)),
  ("guard_selector_extra_bias",lambda p:p["rows"][0]["request"].update(t_min=[1,2**60])),
  ("guard_selector_stale_record",lambda p:p["rows"][0]["request"].update(record_sha256="0"*64))):
  p=copy.deepcopy(base);mutation(p);neg(field,p,"STOP_INPUT")
 synthetic=[]
 for c in controls:
  k=c["case"];source=c["source_id"]
  original=next(v for p in positive if p["id"]==k for v in p["result"]["source_decisions"]if v["source_id"]==source)["plan"]
  plan=copy.deepcopy(original);plan["scope"]="NEW_SYNTHETIC_DECISION_CONTROL_ONLY"
  pid=c["triangle"]["primitive_id"]
  row=dict(id=k,source_id=source,primitive_id=pid,request={},result=copy.deepcopy(c["result"]))
  if c["name"]in ("adjacent_same_object_at_zero","near_same_object_t2m60"):
   plan["triangles"].append(copy.deepcopy(c["triangle"]));plan["rows"].append(row)
   expected="STOP_BLOCKED_TERMINAL"
  elif c["name"].startswith("coplanar"):
   # Feed the already captured unresolved guard verdict, not its alternate segment.
   plan["rows"]=[row if v["primitive_id"]==pid else v for v in plan["rows"]]
   expected="STOP_UNRESOLVED_CONTACT"
  else:
   # Previous-id positive contact cannot impersonate the original certified zero.
   # Original launch triangle is unchanged, so its captured translated-face point
   # cannot pass point-on-original-primitive validation.
   plan["rows"]=[row if v["primitive_id"]==pid else v for v in plan["rows"]]
   expected="STOP_INPUT"
  r=m.consume(plan,m.digest(plan));check(r)
  assert not r["declared_terminal_clear"]and r["status"]==expected,(c["name"],r)
  if expected=="STOP_BLOCKED_TERMINAL":
   assert r["nearest_blocker"]["t"]==c["result"]["contact"]["t"]
   assert len(r["contacts_kept"])==2 and oracle(plan)=="STOP"
  synthetic.append(dict(case=k,source_id=source,name=c["name"],
   label="NEW_DECISION_CONTEXT_USING_OLD_CAPTURE_NOT_ORIGINAL_PROMOTION",plan=plan,result=r))
 assert len(synthetic)==16
 # Exact target-time tie from a distinct primitive on the same object remains blocked.
 p=copy.deepcopy(base);p["scope"]="NEW_SYNTHETIC_DECISION_CONTROL_ONLY"
 t=copy.deepcopy(p["triangles"][0]);t["primitive_id"]=202;p["triangles"].append(t)
 row=copy.deepcopy(p["rows"][0]);row["primitive_id"]=202;row["result"]["contact"]["primitive_id"]=202;p["rows"].append(row)
 r=m.consume(p,m.digest(p));assert r["status"]=="STOP_BLOCKED_TERMINAL"and r["nearest_blocker"]["t"]==[1,1]
 synthetic.append(dict(name="terminal_same_time_distinct_primitive_tie",label="NEW_SYNTHETIC_DECISION_CONTROL_ONLY",plan=p,result=r))
 # Closed API binding and missing S1: neither SOURCE can silently replace the other.
 selectors=[]
 q=m.selector("oblique",e)
 for key,val in (("source_ids",["S1","S0"]),("source_ids",["S0"]),("segment",True),
   ("scene_sha256","0"*64),("policy","OBJECT_SKIP"),("epsilon_BU",[1,2**60])):
  qq=copy.deepcopy(q);qq[key]=val;r=m.evaluate("oblique",qq,e,rows)
  assert r["status"]=="STOP_INPUT";selectors.append(dict(field=key,result=r))
 onlyS0=[r for r in rows if r["source_id"]=="S0"];r=m.evaluate("oblique",q,e,onlyS0)
 assert r["status"]=="STOP_SOURCE_TERMINAL"and not r["declared_terminal_clear"]
 lostSOURCE=dict(result=r,label="IN_MEMORY_S1_REMOVAL_NOT_ORIGINAL")
 api=[];reader=m.retained
 try:
  def missing():raise OSError("SIMULATED_MISSING_DEPENDENCY")
  def drift():raise ValueError("SIMULATED_SHA_DRIFT")
  for replacement in (missing,drift):
   m.retained=replacement;r=m.run("oblique",q);assert r["status"]=="STOP_DEPENDENCY";api.append(r)
 finally:m.retained=reader
 summary=dict(retained_records=44,upstream_stops_preserved=38,positive_scene_packets=6,
  separate_SOURCE_packets=12,original_rows_audited=sum(v["result"]["ledger_rows_audited"]for v in positive),
  synthetic_decision_controls=len(synthetic),negative_packets=len(negatives),
  selector_negatives=len(selectors),lost_SOURCE_rejections=1,API_negative=len(api),dependency_pins=len(pins),
  new_intersections=0,new_guard_calls=0,new_root_calls=0,new_native_RN=0,old_numeric_replays=0,
  full_costs="UNKNOWN_NOT_ZERO",QA_seconds_not_benchmark=True,GPU_used=False,phase_certified=False)
 return dict(status="PASS",summary=summary,evidence=dict(positive=positive,upstream=upstream,
  synthetic_controls=synthetic,negative_packets=negatives,selector_negatives=selectors,lost_SOURCE=lostSOURCE,API_negative=api))
if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
