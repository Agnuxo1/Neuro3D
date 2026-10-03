"""Independent receipt/packet/mirror/SPIRV oracle: no codec/compiler/producer imports."""
from pathlib import Path
import base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-INGRESS-SHADERC-001-CODEX.json"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-WIRE-HOST-001-CODEX.json"
PARENT_SHA="406d8d75fc9b9e4c0c18ab49c650642cf308d554477014cf0b52f0da46c82a0a"
SHADER="Blender/benchmarks/capacity_audit/axial_common_detector_pair64_ingress_v1.comp"
SHADER_SHA="f895fd0b33ad75bd779f929ad28680402386d43fec39bb6d8cb0bd18aca793b4"
DLL="D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll"
DLL_SHA="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
MODEL="precision-axial-common-detector-pair64-ingress-shaderc-HOST-v1"
TAG=0x50363431
KEYS={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","intent"}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def check(ok,label):
    if not ok:raise AssertionError(label)
def unpack64(run,tests):
    check(run["rc"]==0 and run["timed_out"]is False and run["threads"]==1
          and run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60,"bounded child")
    stream=zlib.decompressobj();raw=stream.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    check(len(raw)<=1024*1024 and stream.eof and not stream.unused_data and not stream.unconsumed_tail,"closed stdout")
    check(sha(raw)==run["stdout_sha256"] and len(raw)==run["stdout_bytes"],"stdout identity")
    v=json.loads(raw);check(v["status"]=="PASS" and v["tests"]==tests,"suite verdict");return v["data"]
def packed(value):
    stream=zlib.decompressobj();raw=stream.decompress(base64.b64decode(value["zlib_base64"],validate=True),1024*1024+1)
    check(len(raw)<=1024*1024 and stream.eof and not stream.unused_data and not stream.unconsumed_tail,"closed binary")
    check(len(raw)==value["bytes"] and sha(raw)==value["sha256"],"binary identity");return raw
def pinned(r,n):
    check(len(r["code_doc_sha256"])==n,"pin count")
    for p,h in r["code_doc_sha256"].items():check(sha((ROOT/p).read_bytes())==h,"pin "+p)
def u32(raw):return [int.from_bytes(raw[i:i+4],"little") for i in range(0,len(raw),4)]
def bytes32(words):return b"".join(w.to_bytes(4,"little") for w in words)
def expected_selector(parent,name):
    q=parent["pack_selectors"][name];out=parent["pack_results"][name]
    return {"case":name,"parent_result_sha256":digest(out),"original_scene_sha256":q["original_scene_sha256"],
            "literal_request_sha256":q["literal_request_sha256"],"intent":"CPU_PREPARE_MIRROR_COMPILE_ONLY"}
def selected(q,model,parent):
    if type(model)is not str or model!=MODEL or type(q)is not dict or set(q)!=KEYS        or not all(type(v)is str for v in q.values()) or q["intent"]!="CPU_PREPARE_MIRROR_COMPILE_ONLY":return None
    if q["case"]not in parent["pack_results"]:return None
    want=expected_selector(parent,q["case"])
    if q!=want:return None
    out=parent["pack_results"][q["case"]]
    if out["status"]!="HOST_PAIR64_WIRE_PACK_ONLY":return None
    check(out["HOST_contract_certified"]is True and out["transport_error_cycles"]==[0,1],"parent wire")
    return out["envelope"]
def reference_packet(q,e):
    raw=bytes.fromhex(e["payload_hex"]);check(len(raw)==48 and sha(raw)==e["payload_sha256"],"retained48bytes")
    return {"input_hex":(bytes32([TAG,1,3,16])+raw).hex(),"expected_hex":raw.hex(),"input_bytes":64,
            "expected_bytes":48,"output_bytes":64,"total_SSBO_bytes":176,"shader_sha256":SHADER_SHA,
            "parent_envelope_sha256":digest(e),"parent_result_sha256":q["parent_result_sha256"],
            "original_scene_sha256":q["original_scene_sha256"],"literal_request_sha256":q["literal_request_sha256"],
            "commit_rule":"status==[0x50363431,3,0xffffffff,1] AFTER job completion/readback barrier"}
def reference_mirror(v):
    a=bytes.fromhex(v["input_hex"]);b=bytes.fromhex(v["expected_hex"]);gid=v["global_id"]
    check(len(a)==64 and len(b)==48 and len(gid)==3,"mirror extents")
    if gid!=[0,0,0]:return {"status":"CPU_NO_WRITE","output_hex":None,"record_comparisons":0}
    words=u32(a);expect=u32(b);out=[0,0,0xffffffff,0]+[0]*12
    if words[:4]!=[TAG,1,3,16]:
        out[2]=0xfffffff0;return {"status":"CPU_STOP_UNCOMMITTED","output_hex":bytes32(out).hex(),"record_comparisons":0}
    for i in range(3):
        row=words[4+4*i:8+4*i];correct=expect[4*i:4*i+4]
        if any(((row[k]>>20)&0x7ff)==0x7ff for k in (1,3)) or row!=correct:
            out[2]=i;return {"status":"CPU_STOP_UNCOMMITTED","output_hex":bytes32(out).hex(),"record_comparisons":i+1}
    return {"status":"CPU_COPY_COMMITTED_ONLY","output_hex":bytes32([TAG,3,0xffffffff,1]+words[4:]).hex(),"record_comparisons":3}
def reflect(raw):
    check(len(raw)>=20 and len(raw)%4==0,"SPIRV extent");words=u32(raw)
    check(words[0]==0x07230203 and words[4]==0,"SPIRV header")
    i=5;ops=[];caps=[];bind={};strides={};offset={};variables={};pointers={};structs={};entries=[];modes=[];types=[]
    while i<len(words):
        count=words[i]>>16;op=words[i]&65535;check(count>0 and i+count<=len(words),"SPIRV instruction")
        args=words[i+1:i+count];ops.append(op)
        if op==17:caps.append(args[0])
        if op==15:entries.append(args)
        if op==16:modes.append(args)
        if op==21:types.append(args[1:])
        if op==59:variables[args[1]]=args[0]
        if op==32:pointers[args[0]]=args[2]
        if op==30:structs[args[0]]=args[1:]
        if op==71 and len(args)==3:
            if args[1]==33:bind[args[0]]=args[2]
            if args[1]==6:strides[args[0]]=args[2]
        if op==72 and len(args)==4 and args[2]==35:offset[(args[0],args[1])]=args[3]
        i+=count
    check(22 not in ops and types and all(t[0]==32 for t in types) and caps==[1],"integer32 Shader only")
    check(sorted(bind.values())==[0,1,2] and strides and set(strides.values())=={16},"bindings and stride")
    check(any(e[0]==5 and bytes32([e[2]])==b"main" for e in entries)
          and any(m[1:]==[17,1,1,1] for m in modes),"entrypoint localSize")
    member_offsets={}
    for variable,binding in bind.items():
        sid=pointers[variables[variable]];member_offsets[binding]=[offset[(sid,k)] for k in range(len(structs[sid]))]
    check(member_offsets=={0:[0,16],1:[0],2:[0,16]},"SSBO header/payload offsets")
    return {"instructions":len(ops),"bindings":[0,1,2],"array_strides":sorted(strides.values()),
            "member_offsets":member_offsets,"capabilities":caps,"OpTypeFloat_count":0}
def main():
    receipt=json.loads((ROOT/RECEIPT).read_bytes());pinned(receipt,73)
    raw=(ROOT/PARENT).read_bytes();check(sha(raw)==PARENT_SHA,"parent receipt")
    pr=json.loads(raw);pinned(pr,67);parent=unpack64(pr["test_run"],8)
    initial=unpack64(receipt["retained_initial_passing_capture"],7)
    data=unpack64(receipt["test_run"],7)
    check("model_inputs"not in initial and set(data["model_inputs"])==set(data["requests"])==set(data["prepares"]),"complete model inputs")
    check(receipt["telemetry_failure"]["status"]=="ACCESS_DENIED" and receipt["telemetry_failure"]["RAM_free"]=="UNKNOWN"
          and receipt["telemetry_failure"]["GPU_preflight_performed"]is False,"telemetry not bypassed")
    check(sha((ROOT/SHADER).read_bytes())==SHADER_SHA and sha(Path(DLL).read_bytes())==DLL_SHA,"new shader/compiler identities")
    check(receipt["proof_scope"]["GPU_executed"]is False and all(v is False for v in receipt["proof_scope"].values()),"no promotion scope")
    accept=stopped=0
    for name,out in data["prepares"].items():
        q=data["requests"][name];e=selected(q,data["model_inputs"][name],parent)
        check(out["GPU_executed"]is False and out["native_promotion_allowed"]is False
              and out["phase_RN_executed"]==out["producer_replays"]==0
              and out["full_costs"]=="UNMEASURED_NOT_ZERO","prepare scope")
        if e is None:
            check(out["status"]=="STOP" and out["packet"]is None and type(out["reason"])is str and out["reason"],"STOP no packet");stopped+=1
        else:
            check(out["status"]=="CPU_PAIR64_INGRESS_PACKET_ONLY" and out["packet"]==reference_packet(q,e)
                  and out["reason"]is None,"scene bound packet");accept+=1
    check(set(parent["pack_results"]).issubset(data["prepares"]) and accept==11,"ALLparents")
    successful=failed=no_write=0
    check(set(data["mirrors"])==set(data["mirror_inputs"]),"ALL mirror inputs")
    for name,value in data["mirrors"].items():
        want=reference_mirror(data["mirror_inputs"][name]);check(value==want,"mirror "+name)
        if want["status"]=="CPU_COPY_COMMITTED_ONLY":successful+=1
        elif want["status"]=="CPU_STOP_UNCOMMITTED":failed+=1
        else:no_write+=1
    reflections={}
    for name,row in data["compiles"].items():
        source=packed(row["source"]);binary=packed(row["spirv"])
        check(row["GPU_executed"]is False and row["compiler_sha256"]==DLL_SHA and row["compiler_bytes"]==4478464
              and (row["target_env"],row["target_version"],row["shader_kind"],row["entry_point"],row["optimization"])==(0,4194304,2,"main",0),"compile selection")
        if name=="vulkan1_0_positive":
            check(source==(ROOT/SHADER).read_bytes() and row["status"]==row["errors"]==row["warnings"]==0,"positive compilation")
            reflections[name]=reflect(binary)
            check(row["structural_inspection"]["GPU_semantics_certified"]is False
                  and row["structural_inspection"]["SPIRV_Tools_validated"]is False,"structural only")
        else:
            check(name=="syntax_negative" and source==(ROOT/SHADER).read_bytes()+b"\nINVALID_PAIR64_TOKEN\n"
                  and row["status"]!=0 and row["errors"]>0 and row["diagnostics"] and len(binary)==0,"retained syntax failure")
    check(set(data["compiles"])=={"vulkan1_0_positive","syntax_negative"},"two new compiles per capture")
    check(data["controls"]=={"extent_rejects":3,"changed_shader_rejected_before_packet":True,"before_DLL_load_rejects":2,
                            "SPIRV_corruption_rejects":4,"retained_parent_raw_identity":PARENT_SHA},"controls")
    check(data["mirrors"]["limb_4"]["output_hex"][32:]==bytes(48).hex()
          and data["mirrors"]["limb_8"]["output_hex"][32:]==bytes(48).hex(),"secondSOURCE/relative atomic model")
    print(json.dumps({"status":"PASS","pins":73,"prepares_admitted":accept,"prepares_STOP":stopped,
                      "mirrors_admitted":successful,"mirrors_STOP":failed,"mirrors_NO_WRITE":no_write,
                      "per_capture_compiles":2,"total_new_compile_calls":4,"SPIRV_reflection":reflections,
                      "GPU_executed":False,"GPU_semantics_certified":False,"phase_RN_executed":0,
                      "producer_replays":0,"RAM_free":"UNKNOWN_ACCESS_DENIED"},sort_keys=True))
if __name__=="__main__":main()
