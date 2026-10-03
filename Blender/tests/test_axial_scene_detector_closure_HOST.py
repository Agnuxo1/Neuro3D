"""Endpoint gate over sealed CPU results; negative INPUT edits are not new scene runs."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_scene_detector_closure_HOST_v1 as a
DATA={"requests":{},"results":{},"synthetic_negative_controls":[]}
def request(name="copy_control"):
    data,_=a.load_retained();r=data["results"][name];q=data["requests"][name][0]
    return {"phase_case":name,"phase_result_sha256":a.digest(r),"original_scene_sha256":r["original_scene_sha256"],
      "source_ids":[x["source_id"] for x in r["rows"]],"detector_point_BU":[[0,1],[1,4],[1,4]],
      "reference_plane_x_BU":deepcopy(q["reference_plane_x_BU"]),"reference_normal_x":q["reference_normal_x"],
      "wavelength_BU":deepcopy(q["wavelength_BU"]),"units":"BU/rad"}
def run(name,q,model=a.MODEL):
    DATA["requests"][name]=deepcopy(q);r=a.audit(q,model=model);DATA["results"][name]=deepcopy(r);return r
class Tests(unittest.TestCase):
    def test_actual_two_SOURCE_distinct_endpoints_atomic_STOP(self):
        q=request("two_SOURCE_zero_error")
        for tag,x in (("detector_x0",0),("detector_x1",1)):
            q["detector_point_BU"][0]=[x,1];r=run(tag,q)
            self.assertEqual(r["reason"],"noncoincident_SOURCE_endpoints")
            self.assertEqual(r["endpoint_bundle"],[]);self.assertEqual(len(r["closure_rows"]),2)
            self.assertEqual([x["endpoint_rational_BU"][0] for x in r["closure_rows"]],[[0,1],[1,1]])
    def test_all_retained_single_SOURCE_accepts_metadata_only(self):
        for name in ("copy_control","division_partial_bound","signed_negative_cycles"):
            r=run(name,request(name))
            self.assertEqual(r["status"],"HOST_RATIONAL_ENDPOINT_CLOSED_ONLY")
            self.assertEqual(len(r["endpoint_bundle"]),1)
            self.assertIsNone(r["detector_complex_field"]);self.assertIsNone(r["detector_power"])
            self.assertFalse(r["coherent_field_admission_allowed"])
    def test_declared_detector_exact_3D_not_axis_projection_or_snap(self):
        for axis in range(3):
            q=request();v=F(*q["detector_point_BU"][axis])+F(1,2**56)
            q["detector_point_BU"][axis]=[v.numerator,v.denominator]
            r=run("detector_delta_axis"+str(axis),q)
            self.assertEqual(r["reason"],"declared_detector_not_endpoint");self.assertEqual(r["endpoint_bundle"],[])
        q=request();q["detector_point_BU"][1]=[2,8]
        r=run("noncanonical_same_point",q);self.assertEqual(r["status"],"HOST_RATIONAL_ENDPOINT_CLOSED_ONLY")
        self.assertNotEqual(r["request_sha256"],run("canonical_same_point",request())["request_sha256"])
    def test_all_SOURCE_coverage_order_no_selection_or_duplicate(self):
        for tag,modify in (("subset",lambda q:q.update(source_ids=["S0"])),
                           ("reorder",lambda q:q["source_ids"].reverse()),
                           ("duplicate",lambda q:q.update(source_ids=["S0","S0"]))):
            q=request("two_SOURCE_zero_error");modify(q);r=run(tag,q)
            self.assertEqual(r["status"],"STOP");self.assertEqual(r["closure_rows"],[]);self.assertEqual(r["endpoint_bundle"],[])
    def test_common_gauge_scene_result_INPUTs_not_defaults(self):
        changes=(("bad_plane","reference_plane_x_BU",[1,1]),("bad_lambda","wavelength_BU",[1,4]),
          ("bad_normal","reference_normal_x",-1),("bad_units","units","m"),
          ("bool_normal","reference_normal_x",True),("bad_scene","original_scene_sha256","0"*64),
          ("bad_result","phase_result_sha256","0"*64),("bool_SOURCE","source_ids",[False]),
          ("bool_coordinate","detector_point_BU",[[False,1],[1,4],[1,4]]),
          ("unknown_case","phase_case","missing"),("bad_SHA_type","phase_result_sha256",1))
        for tag,k,v in changes:
            q=request();q[k]=v;r=run(tag,q);self.assertEqual(r["status"],"STOP");self.assertEqual(r["endpoint_bundle"],[])
        q=request();q.pop("wavelength_BU");self.assertEqual(run("missing_wavelength",q)["reason"],"closed_request")
        self.assertEqual(run("bad_model",request(),model="GPU")["reason"],"explicit_model_required")
    def test_parent_identity_and_upstream_budget_STOP_retained(self):
        q=request("division_zero_budget_STOP")
        r=run("upstream_division_budget",q);self.assertTrue(r["reason"].startswith("upstream_phase_STOP:"))
        self.assertEqual(r["closure_rows"],[])
        q=request()
        with patch.object(a,"PARENT_SHA","0"*64):
            r=run("parent_changed",q)
        self.assertEqual(r["reason"],"phase_parent_identity")
    def test_defensive_copies_and_flags_no_producer(self):
        q=request();old=deepcopy(q);r=run("copy_isolation",q);self.assertEqual(q,old)
        q["detector_point_BU"][1]=[9,1]
        self.assertEqual(r["endpoint_bundle"][0]["endpoint_rational_BU"][1],[1,4])
        self.assertTrue(all(r[k] is False for k in a.FLAGS))
        self.assertEqual(r["old_geometry_producers_reexecuted"],0)
        self.assertEqual(r["phase_producer_reexecuted"],0);self.assertEqual(r["new_native_arithmetic"],0)
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,"data":DATA},sort_keys=True))
    raise SystemExit(0 if r.wasSuccessful() else 1)
