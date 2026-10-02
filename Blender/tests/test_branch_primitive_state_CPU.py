"""NEW synthetic branch-state controls only; no old fixture replay or ray tracer."""
import copy, json, sys, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import branch_primitive_state_CPU_v1 as b
SHA="a"*64  # Declared test label, not evaluated geometry.
MAN=[{"primitive_id":0,"object_id":"folded"},{"primitive_id":1,"object_id":"folded"},
     {"primitive_id":2,"object_id":"other"}]
DATA={"origin":"NEW_SYNTHETIC_CPU_DECLARATIONS","cases":{}}
def root(source="SOURCE_A",branch="root",manifest=MAN):
 return b.Branch(snapshot_sha256=SHA,manifest=manifest,source_id=source,branch_id=branch,model=b.MODEL)
def hit(pid,d=1.,normal=(1.,0.,0.)):
 return {"primitive_id":pid,"distance_BU":d,"normal":list(normal)}
def query(branch,hits,**extra):
 args={"snapshot_sha256":SHA,"source_id":branch.view()["source_id"],"branch_id":branch.view()["branch_id"],"candidates":hits}
 args.update(extra)
 return branch.query(**args)
def mirror(parent,name):
 return parent.fork([{"branch_id":name,"departure_event":"mirror"}])
class Tests(unittest.TestCase):
 def test_fork_siblings_and_sources_are_isolated(self):
  p=root();self.assertEqual(query(p,[hit(0)])["state"],"HIT_PENDING_DEPARTURE")
  kids=p.fork([{"branch_id":"t0","departure_event":"t"},{"branch_id":"r0","departure_event":"r"}])
  self.assertEqual(len(kids),2);left,right=kids
  self.assertEqual(query(left,[hit(1)])["state"],"HIT_PENDING_DEPARTURE")
  left2=mirror(left,"left2")[0]
  a=query(left2,[hit(0)])  # A -> B -> A, same object, legitimate by policy only.
  blocked=query(right,[hit(0)])
  other=query(root(source="SOURCE_B",branch="independent"),[hit(0)])
  self.assertEqual(a["state"],"HIT_PENDING_DEPARTURE")
  self.assertEqual(blocked["state"],"STOP")
  self.assertEqual(other["state"],"HIT_PENDING_DEPARTURE")
  self.assertEqual(right.view()["previous"]["primitive_id"],0)
  self.assertEqual(left2.view()["previous"]["primitive_id"],1)
  DATA["cases"]["isolation"]={"parent":p.view(),"left":a,"right":blocked,"other_SOURCE":other}
 def test_previous_anywhere_in_band_abort_never_skip(self):
  p=root();query(p,[hit(0)]);child=mirror(p,"m")[0]
  hits=[hit(1,1e-12),hit(0,2e-12)]
  result=query(child,hits)
  self.assertEqual(result["state"],"STOP")
  self.assertEqual(result["last_policy"]["tie_primitive_ids"],[0,1])
  self.assertEqual(result["last_policy"]["selected_primitive"],1) # Veto still overrides this.
  with patch.object(b.tie,"resolve_candidates",side_effect=AssertionError("terminal query")):
   retry=query(child,[hit(2)])
  self.assertEqual(retry,result);self.assertEqual(mirror(child,"notcreated"),[])
  DATA["cases"]["thin_gap_return"]={"result":result,"retry":retry,"input":hits}
 def test_other_triangle_and_positive_tiny_root_not_excluded(self):
  p=root();query(p,[hit(0)]);child=mirror(p,"m")[0]
  allowed=query(child,[hit(1,2**-56),hit(0,1.)])
  tiny=query(root(branch="tiny"),[hit(0,2**-56)])
  ambiguous=query(root(branch="amb"),[hit(0,1e-12),hit(2,2e-12)])
  self.assertEqual(allowed["state"],"HIT_PENDING_DEPARTURE")
  self.assertEqual(allowed["last_policy"]["tie_primitive_ids"],[1])
  self.assertEqual(tiny["pending"]["distance_BU"],2**-56)
  self.assertEqual(ambiguous["state"],"STOP")
  self.assertEqual(ambiguous["reason"],"tie_policy:ambiguous_object_or_normal")
  DATA["cases"]["tiny_candidate"]={"other_face":allowed,"source":tiny,"ambiguous":ambiguous}
 def test_binding_changes_reject_before_policy(self):
  results=[]
  for changes in ({"source_id":"SOURCE_B"},{"branch_id":"other"},{"snapshot_sha256":"b"*64}):
   branch=root()
   with patch.object(b.tie,"resolve_candidates",side_effect=AssertionError("binding before policy")):
    result=query(branch,[hit(0)],**changes)
   self.assertEqual(result["reason"],"snapshot_SOURCE_branch_binding_mismatch")
   results.append(result)
  changed=root();changed._previous={"snapshot_sha256":SHA,"primitive_id":0,"departure_event":"r"}
  result=query(changed,[hit(1)])
  self.assertEqual(result["reason"],"state_binding_changed")
  results.append(result);DATA["cases"]["binding"]=results
 def test_atomic_invalid_departures_and_pending_gate(self):
  controls=[]
  for events in ([{"branch_id":"root","departure_event":"mirror"}],
                 [{"branch_id":"dup","departure_event":"t"},{"branch_id":"dup","departure_event":"r"}],
                 [{"branch_id":"x","departure_event":"t"}],
                 [{"branch_id":"x","departure_event":"mirror","extra":0}]):
   p=root();query(p,[hit(0)])
   self.assertEqual(p.fork(events),[]);self.assertEqual(p.view()["state"],"STOP")
   controls.append(p.view())
  p=root();query(p,[hit(0)])
  gate=query(p,[hit(1)]);self.assertEqual(gate["reason"],"pending_hit_requires_departure")
  DATA["cases"]["invalid_departures"]={"atomic":controls,"pending_gate":gate}
 def test_external_mutation_and_consumed_parent_no_policy(self):
  manifest=copy.deepcopy(MAN);p=root(manifest=manifest)
  manifest[0]["primitive_id"]=63
  hits=[hit(0)];result=query(p,hits);hits[0]["primitive_id"]=1
  view=p.view();view["pending"]["primitive_id"]=2
  child=mirror(p,"m")[0]
  self.assertEqual(child.view()["previous"]["primitive_id"],0)
  with patch.object(b.tie,"resolve_candidates",side_effect=AssertionError("consumed query")):
   consumed=query(p,[hit(0)])
  self.assertEqual(consumed["state"],"FORKED")
  self.assertEqual(mirror(p,"x"),[])
  DATA["cases"]["defensive_copy"]={"child":child.view(),"consumed":consumed,"original_result":result}
 def test_miss_bad_schema_and_depth_cap_no_optical_truncation(self):
  miss=query(root(),[]);self.assertEqual(miss["state"],"STOP")
  bad=query(root(),[{"primitive_id":0,"distance_BU":1.,"normal":[1.,0.,0.],"extra":0}])
  self.assertEqual(bad["reason"],"invalid_query_INPUT")
  p=root(branch="chain0")
  lineage=[]
  for i in range(64):
   self.assertEqual(query(p,[hit(i%2)])["state"],"HIT_PENDING_DEPARTURE")
   p=mirror(p,"chain"+str(i+1))[0]
   lineage.append({"branch_id":p.view()["branch_id"],"depth":p.view()["depth"],"previous":p.view()["previous"]})
  query(p,[hit(0)])
  self.assertEqual(mirror(p,"overflow"),[])
  self.assertEqual(p.view()["reason"],"state_depth_bound_NOT_optical_truncation")
  DATA["cases"]["limits"]={"miss":miss,"bad":bad,"at_depth64":p.view(),"lineage":lineage}
if __name__=="__main__":
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
 raise SystemExit(0 if result.wasSuccessful() else 1)
