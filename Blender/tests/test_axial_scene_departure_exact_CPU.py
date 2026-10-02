"""Fresh one-mirror scene queries, not old precision sweeps or physical inference."""
from fractions import Fraction as F
from copy import deepcopy
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_scene_departure_exact_CPU_v1 as a
DATA={"scenes":{},"requests":{},"results":{}}
def p(x): return [F(x).numerator,F(x).denominator]
def v(x,y,z): return [p(x),p(y),p(z)]
def scene(xs, source_specs, objects=None):
    return {"schema":a.root.MODEL,"units":"BU","triangles":[
      {"primitive_id":i,"object_id":(objects or ["surface"]*len(xs))[i],
       "vertices_BU":[v(x,0,0),v(x,1,0),v(x,0,1)]} for i,x in enumerate(xs)],
      "sources":[{"id":"S"+str(i),"position_BU":v(x,F(1,4),F(1,4)),"direction":v(sign,0,0)}
                 for i,(x,sign) in enumerate(source_specs)]}
def requests(s):
    h=hashlib.sha256(json.dumps(s,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return [{"scene_sha256":h,"source_id":r["id"],"departure_event":"mirror"} for r in s["sources"]]
def run(name,s,req=None,model=a.MODEL):
    req=requests(s) if req is None else req
    DATA["scenes"][name]=deepcopy(s);DATA["requests"][name]=deepcopy(req)
    # Never calls branch admission or frozen complete-scene writer/history tracer.
    with patch.object(a.root.state.Branch,"query",side_effect=AssertionError("no branch query")):
        out=a.prepare_departures(s,req,model=model)
    DATA["results"][name]=deepcopy(out);return out
class Tests(unittest.TestCase):
    def test_positive_gap_and_no_bias_BOTH_directions(self):
        g=F(1,2**56)
        for name,s in [("tiny_plus",scene([1-g,1],[(1-g/2,1)])),
                       ("tiny_minus",scene([1,1+g],[(1+g/2,-1)]))]:
            r=run(name,s)
            self.assertEqual(r["status"],"CPU_AXIAL_ONE_MIRROR_GEOMETRY_ONLY")
            d=r["departures"][0]
            self.assertEqual(d["origin_rational_BU"][0],[1,1])
            self.assertEqual(d["hits"][0]["distance_rational_BU"],p(g))
            self.assertEqual(d["excluded_zero_ids"],[d["previous_primitive_id"]])
            self.assertEqual(r["emitted_paths"][0]["segments_rational_BU"],[p(g/2),p(g)])
            self.assertEqual(r["emitted_paths"][0]["length_rational_BU"],p(3*g/2))
            self.assertEqual(r["origin_bias_BU"],[0,1])
    def test_SOURCE_separation_no_global_object_veto(self):
        r=run("two_sources",scene([0,1],[(F(1,4),1),(F(3,4),-1)]))
        self.assertEqual([p["primitive_ids"] for p in r["emitted_paths"]],[[1,0],[0,1]])
        self.assertEqual([p["source_id"] for p in r["emitted_paths"]],["S0","S1"])
        self.assertEqual([p["length_rational_BU"] for p in r["emitted_paths"]],[[7,4],[7,4]])
        self.assertEqual([d["excluded_zero_ids"] for d in r["departures"]],[[1],[0]])
    def test_other_primitive_zero_and_miss_STOP(self):
        r=run("other_zero",scene([0,1,1],[(F(1,2),1)]))
        self.assertEqual(r["reason"],"different_primitive_zero_contact")
        r=run("departure_miss",scene([1],[(F(1,2),1)]))
        self.assertEqual(r["reason"],"departure_miss_NOT_escape_certificate")
        self.assertEqual(r["emitted_paths"],[])
    def test_new_departure_cast_gate(self):
        r=run("departure_collision",scene([0,F(1,2**56),1],[(F(1,2),1)]))
        self.assertEqual(r["reason"],"departure_float64_minimum_set_changed")
        self.assertEqual(r["departures"][0]["exact_minimum_ids"],[1])
        self.assertEqual(r["departures"][0]["float64_minimum_ids"],[0,1])
        r=run("departure_band",scene([0,F(a.root.tie.TIE_BU),2],[(1,1)]))
        self.assertEqual(r["reason"],"departure_float64_tie_band_changed")
        self.assertEqual(r["departures"][0]["exact_band_ids"],[0,1])
        self.assertEqual(r["departures"][0]["float64_band_ids"],[1])
        # Distinct objects in tiny *positive* final band are ambiguous, not skipped.
        g=F(1,2**56)
        r=run("departure_ambiguous",scene([1-2*g,1-g,1],[(1-g/2,1)],["A","B","mirror"]))
        self.assertEqual(r["reason"],"departure_tie_policy:ambiguous_object_or_normal")
    def test_all_SOURCE_before_ANY_path_and_binding_controls(self):
        r=run("second_SOURCE_miss",scene([0,1],[(F(1,4),1),(2, -1)]))
        self.assertEqual(r["departure_queries"],2)
        self.assertIn("tie_policy",r["departures"][0])
        self.assertEqual(r["reason"],"departure_miss_NOT_escape_certificate")
        self.assertEqual(r["emitted_paths"],[])
        s=scene([0,1],[(F(1,4),1),(F(3,4),-1)])
        for name,modify in [
          ("bad_sha",lambda q:q[0].update(scene_sha256="a"*64)),
          ("bad_SOURCE",lambda q:q.reverse()),
          ("bad_event",lambda q:q[0].update(departure_event="t")),
          ("extra_key",lambda q:q[0].update(bias=1e-6)),
          ("missing_SOURCE",lambda q:q.pop())]:
            q=requests(s);modify(q);r=run(name,s,q)
            self.assertEqual(r["status"],"STOP");self.assertEqual(r["departure_queries"],0)
        r=run("wrong_model",s,model="native");self.assertEqual(r["departure_queries"],0)
    def test_input_copy_and_root_STOP(self):
        s=scene([0,1],[(F(1,4),1)]);q=requests(s)
        before=deepcopy((s,q));r=run("copy_control",s,q)
        self.assertEqual((s,q),before);s["sources"][0]["id"]="mutated"
        self.assertEqual(r["emitted_paths"][0]["source_id"],"S0")
        r=run("root_zero",scene([0,1],[(1,1)]))
        self.assertEqual(r["reason"],"root_STOP:source_zero_contact_no_departure")
        self.assertEqual(r["departure_queries"],0)
if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
