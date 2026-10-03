"""New parameter protocols over common fixture receipt; no scene/phase producer replay."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_common_detector_phase_CPU_v1 as a
DATA={"requests":{},"results":{}}
def request(ref=0,lam=F(1,8),caps=(0,0),relative_cap=0,normal=1):
    p=a.load_retained()
    return {"original_scene_sha256":p["transport"]["original_scene_sha256"],"prepared_sha256":a.digest(p),
      "detector_point_BU":[[0,1],[1,4],[1,4]],"source_ids":["S0","S1"],
      "reference_plane_x_BU":a.pair(F(ref)),"reference_normal_x":normal,"wavelength_BU":a.pair(F(lam)),
      "SOURCE_phase_budgets_rad":[a.pair(F(x)) for x in caps],"relative_propagation_budget_rad":a.pair(F(relative_cap)),"units":"BU/rad"}
def run(name,q,model=a.MODEL):
    DATA["requests"][name]=deepcopy(q);r=a.audit(q,model=model);DATA["results"][name]=deepcopy(r);return r
class Tests(unittest.TestCase):
    def test_common_endpoint_exact_SOURCE_relative_without_field(self):
        r=run("exact",request())
        self.assertEqual(r["status"],"CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY")
        self.assertEqual([x["original_cycles"] for x in r["rows"]],[[14,1],[10,1]])
        self.assertEqual(r["relative"]["original_cycles"],[4,1])
        self.assertEqual(r["relative"]["propagation_phase_bound_rad"],[0,1])
        self.assertEqual(r["new_shared_reference_RN64_subtractions"],1)
    def test_shared_gauge_changes_individual_not_exact_relative(self):
        r=run("signed_reference",request(ref=1,normal=-1))
        self.assertEqual([x["original_cycles"] for x in r["rows"]],[[6,1],[2,1]])
        self.assertEqual(r["relative"]["original_cycles"],[4,1])
        r=run("large_exact_reference",request(ref=-999999))
        self.assertTrue(all(x["propagation_phase_bound_rad"]==[0,1] for x in r["rows"]))
        self.assertEqual(r["relative"]["cycle_error_bound"],[0,1])
    def test_nonbinary_quotients_SOURCE_and_relative_caps_independent(self):
        q=request(lam=F(3,4),caps=(F(1,10**12),)*2,relative_cap=F(1,10**12))
        r=run("quotient_partial",q);self.assertEqual(r["status"],"CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY")
        self.assertEqual(r["relative"]["original_cycles"],[2,3])
        self.assertGreater(F(*r["relative"]["cycle_error_bound"]),0)
        q["relative_propagation_budget_rad"]=[0,1];z=run("relative_zero_STOP",q)
        self.assertEqual(z["reason"],"relative_propagation_budget_exceeded");self.assertEqual(z["emitted_sources"],[])
        self.assertEqual(z["relative"]["propagation_phase_bound_rad"],r["relative"]["propagation_phase_bound_rad"])
        q["relative_propagation_budget_rad"]=[1,10**12];q["SOURCE_phase_budgets_rad"][1]=[0,1]
        z=run("second_SOURCE_zero_STOP",q);self.assertEqual(z["reason"],"SOURCE_phase_budget_exceeded")
        self.assertEqual(z["emitted_sources"],[]);self.assertTrue(z["relative"]["budget_fits"])
    def test_large_reference_does_not_rescue_SOURCE_by_shared_cancellation(self):
        q=request(ref=-999999,lam=F(3,4),caps=(F(1,10**12),)*2,relative_cap=1)
        r=run("large_reference_SOURCE_STOP",q);self.assertEqual(r["reason"],"SOURCE_phase_budget_exceeded")
        self.assertTrue(r["relative"]["budget_fits"]);self.assertEqual(r["emitted_sources"],[])
    def test_parameter_loss_before_ANY_path_and_no_budget_defaults(self):
        q=request(lam=F(.1),caps=(1,1),relative_cap=1)
        r=run("lambda_transport_loss",q);self.assertEqual(r["reason"],"parameter_transport_loss")
        self.assertEqual(r["new_path_RN64_additions"],0);self.assertEqual(r["rows"],[])
        q=request(ref=F(.1));r=run("reference_transport_loss",q)
        self.assertEqual(r["reason"],"parameter_transport_loss");self.assertIsNone(r["relative"])
    def test_scene_detector_source_identity_atomic_preencoder(self):
        changes=(("source_subset","source_ids",["S0"]),("source_reorder","source_ids",["S1","S0"]),
          ("scene_changed","original_scene_sha256","0"*64),("prepared_changed","prepared_sha256","0"*64),
          ("detector_changed","detector_point_BU",[[1,2**56],[1,4],[1,4]]),
          ("bool_normal","reference_normal_x",True),("units","units","m"),
          ("zero_lambda","wavelength_BU",[0,1]),("negative_cap","relative_propagation_budget_rad",[-1,1]))
        with patch.object(a,"encoder",side_effect=AssertionError("identity before encoder")):
            for tag,k,v in changes:
                q=request();q[k]=v;r=run(tag,q)
                self.assertEqual(r["status"],"STOP");self.assertEqual(r["parameter_RN32_casts"],0)
            q=request();q.pop("SOURCE_phase_budgets_rad")
            self.assertEqual(run("missing_SOURCE_budget",q)["reason"],"closed_request")
            r=run("wrong_model",request(),model="GPU");self.assertEqual(r["reason"],"explicit_model_required")
    def test_parent_guard_copy_and_no_native_field_physics(self):
        q=request()
        with patch.object(a,"PARENT_SHA","0"*64):
            r=run("parent_changed",q)
        self.assertEqual(r["reason"],"sealed_parent_identity")
        q=request();original=deepcopy(q);r=run("copy",q);self.assertEqual(q,original)
        self.assertTrue(all(r[k] is False for k in a.FLAGS));self.assertIsNone(r["detector_power"])
        self.assertEqual(r["geometry_producers_reexecuted"],r["old_phase_producers_reexecuted"],0)
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,"data":DATA},sort_keys=True))
    raise SystemExit(0 if r.wasSuccessful() else 1)
