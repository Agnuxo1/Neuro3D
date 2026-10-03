"""One fresh fixture preparation; cached geometry for new detector INPUT checks."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_common_detector_fixture_CPU_v1 as a
DATA={"prepared":None,"requests":{},"results":{}}
def request():
    return {"prepared_sha256":a.digest(DATA["prepared"]),"original_scene_sha256":a.digest(a.fixture()),
      "source_ids":["S0","S1"],"detector_point_BU":a.vector(0,F(1,4),F(1,4)),"units":"BU"}
def run(name,q,prepared=None):
    DATA["requests"][name]=deepcopy(q)
    r=a.check_detector(DATA["prepared"] if prepared is None else prepared,q,model=a.MODEL)
    DATA["results"][name]=deepcopy(r);return r
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):DATA["prepared"]=a.prepare(model=a.MODEL)
    def test_new_literal_scene_both_directions_plus_ROOT_mirror_detector(self):
        p=DATA["prepared"];self.assertEqual(p["status"],"CPU_NEW_SCENE_COMMON_ENDPOINT_TRANSPORT_ONLY")
        t=p["transport"];self.assertEqual(t["original_scene_sha256"],t["decoded_scene_sha256"])
        paths=t["original_geometry"]["emitted_paths"]
        self.assertEqual([v["segments_rational_BU"] for v in paths],[[[3,4],[1,1]],[[1,4],[1,1]]])
        self.assertEqual([v["primitive_ids"] for v in paths],[[1,0],[1,0]])
        for g in (t["original_geometry"],t["decoded_geometry"]):
            self.assertEqual([v["excluded_zero_ids"] for v in g["departures"]],[[1],[1]])
            self.assertEqual([v["direction_rational"] for v in g["departures"]],[a.vector(-1,0,0)]*2)
        self.assertEqual(p["new_scene_geometry_passes"],2)
    def test_transport_exact_HOST_scalars_not_GPU_ABI(self):
        t=DATA["prepared"]["transport"];self.assertEqual(len(t["scalars"]),30)
        self.assertEqual(t["new_RN32_casts"],60);self.assertEqual(t["new_RN64_subtractions"],30)
        self.assertEqual(t["new_CPU_RN64_decode_additions"],30)
        self.assertTrue(all(v["observed_point_error_abs"]==[0,1] for v in t["scalars"]))
    def test_actual_common_detector_complete_both_SOURCE(self):
        q=request();old=deepcopy(q);r=run("common_detector",q)
        self.assertEqual(q,old);self.assertEqual(r["status"],"CPU_EXACT_COMMON_ENDPOINT_METADATA_ONLY")
        self.assertEqual(len(r["endpoint_bundle"]),2)
        self.assertEqual([p["length_rational_BU"] for p in r["endpoint_bundle"]],[[7,4],[5,4]])
        self.assertEqual(r["new_geometry_passes"],0)
    def test_detector_positive_and_negative_subulp_displacement_exact(self):
        for axis in range(3):
            for sign in (-1,1):
                q=request();v=F(*q["detector_point_BU"][axis])+sign*F(1,2**56)
                q["detector_point_BU"][axis]=a.pair(v)
                r=run("delta_"+str(axis)+"_"+str(sign),q)
                self.assertEqual(r["reason"],"detector_not_all_original_endpoints");self.assertEqual(r["endpoint_bundle"],[])
    def test_SOURCE_subset_order_identity_and_cache_forgeries(self):
        for tag,edit in (("subset",lambda q:q.update(source_ids=["S0"])),
          ("order",lambda q:q["source_ids"].reverse()),("bad_scene",lambda q:q.update(original_scene_sha256="0"*64)),
          ("bad_prepared",lambda q:q.update(prepared_sha256="0"*64)),("missing",lambda q:q.pop("units"))):
            q=request();edit(q);r=run(tag,q);self.assertEqual(r["status"],"STOP");self.assertEqual(r["endpoint_bundle"],[])
        forged=deepcopy(DATA["prepared"]);forged["transport"]["original_geometry"]["emitted_paths"][1]["length_rational_BU"]=[0,1]
        r=run("forged_cache",request(),prepared=forged)
        self.assertEqual(r["reason"],"prepared_binding")
    def test_invalid_model_parent_guard_before_geometry(self):
        r=a.prepare(model="GPU");self.assertEqual(r["reason"],"explicit_model_required")
        with patch.object(a,"PARENT_SHA","0"*64):
            r=a.prepare(model=a.MODEL)
        self.assertEqual(r["reason"],"sealed_parent_identity");self.assertEqual(r["new_scene_geometry_passes"],0)
        DATA["prepare_STOP_controls"]=[{"reason":"explicit_model_required","geometry_passes":0},{"reason":r["reason"],"geometry_passes":0}]
    def test_no_physical_field_phase_claim_and_output_copy(self):
        q=request();r=run("copy_control",q)
        r["endpoint_bundle"][0]["endpoint_rational_BU"][0]=[3,1]
        self.assertEqual(DATA["prepared"]["transport"]["original_geometry"]["emitted_paths"][0]["endpoint_rational_BU"][0],[0,1])
        self.assertTrue(all(DATA["prepared"][k] is False for k in a.FLAGS))
        self.assertIsNone(DATA["prepared"]["detector_power"]);self.assertEqual(DATA["prepared"]["phase_arithmetic_executed"],0)
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,"data":DATA},sort_keys=True))
    raise SystemExit(0 if r.wasSuccessful() else 1)
