"""Own bounded CPU model/compile tests for NEW first-hit scene candidate.
No imports of retained producers, GPU modules or foreign writers. No file writes.
"""
from pathlib import Path
from fractions import Fraction as F
import base64, ctypes as C, hashlib, json, math, os, struct, sys, time, traceback, zlib
ROOT=Path(__file__).resolve().parents[2]
SHADER="Blender/benchmarks/capacity_audit/oblique_scene_first_hit_v1.comp"
GI="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
GSHA="f4814286200766db8494df3f99ff7653d7cf038bd1f51cd34491206a0537016b"
READINESS="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-SHADER-ABI-READINESS-001-CODEX.json"
RSHA="f0844047f70c2f56856d4b4796c8b840e8e48dfa25231df1c46d02c8b4ada24e"
DLL=Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll")
DSHA="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
def need(ok,why):
    if not ok: raise ValueError(why)
def sha(b): return hashlib.sha256(b).hexdigest()
def packed(b):return dict(bytes=len(b),sha256=sha(b),zlib_base64=base64.b64encode(zlib.compress(b,9)).decode())
def capture(w):
    need(w["rc"]==0 and not w["timed_out"],"capture_success")
    z=zlib.decompressobj();b=z.decompress(base64.b64decode(w["stdout_zlib_base64"],validate=True),1048577)
    need(len(b)<=1048576 and z.eof and not z.unconsumed_tail and not z.unused_data,"capture_capacity")
    need(sha(b)==w["stdout_sha256"] and len(b)==w["stdout_bytes"],"capture_SHA")
    return json.loads(b)
def retained():
    g=(ROOT/GI).read_bytes();r=(ROOT/READINESS).read_bytes()
    need(sha(g)==GSHA and sha(r)==RSHA,"parent_SHA")
    rg=json.loads(g);rr=json.loads(r);a=capture(rr["audit_capture"]);pins=dict(a["code_doc_sha256"])
    pins[READINESS]=RSHA;need(len(pins)==394,"context_pins394")
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    originals={x["id"]:x["result"]["packet"]for x in capture(rg["test_run"])["evidence"]["positive"]}
    need(len(originals)==6,"six_original_cases")
    return originals,pins
