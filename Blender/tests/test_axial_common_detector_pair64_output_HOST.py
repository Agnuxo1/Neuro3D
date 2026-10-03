"""New comparator tests over retained ingress bytes, never executing the parent model/compiler."""
import importlib.util, json, struct, unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("new_output",ROOT/"Blender/benchmarks/capacity_audit/axial_common_detector_pair64_output_HOST_v1.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
INPUTS={};RESULTS={};CONTROLS={}

def observation(case="exact"):
    # Explicit fixture from RETAINED CPU mirror; not a new readback or dispatch.
    d=m.retained()
    return {"origin":m.ORIGIN,"output_hex":d["mirrors"]["scene_"+case]["output_hex"]}

def checked(name,q,obs,model=None):
    model=m.MODEL if model is None else model
    INPUTS[name]={"selector":deepcopy(q),"observation":deepcopy(obs),"model":model}
    v=m.compare(q,obs,model=model);RESULTS[name]=v;return v

class Tests(unittest.TestCase):
    def stop(self,v):
        self.assertEqual(v["status"],"STOP");self.assertEqual(v["rows"],[])
        self.assertFalse(v["HOST_bitwise_match_certified"]);self.assertFalse(v["GPU_job_admission"])
    def test_01_all_retained_prepares(self):
        d=m.retained()
        for case,v in d["prepares"].items():
            q=m.selector(case);obs=observation(case) if v["packet"] is not None else observation()
            got=checked("parent_"+case,q,obs)
            if v["packet"] is None:self.stop(got)
            else:
                self.assertEqual(got["status"],"HOST_OUTPUT_BITWISE_MATCH_NOT_EXECUTION_EVIDENCE")
                self.assertEqual(len(got["rows"]),3)
        self.assertEqual(sum(v["status"]!="STOP" for v in RESULTS.values()),11)
        self.assertEqual(sum(v["status"]=="STOP" for v in RESULTS.values()),28)
    def test_02_each_word_and_partial_status(self):
        q=m.selector();obs=observation();raw=bytes.fromhex(obs["output_hex"])
        for i in range(16):
            changed=bytearray(raw);changed[4*i]^=1
            self.stop(checked("word_"+str(i),q,{**obs,"output_hex":changed.hex()}))
        for name,status in (("unwritten",[0,0,0,0]),("row0_fail",[0,0,0,0]),("row1_fail",[0,0,1,0]),
                            ("relative_fail",[0,0,2,0]),("header_fail",[0,0,0xfffffff0,0])):
            self.stop(checked(name,q,{**obs,"output_hex":(struct.pack("<4I",*status)+raw[16:]).hex()}))
        self.stop(checked("partial_S0_then_failS1",q,{**obs,"output_hex":(raw[:16]+raw[16:32]+bytes(32)).hex()}))
    def test_03_sealed_mapping_not_received_reference(self):
        q=m.selector();obs=observation()
        for key in ("prepare_result_sha256","packet_sha256"):
            self.stop(checked("binding_"+key,{**q,key:"0"*64},obs))
        self.stop(checked("cross_case",m.selector("small_SOURCE_zero_STOP"),obs))
        self.stop(checked("claim_received_as_expected",q,{**obs,"expected_hex":obs["output_hex"][32:]}))
        self.stop(checked("caps_override",{**q,"caps_override":[1,1]},obs))
        self.stop(checked("scene_override",{**q,"original_scene_sha256":"0"*64},obs))
        self.stop(checked("old_model",q,obs,"axial-SOURCE-buffer-readback-compare-HOST-v1"))
    def test_04_encoding_and_types(self):
        q=m.selector();obs=observation();hx=obs["output_hex"]
        for name,value in (("missing",None),("short",hx[:-2]),("long",hx+"00"),("uppercase",hx.upper()),
                           ("spaces",hx[:2]+" "+hx[3:]),("not_hex","z"*128),("bool",False)):
            self.stop(checked("encoding_"+name,q,{**obs,"output_hex":value}))
        self.stop(checked("case_bool",{**q,"case":False},obs))
        self.stop(checked("selector_missing",{k:v for k,v in q.items() if k!="intent"},obs))
    def test_05_gpu_barrier_guard_aliases_not_authority(self):
        q=m.selector();obs=observation()
        for name,value in (("GPU_READBACK","GPU_READBACK"),("CPU_AUTHENTICATED","CPU_AUTHENTICATED")):
            self.stop(checked("origin_"+name,q,{**obs,"origin":value}))
        for flag in ("job_completed","barrier_applied","guard_passed","fresh_nonce","reservation_id"):
            self.stop(checked("untrusted_"+flag,q,{**obs,flag:True}))
        self.stop(checked("GPU_intent",{**q,"intent":"GPU_EXECUTE"},obs))
        valid=checked("copied_stale_bytes_still_unattested",q,obs)
        for key in ("GPU_executed","execution_authenticated","freshness_authenticated","host_completion_barrier_certified",
                    "resource_guard_certified","native_promotion_allowed","interference_phase_certified"):
            self.assertFalse(valid[key])
        self.assertTrue(valid["copied_or_stale_CPU_bytes_can_match"])
    def test_06_retained_failed_mirrors_and_tiny(self):
        d=m.retained();q=m.selector("small_SOURCE_zero_STOP")
        for name,old in d["mirrors"].items():
            if old["status"]!="CPU_COPY_COMMITTED_ONLY":
                obs={"origin":m.ORIGIN,"output_hex":old["output_hex"]}
                self.stop(checked("mirror_"+name,q,obs))
        got=checked("tiny_low_word",q,observation("small_SOURCE_zero_STOP"))
        self.assertEqual(got["status"],"HOST_OUTPUT_BITWISE_MATCH_NOT_EXECUTION_EVIDENCE")
        self.assertNotEqual(got["rows"][0]["hi_lo_uint32"][2:], [0,0])
        self.assertIsNone(got["field"]);self.assertIsNone(got["amplitude"])
    def test_07_read_errors_and_frozen_producers_not_imported(self):
        q=m.selector();obs=observation()
        with patch.object(m,"PARENT_SHA","0"*64):self.stop(m.compare(q,obs,model=m.MODEL))
        with patch.object(m.Path,"read_bytes",side_effect=OSError("synthetic_read_denied")):
            self.stop(m.compare(q,obs,model=m.MODEL))
        CONTROLS.update(changed_parent_rejected=True,read_denied_rejected=True,
                        parent_producer_compiler_replays=0,same_value_permutation_not_detectable=True,
                        output_origin="RETAINED_CPU_MIRROR_UNATTESTED_NOT_GPU")
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,
                     "data":{"inputs":INPUTS,"results":RESULTS,"controls":CONTROLS}},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
