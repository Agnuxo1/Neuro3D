"""NEW CPU mirror and shaderc compile tests. No parent producer/compiler replay and no GPU."""
import importlib.util,json,struct,unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("new_ingress",ROOT/"Blender/benchmarks/capacity_audit/axial_common_detector_pair64_ingress_HOST_v1.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
REQUESTS={};PREPARES={};INPUTS={};MIRRORS={};COMPILES={};CONTROLS={}
MODELS={}
def prepared(name,q,model=None):
    MODELS[name]=m.MODEL if model is None else model
    REQUESTS[name]=deepcopy(q);v=m.prepare(q,model=m.MODEL if model is None else model);PREPARES[name]=v;return v
def checked(name,a,b,gid=(0,0,0)):
    INPUTS[name]={"input_hex":a.hex(),"expected_hex":b.hex(),"global_id":list(gid)}
    v=m.mirror(a,b,global_id=gid);MIRRORS[name]=v;return v
class Tests(unittest.TestCase):
    def assertSTOP(self,v):
        self.assertEqual(v["status"],"STOP");self.assertIsNone(v["packet"])
        self.assertFalse(v["GPU_executed"]);self.assertEqual(v["phase_RN_executed"],0)
    def test_01_scene_bound_parent_ALL_cases(self):
        data=m.retained()
        for name,old in data["pack_results"].items():
            v=prepared(name,m.selector(name))
            if old["status"]=="STOP":self.assertSTOP(v)
            else:
                self.assertEqual(v["status"],"CPU_PAIR64_INGRESS_PACKET_ONLY");p=v["packet"]
                value=checked("scene_"+name,bytes.fromhex(p["input_hex"]),bytes.fromhex(p["expected_hex"]))
                self.assertEqual(value["status"],"CPU_COPY_COMMITTED_ONLY")
                raw=bytes.fromhex(value["output_hex"]);self.assertEqual(list(struct.unpack("<4I",raw[:16])),[m.TAG,3,0xffffffff,1])
                self.assertEqual(raw[16:],bytes.fromhex(p["expected_hex"]))
                self.assertEqual(p["total_SSBO_bytes"],176);self.assertEqual(p["shader_sha256"],m.SHADER_SHA)
        self.assertEqual(sum(v["status"]!="STOP" for v in PREPARES.values()),11)
        self.assertEqual(sum(v["status"]=="STOP" for v in PREPARES.values()),19)
    def test_02_each_limb_and_header_atomic(self):
        p=m.prepare(m.selector("small_SOURCE_zero_STOP"),model=m.MODEL)["packet"]
        a=bytes.fromhex(p["input_hex"]);b=bytes.fromhex(p["expected_hex"])
        for j in range(12):
            changed=bytearray(a);w=int.from_bytes(changed[16+4*j:20+4*j],"little")^1
            changed[16+4*j:20+4*j]=w.to_bytes(4,"little")
            v=checked("limb_"+str(j),bytes(changed),b);self.assertEqual(v["status"],"CPU_STOP_UNCOMMITTED")
            out=bytes.fromhex(v["output_hex"]);self.assertEqual(out[16:],bytes(48))
            self.assertEqual(list(struct.unpack("<4I",out[:16])),[0,0,j//4,0])
        for j in range(4):
            changed=bytearray(a);changed[4*j]^=1
            v=checked("header_"+str(j),bytes(changed),b);self.assertEqual(v["status"],"CPU_STOP_UNCOMMITTED")
            self.assertEqual(bytes.fromhex(v["output_hex"])[16:],bytes(48))
        v=checked("other_invocation",a,b,(1,0,0));self.assertEqual(v["status"],"CPU_NO_WRITE")
        self.assertIsNone(v["output_hex"])
    def test_03_synthetic_integer_identity_specials(self):
        # Synthetic byte identity only, not scene admission or a float arithmetic model.
        words=[0,2**63,1,0x8000000000000001,0x0010000000000000,0x7fefffffffffffff]
        raw=b"".join(w.to_bytes(8,"little") for w in words)
        out=checked("synthetic_specials",struct.pack("<4I",m.TAG,1,3,16)+raw,raw)
        self.assertEqual(bytes.fromhex(out["output_hex"])[16:],raw)
        for label,word in (("nan",0x7ff8000000000001),("inf",0x7ff0000000000000)):
            wrong=raw[:24]+word.to_bytes(8,"little")+raw[32:]
            v=checked("synthetic_"+label,struct.pack("<4I",m.TAG,1,3,16)+wrong,wrong)
            self.assertEqual(v["status"],"CPU_STOP_UNCOMMITTED")
            self.assertEqual(bytes.fromhex(v["output_hex"])[16:],bytes(48))
    def test_04_closed_selectors_and_extent(self):
        q=m.selector()
        for key,value in (("parent_result_sha256","0"*64),("original_scene_sha256","0"*64),
                          ("literal_request_sha256","0"*64),("intent","GPU"),("case","missing")):
            wrong=deepcopy(q);wrong[key]=value;self.assertSTOP(prepared("selector_"+key,wrong))
        for name,wrong in (("extra",{**q,"caps_override":[1,1]}),("bool",{**q,"case":False}),
                           ("missing",{k:v for k,v in q.items() if k!="intent"})):
            self.assertSTOP(prepared("selector_"+name,wrong))
        self.assertSTOP(prepared("bad_model",q,"old"))
        for a,b,gid in ((bytes(63),bytes(48),(0,0,0)),(bytes(64),bytes(47),(0,0,0)),
                        (bytes(64),bytes(48),(False,0,0))):
            with self.assertRaises(ValueError):m.mirror(a,b,global_id=gid)
        CONTROLS["extent_rejects"]=3
        with patch.object(m,"SHADER_SHA","0"*64):
            self.assertSTOP(m.prepare(q,model=m.MODEL))
        CONTROLS["changed_shader_rejected_before_packet"]=True
    def test_05_compile_existing_CPU_only(self):
        source=(ROOT/m.SHADER).read_bytes();self.assertEqual(m.sha(source),m.SHADER_SHA)
        positive=m.compile_source(source,model=m.MODEL);COMPILES["vulkan1_0_positive"]=positive
        self.assertEqual((positive["status"],positive["errors"],positive["warnings"]),(0,0,0))
        self.assertFalse(positive["structural_inspection"]["GPU_semantics_certified"])
        negative=m.compile_source(source+b"\nINVALID_PAIR64_TOKEN\n",model=m.MODEL);COMPILES["syntax_negative"]=negative
        self.assertNotEqual(negative["status"],0);self.assertGreater(negative["errors"],0)
        self.assertTrue(negative["diagnostics"]);self.assertEqual(negative["spirv"]["bytes"],0)
        with patch.object(m.C,"CDLL",side_effect=AssertionError("must not load")):
            with self.assertRaises(ValueError):m.compile_source(source,model="old")
            with patch.object(m,"DLL_SHA","0"*64):
                with self.assertRaises(ValueError):m.compile_source(source,model=m.MODEL)
        CONTROLS["before_DLL_load_rejects"]=2
    def test_06_structural_corruption(self):
        # No second compilation here: retained NEW result from test_05.
        raw=__import__("zlib").decompress(__import__("base64").b64decode(COMPILES["vulkan1_0_positive"]["spirv"]["zlib_base64"]))
        for bad in (b"",raw[:-1],bytes(4)+raw[4:],raw[:20]+bytes(4)):
            with self.assertRaises(ValueError):m.inspect_spirv(bad)
        CONTROLS["SPIRV_corruption_rejects"]=4
    def test_07_tiny_old_STOPS_and_no_field_claim(self):
        data=m.retained()
        for name in ("small_SOURCE_zero_STOP","shared_material_SOURCE_STOP","retained_second_SOURCE_zero_STOP"):
            q=m.selector(name);old=data["pack_results"][name];v=m.prepare(q,model=m.MODEL)
            self.assertEqual(v["status"]=="STOP",old["status"]=="STOP")
        p=m.prepare(m.selector("small_SOURCE_zero_STOP"),model=m.MODEL)["packet"]
        raw=bytes.fromhex(p["expected_hex"]);self.assertNotEqual(int.from_bytes(raw[8:16],"little"),0)
        CONTROLS["retained_parent_raw_identity"]=m.PARENT_SHA
if __name__=="__main__":
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if r.wasSuccessful() else "FAIL","tests":r.testsRun,
                     "data":{"requests":REQUESTS,"model_inputs":MODELS,"prepares":PREPARES,"mirror_inputs":INPUTS,"mirrors":MIRRORS,
                             "compiles":COMPILES,"controls":CONTROLS}},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