def decode(raw):
    need(type(raw)is bytes and len(raw)%4==0 and 40<=len(raw)<=2668,"bounded_words")
    w=list(struct.unpack("<%dI"%(len(raw)//4),raw))
    need(w[:4]==[0x4744334e,0x31563233,1,2] and w[9]==0,"original_header")
    n=w[4];need(1<=n<=64,"triangle_count")
    count=17+9*n;need(w[5]==count and w[6]==n and len(w)==10+n+count,"counts_extent")
    ids=w[10:10+n];need(len(set(ids))==n and all(i<2**31 for i in ids),"primitive_ids")
    need(w[7]!=w[8] and w[7]in ids and w[8]in ids,"query_ids")
    b=10+n;values=[]
    for word in w[b:]:
        exp=(word>>23)&255;frac=word&0x7fffff
        need(exp!=255 and not(exp==0 and frac) and word!=0x80000000,"original_word_domain")
    for word in w[b:]:
        value=struct.unpack("<f",struct.pack("<I",word))[0]
        need(abs(value)<=1000000,"original_scalar_domain");values.append(value)
    need(values[15+9*n]>0,"lambda_positive")
    sources=[dict(id="S"+str(i),origin=tuple(values[6*i:6*i+3]),direction=tuple(values[6*i+3:6*i+6]))for i in (0,1)]
    need(all(any(v!=0 for v in s["direction"])for s in sources),"nonzero_directions")
    triangles=[dict(id=ids[i],vertices=[tuple(values[12+9*i+j:15+9*i+j])for j in (0,3,6)])for i in range(n)]
    return sources,triangles
def prepare(case,originals,raw=None):
    need(type(case)is str and case in originals,"closed_case")
    expected=bytes.fromhex(originals[case]["buffer_hex"])
    raw=expected if raw is None else raw
    need(type(raw)is bytes and sha(raw)==originals[case]["manifest"]["buffer_sha256"] and raw==expected,"same_original_INPUT")
    decode(raw)
    return dict(case=case,input=packed(raw),intent="FIRST_HIT_CANDIDATE_ONLY",GPU_launch_allowed=False,
        scene_authenticated=False,exact_contact_allowed=False,native_IEEE_RN_graph_certified=False,
        phase_error_bound=None,phase_certified=False,complete_trace_output=False,
        source_ids=["S0","S1"],scene_sha256=originals[case]["manifest"]["scene_sha256"],query_sha256=originals[case]["manifest"]["query_sha256"])
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return (a[0]*b[0]+a[1]*b[1])+a[2]*b[2]
def candidate(source,triangles):
    chosen=0xffffffff;state=2;amb=0;best=(0.0,0.0,0.0);rows=[]
    for tr in triangles:
        a,b,c=tr["vertices"];e1=sub(b,a);e2=sub(c,a);p=cross(source["direction"],e2);det=dot(e1,p)
        row=dict(primitive_id=tr["id"],kind="MISS")
        if not math.isfinite(det)or det==0:amb=3;row["kind"]="AMBIGUOUS";rows.append(row);continue
        s=sub(source["origin"],a);q=cross(s,e1)
        u=dot(s,p)/det;v=dot(source["direction"],q)/det;t=dot(e2,q)/det;uv=u+v
        if not all(math.isfinite(z)for z in (u,v,t,uv)):amb=3;row["kind"]="AMBIGUOUS";rows.append(row);continue
        if u<0 or v<0 or uv>1 or t<0:rows.append(row);continue
        row.update(kind="FLOAT64_HIT_CANDIDATE",tuv_binary64_le=[struct.pack("<d",z).hex()for z in (t,u,v)])
        rows.append(row)
        if t==0:amb=4;continue
        if u==0 or v==0 or uv==1:
            if amb==0:amb=3
            continue
        if state==1 and t==best[0]:
            if amb==0:amb=5
            continue
        if state!=1 or t<best[0]:state=1;chosen=tr["id"];best=(t,u,v)
    return dict(source_id=source["id"],status_code=amb or state,chosen_primitive_id=chosen,triangle_tests=len(triangles),
        tuv_binary64_le=[struct.pack("<d",z).hex()for z in best],rows=rows,exact_contact_allowed=False,
        native_precision_certified=False,full_path_visibility_certified=False,phase_certified=False,phase_error_bound=None)
def exact_rows(source,triangles):
    origin=tuple(F.from_float(x)for x in source["origin"]);direction=tuple(F.from_float(x)for x in source["direction"]);out=[]
    for tr in triangles:
        a,b,c=[tuple(F.from_float(x)for x in v)for v in tr["vertices"]];e1=sub(b,a);e2=sub(c,a);p=cross(direction,e2);det=dot(e1,p)
        row=dict(primitive_id=tr["id"],kind="MISS")
        if det==0:row["kind"]="EXACT_DETERMINANT_ZERO";out.append(row);continue
        s=sub(origin,a);q=cross(s,e1);u=dot(s,p)/det;v=dot(direction,q)/det;t=dot(e2,q)/det
        if u>=0 and v>=0 and u+v<=1 and t>=0:row.update(kind="EXACT_HIT",tuv=[[z.numerator,z.denominator]for z in (t,u,v)])
        out.append(row)
    return out
def encode_control(sources,triangle_count):
    """INTERNAL CPU control codec, never device readback or public admission."""
    need(type(triangle_count)is int and 1<=triangle_count<=64 and len(sources)==2,"control_shape")
    raw=struct.pack("<8I",0x4846334e,0x31563436,1,2,10,1,triangle_count,0)
    for i,s in enumerate(sources):
        need(s["source_id"]=="S"+str(i) and s["triangle_tests"]==triangle_count,"control_SOURCE")
        need(type(s["status_code"])is int and 1<=s["status_code"]<=5,"control_state")
        need(type(s["chosen_primitive_id"])is int and 0<=s["chosen_primitive_id"]<=0xffffffff,"control_primitive")
        vals=s["tuv_binary64_le"]
        need(type(vals)is list and len(vals)==3 and all(type(v)is str and len(v)==16 and bytes.fromhex(v).hex()==v for v in vals),"control_words")
        raw+=struct.pack("<4I",i,s["status_code"],s["chosen_primitive_id"],triangle_count)+b"".join(bytes.fromhex(h)for h in vals)
    inspect_control(raw)
    return dict(raw=packed(raw),origin="NEW_CPU_CALCULATION_CONTROL_NOT_GPU_READBACK",GPU_used=False,GPU_launch_allowed=False,phase_error_bound=None)
def inspect_control(raw):
    need(type(raw)is bytes and len(raw)==112,"control_output_extent")
    w=list(struct.unpack("<28I",raw))
    need(w[:6]==[0x4846334e,0x31563436,1,2,10,1] and 1<=w[6]<=64 and w[7]==0,"UNCERTIFIED_control_header")
    records=[]
    for sid in (0,1):
        b=8+10*sid;need(w[b]==sid and 1<=w[b+1]<=5 and w[b+3]==w[6],"control_record")
        need(w[b+2]<2**31 or w[b+2]==0xffffffff,"control_primitive_word")
        for j in (4,6,8):
            bits=w[b+j]|(w[b+j+1]<<32)
            need((bits>>52)&2047!=2047,"nonfinite_control_output")
        records.append(dict(source_id="S"+str(sid),status_code=w[b+1],chosen_primitive_id=w[b+2],triangle_tests=w[b+3],
            tuv_binary64_le=[raw[4*(b+j):4*(b+j+2)].hex()for j in (4,6,8)]))
    return dict(records=records,scope="HOST_CODEC_ONLY",GPU_used=False,exact_contact_allowed=False,native_precision_certified=False,phase_certified=False,phase_error_bound=None)
def contrast(candidate_rows,exact):
    out=[]
    for c,e in zip(candidate_rows,exact):
        need(c["primitive_id"]==e["primitive_id"],"ALL_triangle_order")
        match=c["kind"]=="FLOAT64_HIT_CANDIDATE" and e["kind"]=="EXACT_HIT"
        if match:
            errors=[F.from_float(struct.unpack("<d",bytes.fromhex(h))[0])-F(*q)for h,q in zip(c["tuv_binary64_le"],e["tuv"])]
            out.append(dict(primitive_id=c["primitive_id"],kind_match=True,signed_errors=[[z.numerator,z.denominator]for z in errors],zero_error=all(z==0 for z in errors)))
        else:out.append(dict(primitive_id=c["primitive_id"],kind_match=(c["kind"]=="MISS"and e["kind"]=="MISS")or(c["kind"]=="AMBIGUOUS"and e["kind"]=="EXACT_DETERMINANT_ZERO"),zero_error=None))
    return out
def compile_new(source):
    need(type(source)is bytes and len(source)<=65536,"source_capacity")
    original=(ROOT/SHADER).read_bytes()
    need(source in (original,original+b"\nINVALID_FIRST_HIT_TOKEN\n"),"only_NEW_source_or_negative")
    need(sha(DLL.read_bytes())==DSHA,"existing_DLL_seal")
    directory=os.add_dll_directory(str(DLL.parent));compiler=options=result=None
    try:
        lib=C.CDLL(str(DLL))
        def api(name,ret,args):
            f=getattr(lib,name);f.restype=ret;f.argtypes=args;return f
        P=C.c_void_p;Z=C.c_size_t;I=C.c_int
        init=api("shaderc_compiler_initialize",P,[]);release=api("shaderc_compiler_release",None,[P])
        oi=api("shaderc_compile_options_initialize",P,[]);orelease=api("shaderc_compile_options_release",None,[P])
        target=api("shaderc_compile_options_set_target_env",None,[P,I,C.c_uint])
        opt=api("shaderc_compile_options_set_optimization_level",None,[P,I])
        run=api("shaderc_compile_into_spv",P,[P,C.c_char_p,Z,I,C.c_char_p,C.c_char_p,P])
        rr=api("shaderc_result_release",None,[P]);status=api("shaderc_result_get_compilation_status",I,[P])
        errors=api("shaderc_result_get_num_errors",Z,[P]);warnings=api("shaderc_result_get_num_warnings",Z,[P])
        length=api("shaderc_result_get_length",Z,[P]);contents=api("shaderc_result_get_bytes",P,[P])
        msg=api("shaderc_result_get_error_message",C.c_char_p,[P])
        compiler=init();options=oi();need(bool(compiler)and bool(options),"compiler_allocation")
        target(options,0,4194304);opt(options,0);start=time.perf_counter()
        result=run(compiler,source,len(source),2,b"oblique_scene_first_hit_v1.comp",b"main",options)
        need(bool(result),"compiler_result")
        raw=C.string_at(contents(result),length(result))if length(result)else b""
        return dict(status=status(result),errors=errors(result),warnings=warnings(result),diagnostics=(msg(result)or b"").decode("utf-8","replace"),
            source=packed(source),spirv=packed(raw),compiler_sha256=DSHA,compiler_bytes=DLL.stat().st_size,compiler_version="UNKNOWN_HASH_IDENTITY",
            target_env=0,target_version=4194304,shader_kind=2,optimization=0,entry_point="main",compile_QA_seconds=time.perf_counter()-start,GPU_used=False)
    finally:
        if result:rr(result)
        if options:orelease(options)
        if compiler:release(compiler)
        directory.close()
def mutate_words(raw,index,value):
    w=list(struct.unpack("<%dI"%(len(raw)//4),raw));w[index]=value
    return struct.pack("<%dI"%len(w),*w)
def rejection(raw):
    try:decode(raw);return None
    except(ValueError,struct.error)as ex:return str(ex)
def run_suite(report):
    originals,pins=retained();report["context_pins"]=pins
    report["original_cases"]=[]
    failures=[]
    for case,packet in originals.items():
        prep=prepare(case,originals);raw=bytes.fromhex(packet["buffer_hex"]);sources,triangles=decode(raw);cs=[]
        for s in sources:
            c=candidate(s,triangles);e=exact_rows(s,triangles);comparison=contrast(c["rows"],e)
            for z in comparison:
                if not z["kind_match"]or z.get("zero_error")is False:failures.append(dict(case=case,source_id=s["id"],comparison=z))
            cs.append(dict(candidate=c,exact_rows=e,contrast=comparison))
        report["original_cases"].append(dict(case=case,prepared=prep,sources=cs,triangle_count=len(triangles),CPU_control_output=encode_control([x["candidate"]for x in cs],len(triangles))))
    report["retained_precision_failures"]=failures
    report["precision_result"]="STOP_NONEXACT_OR_CLASSIFICATION"if failures else"CPU_ZERO_ERROR_CONTROL_ONLY_NOT_NATIVE"
    raw=bytes.fromhex(originals["oblique"]["buffer_hex"]);n=2;base=12
    negatives=[("short",raw[:-4]),("extra",raw+b"\0\0\0\0")]
    for label,index,value in (("magic",0,0),("version",2,2),("sources",3,1),("triangles_zero",4,0),("triangles65",4,65),
        ("scalars",5,0),("id_count",6,1),("same_query_ids",7,0),("absent_root",7,1234),("reserved",9,1),
        ("duplicate_id",11,struct.unpack_from("<I",raw,40)[0]),("id_sign",10,2**31),("nan",base,0x7fc00001),("inf",base,0x7f800000),
        ("subnormal",base,1),("negative_zero",base,0x80000000),("over_domain",base,0x4b000000),("zero_lambda",base+33,0)):
        negatives.append((label,mutate_words(raw,index,value)))
    w=list(struct.unpack("<47I",raw))
    for j in (3,4,5):w[base+j]=0
    negatives.append(("zero_direction",struct.pack("<47I",*w)))
    report["input_negatives"]=[dict(id=k,reason=rejection(b),status="STOP_INPUT")for k,b in negatives]
    need(all(x["reason"]for x in report["input_negatives"]),"ALL_negative_rejected")
    report["public_negatives"]=[]
    for name,case,payload in (("bool_case",True,None),("wrong_scene","unknown",None),("other_valid_scene","oblique",bytes.fromhex(originals["shared_ref1000"]["buffer_hex"]))):
        try:prepare(case,originals,payload);raise AssertionError("negative_public_accept")
        except ValueError as ex:report["public_negatives"].append(dict(id=name,reason=str(ex)))
    sources,tris=decode(raw)
    s=dict(sources[0]);s["origin"]=tris[0]["vertices"][0]
    contact=candidate(s,tris);need(contact["status_code"]==4,"zero_contact_STOP")
    parallel=[dict(t)for t in tris];parallel[1]=dict(tris[1],vertices=[tris[1]["vertices"][0]]*3)
    unresolved=candidate(sources[0],parallel);need(unresolved["status_code"]==3,"degenerate_unresolved")
    duplicate=[dict(tris[0],vertices=tris[1]["vertices"]),tris[1]]
    tie=candidate(sources[0],duplicate);need(tie["status_code"]==5,"equal_tie_STOP")
    report["synthetic_stage_controls"]=dict(zero_contact=contact,degenerate=unresolved,equal_tie=tie,origin="FABRICATED_CPU_STAGE_DATA_NOT_ORIGINAL_SCENE_OR_GPU")
    source=(ROOT/SHADER).read_bytes();report["valid_compile"]=compile_new(source)
    report["negative_compile"]=compile_new(source+b"\nINVALID_FIRST_HIT_TOKEN\n")
    v=report["valid_compile"];bad=report["negative_compile"]
    need(v["status"]==0 and v["errors"]==0 and v["spirv"]["bytes"]>20,"new_compile_success")
    need(bad["status"]!=0 and bad["errors"]>0 and bad["spirv"]["bytes"]==0,"syntaxnegative_preserved")
    b=zlib.decompress(base64.b64decode(v["spirv"]["zlib_base64"]));w=list(struct.unpack("<%dI"%(len(b)//4),b));need(w[0]==0x07230203 and w[1]==0x10000,"SPIRV_header")
    ins=[];i=5
    while i<len(w):
        count=w[i]>>16;need(count>0 and i+count<=len(w),"instruction_extent");ins.append((w[i]&65535,w[i+1:i+count]));i+=count
    need(any(op==17 and a==[10]for op,a in ins),"Float64_capability")
    need(any(op==22 and a[1]==64 for op,a in ins),"Float64_type")
    report["spirv_structure"]=dict(instructions=len(ins),float64_capability=True,float64_type=True,SPIRV_Tools_validated=False,control_flow_runtime_certified=False)
    report["summary"]=dict(original_cases=6,original_sources=12,negative_INPUT=len(negatives),negative_public=3,synthetic_stage_controls=3,
        compiler_calls=2,retained_precision_failures=len(failures),context_pins=len(pins),GPU_used=False,old_numeric_producer_replays=0,
        exact_contact_allowed=False,native_IEEE_RN_graph_certified=False,phase_certified=False,phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO",
        output="NEW_N3FH64V1_CANDIDATE_NOT_N3OH32V1_NOT_HILO",FIRST_HIT_ONLY_NOT_WHOLE_TRACE=True)
    report["status"]="PASS_TESTS_CANDIDATE_ONLY_PRECISION_STOP"
if __name__=="__main__":
    report=dict(status="IN_PROGRESS",GPU_used=False,GPU_launch_allowed=False,JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    try:run_suite(report)
    except Exception as ex:
        report.update(status="FAIL_RETAINED",error=str(ex),traceback=traceback.format_exc())
        print(json.dumps(report,allow_nan=False));sys.exit(1)
    print(json.dumps(report,allow_nan=False))
