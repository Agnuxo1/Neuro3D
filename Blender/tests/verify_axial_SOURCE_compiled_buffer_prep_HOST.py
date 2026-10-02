"""Independent retained receipt verifier; no production/compiler/decoder imports."""
import base64,hashlib,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"coordinacion/respuestas/AXIAL-SOURCE-COMPILED-BUFFER-PREP-HOST-001-CODEX.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
r=json.loads(P.read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
t=r["test_run"];assert t["rc"]==0 and not t["timed_out"] and t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True));assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
a=json.loads(raw);assert a["status"]=="PASS" and a["tests"]==4
d=a["data"];plan=d["plan"];request=d["request"];snapshot=request["upstream_CPU_snapshot"]
payload=b""
for i,(row,frame) in enumerate(zip(snapshot["decoder_INPUT"]["SOURCE_limb_records"],snapshot["frames"])):
 rawframe=base64.b64decode(frame["frame_base64"],validate=True)
 assert len(rawframe)==120 and rawframe[:8]==b"N3DZAD01"
 assert rawframe[8:40].hex()=="9f22f2c7709360b61a1d0765cf9776af47a2306efd8c1c61bfbd09a12077ef03"
 assert rawframe[40:72].hex()==row["context_sha256"] and rawframe[72:104].hex()==canonical(row)
 assert list(struct.unpack("<4I",rawframe[104:]))==row["limb_uint32"]
 payload+=rawframe[104:]
 for j,label in enumerate(("real","imag")):
  m=plan["scalar_mapping"][2*i+j]
  assert m["scalar_index"]==2*i+j and m["component"]==label
  assert (m["case_name"],m["source_id"],m["context_sha256"])==(row["case_name"],row["source_id"],row["context_sha256"])
  assert m["input_byte_offset"]==8*(2*i+j) and m["output_byte_offset"]==16*(2*i+j)
  assert m["ORIGINAL_uint64"]==row["scalars"][j]["original_uint64"]
  assert m["upstream_CPU_frame_sha256"]==sha(rawframe)
assert len(payload)==64 and base64.b64decode(plan["input_buffer"]["base64"],validate=True)==payload and plan["input_buffer"]["sha256"]==sha(payload)
assert plan["output_buffer"]["planned_bytes"]==128 and plan["output_buffer"]["result_bytes"] is None
assert plan["dispatch_plan_unexecuted"]==[8,1,1] and plan["module_bytes"]==15188
assert plan["compiled_selection"]==request["compiled_selection"]
selector=plan["compiled_selection"]
assert selector["compile_receipt_sha256"]==sha((ROOT/"coordinacion/respuestas/AXIAL-SOURCE-INTEGER-SHADERC-COMPILE-001-CODEX.json").read_bytes())
assert selector["SOURCE_header_sha256"]==sha((ROOT/"Blender/benchmarks/capacity_audit/axial_SOURCE_zero_aware_integer_v1.glsl").read_bytes())
assert selector["signed512_sha256"]==sha((ROOT/"Blender/benchmarks/capacity_audit/axial_native_signed512_v1.glsl").read_bytes())
assert selector["wrapper_sha256"]==sha((ROOT/"Blender/benchmarks/capacity_audit/axial_SOURCE_integer_compile_probe_v1.comp").read_bytes())
assert (selector["target_env"],selector["target_version"],selector["entry_point"],selector["shader_kind"])==(0,4194304,"main",2)
assert plan["compiled_selection"]["SOURCE_header_sha256"]!=rawframe[8:40].hex()
assert plan["request_sha256"]==canonical(request)
assert len(d["atomic_rejections"])==13 and all(x["rejected"] and x["emissions"]==0 for x in d["atomic_rejections"])
assert len(d["frame_rejections"])==13 and d["dispatch_rejections"]==9 and d["module_rejections"]==3 and d["model_rejections"]==4
assert len(plan["general_proof_scope"])==38 and all(v is False for v in plan["general_proof_scope"].values())
assert plan["GPU_job_admission"] is plan["GPU_executed"] is plan["scene_authentication"] is False
assert plan["runtime_runner_integrated"] is plan["numerical_GPU_semantics_proved"] is False
assert plan["new_decoder_calls"]==plan["new_compiler_calls"]==plan["group_admissions"]==0
assert plan["GROUP_field_evaluation"] is plan["phase_quota"] is None
assert sum(m["whole_box_guard_disproved"] is True for m in plan["scalar_mapping"])==4
assert sum(m["whole_box_guard_disproved"] is None for m in plan["scalar_mapping"])==4
# Independent parse of actual compiled descriptor decorations, without helper reflection.
sc=json.loads((ROOT/"coordinacion/respuestas/AXIAL-SOURCE-INTEGER-SHADERC-COMPILE-001-CODEX.json").read_bytes())
st=sc["test_run"];cv=json.loads(zlib.decompress(base64.b64decode(st["stdout_zlib_base64"])))
packed=cv["compilations"][0]["spirv"];module=zlib.decompress(base64.b64decode(packed["zlib_base64"]))
assert sha(module)==plan["module_sha256"]==packed["sha256"]
words=struct.unpack("<"+"I"*(len(module)//4),module);pos=5;types={};dec={};offs={};variables=[]
while pos<len(words):
 n,op=divmod(words[pos],65536);assert n>0 and pos+n<=len(words);ins=words[pos+1:pos+n]
 if op in (21,23,29,30,32):types[ins[0]]=(op,ins[1:])
 if op==71:dec.setdefault(ins[0],{})[ins[1]]=ins[2:]
 if op==72 and ins[2]==35:offs[(ins[0],ins[1])]=ins[3:]
 if op==59:variables.append(ins[:3])
 pos+=n
reflected=[]
for pointer,var,storage in variables:
 if 33 not in dec.get(var,{}):continue
 binding=dec[var][33][0];assert dec[var][34]==(0,)
 op,p=types[pointer];assert op==32 and p[0]==storage
 op,members=types[p[1]];assert op==30 and len(members)==1 and offs[(p[1],0)]==(0,)
 array=members[0];op,elem=types[array];assert op==29
 op,vec=types[elem[0]];assert op==23
 op,i=types[vec[0]];assert op==21 and i==(32,0)
 reflected.append({"set":0,"binding":binding,"stride_bytes":dec[array][6][0],"components_uint32":vec[1],"member_offset":0})
assert sorted(reflected,key=lambda v:v["binding"])==plan["compiled_layout"]
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"SOURCEs":4,"scalar_slots":8,"input_bytes":64,"planned_output_bytes":128,"new_decoder_compiler_calls":0,"GPU_executed":False,"scope":"HOST preparation and actual retained binary ABI only"}))
