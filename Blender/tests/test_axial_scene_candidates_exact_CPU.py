"""Fresh exact reduced CPU scenes, no retained sweep/fixture replay."""
from fractions import Fraction as F
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_scene_candidates_exact_CPU_v1 as a
DATA={"scenes":{},"results":{}}
def p(x):return [F(x).numerator,F(x).denominator]
def v(x,y,z):return [p(x),p(y),p(z)]
def scene(xs,objects=None,source_xs=(0,)):
 return {"schema":a.MODEL,"units":"BU","triangles":[
  {"primitive_id":i,"object_id":(objects or ["mirror"]*len(xs))[i],
   "vertices_BU":[v(x,0,0),v(x,1,0),v(x,0,1)]} for i,x in enumerate(xs)],
  "sources":[{"id":"SOURCE_"+str(i),"position_BU":v(x,F(1,4),F(1,4)),"direction":v(1,0,0)}
             for i,x in enumerate(source_xs)]}
def run(name,s):
 out=a.query_sources(s,model=a.MODEL)
 DATA["scenes"][name]=copy.deepcopy(s);DATA["results"][name]=out
 return out
class Tests(unittest.TestCase):
 def test_exact_scene_TWO_SOURCE_and_defensive_copy(self):
  s=scene([1,2],source_xs=(0,F(1,2)))
  out=run("two_sources",s)
  self.assertEqual(out["status"],"CPU_AXIAL_ROOT_CANDIDATES_ONLY")
  self.assertEqual(out["branch_queries"],2)
  self.assertEqual(out["sources"][0]["hits"][0]["distance_rational_BU"],[1,1])
  self.assertEqual(out["sources"][1]["hits"][0]["distance_rational_BU"],[1,2])
  self.assertNotEqual(out["branch_results"][0]["source_id"],out["branch_results"][1]["source_id"])
  self.assertTrue(all(x["previous"] is None for x in out["branch_results"]))
  s["triangles"][0]["vertices_BU"][0][0]=p(99)
  self.assertEqual(out["sources"][0]["hits"][0]["distance_rational_BU"],[1,1])
 def test_float64_cast_collision_STOP_before_ANY_branch(self):
  s=scene([1,1+F(1,2**56)])
  with patch.object(a.state.Branch,"query",side_effect=AssertionError("no branch admission")):
   out=run("cast_collision",s)
  self.assertEqual(out["reason"],"float64_minimum_set_changed")
  self.assertEqual(out["sources"][0]["exact_minimum_ids"],[0])
  self.assertEqual(out["sources"][0]["float64_minimum_ids"],[0,1])
  self.assertEqual(out["branch_queries"],0)
  band=run("tieband_rounding",scene([1,1+F(a.tie.TIE_BU)]))
  self.assertEqual(band["reason"],"float64_tie_band_changed")
  self.assertEqual(band["branch_queries"],0)
 def test_positive_thin_gap_no_epsilon_and_object_ambiguity(self):
  thin=run("thin_positive",scene([F(1,2**56),F(1,2**55)]))
  self.assertEqual(thin["branch_queries"],1)
  self.assertEqual(thin["sources"][0]["hits"][0]["distance_rational_BU"],[1,2**56])
  self.assertEqual(thin["sources"][0]["exact_band_ids"],[0,1])
  amb=run("thin_ambiguous",scene([F(1,2**56),F(1,2**55)],objects=["A","B"]))
  self.assertEqual(amb["reason"],"root_tie_policy:ambiguous_object_or_normal")
  self.assertEqual(amb["branch_queries"],0)
 def test_CONTACT_miss_underflow_stop(self):
  for name,s,reason in [
   ("zero_contact",scene([0]),"source_zero_contact_no_departure"),
   ("root_miss",scene([-1]),"root_miss_NOT_certified"),
   ("cast_underflow",scene([F(1,2**1075)]),"float64_positive_finite_required")]:
   out=run(name,s);self.assertEqual(out["reason"],reason);self.assertEqual(out["branch_queries"],0)
 def test_all_SOURCE_preflight_atomic(self):
  s=scene([1,1+F(1,2**56)],source_xs=(1-F(1,2**54),0))
  with patch.object(a.state.Branch,"query",side_effect=AssertionError("all SOURCE before ANY")):
   out=run("second_SOURCE_collapse",s)
  self.assertEqual(out["root_queries_computed"],2)
  self.assertEqual(out["sources"][0]["exact_minimum_ids"],out["sources"][0]["float64_minimum_ids"])
  self.assertEqual(out["reason"],"float64_minimum_set_changed")
  self.assertEqual(out["branch_queries"],0)
 def test_schema_domain_and_binding(self):
  base=scene([1,2]);changed=scene([1,2]);changed["sources"].reverse()
  valid=run("binding_base",base)
  changed["triangles"].reverse()
  for i,row in enumerate(changed["triangles"]):row["primitive_id"]=i
  other=run("binding_reorder",changed)
  self.assertNotEqual(valid["scene_sha256"],other["scene_sha256"])
  controls=[]
  for field,value in [("units","m"),("schema","Bpy")]:
   s=copy.deepcopy(base);s[field]=value
   controls.append(run("bad_"+field,s))
  s=copy.deepcopy(base);s["sources"][0]["direction"]=v(2,0,0);controls.append(run("nonunit",s))
  s=copy.deepcopy(base);s["triangles"][0]["vertices_BU"]=[v(1,0,0),v(1,0,0),v(1,0,0)];controls.append(run("degenerate",s))
  s=copy.deepcopy(base);s["sources"][0]["position_BU"][0]=[True,1];controls.append(run("bool_coordinate",s))
  self.assertTrue(all(x["status"]=="STOP" and x["root_queries_computed"]==0 for x in controls))
if __name__=="__main__":
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
 raise SystemExit(0 if result.wasSuccessful() else 1)
