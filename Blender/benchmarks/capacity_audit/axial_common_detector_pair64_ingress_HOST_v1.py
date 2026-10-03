"""Opt-in CPU preparation/mirror and CPU compilation. Never creates a GPU device."""
from copy import deepcopy
from pathlib import Path
import base64, ctypes as C, hashlib, json, os, struct, time, zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-common-detector-pair64-ingress-shaderc-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-WIRE-HOST-001-CODEX.json"
PARENT_SHA="406d8d75fc9b9e4c0c18ab49c650642cf308d554477014cf0b52f0da46c82a0a"
SHADER="Blender/benchmarks/capacity_audit/axial_common_detector_pair64_ingress_v1.comp"
SHADER_SHA="f895fd0b33ad75bd779f929ad28680402386d43fec39bb6d8cb0bd18aca793b4"
DLL=Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll")
DLL_SHA="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
TAG=0x50363431
KEYS={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","intent"}
def require(ok, why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def packed(raw):return {"bytes":len(raw),"sha256":sha(raw),"zlib_base64":base64.b64encode(zlib.compress(raw)).decode()}
def read_capture(run):
    require(run["rc"]==0 and run["timed_out"]is False,"retained_PASS")
    stream=zlib.decompressobj();raw=stream.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    require(len(raw)<=1024*1024 and stream.eof and not stream.unused_data and not stream.unconsumed_tail,"closed_parent_payload")
    require(len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"],"parent_stdout_identity")
    value=json.loads(raw);require(value["status"]=="PASS" and value["tests"]==8,"parent_suite_identity")
    return value["data"]
def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"parent_receipt_identity")
    r=json.loads(raw);require(len(r["code_doc_sha256"])==67,"parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"parent_dependency")
    return read_capture(r["test_run"])
def selector(case="exact"):
    d=retained();result=d["pack_results"][case];q=d["pack_selectors"][case]
    return {"case":case,"parent_result_sha256":digest(result),"original_scene_sha256":q["original_scene_sha256"],
            "literal_request_sha256":q["literal_request_sha256"],"intent":"CPU_PREPARE_MIRROR_COMPILE_ONLY"}
def prepare(q,*,model):
    out={"status":"STOP","reason":None,"packet":None,"GPU_executed":False,"phase_RN_executed":0,
         "producer_replays":0,"native_promotion_allowed":False,"full_costs":"UNMEASURED_NOT_ZERO"}
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        require(type(q)is dict and set(q)==KEYS and all(type(v)is str for v in q.values()),"closed_typed_request")
        require(q["intent"]=="CPU_PREPARE_MIRROR_COMPILE_ONLY","explicit_intent")
        d=retained();require(q["case"]in d["pack_results"],"case_identity")
        result=d["pack_results"][q["case"]];old=d["pack_selectors"][q["case"]]
        require(q["parent_result_sha256"]==digest(result),"result_binding")
        require(q["original_scene_sha256"]==old["original_scene_sha256"]
                and q["literal_request_sha256"]==old["literal_request_sha256"],"scene_literal_binding")
        require(result["status"]=="HOST_PAIR64_WIRE_PACK_ONLY" and result["HOST_contract_certified"]is True,"retained_STOP_no_packet")
        e=result["envelope"];raw=bytes.fromhex(e["payload_hex"])
        require(e["abi"]=="HOST_LE_U32_PAIR64_PHASE_V1_NOT_GPU_ABI" and len(raw)==48
                and sha(raw)==e["payload_sha256"] and e["record_ids"]==["S0","S1","S0-minus-S1"]
                and (e["record_count"],e["record_stride_bytes"])==(3,16),"specific_wire_ABI")
        require(result["transport_error_cycles"]==[0,1] and all(result[k]is False for k in
               ("GPU_executed","native_promotion_allowed","physical_scene_authenticated",
                "native_hit_coverage_certified","length_reference_phase_bound_certified","mirror_material_certified",
                "full_field_certified","coherent_field_admission_allowed","interference_phase_certified")),"partial_HOST_only")
        source=(ROOT/SHADER).read_bytes()
        require(sha(source)==SHADER_SHA,"specific_new_shader_identity")
        out["packet"]={"input_hex":(struct.pack("<4I",TAG,1,3,16)+raw).hex(),"expected_hex":raw.hex(),
                       "input_bytes":64,"expected_bytes":48,"output_bytes":64,"total_SSBO_bytes":176,
                       "shader_sha256":sha(source),"parent_envelope_sha256":digest(e),
                       "parent_result_sha256":q["parent_result_sha256"],"original_scene_sha256":q["original_scene_sha256"],
                       "literal_request_sha256":q["literal_request_sha256"],
                       "commit_rule":"status==[0x50363431,3,0xffffffff,1] AFTER job completion/readback barrier"}
        out["status"]="CPU_PAIR64_INGRESS_PACKET_ONLY"
    except (ValueError,TypeError,KeyError,OSError,zlib.error) as e:out["reason"]=str(e)
    return out
def mirror(input_raw,expected_raw,*,global_id=(0,0,0)):
    # CPU integer model ONLY. No assertion about GPU execution ordering/hardware atomicity.
    require(type(global_id)is tuple and len(global_id)==3 and all(type(x)is int and 0<=x<2**32 for x in global_id),"typed_global_id")
    require(type(input_raw)is bytes and len(input_raw)==64 and type(expected_raw)is bytes and len(expected_raw)==48,"exact_buffer_extents")
    if global_id!=(0,0,0):return {"status":"CPU_NO_WRITE","output_hex":None,"record_comparisons":0}
    a=list(struct.unpack("<16I",input_raw));b=list(struct.unpack("<12I",expected_raw));out=[0,0,0xffffffff,0]+[0]*12
    if a[:4]!=[TAG,1,3,16]:
        out[2]=0xfffffff0
        return {"status":"CPU_STOP_UNCOMMITTED","output_hex":struct.pack("<16I",*out).hex(),"record_comparisons":0}
    checked=0
    for i in range(3):
        row=a[4+4*i:8+4*i];target=b[4*i:4*i+4];checked+=1
        if any(((row[j]>>20)&0x7ff)==0x7ff for j in (1,3)) or row!=target:
            out[2]=i
            return {"status":"CPU_STOP_UNCOMMITTED","output_hex":struct.pack("<16I",*out).hex(),"record_comparisons":checked}
    out=[TAG,3,0xffffffff,1]+a[4:]
    return {"status":"CPU_COPY_COMMITTED_ONLY","output_hex":struct.pack("<16I",*out).hex(),"record_comparisons":checked}
def inspect_spirv(data):
    require(len(data)>=20 and len(data)%4==0,"SPIRV_extent")
    words=struct.unpack("<"+"I"*(len(data)//4),data);require(words[0]==0x07230203 and words[4]==0,"SPIRV_header")
    ops=[];caps=[];entries=[];modes=[];binding=[];strides=[];types=[];i=5
    while i<len(words):
        n=words[i]>>16;op=words[i]&65535;require(n>0 and i+n<=len(words),"SPIRV_instruction_extent")
        operands=list(words[i+1:i+n]);ops.append(op)
        if op==17:caps.append(operands[0])
        if op==15:entries.append(operands)
        if op==16:modes.append(operands)
        if op==21:types.append(operands[1:])
        if op==71 and len(operands)==3 and operands[1]==33:binding.append(operands[2])
        if op==71 and len(operands)==3 and operands[1]==6:strides.append(operands[2])
        i+=n
    require(22 not in ops and all(t[0]==32 for t in types),"no_float_or_64bit_types")
    require(caps==[1] and sorted(binding)==[0,1,2] and strides and set(strides)=={16},"specific_integer_SSBO_layout")
    require(any(e[0]==5 and struct.pack("<I",e[2])==b"main" for e in entries)
            and any(m[1:]==[17,1,1,1] for m in modes),"compute_main_local_size1")
    return {"instructions":len(ops),"OpTypeFloat_count":0,"capabilities":caps,"bindings":sorted(binding),
            "array_strides":strides,"LocalSize":[1,1,1],"SPIRV_Tools_validated":False,"GPU_executed":False,
            "GPU_semantics_certified":False}
def compile_source(source,*,model):
    require(type(model)is str and model==MODEL,"explicit_compile_model")
    require(type(source)is bytes and len(source)<=65536,"bounded_source")
    require(sha(DLL.read_bytes())==DLL_SHA,"existing_DLL_identity")
    directory=os.add_dll_directory(str(DLL.parent))
    compiler=options=result=None
    try:
        lib=C.CDLL(str(DLL))
        def api(name,ret,args):
            f=getattr(lib,name);f.restype=ret;f.argtypes=args;return f
        P=C.c_void_p;Z=C.c_size_t;I=C.c_int
        init=api("shaderc_compiler_initialize",P,[]);release=api("shaderc_compiler_release",None,[P])
        oi=api("shaderc_compile_options_initialize",P,[]);orelease=api("shaderc_compile_options_release",None,[P])
        target=api("shaderc_compile_options_set_target_env",None,[P,I,C.c_uint])
        optimization=api("shaderc_compile_options_set_optimization_level",None,[P,I])
        run=api("shaderc_compile_into_spv",P,[P,C.c_char_p,Z,I,C.c_char_p,C.c_char_p,P])
        rr=api("shaderc_result_release",None,[P]);status=api("shaderc_result_get_compilation_status",I,[P])
        errors=api("shaderc_result_get_num_errors",Z,[P]);warnings=api("shaderc_result_get_num_warnings",Z,[P])
        length=api("shaderc_result_get_length",Z,[P]);contents=api("shaderc_result_get_bytes",P,[P])
        msg=api("shaderc_result_get_error_message",C.c_char_p,[P])
        compiler=init();options=oi();require(bool(compiler) and bool(options),"compiler_options_allocation")
        target(options,0,4194304);optimization(options,0)
        start=time.perf_counter()
        result=run(compiler,source,len(source),2,b"pair64_ingress.comp",b"main",options);require(bool(result),"compiler_result")
        raw=C.string_at(contents(result),length(result)) if length(result) else b""
        out={"status":status(result),"errors":errors(result),"warnings":warnings(result),
             "diagnostics":(msg(result)or b"").decode("utf-8","replace"),"source":packed(source),"spirv":packed(raw),
             "target_env":0,"target_version":4194304,"shader_kind":2,"entry_point":"main","optimization":0,
             "compiler_sha256":DLL_SHA,"compiler_bytes":DLL.stat().st_size,
             "compiler_version":"UNKNOWN_LOCAL_HASH_IDENTITY","compile_call_seconds":time.perf_counter()-start,
             "GPU_executed":False,"full_costs":"UNMEASURED_NOT_ZERO"}
        if out["status"]==0:out["structural_inspection"]=inspect_spirv(raw)
        return out
    finally:
        if result:rr(result)
        if options:orelease(options)
        if compiler:release(compiler)
        directory.close()
