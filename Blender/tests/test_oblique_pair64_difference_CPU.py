"""Bounded new CPU arithmetic tests, no parent producer/suite replay."""
import importlib.util,json,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("new_diff",ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_difference_CPU_v1.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
INPUTS={};RESULTS={};CONTROLS={};SYNTHETIC={}
def checked(name,q,model=None):
    model=m.MODEL if model is None else model;INPUTS[name]=dict(selector=q,model=model)
    v=m.transport(q,model=model);RESULTS[name]=v;return v
class Tests(unittest.TestCase):
    def stop(self,v):
        self.assertEqual(v["status"],"STOP");self.assertEqual(v["rows"],[])
    def test_01_retained_ALL_cases(self):
        d=m.retained()
        for name,v in d["results"].items():
            got=checked(name,m.selector(name))
            if v["status"]=="STOP":self.stop(got);self.assertEqual(got["RN64_operations"],0)
            else:
                self.assertEqual(got["status"],"CPU_OBLIQUE_PAIR64_DIFFERENCE_ONLY")
                self.assertEqual(got["RN64_operations"],26);self.assertEqual(len(got["rows"]),3)
                self.assertTrue(all(e["residual_exact"] for e in got["trace"]["eft"]))
        self.assertEqual(sum(v["status"]!="STOP" for v in RESULTS.values()),4)
    def test_02_binding_and_model(self):
        q=m.selector()
        for key,value in (("case","missing"),("case",False),("parent_result_sha256","0"*64),
            ("original_scene_sha256","0"*64),("literal_request_sha256","0"*64),("representation","old_GPU_ABI")):
            wrong={**q,key:value};self.stop(checked("new_bad_"+key+str(value),wrong))
        self.stop(checked("new_extra_cap",{**q,"cap_override":1}))
        self.stop(checked("new_missing_rep",{k:v for k,v in q.items() if k!="representation"}))
        self.stop(checked("new_wrong_model",q,"old"))
    def test_03_single_collapsed_CONTROL(self):
        for case in ("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60"):
            p=m.retained()["results"][case];rows=p["rows"];a,b=[tuple(m.scalar(s[k]["word_le_hex"]) for k in ("hi","lo")) for s in rows[:2]]
            trace={"nodes":[],"eft":[]}
            x=m.rounded(*a,"+","collapse0",trace);z=m.rounded(*b,"+","collapse1",trace)
            y=m.rounded(x,z,"-","difference",trace);aa,bb=[F(*v) for v in rows[2]["interval"]]
            bound=8*max(abs(m.exact(y)-aa),abs(m.exact(y)-bb));cap=F(*rows[2]["literal_cap_rad"])
            CONTROLS[case]=dict(trace=trace,value=m.word(y),bound_rad=m.pair(bound),cap_rad=m.pair(cap),fits=bound<=cap)
        self.assertFalse(CONTROLS["parent_oblique"]["fits"])
        self.assertTrue(CONTROLS["parent_tiny_gap_2m60"]["fits"])
    def test_04_synthetic_native_NOT_scene(self):
        fixtures={"cancel_lo":((1.0,2.**-56),(1.0,0.0)),
            "shared_large":((1000.0,2.**-44),(1000.0,2.**-45)),
            "negative":((-1.0,-2.**-56),(1.0,2.**-56)),
            "zero":((1.0,2.**-56),(1.0,2.**-56)),
            "subnormal":((2.**-1074,0.0),(0.0,0.0))}
        for name,(a,b) in fixtures.items():
            trace={"nodes":[],"eft":[]};h,l=m.native_difference(a,b,trace)
            SYNTHETIC[name]=dict(a=[m.word(x) for x in a],b=[m.word(x) for x in b],hi=m.word(h),lo=m.word(l),trace=trace)
            self.assertEqual(m.exact(h)+m.exact(l),sum(map(m.exact,a))-sum(map(m.exact,b)))
            self.assertEqual(len(trace["nodes"]),26)
        for a in ((1,0.0),(float("inf"),0.0),(2.**41,0.0)):
            trace={"nodes":[],"eft":[]}
            with self.assertRaises(ValueError):m.native_difference(a,(0.0,0.0),trace)
            self.assertEqual(trace["nodes"],[])
        CONTROLS["typed_nonfinite_domain_rejects"]=3
    def test_05_faults_are_STOP_not_RNE(self):
        q=m.selector()
        with patch.object(m,"PSHA","0"*64):self.stop(m.transport(q,model=m.MODEL))
        with patch.object(m.Path,"read_bytes",side_effect=OSError("synthetic_denied")):self.stop(m.transport(q,model=m.MODEL))
        genuine=m.native_difference
        def lost(a,b,trace):
            h,l=genuine(a,b,trace);return h,0.0
        with patch.object(m,"native_difference",lost):
            v=m.transport(q,model=m.MODEL);self.stop(v);self.assertEqual(v["reason"],"arithmetic_output_identity")
            CONTROLS["output_low_loss"]=v
        genuine_round=m.rounded
        def corrupt(a,b,op,name,trace):
            y=genuine_round(a,b,op,name,trace)
            if name=="h_e":
                trace["nodes"][-1]["fault_original_y"]=m.word(y)
                y=0.0;trace["nodes"][-1]["y"]=m.word(y)
                target=m.exact(a)+m.exact(b)
                trace["nodes"][-1]["error"]=m.pair(abs(m.exact(y)-target))
            return y
        trace={"nodes":[],"eft":[]}
        with patch.object(m,"rounded",corrupt):
            with self.assertRaisesRegex(ValueError,"measured_EFT_identity"):m.native_difference((1.0,0.0),(-2.**-56,0.0),trace)
        CONTROLS["corrupt_EFT_trace"]=trace
        CONTROLS.update(parent_identity_STOP=True,read_denied_STOP=True)
    def test_06_scope_and_budget(self):
        for v in RESULTS.values():
            self.assertTrue(all(v[k]is False for k in m.FLAGS))
            self.assertTrue(all(v[k]is None for k in ("source_phase","mirror_phase","amplitude","field","power")))
            self.assertEqual(v["frozen_producer_replays"],0)
            if v["rows"]:
                e=v["rows"][2]
                total=F(*e["interval_radius_cycles"])+F(*e["source_rounding_budget_cycles"])+F(*e["arithmetic_error_cycles"])
                self.assertEqual(F(*e["conservative_error_bound_rad"]),8*total)
                self.assertLessEqual(F(*e["direct_error_bound_rad"]),8*total)
                self.assertLessEqual(8*total,F(*e["literal_cap_rad"]))
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps(dict(status="PASS" if r.wasSuccessful() else "FAIL",tests=r.testsRun,
        data=dict(inputs=INPUTS,results=RESULTS,controls=CONTROLS,synthetic=SYNTHETIC)),sort_keys=True,allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
