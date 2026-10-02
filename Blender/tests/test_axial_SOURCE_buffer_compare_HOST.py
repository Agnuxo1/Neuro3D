"""Synthetic byte controls ONLY. Does not generate or simulate GPU execution."""
import base64,copy,json,struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import axial_SOURCE_buffer_compare_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.retained=c.load_retained()
  with patch.object(c,"load_retained",return_value=cls.retained):cls.request=c.make_request(model=c.MODEL)
  cls.raw=b"".join(struct.pack("<4I",*v,1,0) for v in cls.retained["expected"])
  cls.packet={"origin":c.ORIGIN,"data_base64":base64.b64encode(cls.raw).decode()}
 def run_compare(self,r,p):
  with patch.object(c,"load_retained",return_value=self.retained):return c.compare(r,p,model=c.MODEL)
 def test_synthetic_words_not_execution(self):
  result=self.run_compare(self.request,self.packet)
  self.assertEqual(len(result["sources"]),4)
  self.assertEqual(result["sources"][-1]["source_id"],"other")
  self.assertTrue(all(s["word_match_to_retained_CPU_reference"] for s in result["sources"]))
  self.assertTrue(all(v is False for v in result["general_proof_scope"].values()))
  for key in ("GPU_executed","GPU_job_admission","execution_authenticated","scene_authenticated","actual_GPU_readback_available"):
   self.assertFalse(result[key])
  self.assertEqual(result["new_RN_operations"],0)
  self.assertIsNone(result["FIELD_evaluation"]);self.assertIsNone(result["phase_quota"])
  DATA.update(request=self.request,synthetic_packet=self.packet,result=result)
 def test_request_origin_rejections_atomic(self):
  cases=[]
  def mutation(name,fn):
   r,p=copy.deepcopy(self.request),copy.deepcopy(self.packet);fn(r,p);cases.append((name,r,p))
  mutation("GPU intent",lambda r,p:r.update(intent="GPU"))
  mutation("legacy model",lambda r,p:r.update(model="axial-SOURCE-compiled-buffer-prep-HOST-v1"))
  mutation("prepared plan mismatch",lambda r,p:r["selector"].update(prepared_plan_sha256="0"*64))
  mutation("module mismatch",lambda r,p:r["selector"].update(module_sha256="0"*64))
  mutation("INPUT mismatch",lambda r,p:r["selector"].update(input_buffer_sha256="0"*64))
  mutation("reference ORIGINAL alias",lambda r,p:r["selector"].update(expected_words_reference="ORIGINAL_SOURCE"))
  mutation("GPU origin assertion",lambda r,p:p.update(origin="GPU"))
  mutation("extra execution receipt",lambda r,p:p.update(GPU_job_receipt_sha256="1"*64))
  mutation("extra output tolerance",lambda r,p:r.update(tolerance=1))
  records=[]
  for name,r,p in cases:
   with patch.object(c,"load_retained",return_value=self.retained),patch.object(c,"emit_matches",wraps=c.emit_matches) as emit:
    with self.assertRaises(ValueError):c.compare(r,p,model=c.MODEL)
    self.assertEqual(emit.call_count,0);records.append({"control":name,"emissions":0,"rejected":True})
  DATA["request_rejections"]=records
 def test_byte_status_and_word_rejections_atomic(self):
  controls=[]
  for label,word_index,value in [
   ("late status0 correct words",30,0),("late status2",30,2),("late reserved1",31,1),
   ("late lowbitflip",28,1),("late signedzero",29,0x80000000),
   ("late NaNbits",29,0x7ff80000),("late Infbits",29,0x7ff00000),
   ("real ORIGINAL not decoded",0,2576980378)]:
   b=bytearray(self.raw);struct.pack_into("<I",b,4*word_index,value);controls.append((label,bytes(b)))
  controls.extend([("truncated",self.raw[:-1]),("trailing",self.raw+b"X"),("allzero",bytes(128))])
  swap=self.raw[:-32]+self.raw[-16:]+self.raw[-32:-16];controls.append(("late realimag swap",swap))
  records=[]
  for name,b in controls:
   p={"origin":c.ORIGIN,"data_base64":base64.b64encode(b).decode()}
   with patch.object(c,"load_retained",return_value=self.retained),patch.object(c,"emit_matches",wraps=c.emit_matches) as emit:
    with self.assertRaises(ValueError):c.compare(self.request,p,model=c.MODEL)
    self.assertEqual(emit.call_count,0);records.append({"control":name,"emissions":0,"rejected":True})
  for value in (None,False,128,b"",[],self.packet["data_base64"][:-1]+"!",self.packet["data_base64"]+"="):
   with self.assertRaises((ValueError,TypeError)):self.run_compare(self.request,{"origin":c.ORIGIN,"data_base64":value})
  DATA["byte_rejections"]=records;DATA["typed_base64_rejections"]=7
 def test_indistinguishable_equal_slots_limit(self):
  # All retained real SOURCE values match. Swapping equal complete scalar slots is unobservable.
  b=bytearray(self.raw);a,bslot=bytes(b[:16]),bytes(b[32:48])
  self.assertEqual(a,bslot);b[:16]=bslot;b[32:48]=a
  self.assertEqual(bytes(b),self.raw)
  result=self.run_compare(self.request,{"origin":c.ORIGIN,"data_base64":base64.b64encode(b).decode()})
  self.assertFalse(result["execution_authenticated"])
  self.assertTrue(result["same_value_slot_permutation_not_detectable"])
  self.assertTrue(result["copied_CPU_reference_can_match_without_GPU"])
  for model in (None,False,"GPU"):
   with self.assertRaises(ValueError):c.compare(self.request,self.packet,model=model)
  DATA["limits"]={"synthetic_copied_reference_matches_without_GPU":True,"equal_slots_swap_bytes_identical":True,"GPU_execution_still_unproved":True}
  DATA["model_rejections"]=3
if __name__=="__main__":
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
 raise SystemExit(0 if result.wasSuccessful() else 1)
