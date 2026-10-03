"""Seven bounded tests of a NEW twofold representation; baseline words and caps are never rewritten."""
import importlib.util,json,sys,unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("twofold_phase",ROOT/"Blender/benchmarks/capacity_audit/axial_common_detector_twofold_CPU_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REQUESTS={};RESULTS={};CONTROLS={}
def request(case="exact"):
    old,_=m.load_retained();q=old["requests"][case];v=old["results"][case]
    return {"retained_case":case,"retained_result_sha256":m.digest(v),"literal_request_sha256":m.digest(q),
            "original_scene_sha256":q["original_scene_sha256"],"representation":m.REPRESENTATION,"units":"cycles/rad"}
def record(name,q,model=None):
    REQUESTS[name]=deepcopy(q);v=m.audit(q,model=m.MODEL if model is None else model);RESULTS[name]=v;return v
class Tests(unittest.TestCase):
    def test_01_exact_cases_same_caps(self):
        for name in ("exact","signed_reference","large_exact_reference","explicit_zero"):
            r=record(name,request(name));self.assertEqual(r["status"],"CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY")
            self.assertEqual(r["relative"]["total_cycle_error_bound"],[0,1])
            self.assertEqual(r["relative"]["original_declared_cycles"],[4,1] if name=="explicit_zero" else [31,8])
            self.assertEqual(len(r["nodes"]),52);self.assertEqual(len(r["two_sum_checks"]),8)
    def test_02_twofold_retains_lost_SOURCE_and_material(self):
        for name in ("small_SOURCE_zero_STOP","small_SOURCE_partial","small_SOURCE_relative_STOP",
                     "shared_material_SOURCE_STOP","shared_material_relative_STOP"):
            r=record(name,request(name));self.assertEqual(r["status"],"CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY")
            self.assertEqual(r["relative"]["total_cycle_error_bound"],[0,1])
            self.assertEqual(r["rows"][0]["total_cycle_error_bound"],[0,1])
        r=RESULTS["small_SOURCE_zero_STOP"];self.assertEqual(r["retained_baseline_status"],"STOP")
        self.assertEqual(r["rows"][0]["represented_cycles"],m.pair(F(14)+F(1,2**56)))
        self.assertNotEqual(r["rows"][0]["pair_uint64"][1],0)
        self.assertEqual(RESULTS["shared_material_relative_STOP"]["relative"]["represented_cycles"],[4,1])
    def test_03_retained_propagation_error_not_repaired_by_sums(self):
        r=record("quotient_partial",request("quotient_partial"));self.assertEqual(r["status"],"CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY")
        self.assertEqual(r["relative"]["original_declared_cycles"],[13,24]);self.assertGreater(F(*r["relative"]["total_cycle_error_bound"]),0)
        r=record("retained_second_SOURCE_zero_STOP",request("retained_second_SOURCE_zero_STOP"))
        self.assertEqual(r["reason"],"SOURCE_total_phase_budget_exceeded");self.assertEqual(r["emitted_sources"],[])
    def test_04_upstream_transport_INPUT_STOP_not_rescued(self):
        for name in ("source_transport_loss","material_transport_loss","first_cast_loss","upstream_STOP","missing_material","parent_changed"):
            r=record("upstream_"+name,request(name));self.assertEqual(r["status"],"STOP");self.assertEqual(r["nodes"],[])
    def test_05_selector_integrity_and_no_cap_override(self):
        variants={
          "case_missing":lambda q:q.update(retained_case="no_case"),
          "result_changed":lambda q:q.update(retained_result_sha256="0"*64),
          "literal_changed":lambda q:q.update(literal_request_sha256="0"*64),
          "scene_changed":lambda q:q.update(original_scene_sha256="0"*64),
          "representation_changed":lambda q:q.update(representation="SINGLE_FLOAT64"),
          "units_changed":lambda q:q.update(units="radians"),
          "cap_override":lambda q:q.update(SOURCE_total_phase_budgets_rad=[[1,1],[1,1]]),
          "bool_selector":lambda q:q.update(retained_case=True),
          "missing_field":lambda q:q.pop("literal_request_sha256")}
        for name,mutate in variants.items():
            q=request();mutate(q)
            with patch.object(m,"two_sum",side_effect=AssertionError("TwoSum must not run")):r=record(name,q)
            self.assertEqual(r["status"],"STOP");self.assertEqual(r["nodes"],[]);self.assertEqual(r["emitted_sources"],[])
        self.assertEqual(record("wrong_model",request(),model="wrong")["reason"],"explicit_model_required")
        q=request()
        with patch.object(m,"PARENT_SHA","0"*64):self.assertEqual(record("parent_changed",q)["reason"],"sealed_parent_identity")
    def test_06_TwoSum_RN_order_ties_subnormals_and_overflow(self):
        tiny=float.fromhex("0x1p-56");sub=float.fromhex("0x0.0000000000001p-1022")
        values={"tiny":(14.,tiny),"reverse":(tiny,14.),"tie":(1.,float.fromhex("0x1p-53")),
                "cancel":(1.,-1.),"subnormal":(sub,sub),
                "normal_subnormal":(float.fromhex("0x1p-1022"),sub),"mixed_sign":(1.,-tiny),
                "overflow":(1e308,1e308)}
        for name,(a,b) in values.items():
            v={"a_uint64":m.word(a),"b_uint64":m.word(b),"nodes":[],"two_sum_checks":[],"status":"STOP","reason":None}
            try:
                h,l=m.two_sum(v,"control",a,b);v["pair_uint64"]=[m.word(h),m.word(l)];v["status"]="EXACT_PAIR"
                self.assertEqual(F(h)+F(l),F(a)+F(b))
            except m.ModelStop as e:v["reason"]=str(e)
            CONTROLS[name]=v
        self.assertEqual(CONTROLS["overflow"]["reason"],"finite_RN_result")
        self.assertEqual(len(CONTROLS["overflow"]["nodes"]),1)
        # Deliberate local return corruption must fail even if individual RN node traces are finite.
        q=request("small_SOURCE_zero_STOP");original=m.native
        def corrupt(out,label,kind,a,b):
            v=original(out,label,kind,a,b);return 0. if label=="S0.source.e" else v
        with patch.object(m,"native",side_effect=corrupt):r=record("injected_pair_fault",q)
        self.assertEqual(r["reason"],"TwoSum_exact_pair_failure");self.assertEqual(r["emitted_sources"],[])
        self.assertGreater(F(*r["two_sum_checks"][0]["exact_pair_defect_cycles"]),0)
    def test_07_no_native_FIELD_claim_or_input_mutation(self):
        q=request();before=deepcopy(q);r=record("copy",q);self.assertEqual(q,before)
        r["emitted_sources"][0]["source_id"]="changed";self.assertEqual(r["rows"][0]["source_id"],"S0")
        r["emitted_sources"]=deepcopy(r["rows"])
        for v in RESULTS.values():
            self.assertTrue(all(v[k] is False for k in m.FLAGS))
            self.assertTrue(all(v[k] is None for k in ("detector_complex_field","detector_power","source_amplitude")))
            self.assertEqual(v["representation"],m.REPRESENTATION)
            for k in ("geometry_producers_reexecuted","propagation_producers_reexecuted",
                      "baseline_material_producers_reexecuted","parameter_encoders_reexecuted"):self.assertEqual(v[k],0)
if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,
                     "data":{"requests":REQUESTS,"results":RESULTS,"controls":CONTROLS}},sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
