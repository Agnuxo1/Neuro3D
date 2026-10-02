"""New HOST staging tests. Never imports decoder/compiler or launches GPU."""
import base64,copy,json,struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_SOURCE_compiled_buffer_prep_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.retained=c.load_retained()
  with patch.object(c,"load_retained",return_value=cls.retained):
   cls.request=c.make_request(model=c.MODEL)
 def test_compiled_layout_and_source_buffers(self):
  with patch.object(c,"load_retained",return_value=self.retained):
   plan=c.prepare(copy.deepcopy(self.request),model=c.MODEL)
  packed=base64.b64decode(plan["input_buffer"]["base64"],validate=True)
  expected=b"".join(base64.b64decode(r["hilo_le_base64"]) for r in self.retained["input"]["decoder_INPUT"]["SOURCE_limb_records"])
  self.assertEqual(packed,expected);self.assertEqual(len(packed),64)
  self.assertEqual(plan["output_buffer"]["planned_bytes"],128);self.assertIsNone(plan["output_buffer"]["result_bytes"])
  self.assertEqual(plan["compiled_layout"],[{"set":0,"binding":0,"stride_bytes":8,"components_uint32":2,"member_offset":0},{"set":0,"binding":1,"stride_bytes":16,"components_uint32":4,"member_offset":0}])
  self.assertEqual([v["scalar_index"] for v in plan["scalar_mapping"]],list(range(8)))
  self.assertEqual([v["component"] for v in plan["scalar_mapping"]],["real","imag"]*4)
  self.assertEqual(plan["scalar_mapping"][-1]["source_id"],"other")
  self.assertEqual(len({v["context_sha256"] for v in plan["scalar_mapping"]}),3)
  self.assertFalse(plan["GPU_executed"]);self.assertFalse(plan["GPU_job_admission"])
  self.assertEqual(plan["group_admissions"],0);self.assertTrue(all(v is False for v in plan["general_proof_scope"].values()))
  self.assertEqual(plan["new_decoder_calls"],plan["new_compiler_calls"]);self.assertEqual(plan["new_decoder_calls"],0)
  self.assertTrue(plan["old_CPU_tag_is_NOT_compiled_program_selection"])
  DATA.update(request=self.request,plan=plan)
 def test_atomic_request_rejections(self):
  controls=[]
  def mutant(name,fn):
   r=copy.deepcopy(self.request);fn(r);controls.append((name,r))
  mutant("compiled module",lambda r:r["compiled_selection"].update(module_sha256="0"*64))
  mutant("wrapper SHA",lambda r:r["compiled_selection"].update(wrapper_sha256="0"*64))
  mutant("legacy decoder alias",lambda r:r["compiled_selection"].update(SOURCE_header_sha256=c.OLD_CPU_SHA))
  mutant("opengl target alias",lambda r:r["compiled_selection"].update(target_env=1,target_version=450))
  mutant("legacy model",lambda r:r.update(model="axial-SOURCE-zero-aware-integer-words-GLSL-v1"))
  mutant("GPU intent",lambda r:r.update(intent="GPU"))
  mutant("extra dispatch",lambda r:r.update(dispatch=[9,1,1]))
  mutant("truncated source",lambda r:r["upstream_CPU_snapshot"]["frames"].pop())
  mutant("late frame corrupt",lambda r:r["upstream_CPU_snapshot"]["frames"][-1].update(frame_base64="AA=="))
  mutant("source mixing",lambda r:r["upstream_CPU_snapshot"]["frames"][-1].update(source_id="s"))
  mutant("ORIGINAL changed",lambda r:r["upstream_CPU_snapshot"]["decoder_INPUT"]["SOURCE_limb_records"][-1]["scalars"][0].update(original_uint64=0))
  mutant("limbs reordered",lambda r:r["upstream_CPU_snapshot"]["decoder_INPUT"]["SOURCE_limb_records"][-1]["limb_uint32"].reverse())
  mutant("boolean target alias",lambda r:r["compiled_selection"].update(target_env=False))
  records=[]
  for name,r in controls:
   with patch.object(c,"load_retained",return_value=self.retained),patch.object(c,"emit_plan",wraps=c.emit_plan) as emit:
    with self.assertRaises(ValueError):c.prepare(r,model=c.MODEL)
    self.assertEqual(emit.call_count,0);records.append({"control":name,"emissions":0,"rejected":True})
  DATA["atomic_rejections"]=records
 def test_frame_boundary_rejections(self):
  good=self.retained["input"];controls=[]
  for offset in (0,8,40,72,104):
   v=copy.deepcopy(good);f=v["frames"][-1];raw=bytearray(base64.b64decode(f["frame_base64"]));raw[offset]^=1
   f["frame_base64"]=base64.b64encode(raw).decode()
   controls.append(("frame byte "+str(offset),v))
  for label,word in (("bool",True),("negative",-1),("overflow",1<<32),("float",0.0),("subnormal",1),("Inf",0x7f800000),("NaN",0x7fc00000)):
   v=copy.deepcopy(good);v["decoder_INPUT"]["SOURCE_limb_records"][-1]["limb_uint32"][3]=word
   v["program_INPUT"]["decoder_INPUT_sha256"]=c.digest(v["decoder_INPUT"])
   controls.append((label,v))
  v=copy.deepcopy(good);v["frames"][-1]["source_id"]="s";controls.append(("SOURCE mixing",v))
  for name,v in controls:
   with self.assertRaises(ValueError):c.frame_payloads(v)
  DATA["frame_rejections"]=[name for name,_ in controls]
 def test_dispatch_and_module_rejections(self):
  bad=[(9,72,144,[9,1,1]),(8,64,128,[9,1,1]),(8,64,128,[7,1,1]),(8,64,128,[8,2,1]),(8,64,128,[8,1,True]),(True,64,128,[8,1,1]),(8,63,128,[8,1,1]),(8,64,127,[8,1,1]),(8,64,128,(8,1,1))]
  for args in bad:
   with self.assertRaises(ValueError):c.dispatch_contract(*args)
  for module in (b"",self.retained["module"][:-4],b"X"+self.retained["module"][1:]):
   with self.assertRaises(ValueError):c.reflect_layout(module)
  for model in (None,False,"", "GPU"):
   with self.assertRaises(ValueError):c.prepare(self.request,model=model)
  DATA["dispatch_rejections"]=len(bad);DATA["module_rejections"]=3;DATA["model_rejections"]=4
if __name__=="__main__":
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
 raise SystemExit(0 if result.wasSuccessful() else 1)
