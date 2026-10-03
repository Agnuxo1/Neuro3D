"""CPU-only preparation/compilation of NEW oblique arithmetic shader candidate."""
from pathlib import Path
import base64,ctypes as C,hashlib,json,os,struct,time,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-pair64-difference-shaderc-HOST-v1"
REP="OBLIQUE_DIFFERENCE_SHADER_CANDIDATE_NO_GPU_ADMISSION"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json"
PSHA="bb67a76885010c9485415007b1f1b5e7fbe03689812216d464baf21dcf4a9dfb"
SHADER="Blender/benchmarks/capacity_audit/oblique_pair64_difference_v1.comp"
SHADER_SHA="8fcc8f6df4f4ef061c94208a43af70797c03f983532d1363f6526360bfc5766d"
DLL=Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll")
DLL_SHA="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
TAG=0x4f444631
KEYS={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","representation","shader_sha256","intent"}
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def packed(raw):return dict(bytes=len(raw),sha256=sha(raw),zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    require(len(r["code_doc_sha256"])==93,"parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    t=r["test_run"];require(t["rc"]==0 and t["timed_out"]is False,"parent_PASS")
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    require(len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail,"closed_capture")
    require(len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"],"capture_identity")
    v=json.loads(raw);require(v["status"]=="PASS" and v["tests"]==6,"specific_suite");return v["data"]
def selector(case="parent_oblique"):
    v=retained()["results"][case];rows=v["rows"]
    return dict(case=case,parent_result_sha256=digest(v),original_scene_sha256=rows[0]["original_scene_sha256"] if rows else "",
        literal_request_sha256=rows[0]["literal_request_sha256"] if rows else "",representation=REP,
        shader_sha256=SHADER_SHA,intent="CPU_PREPARE_COMPILE_ONLY")
def prepare(q,*,model):
    out=dict(model=MODEL,status="STOP",reason=None,packet=None,GPU_executed=False,GPU_launch_allowed=False,
        GPU_semantics_certified=False,physical_field_certified=False,native_promotion_allowed=False,
        new_RN_operations=0,frozen_producer_replays=0,full_costs="UNMEASURED_NOT_ZERO")
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        require(type(q)is dict and set(q)==KEYS and all(type(v)is str for v in q.values()),"closed_selector")
        require(q["representation"]==REP and q["intent"]=="CPU_PREPARE_COMPILE_ONLY","explicit_CPU_intent")
        require(q["shader_sha256"]==SHADER_SHA and sha((ROOT/SHADER).read_bytes())==SHADER_SHA,"specific_shader")
        d=retained();require(q["case"]in d["results"],"case_identity");v=d["results"][q["case"]]
        require(q["parent_result_sha256"]==digest(v),"parent_result_identity")
        require(v["status"]=="CPU_OBLIQUE_PAIR64_DIFFERENCE_ONLY" and len(v["rows"])==3,"retained_STOP_no_packet")
        require(all(s["original_scene_sha256"]==q["original_scene_sha256"] and s["literal_request_sha256"]==q["literal_request_sha256"] for s in v["rows"]),"scene_literal")
        require(v["GPU_executed"]is False and v["native_promotion_allowed"]is False,"CPU_partial_only")
        rows=v["rows"];require([s["record_id"] for s in rows]==["S0","S1","S0-minus-S1"],"ALL_sources")
        raw=b"".join(bytes.fromhex(s[k]["word_le_hex"]) for s in rows[:2] for k in ("hi","lo"))
        expected=bytes.fromhex(rows[2]["hi_word"]+rows[2]["lo_word"])
        require(len(raw)==32 and len(expected)==16,"specific_pair_extent")
        out["packet"]=dict(input_hex=(struct.pack("<4I",TAG,8,2,1)+raw).hex(),
            expected_CONTROL_ONLY_hex=(struct.pack("<4I",TAG,4,2,1)+expected).hex(),
            input_bytes=48,output_bytes=32,total_SSBO_bytes=80,expected_HOST_bytes=32,work_sources=2,work_relative_outputs=1,
            scene_sha256=q["original_scene_sha256"],literal_sha256=q["literal_request_sha256"],shader_sha256=SHADER_SHA,
            retained_CPU_budget=rows[2],source_literal_caps=[s["literal_cap_rad"] for s in rows[:2]],
            execution_status="NOT_EXECUTED",GPU_launch_allowed=False,
            runtime_requirements="NEW_EXCLUSIVE_JOB_GUARD_TELEMETRY_DEADLINE_FLOAT64_RTE_DENORM_SIGNEDZERO_BARRIERS_ATTESTATION_ALL_BUDGETS",
            commit_rule="marker only NOT PASS; authenticated completion/readback and recomputed ALL caps required")
        out["status"]="CPU_SHADER_CANDIDATE_PACKET_ONLY"
    except (ValueError,TypeError,KeyError,OSError,zlib.error) as e:out["reason"]=str(e)
    return out
def inspect_spirv(raw):
    require(len(raw)>=20 and len(raw)%4==0,"SPIRV_extent")
    w=struct.unpack("<"+"I"*(len(raw)//4),raw);require(w[0]==0x07230203 and w[4]==0,"SPIRV_header")
    i=5;caps=[];bind=[];strides=[];floats={};arith=[];decorated=set();calls=0;modes=[];entries=[];negates=0
    while i<len(w):
        n=w[i]>>16;op=w[i]&65535;require(n>0 and i+n<=len(w),"instruction_extent");a=w[i+1:i+n]
        if op==17:caps.append(a[0])
        if op==22:floats[a[0]]=a[1]
        if op in (129,131):arith.append((op,a[0],a[1]))
        if op==127:negates+=1
        if op==57:calls+=1
        if op==15:entries.append(a)
        if op==16:modes.append(a)
        if op==71:
            if a[1]==42:decorated.add(a[0])
            if a[1]==33:bind.append(a[2])
            if a[1]==6:strides.append(a[2])
        i+=n
    require(sorted(caps)==[1,10] and set(floats.values())=={64},"specific_Float64")
    require(len(arith)==8 and sum(o==129 for o,_,_ in arith)==4 and all(floats.get(t)==64 and r in decorated for _,t,r in arith),"ALL_FAdd_FSub_NoContraction64")
    require(calls==4 and negates==2,"four_TwoSum_calls_two_signs")
    require(sorted(bind)==[0,1] and strides and set(strides)=={4},"new_two_SSBO_layout")
    require(any(a[0]==5 and struct.pack("<I",a[2])==b"main" for a in entries) and any(list(a[1:])==[17,1,1,1] for a in modes),"compute_main_local_size1")
    return dict(capabilities=caps,float_widths=sorted(set(floats.values())),static_FAdd=4,static_FSub=4,
        NoContraction_arithmetic_nodes=8,TwoSum_function_calls=4,source_graph_operations_per_valid_invocation=26,
        sign_negations=negates,bindings=sorted(bind),array_strides=strides,LocalSize=[1,1,1],
        SPIRV_Tools_validated=False,GPU_executed=False,GPU_RNE_certified=False,GPU_denorm_certified=False)
def compile_source(source,*,model):
    require(type(model)is str and model==MODEL,"explicit_compile_model")
    require(type(source)is bytes and len(source)<=65536,"bounded_source")
    require(sha(DLL.read_bytes())==DLL_SHA,"existing_DLL_identity")
    directory=os.add_dll_directory(str(DLL.parent));compiler=options=result=None
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
        start=time.perf_counter();result=run(compiler,source,len(source),2,b"oblique_difference.comp",b"main",options)
        require(bool(result),"compiler_result");raw=C.string_at(contents(result),length(result)) if length(result) else b""
        out=dict(status=status(result),errors=errors(result),warnings=warnings(result),diagnostics=(msg(result)or b"").decode("utf-8","replace"),
            source=packed(source),spirv=packed(raw),target_env=0,target_version=4194304,shader_kind=2,entry_point="main",optimization=0,
            compiler_sha256=DLL_SHA,compiler_bytes=DLL.stat().st_size,compiler_version="UNKNOWN_LOCAL_HASH_IDENTITY",
            compile_call_seconds=time.perf_counter()-start,GPU_executed=False,GPU_launch_allowed=False,full_costs="UNMEASURED_NOT_ZERO")
        if out["status"]==0:
            try:out["inspection"]=inspect_spirv(raw)
            except ValueError as e:out["inspection_failure"]=str(e)
        return out
    finally:
        if result:rr(result)
        if options:orelease(options)
        if compiler:release(compiler)
        directory.close()
