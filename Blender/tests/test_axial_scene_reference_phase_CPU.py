"""New optical-parameter requests over retained scene evidence, no geometry producers or sweeps."""
from fractions import Fraction as F
from copy import deepcopy
import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_scene_reference_phase_CPU_v1 as a
DATA={"requests":{},"cases":{},"results":{}}
def p(x):return [F(x).numerator,F(x).denominator]
def requests(case,ref=0,normal=1,lam=F(1,8),cap=0):
    upstream=a.load_retained()["results"][case]
    return [{"original_scene_sha256":upstream["original_scene_sha256"],"source_id":path["source_id"],
      "branch_id":path["branch_id"],"reference_plane_x_BU":p(ref),"reference_normal_x":normal,
      "wavelength_BU":p(lam),"phase_budget_rad":p(cap),"units":"BU/rad"}
      for path in upstream["original_geometry"]["emitted_paths"]]
def run(name,case,q,model=a.MODEL):
    DATA["cases"][name]=case;DATA["requests"][name]=deepcopy(q)
    r=a.audit(case,q,model=model);DATA["results"][name]=deepcopy(r);return r
class Tests(unittest.TestCase):
    def test_two_SOURCE_exact_signed_cycles_and_request_gauges(self):
        case="two_SOURCE_exact";q=requests(case)
        r=run("two_SOURCE_zero_error",case,q)
        self.assertEqual(r["status"],"CPU_DECLARED_PROPAGATION_PHASE_BOUND_ONLY")
        self.assertEqual([x["original_cycles"] for x in r["rows"]],[[14,1],[6,1]])
        self.assertEqual([x["propagation_phase_error_bound_rad"] for x in r["rows"]],[[0,1],[0,1]])
        s=run("signed_negative_cycles","noncanonical_literal",requests("noncanonical_literal",ref=5,normal=-1))
        self.assertEqual(s["rows"][0]["original_cycles"],[-26,1])
        self.assertNotEqual(r["request_sha256"],s["request_sha256"])
    def test_reference_cancellation_keeps_nonzero_bound_and_STOP(self):
        case="exact_pair_plus"
        q=requests(case,ref=-999999,lam=F(1,2**30),cap=F(1,10**12))
        r=run("reference_cancellation",case,q)
        self.assertEqual(r["reason"],"declared_phase_budget_exceeded")
        self.assertEqual(r["rows"][0]["reference_error_bound_BU"],[1,2**48])
        self.assertEqual(r["rows"][0]["propagation_phase_error_bound_rad"],[5,65536])
        self.assertEqual(r["emitted_sources"],[])
    def test_division_rounding_budget_explicit_no_silent_relaxation(self):
        case="noncanonical_literal"
        r=run("division_partial_bound",case,requests(case,lam=F(3,4),cap=F(1,10**12)))
        self.assertEqual(r["status"],"CPU_DECLARED_PROPAGATION_PHASE_BOUND_ONLY")
        self.assertGreater(F(*r["rows"][0]["quotient_div_RN64_error_bound_cycles"]),0)
        z=run("division_zero_budget_STOP",case,requests(case,lam=F(3,4),cap=0))
        self.assertEqual(z["reason"],"declared_phase_budget_exceeded")
        self.assertEqual(z["rows"][0]["propagation_phase_error_bound_rad"],r["rows"][0]["propagation_phase_error_bound_rad"])
        self.assertNotEqual(r["request_sha256"],z["request_sha256"])
    def test_parameter_transport_and_allSOURCE_atomicity(self):
        case="two_SOURCE_exact";q=requests(case);q[1]["wavelength_BU"]=p(F(.1))
        r=run("second_SOURCE_parameter_loss",case,q)
        self.assertEqual(r["reason"],"reference_or_wavelength_transport_loss")
        self.assertEqual(r["new_path_RN64_additions"],0);self.assertEqual(r["emitted_sources"],[])
        self.assertEqual(len(r["rows"]),2)
        self.assertTrue(all(not x["propagation_phase_bound_computed"] for x in r["rows"]))
        q=requests("noncanonical_literal",ref=F(.1))
        r=run("reference_parameter_loss","noncanonical_literal",q)
        self.assertEqual(r["reason"],"reference_or_wavelength_transport_loss")
    def test_binding_schema_budget_lambda_model_preencoder(self):
        case="two_SOURCE_exact"
        with patch.object(a,"encoder_module",side_effect=AssertionError("preflight first")):
            for name,modify in [
              ("bad_source_order",lambda q:q.reverse()),
              ("bad_branch",lambda q:q[0].update(branch_id="alien")),
              ("missing_lambda",lambda q:q[0].pop("wavelength_BU")),
              ("zero_lambda",lambda q:q[0].update(wavelength_BU=[0,1])),
              ("negative_budget",lambda q:q[0].update(phase_budget_rad=[-1,1])),
              ("bool_normal",lambda q:q[0].update(reference_normal_x=True)),
              ("wrong_units",lambda q:q[0].update(units="m")),
              ("missing_SOURCE",lambda q:q.pop())]:
                q=requests(case);modify(q);r=run(name,case,q)
                self.assertEqual(r["status"],"STOP");self.assertEqual(r["new_parameter_RN32_casts"],0)
            r=run("wrong_model",case,requests(case),model="GPU");self.assertEqual(r["reason"],"explicit_model_required")
    def test_upstream_STOP_no_replay_and_parent_guard(self):
        with patch.object(a,"encoder_module",side_effect=AssertionError("no upstream resurrection")):
            r=run("upstream_world_thin","world_thin",[])
            self.assertTrue(r["reason"].startswith("upstream_STOP:"))
        q=requests("noncanonical_literal")
        with patch.object(a,"PARENT_SHA","0"*64):
            r=run("parent_identity_STOP","noncanonical_literal",q)
        self.assertEqual(r["reason"],"sealed_parent_changed")
    def test_defensive_INPUT_no_hidden_material_or_native_proof(self):
        case="noncanonical_literal";q=requests(case);original=deepcopy(q)
        r=run("copy_control",case,q);self.assertEqual(q,original)
        q[0]["reference_plane_x_BU"]=[99,1]
        self.assertEqual(r["rows"][0]["request"]["reference_plane_x_BU"],[0,1])
        self.assertFalse(r["length_reference_phase_bound_certified"])
        self.assertFalse(r["mirror_material_certified"])
        self.assertEqual(r["old_geometry_producers_reexecuted"],0)
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,"data":DATA},sort_keys=True))
    raise SystemExit(0 if r.wasSuccessful() else 1)
