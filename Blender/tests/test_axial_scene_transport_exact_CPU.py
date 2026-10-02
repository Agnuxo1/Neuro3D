"""New rational scene transport cases, not earlier retained precision sweeps."""
from fractions import Fraction as F
from copy import deepcopy
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_scene_transport_exact_CPU_v1 as a
DATA={"scenes":{},"requests":{},"results":{}}
def p(x):return [F(x).numerator,F(x).denominator]
def v(x,y,z):return [p(x),p(y),p(z)]
def scene(xs,specs):
    return {"schema":a.departure.root.MODEL,"units":"BU","triangles":[
        {"primitive_id":i,"object_id":"surface","vertices_BU":[v(x,0,0),v(x,1,0),v(x,0,1)]}
        for i,x in enumerate(xs)],"sources":[
        {"id":"S"+str(i),"position_BU":v(x,F(1,4),F(1,4)),"direction":v(sign,0,0)}
        for i,(x,sign) in enumerate(specs)]}
def requests(s):
    h=hashlib.sha256(json.dumps(s,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return [{"scene_sha256":h,"source_id":r["id"],"departure_event":"mirror"} for r in s["sources"]]
def run(name,s,q=None,model=a.MODEL):
    q=requests(s) if q is None else q;DATA["scenes"][name]=deepcopy(s);DATA["requests"][name]=deepcopy(q)
    with patch.object(a.departure.root.state.Branch,"query",side_effect=AssertionError("no native/branch admission")):
        r=a.audit(s,q,model=model)
    DATA["results"][name]=deepcopy(r);return r
class Tests(unittest.TestCase):
    def test_binary64_source_loss_preserved_not_hidden_by_good_distances(self):
        g=F(1,2**56)
        r=run("world_thin",scene([1-g,1],[(1-g/2,1)]))
        self.assertEqual(r["original_geometry"]["status"],"CPU_AXIAL_ONE_MIRROR_GEOMETRY_ONLY")
        self.assertEqual(r["reason"],"ORIGINAL_rational_to_float64_loss")
        self.assertEqual(r["decoded_geometry"]["reason"],"root_STOP:source_zero_contact_no_departure")
        self.assertEqual(r["emitted_paths"],[])
    def test_HOST_hilo_loss_and_nonbinary_original_are_distinct(self):
        r=run("FP64_input_hilo_loss",scene([0,1],[(F(0.1),1)]))
        self.assertEqual(r["reason"],"HOST_hilo_CPU_decode_point_loss")
        xs=[s for s in r["scalars"] if s["path"]==["sources",0,"position_BU",0]]
        self.assertEqual(xs[0]["first_cast_error_abs"],[0,1])
        self.assertGreater(F(*xs[0]["observed_point_error_abs"]),0)
        r=run("rational_tenth",scene([0,1],[(F(1,10),1)]))
        self.assertEqual(r["reason"],"ORIGINAL_rational_to_float64_loss")
        r=run("tiny_underflow_hilo",scene([0,F(1,2**160)],[(F(1,2**162),1)]))
        self.assertEqual(r["reason"],"HOST_hilo_CPU_decode_point_loss")
        self.assertEqual(r["decoded_geometry"]["reason"],"root_STOP:source_zero_contact_no_departure")
    def test_exact_pair_thin_and_two_SOURCE(self):
        g=F(1,2**48)
        for name,s in [("exact_pair_plus",scene([1-g,1],[(1-g/2,1)])),
                       ("exact_pair_minus",scene([1,1+g],[(1+g/2,-1)])),
                       ("two_SOURCE_exact",scene([0,1],[(F(1,4),1),(F(3,4),-1)]))]:
            r=run(name,s);self.assertEqual(r["status"],"CPU_EXACT_POINT_TRANSPORT_ONLY")
            self.assertEqual(len(r["emitted_paths"]),len(s["sources"]))
            self.assertTrue(all(s["observed_point_error_abs"]==[0,1] for s in r["scalars"]))
            self.assertEqual(r["new_RN32_casts"],2*len(r["scalars"]))
    def test_all_SOURCE_no_partial_emission_and_no_input_mutation(self):
        s=scene([0,1],[(F(1,4),1),(F(.1),1)]);q=requests(s);before=deepcopy((s,q))
        r=run("second_SOURCE_hilo_loss",s,q)
        self.assertEqual((s,q),before)
        self.assertEqual(r["reason"],"HOST_hilo_CPU_decode_point_loss")
        self.assertEqual(r["emitted_paths"],[])
        self.assertEqual(len(r["original_geometry"]["emitted_paths"]),2)
        self.assertEqual(len(r["decoded_geometry"]["emitted_paths"]),2)
    def test_binding_domain_fail_before_encoder(self):
        s=scene([0,1],[(F(1,4),1)])
        with patch.object(a.importlib.util,"spec_from_file_location",side_effect=AssertionError("no encoder")):
            q=requests(s);q[0]["scene_sha256"]="a"*64;r=run("bad_SHA",s,q)
            self.assertTrue(r["reason"].startswith("original_geometry_STOP:"))
            r=run("wrong_model",s,model="GPU");self.assertEqual(r["reason"],"explicit_model_required")
            s2=deepcopy(s);s2["sources"][0]["position_BU"]=v(1,F(1,4),F(1,4))
            r=run("original_zero",s2);self.assertTrue(r["reason"].startswith("original_geometry_STOP:"))
        for name in ("bad_SHA","wrong_model","original_zero"):
            self.assertEqual(DATA["results"][name]["scalars"],[])
    def test_encoder_hash_guard_and_literal_representation_BINDING(self):
        s=scene([0,1],[(F(1,4),1)])
        with patch.object(a,"ENCODER_SHA","0"*64):
            r=run("encoder_identity_STOP",s)
        self.assertEqual(r["reason"],"frozen_encoder_identity_changed");self.assertEqual(r["scalars"],[])
        s["triangles"][1]["vertices_BU"][0][0]=[2,2]
        r=run("noncanonical_literal",s)
        self.assertEqual(r["status"],"CPU_EXACT_POINT_TRANSPORT_ONLY")
        self.assertNotEqual(r["original_scene_sha256"],r["decoded_scene_sha256"])
        self.assertEqual(r["original_geometry"]["emitted_paths"][0]["length_rational_BU"],[7,4])
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,"data":DATA},sort_keys=True))
    raise SystemExit(0 if r.wasSuccessful() else 1)
