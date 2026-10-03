"""Fresh oblique fixtures only. No frozen suite, GPU or material phase."""
import importlib.util,json,unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("oblique_new",ROOT/"Blender/benchmarks/capacity_audit/oblique_common_detector_length_CPU_v1.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
INPUTS={};RESULTS={};ROOTS={}
def checked(name,s,q=None,model=None):
    q=m.request(s) if q is None else q;model=m.MODEL if model is None else model
    INPUTS[name]={"scene":deepcopy(s),"request":deepcopy(q),"model":model}
    v=m.audit(s,q,model=model);RESULTS[name]=v;return v
class Tests(unittest.TestCase):
    def stop(self,v):
        self.assertEqual(v["status"],"STOP");self.assertEqual(v["paths"],[])
        self.assertFalse(v["native_promotion_allowed"])
    def test_01_oblique_scene_irrational_lengths(self):
        s=m.fixture();v=checked("oblique",s)
        self.assertEqual(v["status"],"CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY")
        self.assertEqual([p["primitive_ids"] for p in v["paths"]],[[1,0],[1,0]])
        for p,k in zip(v["paths"],(F(7,4),F(5,4))):
            lo,hi=[F(*x) for x in p["length_interval_BU"]]
            self.assertLessEqual(lo*lo,2*k*k);self.assertGreaterEqual(hi*hi,2*k*k)
            self.assertNotEqual(lo,hi)
            self.assertEqual(p["reflected_direction"],m.enc((-1,1,0)))
        self.assertEqual(v["counters"],{"triangle_plane_tests":8,"exact_previous_zero_skips":2,"sqrt_brackets":4})
        self.assertIsNone(v["mirror_phase"]);self.assertIsNone(v["detector_field"])
    def test_02_tiny_positive_and_direction_scaling(self):
        s=m.fixture(F(1,2**60));v=checked("tiny_gap_2m60",s)
        self.assertEqual(v["status"],"CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY")
        self.assertTrue(all(F(*p["hit_parameters"][0])>0 for p in v["paths"]))
        s=m.fixture()
        for source in s["sources"]:source["direction"]=m.enc((2,2,0))
        v=checked("direction_scaled",s)
        self.assertEqual([p["length_interval_BU"] for p in v["paths"]],[p["length_interval_BU"] for p in RESULTS["oblique"]["paths"]])
        self.assertEqual(v["paths"][0]["hit_parameters"][0],[3,8])
    def test_03_tie_otherface_contact_and_initial_contact(self):
        s=m.fixture();s["triangles"].append({**deepcopy(s["triangles"][1]),"primitive_id":2})
        self.stop(checked("root_tie_same_object",s))
        s=m.fixture();s["triangles"].append({**deepcopy(s["triangles"][1]),"primitive_id":2,"vertices_BU":[m.enc((1,0,0)),m.enc((1,3,0)),m.enc((1,0,3))]})
        self.stop(checked("duplicate_otherface",s))
        s=m.fixture();s["sources"][0]["position_BU"]=m.enc((1,1,F(1,4)))
        self.stop(checked("initial_contact",s))
        s=m.fixture();s["sources"][1]["direction"]=m.enc((-1,1,0))
        self.stop(checked("SOURCE1_wrong_root_ALL_STOP",s))
    def test_04_all_caps_before_any_output(self):
        for name,idx in (("SOURCE0_cap_zero",0),("SOURCE1_cap_zero",1)):
            s=m.fixture();q=m.request(s);q["source_width_caps_rad"][idx]=[0,1]
            self.stop(checked(name,s,q));self.assertEqual(len(RESULTS[name]["diagnostics"]),2)
        s=m.fixture();q=m.request(s);q["relative_width_cap_rad"]=[0,1]
        self.stop(checked("relative_cap_zero",s,q))
        s=m.fixture();q=m.request(s);q["reference_BU"]=[1000,1]
        v=checked("shared_ref1000",s,q);self.assertEqual(v["relative_diagnostic"],RESULTS["oblique"]["relative_diagnostic"])
    def test_05_closed_inputs_and_bound_types(self):
        s=m.fixture();q=m.request(s)
        for name,k,value in (("stale","original_scene_sha256","0"*64),("order","source_ids",["S1","S0"]),
                             ("root_bool","root_primitive_id",True),("wave_zero","lambda_BU",[0,1]),
                             ("wave_negative","lambda_BU",[-1,1]),("caps_missing","source_width_caps_rad",[[1,1]]),
                             ("rational_bool","reference_BU",[False,1]),("fraction_float","reference_BU",[1.0,1]),
                             ("denominator_zero","reference_BU",[1,0]),("bits_overflow","reference_BU",[2**129,1]),
                             ("detector_wrong","detector_point_BU",m.enc((0,2,F(1,4)+F(1,2**60))))):
            wrong=deepcopy(q);wrong[k]=value;self.stop(checked(name,s,wrong))
        self.stop(checked("extra_cap_override",s,{**q,"caps_override":1}))
        self.stop(checked("wrong_model",s,q,"axial_common"))
        s=m.fixture();s["sources"][1]["direction"]=m.enc((0,0,0));self.stop(checked("zero_direction",s))
        s=m.fixture();s["triangles"][0]["vertices_BU"][2]=s["triangles"][0]["vertices_BU"][1];self.stop(checked("degenerate",s))
        s=m.fixture();s["sources"]=s["sources"][:1];self.stop(checked("subset_SOURCE",s))
        s=m.fixture();s["triangles"][1]["primitive_id"]=0;self.stop(checked("duplicate_id",s))
    def test_06_square_bounds_synthetic(self):
        for label,x in (("zero",F(0)),("square",F(9,16)),("sqrt2",F(2)),
                        ("tiny",F(1,2**240)),("nondyadic",F(2,3)),("large",F(10**12))):
            lo,hi=m.root_bracket(x);ROOTS[label]={"squared":m.pair(x),"interval":[m.pair(lo),m.pair(hi)]}
            self.assertLessEqual(lo*lo,x);self.assertGreaterEqual(hi*hi,x)
            self.assertLessEqual(hi-lo,F(1,2**96))
        with self.assertRaises(ValueError):m.root_bracket(F(-1))
        with self.assertRaises(ValueError):m.root_bracket(2.0)
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,
        "data":{"inputs":INPUTS,"results":RESULTS,"root_controls":ROOTS}},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
