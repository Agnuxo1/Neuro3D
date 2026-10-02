"""Independent retained checker; no producer/decoder/compiler imports or execution."""
import base64,hashlib,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def payload(r):
 t=r["test_run"];assert t["rc"]==0 and not t["timed_out"]
 raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
 assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
 return json.loads(raw)["data"]
r=json.loads((ROOT/"coordinacion/respuestas/AXIAL-SOURCE-BUFFER-READBACK-COMPARE-HOST-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
t=r["test_run"];assert t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
d=payload(r);out=d["result"];packet=d["synthetic_packet"];request=d["request"]
hp_path="coordinacion/respuestas/AXIAL-SOURCE-COMPILED-BUFFER-PREP-HOST-001-CODEX.json"
hp=payload(json.loads((ROOT/hp_path).read_bytes()));plan=hp["plan"]
integer=payload(json.loads((ROOT/"coordinacion/respuestas/AXIAL-SOURCE-ZERO-AWARE-INTEGER-GLSL-001-CODEX.json").read_bytes()))
assert request["model"]==out["model"]=="axial-SOURCE-buffer-readback-compare-HOST-v1"
assert request["intent"]=="COMPARE_UNATTESTED_BYTES_ONLY"
assert request["selector"]==out["selector"]
sel=request["selector"]
assert sel["prepared_receipt_sha256"]==sha((ROOT/hp_path).read_bytes())
assert sel["prepared_plan_sha256"]==digest(plan)
assert sel["module_sha256"]==plan["module_sha256"] and sel["input_buffer_sha256"]==plan["input_buffer"]["sha256"]
assert sel["expected_words_reference"]=="RETAINED_CPU_INTEGER_OUTPUT_NOT_GPU_EXECUTION"
assert packet["origin"]=="UNATTESTED_BYTES_NOT_GPU_EVIDENCE"
raw=base64.b64decode(packet["data_base64"],validate=True);assert len(raw)==128 and sha(raw)==out["bytes_sha256"]
assert raw==base64.b64decode(out["observed_bytes_base64"],validate=True)
expected=b""
for i,src in enumerate(integer["audit"]["sources"]):
 words=[]
 for j,scalar in enumerate(src["scalars"]):
  low,high,status,reserved=struct.unpack_from("<4I",raw,16*(2*i+j))
  assert status==1 and reserved==0 and [low,high]==scalar["decoded_low_high_uint32"]
  assert low|(high<<32)==scalar["decoded_uint64"]
  expected+=struct.pack("<4I",low,high,1,0);words.append(low|(high<<32))
  m=plan["scalar_mapping"][2*i+j]
  assert (m["case_name"],m["source_id"],m["context_sha256"],m["SOURCE_row_sha256"])==(src["case_name"],src["source_id"],src["context_sha256"],src["encoder_row_sha256"])
 observed=out["sources"][i]
 assert (observed["case_name"],observed["source_id"],observed["context_sha256"])==(src["case_name"],src["source_id"],src["context_sha256"])
 assert observed["observed_uint64"]==words and observed["word_match_to_retained_CPU_reference"] is True
 assert observed["bytes_origin_authenticated"] is False
assert raw==expected
assert plan["output_buffer"]["result_bytes"] is None # Parent still has NO actual output.
assert len(out["general_proof_scope"])==38 and all(v is False for v in out["general_proof_scope"].values())
for key in ("GPU_executed","GPU_job_admission","execution_authenticated","scene_authenticated","actual_GPU_readback_available"):assert out[key] is False
assert out["group_admissions"]==out["new_decoder_calls"]==out["new_compiler_calls"]==out["new_RN_operations"]==0
assert out["FIELD_evaluation"] is out["phase_quota"] is None
assert len(d["request_rejections"])==9 and len(d["byte_rejections"])==12
assert all(v["emissions"]==0 and v["rejected"] for v in d["request_rejections"]+d["byte_rejections"])
assert d["typed_base64_rejections"]==7 and d["model_rejections"]==3
assert out["same_value_slot_permutation_not_detectable"] and out["copied_CPU_reference_can_match_without_GPU"]
assert all(v is True for v in d["limits"].values())
assert raw[:16]==raw[32:48] and out["execution_authenticated"] is False
assert out["request_sha256"]==digest(request)
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"synthetic_comparisons_SOURCE":4,"untrusted_bytes":128,"rejects":31,"GPU_readback_available":False,"scope":"word-match only; equal-slot swaps and fabricated CPU copy NOT execution certificates"}))
