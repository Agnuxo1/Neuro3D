"""Strict HOST word comparator for untrusted bytes. NEVER an execution certificate."""
import base64
import hashlib
import json
import struct
import zlib
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL="axial-SOURCE-buffer-readback-compare-HOST-v1"
INTENT="COMPARE_UNATTESTED_BYTES_ONLY"
ORIGIN="UNATTESTED_BYTES_NOT_GPU_EVIDENCE"
PARENT="coordinacion/respuestas/AXIAL-SOURCE-COMPILED-BUFFER-PREP-HOST-001-CODEX.json"
PARENT_SHA="cf1dd4bd4cb8d9820eda582f1ee5c369ea8774d9eabce1ba8a6f86aa5e43fcac"
INTEGER="coordinacion/respuestas/AXIAL-SOURCE-ZERO-AWARE-INTEGER-GLSL-001-CODEX.json"
def require(ok,message):
 if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def data(r):
 t=r["test_run"];require(t["rc"]==0 and not t["timed_out"],"retained suite status")
 v=t.get("stdout_zlib_base64") or "".join(t["stdout_zlib_base64_chunks"])
 raw=zlib.decompress(base64.b64decode(v,validate=True))
 require(sha(raw)==t["stdout_sha256"] and len(raw)==t["stdout_bytes"],"lossless retained suite")
 return json.loads(raw)["data"]
def load_retained():
 raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"specific HOST preparation receipt")
 r=json.loads(raw);pins={**r["code_doc_sha256"],PARENT:PARENT_SHA}
 for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"sealed dependency "+p)
 hp=data(r);plan=hp["plan"];integer=data(json.loads((ROOT/INTEGER).read_bytes()))
 require(plan["output_buffer"]["result_bytes"] is None and plan["output_buffer"]["planned_bytes"]==128,"planned output NOT GPU result")
 require(plan["GPU_job_admission"] is plan["GPU_executed"] is False,"upstream no execution")
 require(len(plan["scalar_mapping"])==8 and len(plan["general_proof_scope"])==38 and
         all(v is False for v in plan["general_proof_scope"].values()),"general STOP")
 expected=[]
 rows=integer["audit"]["sources"]
 require(len(rows)==4,"four complete retained SOURCE references")
 for source_index,row in enumerate(rows):
  for j,scalar in enumerate(row["scalars"]):
   i=2*source_index+j;m=plan["scalar_mapping"][i]
   require((m["scalar_index"],m["case_name"],m["source_id"],m["context_sha256"],m["SOURCE_row_sha256"])==
           (i,row["case_name"],row["source_id"],row["context_sha256"],row["encoder_row_sha256"]),
           "expected CPU words bound to prepared SOURCE mapping")
   words=scalar["decoded_low_high_uint32"]
   require(type(words) is list and len(words)==2 and all(type(w) is int and 0<=w<2**32 for w in words),
           "retained uint32 expected words")
   require(words[0]|(words[1]<<32)==scalar["decoded_uint64"],"retained words identity")
   expected.append(deepcopy(words))
 require(len(expected)==8,"eight complete expected scalar words")
 return {"plan":plan,"expected":expected,"pins":pins}
def selector(retained):
 return {"prepared_receipt_sha256":PARENT_SHA,"prepared_plan_sha256":digest(retained["plan"]),
         "module_sha256":retained["plan"]["module_sha256"],
         "input_buffer_sha256":retained["plan"]["input_buffer"]["sha256"],
         "expected_words_reference":"RETAINED_CPU_INTEGER_OUTPUT_NOT_GPU_EXECUTION"}
def make_request(*,model):
 require(type(model) is str and model==MODEL,"explicit comparison-only model")
 retained=load_retained()
 return {"model":MODEL,"intent":INTENT,"selector":selector(retained)}
def emit_matches(retained,raw):
 plan=retained["plan"];mapping=plan["scalar_mapping"];matched=[]
 for i in range(4):
  re,im=[struct.unpack_from("<4I",raw,16*(2*i+j))[:2] for j in (0,1)]
  m=mapping[2*i]
  matched.append({"case_name":m["case_name"],"source_id":m["source_id"],
                  "context_sha256":m["context_sha256"],"SOURCE_row_sha256":m["SOURCE_row_sha256"],
                  "observed_uint64":[re[0]|(re[1]<<32),im[0]|(im[1]<<32)],
                  "word_match_to_retained_CPU_reference":True,
                  "bytes_origin_authenticated":False,"whole_box_guard_disproved":m["whole_box_guard_disproved"]})
 return {"model":MODEL,"status":"BYTE_WORD_MATCH_NOT_EXECUTION_EVIDENCE","sources":matched,
         "bytes_sha256":sha(raw),"bytes":len(raw),"selector":selector(retained),
         "observed_bytes_base64":base64.b64encode(raw).decode(),
         "general_proof_scope":deepcopy(plan["general_proof_scope"]),"GPU_executed":False,
         "GPU_job_admission":False,"execution_authenticated":False,"scene_authenticated":False,
         "new_decoder_calls":0,"new_compiler_calls":0,"new_RN_operations":0,
         "group_admissions":0,"FIELD_evaluation":None,"phase_quota":None,
         "same_value_slot_permutation_not_detectable":True,
         "copied_CPU_reference_can_match_without_GPU":True,
         "full_costs":"UNMEASURED_NOT_ZERO","actual_GPU_readback_available":False}
def compare(request,packet,*,model):
 require(type(model) is str and model==MODEL,"explicit comparison-only model")
 require(type(request) is dict and set(request)=={"model","intent","selector"},"closed HOST comparison INPUT")
 require(request["model"]==MODEL and request["intent"]==INTENT,"no GPU/authentication alias")
 require(type(packet) is dict and set(packet)=={"origin","data_base64"},"closed untrusted byte packet")
 require(packet["origin"]==ORIGIN,"unattested origin only; cannot claim GPU provenance")
 text=packet["data_base64"]
 require(type(text) is str and len(text)==172,"exact bounded base64 for128bytes")
 retained=load_retained()
 require(digest(request["selector"])==digest(selector(retained)),"complete prepared plan/module/input/reference binding")
 raw=base64.b64decode(text,validate=True)
 require(len(raw)==128 and base64.b64encode(raw).decode()==text,"exact canonical128bytes")
 # ALL eight scalar statuses/reserved/words before any SOURCE emission.
 for i,expected in enumerate(retained["expected"]):
  low,high,valid,reserved=struct.unpack_from("<4I",raw,16*i)
  require(valid==1,"invalid status: words MUST be discarded")
  require(reserved==0,"reserved word must be zero")
  require([low,high]==expected,"bitwise CPU-reference mismatch incl signed zero")
 result=emit_matches(retained,raw)
 result["pins_verified"]=len(retained["pins"])
 result["request_sha256"]=digest(request)
 return result
