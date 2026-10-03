"""Seven focused tests; new source/mirror additions only, no old numerical producer replay."""
import importlib.util,json,sys,unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("source_material_phase",ROOT/"Blender/benchmarks/capacity_audit/axial_common_detector_source_material_CPU_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REQUESTS={};RESULTS={}
def request(case="exact"):
    data,prepared=m.load_retained();p=data["results"][case];q=data["requests"][case]
    return {"propagation_case":case,"propagation_result_sha256":m.digest(p),
      "original_scene_sha256":q["original_scene_sha256"],"prepared_sha256":q["prepared_sha256"],
      "detector_point_BU":deepcopy(q["detector_point_BU"]),
      "source_phases":[{"source_id":"S0","branch_id":"S0/mirror","phase_cycles":[0,1]},
                       {"source_id":"S1","branch_id":"S1/mirror","phase_cycles":[1,8]}],
      "material_phase":{"object_id":"common_detector_fixture_surface","primitive_id":1,"profile":m.PROFILE,"phase_cycles":[1,2]},
      "SOURCE_total_phase_budgets_rad":[[0,1],[0,1]],"relative_total_phase_budget_rad":[0,1],
      "units":"cycles/rad","declaration":m.DECLARATION}
def record(name,q,model=None):
    REQUESTS[name]=deepcopy(q);v=m.audit(q,model=m.MODEL if model is None else model);RESULTS[name]=v;return v
class Tests(unittest.TestCase):
    def test_01_exact_signed_and_explicit_zero(self):
        for name,case in (("exact","exact"),("signed_reference","signed_reference"),("large_exact_reference","large_exact_reference")):
            r=record(name,request(case));self.assertEqual(r["status"],"CPU_DECLARED_SOURCE_MATERIAL_PHASE_BOUNDS_ONLY")
            self.assertEqual(r["relative"]["declared_original_cycles"],[31,8])
            self.assertEqual(r["relative"]["total_cycle_error_bound"],[0,1])
        self.assertEqual(RESULTS["exact"]["rows"][0]["declared_total_original_cycles"],[29,2])
        self.assertEqual(RESULTS["exact"]["rows"][1]["declared_total_original_cycles"],[85,8])
        q=request();q["material_phase"]["phase_cycles"]=[0,1];q["source_phases"][1]["phase_cycles"]=[0,1]
        r=record("explicit_zero",q);self.assertEqual(r["relative"]["declared_original_cycles"],[4,1])
    def test_02_retained_quotient_error_not_reset(self):
        q=request("quotient_partial");q["SOURCE_total_phase_budgets_rad"]=[[1,10**12],[1,10**12]];q["relative_total_phase_budget_rad"]=[1,10**12]
        r=record("quotient_partial",q);self.assertEqual(r["status"],"CPU_DECLARED_SOURCE_MATERIAL_PHASE_BOUNDS_ONLY")
        self.assertEqual(r["relative"]["declared_original_cycles"],[13,24])
        self.assertGreater(F(*r["relative"]["total_cycle_error_bound"]),0)
        q["SOURCE_total_phase_budgets_rad"][1]=[0,1]
        self.assertEqual(record("retained_second_SOURCE_zero_STOP",q)["reason"],"SOURCE_total_phase_budget_exceeded")
    def test_03_small_SOURCE_loss_has_separate_caps(self):
        q=request();q["source_phases"][0]["phase_cycles"]=[1,2**56];q["source_phases"][1]["phase_cycles"]=[0,1];q["material_phase"]["phase_cycles"]=[0,1]
        q["relative_total_phase_budget_rad"]=[1,10**12]
        r=record("small_SOURCE_zero_STOP",q);self.assertEqual(r["reason"],"SOURCE_total_phase_budget_exceeded")
        self.assertTrue(r["relative"]["budget_fits"]);self.assertEqual(r["rows"][0]["source_add_RN_error_cycles"],[1,2**56])
        q["SOURCE_total_phase_budgets_rad"]=[[1,10**12],[1,10**12]]
        r=record("small_SOURCE_partial",q);self.assertEqual(r["status"],"CPU_DECLARED_SOURCE_MATERIAL_PHASE_BOUNDS_ONLY")
        q["relative_total_phase_budget_rad"]=[0,1]
        self.assertEqual(record("small_SOURCE_relative_STOP",q)["reason"],"relative_total_phase_budget_exceeded")
    def test_04_shared_material_cancels_not_its_addition_errors(self):
        q=request();q["source_phases"][1]["phase_cycles"]=[0,1];q["material_phase"]["phase_cycles"]=[1,2**56]
        q["relative_total_phase_budget_rad"]=[1,10**12]
        r=record("shared_material_SOURCE_STOP",q);self.assertEqual(r["reason"],"SOURCE_total_phase_budget_exceeded")
        self.assertTrue(r["relative"]["shared_material_phase_cancels_exactly"])
        self.assertTrue(r["relative"]["budget_fits"])
        self.assertEqual(r["rows"][1]["material_add_RN_error_cycles"],[1,2**56])
        q["SOURCE_total_phase_budgets_rad"]=[[1,10**12],[1,10**12]];q["relative_total_phase_budget_rad"]=[0,1]
        self.assertEqual(record("shared_material_relative_STOP",q)["reason"],"relative_total_phase_budget_exceeded")
    def test_05_parameter_loss_before_ANY_path_addition(self):
        for name,target,value in (("source_transport_loss","source",F(0.1)),("material_transport_loss","material",F(0.1)),
                                  ("first_cast_loss","source",F(1,10))):
            q=request()
            if target=="source":q["source_phases"][1]["phase_cycles"]=m.pair(value)
            else:q["material_phase"]["phase_cycles"]=m.pair(value)
            r=record(name,q);self.assertEqual(r["reason"],"phase_parameter_transport_loss")
            self.assertEqual(r["rows"],[]);self.assertEqual(r["new_source_phase_RN64_additions"],0)
    def test_06_ALL_binding_before_encoder(self):
        variants={
          "source_subset":lambda q:q["source_phases"].pop(),
          "source_reorder":lambda q:q["source_phases"].reverse(),
          "branch_changed":lambda q:q["source_phases"][1].update(branch_id="S0/mirror"),
          "primitive_changed":lambda q:q["material_phase"].update(primitive_id=0),
          "primitive_bool":lambda q:q["material_phase"].update(primitive_id=True),
          "object_changed":lambda q:q["material_phase"].update(object_id="foreign"),
          "profile_changed":lambda q:q["material_phase"].update(profile="physical_Fresnel"),
          "declaration_changed":lambda q:q.update(declaration="PHYSICALLY_AUTHENTICATED"),
          "scene_changed":lambda q:q.update(original_scene_sha256="0"*64),
          "prepared_changed":lambda q:q.update(prepared_sha256="0"*64),
          "result_changed":lambda q:q.update(propagation_result_sha256="0"*64),
          "detector_changed":lambda q:q["detector_point_BU"].__setitem__(0,[1,2**56]),
          "negative_cap":lambda q:q.update(relative_total_phase_budget_rad=[-1,1]),
          "missing_caps":lambda q:q.pop("SOURCE_total_phase_budgets_rad"),
          "missing_material":lambda q:q.pop("material_phase"),
          "units_changed":lambda q:q.update(units="BU/rad")}
        for name,mutate in variants.items():
            q=request();mutate(q)
            with patch.object(m,"encoder",side_effect=AssertionError("encoder must not run")):r=record(name,q)
            self.assertEqual(r["status"],"STOP");self.assertEqual(r["new_RN32_casts"],0);self.assertEqual(r["emitted_sources"],[])
        q=request("relative_zero_STOP")
        self.assertEqual(record("upstream_STOP",q)["reason"],"upstream_propagation_STOP")
        q=request()
        with patch.object(m,"PARENT_SHA","0"*64):self.assertEqual(record("parent_changed",q)["reason"],"sealed_parent_identity")
        self.assertEqual(record("wrong_model",request(),model="wrong")["reason"],"explicit_model_required")
    def test_07_no_FIELD_claim_and_defensive_copy(self):
        q=request();before=deepcopy(q);r=record("copy",q);self.assertEqual(q,before)
        r["emitted_sources"][0]["source_id"]="changed"
        self.assertEqual(r["rows"][0]["source_id"],"S0")
        # Do not corrupt the sealed evidence with the deliberate local output mutation.
        RESULTS["copy"]["emitted_sources"]=deepcopy(r["rows"])
        for v in RESULTS.values():
            self.assertTrue(all(v[k] is False for k in m.FLAGS))
            self.assertTrue(all(v[k] is None for k in ("detector_complex_field","detector_power","source_amplitude")))
            self.assertEqual(v["geometry_producers_reexecuted"],0);self.assertEqual(v["propagation_producers_reexecuted"],0)
if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,
                      "data":{"requests":REQUESTS,"results":RESULTS}},sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
