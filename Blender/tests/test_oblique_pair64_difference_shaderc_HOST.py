"""New shader packets/static compile only. Zero GPU and zero parent arithmetic replays."""
import base64,importlib.util,json,struct,unittest,zlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("new_shader",ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_difference_shaderc_HOST_v1.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
INPUTS={};RESULTS={};COMPILES={};CONTROLS={}
def checked(name,q,model=None):
    model=m.MODEL if model is None else model;INPUTS[name]=dict(selector=q,model=model)
    out=m.prepare(q,model=model);RESULTS[name]=out;return out
class Tests(unittest.TestCase):
    def stop(self,v):
        self.assertEqual(v["status"],"STOP");self.assertIsNone(v["packet"]);self.assertFalse(v["GPU_launch_allowed"])
    def test_01_retained_ALL_work_without_RN_replay(self):
        for name,v in m.retained()["results"].items():
            got=checked(name,m.selector(name))
            if v["status"]=="STOP":self.stop(got)
            else:
                self.assertEqual(got["status"],"CPU_SHADER_CANDIDATE_PACKET_ONLY")
                p=got["packet"];raw=bytes.fromhex(p["input_hex"])
                self.assertEqual(len(raw),48);self.assertEqual(struct.unpack("<4I",raw[:16]),(m.TAG,8,2,1))
                want=b"".join(bytes.fromhex(s[k]["word_le_hex"]) for s in v["rows"][:2] for k in ("hi","lo"))
                self.assertEqual(raw[16:],want);self.assertEqual(p["total_SSBO_bytes"],80)
                self.assertEqual(p["retained_CPU_budget"],v["rows"][2]);self.assertEqual(p["execution_status"],"NOT_EXECUTED")
        self.assertEqual(sum(v["status"]!="STOP" for v in RESULTS.values()),4)
    def test_02_closed_scene_literal_shader_intent(self):
        q=m.selector()
        for key,value in (("case","missing"),("case",False),("parent_result_sha256","0"*64),
            ("original_scene_sha256","0"*64),("literal_request_sha256","0"*64),("representation","old"),
            ("shader_sha256","0"*64),("intent","RUN_GPU")):
            self.stop(checked("bad_"+key+str(value),{**q,key:value}))
        self.stop(checked("extra_launch",{**q,"GPU_launch_allowed":True}))
        self.stop(checked("missing_shader",{k:v for k,v in q.items() if k!="shader_sha256"}))
        self.stop(checked("shader_wrong_model",q,"old"))
    def test_03_dependency_failure_before_packet(self):
        q=m.selector()
        with patch.object(m,"PSHA","0"*64):self.stop(m.prepare(q,model=m.MODEL))
        with patch.object(m,"SHADER_SHA","0"*64):self.stop(m.prepare(q,model=m.MODEL))
        with patch.object(m.Path,"read_bytes",side_effect=OSError("synthetic_denied")):self.stop(m.prepare(q,model=m.MODEL))
        CONTROLS["parent_shader_read_rejects"]=3
    def test_04_compile_NEW_existing_DLL(self):
        source=(ROOT/m.SHADER).read_bytes()
        pos=m.compile_source(source,model=m.MODEL);COMPILES["positive"]=pos
        neg=m.compile_source(source+b"\nINVALID_OBLIQUE_TOKEN\n",model=m.MODEL);COMPILES["syntax_negative"]=neg
        self.assertEqual(pos["status"],0,pos["diagnostics"]);self.assertNotIn("inspection_failure",pos,pos)
        self.assertEqual(pos["inspection"]["NoContraction_arithmetic_nodes"],8)
        self.assertNotEqual(neg["status"],0);self.assertGreater(neg["errors"],0)
        with patch.object(m.C,"CDLL",side_effect=AssertionError("must not load")):
            with self.assertRaises(ValueError):m.compile_source(source,model="old")
            with patch.object(m,"DLL_SHA","0"*64):
                with self.assertRaises(ValueError):m.compile_source(source,model=m.MODEL)
        CONTROLS["before_DLL_load_rejects"]=2
    def test_05_structural_failures_retained(self):
        raw=zlib.decompress(base64.b64decode(COMPILES["positive"]["spirv"]["zlib_base64"]))
        w=list(struct.unpack("<"+"I"*(len(raw)//4),raw));changed=w.copy();i=5
        while i<len(changed):
            n=changed[i]>>16;op=changed[i]&65535
            if op==71 and changed[i+2]==42:changed[i+2]=0;break
            i+=n
        with self.assertRaises(ValueError):m.inspect_spirv(struct.pack("<"+"I"*len(changed),*changed))
        changed=w.copy();i=5
        while i<len(changed):
            n=changed[i]>>16;op=changed[i]&65535
            if op==17 and changed[i+1]==10:changed[i+1]=9;break
            i+=n
        with self.assertRaises(ValueError):m.inspect_spirv(struct.pack("<"+"I"*len(changed),*changed))
        with self.assertRaises(ValueError):m.inspect_spirv(raw[:-1])
        with self.assertRaises(ValueError):m.inspect_spirv(b"\x00"*20)
        CONTROLS["structural_rejects"]=4
    def test_06_NEVER_runtime_or_physical_admission(self):
        for v in RESULTS.values():
            self.assertTrue(all(v[k]is False for k in ("GPU_executed","GPU_launch_allowed","GPU_semantics_certified","physical_field_certified","native_promotion_allowed")))
            self.assertEqual(v["new_RN_operations"],0);self.assertEqual(v["frozen_producer_replays"],0)
            self.assertEqual(v["full_costs"],"UNMEASURED_NOT_ZERO")
            if v["packet"]:self.assertFalse(v["packet"]["GPU_launch_allowed"])
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps(dict(status="PASS" if r.wasSuccessful() else "FAIL",tests=r.testsRun,
        data=dict(inputs=INPUTS,results=RESULTS,compiles=COMPILES,controls=CONTROLS)),sort_keys=True,allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
