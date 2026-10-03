"""New CPU representation tests, retained parent intervals; zero geometry/old producer calls."""
import importlib.util,json,unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("new_pair",ROOT/"Blender/benchmarks/capacity_audit/oblique_cycles_pair64_CPU_v1.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
INPUTS={};RESULTS={};CONTROLS={};SYNTHETIC={}
def checked(name,q,model=None):
    model=m.MODEL if model is None else model;INPUTS[name]={"selector":deepcopy(q),"model":model}
    v=m.transport(q,model=model);RESULTS[name]=v;return v
class Tests(unittest.TestCase):
    def stop(self,v):
        self.assertEqual(v["status"],"STOP");self.assertEqual(v["rows"],[])
        self.assertFalse(v["native_promotion_allowed"])
    def test_01_all_parent_cases_no_replay(self):
        d=m.retained()
        for name,v in d["results"].items():
            got=checked("parent_"+name,m.selector(name))
            if v["status"]=="STOP":
                self.stop(got);self.assertEqual(got["RN64_casts"],0)
            else:
                self.assertEqual(got["status"],"CPU_OBLIQUE_PAIR64_GEOMETRIC_TRANSPORT_ONLY")
                self.assertEqual(len(got["rows"]),3);self.assertEqual(got["RN64_casts"],6)
                self.assertTrue(all(r["pair_fits"] for r in got["rows"]))
        self.assertEqual(sum(v["status"]!="STOP" for v in RESULTS.values()),4)
    def test_02_single_word_control_same_literal_caps(self):
        for case in ("oblique","direction_scaled","shared_ref1000"):
            v=RESULTS["parent_"+case];self.assertFalse(v["single_word_ALL_caps_fit"])
            self.assertTrue(any(F(*r["hi"]["error"])>0 for r in v["rows"]))
            self.assertTrue(any(r["lo"]["word_le_hex"]!="0000000000000000" for r in v["rows"]))
        # Tiny magnitude CAN fit one-word absolute cap: no universal superiority claim.
        self.assertTrue(RESULTS["parent_tiny_gap_2m60"]["single_word_ALL_caps_fit"])
        CONTROLS["single_word_scene_ALL_caps"]={k:RESULTS["parent_"+k]["single_word_ALL_caps_fit"] for k in
            ("oblique","direction_scaled","shared_ref1000","tiny_gap_2m60")}
    def test_03_closed_binding_and_types(self):
        q=m.selector()
        for key,value in (("case","missing"),("case",False),("parent_result_sha256","0"*64),
                          ("original_scene_sha256","0"*64),("literal_request_sha256","0"*64),("representation","old_GPU_ABI")):
            wrong=deepcopy(q);wrong[key]=value;self.stop(checked("bad_"+key+"_"+str(value),wrong))
        self.stop(checked("extra_cap",{**q,"caps_override":[1,1]}))
        self.stop(checked("missing_rep",{k:v for k,v in q.items() if k!="representation"}))
        self.stop(checked("wrong_model",q,"old"))
    def test_04_parent_changed_read_denied_and_bad_RN(self):
        q=m.selector()
        with patch.object(m,"PARENT_SHA","0"*64):
            self.stop(m.transport(q,model=m.MODEL))
        with patch.object(m.Path,"read_bytes",side_effect=OSError("synthetic_denied")):
            self.stop(m.transport(q,model=m.MODEL))
        # Inject low component loss only; preserve the genuine measured ledger for high.
        genuine=m.rn64;calls=[0]
        def bad(x):
            calls[0]+=1
            if calls[0]%2==0:return {"input":m.pair(x),"word_le_hex":"0000000000000000","decoded":[0,1],"error":m.pair(abs(x))}
            return genuine(x)
        with patch.object(m,"rn64",bad):
            v=m.transport(q,model=m.MODEL);self.stop(v);self.assertEqual(v["reason"],"pair_SOURCE_relative_cap")
            CONTROLS["low_loss_result"]=v
        CONTROLS.update(parent_changed_STOP=True,read_denied_STOP=True,low_loss_RN_casts=calls[0])
    def test_05_synthetic_not_scene_models(self):
        for name,x in (("third",F(1,3)),("tiny_lo",F(1)+F(1,2**56)),("negative_tiny",F(-1)+F(1,2**56)),
                       ("negative",F(-1,3)),("zero",F(0)),("half_subnormal",F(1,2**1075))):
            e=m.encode_interval((x,x));SYNTHETIC[name]=e
            self.assertEqual(F(*e["pair_error_bound_cycles"]),abs(F(*e["pair_value"])-x))
        self.assertGreater(F(*SYNTHETIC["third"]["lo"]["error"]),0)
        self.assertEqual(SYNTHETIC["tiny_lo"]["pair_rounding_error"],[0,1])
        with self.assertRaises(ValueError):m.rn64(F(2**1024))
        with self.assertRaises(ValueError):m.rn64(1.0)
        CONTROLS["synthetic_overflow_type_rejects"]=2
    def test_06_no_material_or_gpu_inference(self):
        for v in RESULTS.values():
            self.assertIsNone(v["source_phase"]);self.assertIsNone(v["mirror_phase"])
            self.assertIsNone(v["amplitude"]);self.assertIsNone(v["field"]);self.assertIsNone(v["power"])
            self.assertTrue(all(v[k]is False for k in m.FLAGS))
            self.assertEqual(v["new_geometry_queries"],0);self.assertEqual(v["new_sqrt_calls"],0)
            self.assertEqual(v["frozen_producer_replays"],0)
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,
        "data":{"inputs":INPUTS,"results":RESULTS,"controls":CONTROLS,"synthetic":SYNTHETIC}},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
