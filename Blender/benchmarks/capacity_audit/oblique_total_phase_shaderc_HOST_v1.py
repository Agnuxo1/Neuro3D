"""Opt-in TOTAL phase shader CPU compiler/topology/prefix diagnostics. No GPU."""
from pathlib import Path
import base64,ctypes as C,hashlib,json,os,struct,time,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-total-phase-shaderc-HOST-v1"
SHADER="Blender/benchmarks/capacity_audit/oblique_total_phase_v1.comp"
SHADER_SHA="52d54317644b51293df075e4e1df1b328a7dbf83937b9144638b5b9c95b0ab6f"
DLL=Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll")
DLL_SHA="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001-CODEX.json"
PSHA="acc107cb584dba1d7845584ac1040569fa3a2dd4be7d2f9c39d702d2ce06b6c3"
SEAL="coordinacion/respuestas/PRECISION-VISIBILITY-LEDGER-COVERAGE-HOST-001-CODEX.json"
SSHA="dda978eced1bf958c61325e3d29f013b713ad5524ed9f39bc474d9ab9028f45f"
TAG=0x54504731
EXP_MASK=0x7ff0000000000000
FRAC_MASK=(1<<52)-1
ABS_MASK=(1<<63)-1
POLICIES=("BIT_PRESERVE_DIAGNOSTIC","UNSPECIFIED_TO_POSITIVE_ZERO")
NAMES=("P0.hi","P0.lo","P1.hi","P1.lo","gamma0.hi","gamma0.lo","gamma1.hi","gamma1.lo","mu.hi","mu.lo")
def require(x,why):
    if not x:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def packed(raw):return dict(bytes=len(raw),sha256=sha(raw),zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
def unpack_capture(t):
    d=zlib.decompressobj();raw=d.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),2097153)
    require(len(raw)<=2097152 and d.eof and not d.unused_data and not d.unconsumed_tail,"capture_extent")
    require(t["rc"]==0 and t["timed_out"]is False and len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"],"capture_integrity")
    return json.loads(raw)["data"]
def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PSHA,"native_receipt_identity");r=json.loads(raw)
    seal=(ROOT/SEAL).read_bytes();require(sha(seal)==SSHA,"latest_parent_seal")
    pins=json.loads(seal)["code_doc_sha256"]
    for p,h in pins.items():require(sha(Path(p).read_bytes() if Path(p).is_absolute() else (ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    data=unpack_capture(r["test_run"])
    require(len(data["runs"])==46,"closed_native_census")
    return data,pins
def selector(case,data):
    entry=data["registry"][case]
    return dict(case=case,native_receipt_sha256=PSHA,phase_request_sha256=digest(entry["request"]),
        original_scene_sha256=entry["request"]["original_scene_sha256"],
        literal_request_sha256=entry["request"]["literal_request_sha256"],
        shader_sha256=SHADER_SHA,intent="HOST_UNATTESTED_ENCODED_TOTAL_PHASE_ONLY")
def validate_input(raw):
    require(type(raw)is bytes and len(raw)==96,"input_extent")
    w=struct.unpack("<24I",raw);require(w[:4]==(TAG,10,2,1),"new_TAG_input_header")
    for i in range(10):
        bits=w[4+2*i]|(w[5+2*i]<<32)
        require(bits&EXP_MASK!=EXP_MASK,"raw_nonfinite_"+NAMES[i])
        require(bits&ABS_MASK<=0x4270000000000000,"input_domain_"+NAMES[i])
    return w
def _prepare(model,request,data):
    out=dict(status="STOP",reason=None,input=None,expected_output=None,GPU_launch_allowed=False,
        scene_authenticated=False,material_authenticated=False,device_egress_authenticated=False,
        native_promotion_allowed=False,physical_field_certified=False,full_costs="UNMEASURED_NOT_ZERO")
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        require(type(request)is dict and type(request.get("case"))is str and request["case"]in data["registry"],"closed_case")
        case=request["case"];require(request==selector(case,data),"closed_selector_identity")
        run=next(x for x in data["runs"]if x["id"]==case);result=run["result"]
        require(result["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY","parent_STOP:"+str(result["reason"]))
        require(len(result["rows"])==3 and all(x["fits"]is True for x in result["rows"]),"ALL_SOURCE_relative_caps")
        fixture=data["registry"][case]["fixture"]
        words=[r[part]["word_le_hex"] for r in fixture["rows"][:2]for part in ("hi","lo")]
        enc=result["encodings"];require([e["name"]for e in enc]==["gamma0","gamma1","mu"],"source_material_order")
        words += [e[part]for e in enc for part in ("hi","lo")]
        raw=struct.pack("<4I",TAG,10,2,1)+b"".join(bytes.fromhex(h)for h in words)
        validate_input(raw)
        expected=struct.pack("<4I",TAG,6,2,1)+b"".join(bytes.fromhex(r[part])for r in result["rows"]for part in ("hi","lo"))
        require(len(expected)==64,"expected_extent")
        out.update(status="HOST_PREPARED_UNATTESTED",input=packed(raw),expected_output=packed(expected),words=words,
            phase_request_sha256=request["phase_request_sha256"],expected_is_retagged_CPU_CONTROL_NOT_DEVICE=True)
    except (ValueError,KeyError,StopIteration,TypeError)as e:out["reason"]=str(e)
    return out
def prepare(model,request):
    data,_=retained()
    return _prepare(model,request,data)
def expected_edges():
    e=[]
    def add(op,a,b):e.append((op,a,b));return ("node",len(e)-1)
    def two(a,b):
        s=add("+",a,b);bb=add("-",s,a);ab=add("-",s,bb)
        db=add("-",b,bb);da=add("-",a,ab);return s,add("+",da,db)
    def plus(a,b):
        h=two(a[0],b[0]);l=two(a[1],b[1]);m=two(h[0],add("+",h[1],l[0]))
        return two(m[0],add("+",m[1],l[1]))
    src=lambda name:tuple(("source",name+"."+part)for part in ("hi","lo"))
    t0=plus(plus(src("P0"),src("gamma0")),src("mu"))
    t1=plus(plus(src("P1"),src("gamma1")),src("mu"))
    plus(t0,tuple(("neg",x)for x in t1))
    return e
def instructions(raw):
    require(type(raw)is bytes and 20<=len(raw)<=65536 and len(raw)%4==0,"binary_extent")
    w=struct.unpack("<%dI"%(len(raw)//4),raw)
    require(w[0]==0x07230203 and w[1]==0x10000 and w[4]==0 and 0<w[3]<4096,"binary_header")
    out=[];i=5
    while i<len(w):
        count=w[i]>>16
        require(count>0 and i+count<=len(w),"instruction_extent")
        out.append((i,w[i]&65535,tuple(w[i+1:i+count])));i+=count
    return out

def extract_graph(raw):
    """Only unoptimized compiler-lowered arithmetic slice. Guards are NOT evaluated."""
    ins=instructions(raw);floats={};ints={};vectors={};const={};bind={};nc=set();ext={};funcs={};current=None;main=None
    for pos,op,a in ins:
        if op==15: require(main is None,"one_entry");main=a[1]
        elif op==11:ext[a[0]]=struct.pack("<%dI"%(len(a)-1),*a[1:]).split(b"\0")[0].decode()
        elif op==22:floats[a[0]]=a[1]
        elif op==21:ints[a[0]]=a[1:]
        elif op==23:vectors[a[0]]=a[1:]
        elif op==43 and a[0]in ints:const[a[1]]=a[2]
        elif op==71 and a[1]==33:bind[a[0]]=a[2]
        elif op==71 and a[1]==42:nc.add(a[0])
        elif op==54:
            require(current is None,"nested_function");current=a[1]
            require(current not in funcs,"unique_function");funcs[current]=[]
        elif op==56:
            require(current is not None and len(a)==0,"function_end");current=None
        elif current is not None:funcs[current].append((pos,op,a))
    require(current is None and ins[-1][1]==56,"unclosed_function")
    require(main in funcs and len(funcs)==3 and sorted(bind.values())==[0,1],"closed_entry_bindings")
    nodes=[];outputs={};calls=[];packs=[]
    def run(fid,args=(),ctx=()):
        require(len(ctx)<=2,"no_recursive_calls")
        values={k:("int",v) for k,v in const.items()};ptr={};mem={};params=[]
        for k,v in bind.items():ptr[k]=("buffer",v,())
        def value(k):require(k in values,"unresolved_value:"+str(k));return values[k]
        def read(k):
            require(k in ptr,"unresolved_pointer")
            kind,base,idx=ptr[k]
            if kind=="buffer":
                require(base==0 and len(idx)==2 and idx[0]==0 and 0<=idx[1]<24,"source_pointer")
                return ("word",idx[1])
            require(base in mem,"uninitialized_local")
            v=mem[base]
            for j in idx:require(v[0]=="vector" and 0<=j<len(v[1]),"vector_index");v=v[1][j]
            return v
        def write(k,v):
            require(k in ptr,"store_pointer");kind,base,idx=ptr[k]
            if kind=="buffer":
                require(base==1 and len(idx)==2 and idx[0]==0,"output_pointer")
                outputs[idx[1]]=v
            else:require(not idx,"whole_local_store");mem[base]=v
        for pos,op,a in funcs[fid]:
            if op==55:
                j=len(params);require(j<len(args),"parameter_count");params.append(a[1]);ptr[a[1]]=("local",a[1],());mem[a[1]]=args[j]
            elif op==59:ptr[a[1]]=("local",a[1],())
            elif op==65:
                if a[2]not in ptr:continue # builtin/guard-only pointer, not an arithmetic operand
                indices=[]
                for k in a[3:]:
                    require(value(k)[0]=="int","constant_index");indices.append(value(k)[1])
                kind,base,idx=ptr[a[2]];ptr[a[1]]=(kind,base,idx+tuple(indices))
            elif op==61:
                if a[2]in ptr:values[a[1]]=read(a[2])
            elif op==62:
                if a[0]in ptr:write(a[0],value(a[1]))
            elif op==80:values[a[1]]=("vector",tuple(value(k) for k in a[2:]))
            elif op==12 and a[3]in (59,65):
                require(ext.get(a[2])=="GLSL.std.450" and len(a)==5,"pack_instruction")
                v=value(a[4])
                if a[3]==59:
                    require(floats.get(a[0])==64 and v[0]=="vector" and len(v[1])==2,"pack_type")
                    pair=tuple(x[1] if x[0]=="word" else -1 for x in v[1])
                    names={(4+2*i,5+2*i):name for i,name in enumerate(NAMES)}
                    require(pair in names,"SOURCE_word_order");values[a[1]]=("source",names[pair]);packs.append(names[pair])
                else:
                    require(v[0]=="node" and a[0]in vectors and ints.get(vectors[a[0]][0])==(32,0) and vectors[a[0]][1]==2,"unpack_type")
                    values[a[1]]=("vector",(("limb",v,0),("limb",v,1)))
            elif op==127:
                require(floats.get(a[0])==64 and a[1]in nc,"negate_float64_precise")
                v=value(a[2]);require(v[0]in ("source","node"),"total_negation");values[a[1]]=("neg",v)
            elif op in (129,131):
                require(floats.get(a[0])==64 and a[1]in nc,"arithmetic_float64_precise")
                left,right=value(a[2]),value(a[3])
                require(left[0]in ("source","neg","node") and right[0]in ("source","neg","node"),"arithmetic_operands")
                nodes.append(dict(op="+" if op==129 else "-",a=left,b=right,result_id=a[1],word_offset=pos,call_context=ctx,float_width=64,NoContraction=True))
                values[a[1]]=("node",len(nodes)-1)
            elif op==57:
                require(len(a)==5 and a[2]!=main,"closed_helper_call");calls.append(a[1])
                values[a[1]]=run(a[2],tuple(read(k) for k in a[3:]),ctx+(a[1],))
            elif op==254:
                require(fid!=main and len(params)==2,"helper_return");return value(a[0])
            # Other opcodes, early returns and labels are guard-only/metadata in this pinned binary.
            # No branch feasibility, runtime memory layout or SPIR-V validity is certified.
        require(fid==main,"missing_helper_return")
    run(main)
    require(packs==list(NAMES) and len(calls)==25,"source_call_order")
    edges=[(n["op"],n["a"],n["b"]) for n in nodes]
    require(edges==expected_edges(),"130node_topology")
    expected={4+2*i+j:("limb",("node",n),j) for i,n in enumerate((46,51,98,103,124,129)) for j in (0,1)}
    require({k:v for k,v in outputs.items() if k>=4}==expected,"egress_order")
    return dict(nodes=nodes,source_order=packs,helper_calls=calls,egress={str(k):v for k,v in expected.items()},control_flow_certified=False,GPU_RNE_certified=False)
def decode(raw):
    require(type(raw)is bytes and 20<=len(raw)<=65536 and len(raw)%4==0,"binary_extent")
    w=struct.unpack("<%dI"%(len(raw)//4),raw)
    require(w[0]==0x07230203 and w[1]==0x10000 and w[4]==0,"binary_header")
    ins=[];i=5
    while i<len(w):
        count=w[i]>>16;require(count>0 and i+count<=len(w),"instruction_extent")
        ins.append((i,w[i]&65535,w[i+1:i+count]));i+=count
    values={};bind={};builtin={};ext={};funcs={};active=None;main=None
    for pos,op,a in ins:
        if op==15:require(main is None and a[0]==5,"one_compute_entry");main=a[1]
        elif op==11:ext[a[0]]=struct.pack("<%dI"%(len(a)-1),*a[1:]).split(b"\0")[0].decode()
        elif op==43:values[a[1]]=("f64",a[2]|(a[3]<<32)) if len(a)==4 else a[2]
        elif op==44:values[a[1]]=tuple(values[x] for x in a[2:])
        elif op==71 and a[1]==33:bind[a[0]]=a[2]
        elif op==71 and a[1]==11:builtin[a[0]]=a[2]
        elif op==54:
            require(active is None and a[1]not in funcs,"function_start");active=a[1];funcs[active]=[]
        elif op==56:require(active is not None,"function_end");active=None
        elif active is not None:funcs[active].append((pos,op,a))
    require(active is None and ins[-1][1]==56 and main in funcs and sorted(bind.values())==[0,1],"closed_structure")
    blocks={};label=None
    for item in funcs[main]:
        pos,op,a=item
        if op==248:label=a[0];require(label not in blocks,"unique_label");blocks[label]=[]
        else:require(label is not None,"instruction_before_label");blocks[label].append(item)
    for block in blocks.values():
        require(block and block[-1][1]in(249,250,253),"block_terminator")
        for pos,op,a in block:
            if op==249:require(a[0]in blocks,"branch_target")
            if op==250:require(len(a)==3 and a[1]in blocks and a[2]in blocks,"conditional_targets")
            if op==247:require(a[0]in blocks,"merge_target")
    return values,bind,builtin,ext,blocks
def simulate_prefix(raw,q):
    """Diagnostic scenarios only. IEEE bit behavior is an explicit model assumption."""
    require(type(q)is dict and set(q)=={"input_words","output_extent","gid","pack_policy"},"closed_scenario")
    words=q["input_words"];require(type(words)is list and len(words)<=64 and all(type(x)is int and 0<=x<2**32 for x in words),"uint32_words")
    require(type(q["output_extent"])is int and 0<=q["output_extent"]<=64,"output_extent")
    require(type(q["gid"])is list and len(q["gid"])==3 and all(type(x)is int and 0<=x<2**32 for x in q["gid"]),"gid")
    require(q["pack_policy"]in POLICIES,"explicit_pack_policy")
    v,bind,builtin,ext,blocks=decode(raw)
    pointers={k:("buffer",b,()) for k,b in bind.items()}
    pointers.update({k:("builtin",b,()) for k,b in builtin.items()})
    mem={};reads=[];writes=[];packs=[];raw_checks=[];branches=[];labels=[];previous=None;current=next(iter(blocks))
    def value(k):require(k in v,"unresolved_value");return v[k]
    def fp(k):
        x=value(k);require(type(x)is tuple and len(x)==2 and x[0]=="f64","f64_value");return x[1]
    def read(k):
        require(k in pointers,"load_pointer");kind,base,idx=pointers[k]
        if kind=="builtin":require(base==28 and not idx,"global_ID");return tuple(q["gid"])
        if kind=="buffer":
            require(base==0 and len(idx)==2 and idx[0]==0 and 0<=idx[1]<len(words),"input_read_extent");reads.append(idx[1]);return words[idx[1]]
        require(base in mem and not idx,"local_load");return mem[base]
    def write(k,x):
        require(k in pointers,"store_pointer");kind,base,idx=pointers[k]
        if kind=="buffer":
            require(base==1 and len(idx)==2 and idx[0]==0 and 0<=idx[1]<q["output_extent"] and type(x)is int,"output_write_extent");writes.append([idx[1],x])
        else:require(kind=="local" and not idx,"local_store");mem[base]=x
    for step in range(256):
        require(current not in labels,"cycle_not_supported");labels.append(current);target=None
        for pos,op,a in blocks[current]:
            if op==59:pointers[a[1]]=("local",a[1],())
            elif op==61:v[a[1]]=read(a[2])
            elif op==62:write(a[0],value(a[1]))
            elif op==65:
                require(a[2]in pointers,"access_pointer");kind,base,idx=pointers[a[2]]
                ii=tuple(value(k) for k in a[3:]);require(all(type(x)is int for x in ii),"access_indices");pointers[a[1]]=(kind,base,idx+ii)
            elif op==68:
                require(a[2]in bind and a[3]==0,"array_length");v[a[1]]=len(words) if bind[a[2]]==0 else q["output_extent"]
            elif op==124:require(type(value(a[2]))is int,"integer_bitcast");v[a[1]]=value(a[2])
            elif op in(170,171):
                x,y=value(a[2]),value(a[3])
                require(op==171 or (type(x)is int and type(y)is int),"integer_equal")
                v[a[1]]=x==y if op==170 else (tuple(u!=t for u,t in zip(x,y)) if type(x)is tuple else x!=y)
            elif op==199:
                x,y=value(a[2]),value(a[3]);require(type(x)is int and type(y)is int,"uint_AND")
                v[a[1]]=x&y;raw_checks.append(dict(word_offset=pos,raw_high_word=x,mask=y,result=x&y))
            elif op==154:require(type(value(a[2]))is tuple,"any_vector");v[a[1]]=any(value(a[2]))
            elif op==168:require(type(value(a[2]))is bool,"logical_not");v[a[1]]=not value(a[2])
            elif op==80:v[a[1]]=tuple(value(k) for k in a[2:])
            elif op==12:
                require(ext.get(a[2])=="GLSL.std.450" and a[3]in(4,59),"prefix_ext")
                if a[3]==59:
                    x=value(a[4]);require(type(x)is tuple and len(x)==2 and all(type(k)is int for k in x),"pack_words")
                    bits=x[0]|(x[1]<<32);nonfinite=(bits&EXP_MASK)==EXP_MASK
                    result=0 if nonfinite and q["pack_policy"]=="UNSPECIFIED_TO_POSITIVE_ZERO" else bits
                    packs.append(dict(result_id=a[1],original_bits_le=bits.to_bytes(8,"little").hex(),modeled_bits_le=result.to_bytes(8,"little").hex(),raw_nonfinite=nonfinite,unspecified_choice_used=nonfinite and result==0))
                    v[a[1]]=("f64",result)
                else:v[a[1]]=("f64",fp(a[4])&ABS_MASK)
            elif op in(156,157):
                bits=fp(a[2]);isnf=(bits&EXP_MASK)==EXP_MASK;v[a[1]]=isnf and (bool(bits&FRAC_MASK) if op==156 else not bits&FRAC_MASK)
            elif op==186:
                x,y=fp(a[2]),fp(a[3]);require(not(x>>63) and not(y>>63),"positive_order_only")
                nan=lambda b:(b&EXP_MASK)==EXP_MASK and bool(b&FRAC_MASK)
                v[a[1]]=not nan(x) and not nan(y) and x>y
            elif op==245:
                choices=[a[j] for j in range(2,len(a),2) if a[j+1]==previous];require(len(choices)==1,"phi_predecessor");v[a[1]]=value(choices[0])
            elif op==247:pass
            elif op==249:target=a[0]
            elif op==250:
                condition=value(a[0]);require(type(condition)is bool,"branch_bool");target=a[1] if condition else a[2]
                branches.append(dict(word_offset=pos,label=current,condition_id=a[0],condition=condition,target=target))
            elif op==127:v[a[1]]=("f64",fp(a[2])^(1<<63)) # sign flip only, not RN
            elif op in(57,253):
                return dict(status="HOST_PREFIX_REACHED_ARITHMETIC" if op==57 else "HOST_PREFIX_RETURNED",terminal_word_offset=pos,terminal_label=current,labels=labels,branches=branches,input_reads=reads,output_writes=writes,packs=packs,raw_exponent_checks=raw_checks,pack_policy=q["pack_policy"],GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,new_RN_operations=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")
            else:raise ValueError("unsupported_prefix_opcode:"+str(op))
        require(target is not None,"no_terminator");previous,current=current,target
    raise ValueError("step_budget")

def compile_source(source,*,model):
    require(type(model)is str and model==MODEL,"explicit_compile_model")
    require(type(source)is bytes and len(source)<=65536,"bounded_source")
    base=(ROOT/SHADER).read_bytes();require(sha(base)==SHADER_SHA,"new_shader_identity")
    require(source in (base,base+b"\nINVALID_TOTAL_PHASE_TOKEN\n"),"only_new_source_or_negative")
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
        start=time.perf_counter();result=run(compiler,source,len(source),2,b"oblique_total_phase_v1.comp",b"main",options)
        require(bool(result),"compiler_result");raw=C.string_at(contents(result),length(result)) if length(result) else b""
        out=dict(status=status(result),errors=errors(result),warnings=warnings(result),diagnostics=(msg(result)or b"").decode("utf-8","replace"),
            source=packed(source),spirv=packed(raw),target_env=0,target_version=4194304,shader_kind=2,entry_point="main",optimization=0,
            compiler_sha256=DLL_SHA,compiler_bytes=DLL.stat().st_size,compiler_version="UNKNOWN_LOCAL_HASH_IDENTITY",
            compile_call_seconds=time.perf_counter()-start,GPU_executed=False,GPU_launch_allowed=False,full_costs="UNMEASURED_NOT_ZERO")
        if out["status"]==0:
            try:out["inspection"]=dict(graph=extract_graph(raw),GPU_guard_certified=False)
            except ValueError as e:out["inspection_failure"]=str(e)
        return out
    finally:
        if result:rr(result)
        if options:orelease(options)
        if compiler:release(compiler)
        directory.close()


def compare_trace(graph,prepared,result):
    trace=result["trace"];require(len(trace)==130,"native_130_trace")
    source=dict(zip(NAMES,prepared["words"]))
    def bits(ref):
        tag,x=ref
        if tag=="source":return source[x]
        if tag=="node":return trace[x]["y"]
        require(tag=="neg","trace_reference")
        return (int.from_bytes(bytes.fromhex(bits(x)),"little")^(1<<63)).to_bytes(8,"little").hex()
    for node,t in zip(graph["nodes"],trace):
        require((node["op"],bits(node["a"]),bits(node["b"]))==(t["op"],t["a"],t["b"]),"retained_trace_edge")
    require([r[p] for r in result["rows"]for p in ("hi","lo")]==[trace[i]["y"] for i in (46,51,98,103,124,129)],"retained_output_nodes")
    return dict(matched_edges=130,new_RN_operations=0,device_RNE_certified=False)
def run_suite():
    data,pins=retained();base=(ROOT/SHADER).read_bytes()
    valid=compile_source(base,model=MODEL)
    negative=compile_source(base+b"\nINVALID_TOTAL_PHASE_TOKEN\n",model=MODEL)
    report=dict(valid_compile=valid,negative_compile=negative,preparations=[],traces={},prefix=[],new_RN_operations=0,
        producer_replays=0,compiler_calls=2,GPU_executed=False,GPU_launch_allowed=False,JEV="LOCAL_FALLBACK_SECURITY_BLOCKED_NO_RETRY")
    if valid["status"]!=0 or "inspection_failure"in valid:
        report["status"]="STOP_COMPILER_OR_GRAPH";return report
    graph=valid["inspection"]["graph"]
    for run in data["runs"]:
        if run["id"]in data["registry"]:
            q=_prepare(MODEL,selector(run["id"],data),data)
        else:
            require(run["result"]["status"]=="STOP","native_negative_selector_preserved")
            q=dict(status="STOP",reason="sealed_native_negative_selector:"+str(run["result"]["reason"]),input=None,
                expected_output=None,GPU_launch_allowed=False,native_promotion_allowed=False)
        report["preparations"].append(dict(id=run["id"],result=q))
        if q["status"]=="HOST_PREPARED_UNATTESTED":report["traces"][run["id"]]=compare_trace(graph,q,run["result"])
    require(len(report["traces"])==11,"eleven_admitted_native")
    raw=zlib.decompress(base64.b64decode(report["preparations"][0]["result"]["input"]["zlib_base64"]))
    words=list(validate_input(raw));spv=zlib.decompress(base64.b64decode(valid["spirv"]["zlib_base64"]))
    cases=[("valid",words,16,[0,0,0])]
    for i in range(10):
        for label,bits in (("positive_inf",0x7ff0000000000000),("negative_inf",0xfff0000000000000),("qnan",0x7ff8000000000001)):
            w=words.copy();w[4+2*i]=bits&0xffffffff;w[5+2*i]=bits>>32
            cases.append((NAMES[i]+":"+label,w,16,[0,0,0]))
    for i in range(4):
        w=words.copy();w[i]^=1;cases.append(("bad_header_"+str(i),w,16,[0,0,0]))
    cases += [("short_input",words[:-1],16,[0,0,0]),("short_output",words,15,[0,0,0]),("other_gid",words,16,[1,0,0])]
    w=words.copy();w[5]=0x42800000;cases.append(("over_domain",w,16,[0,0,0]))
    for name,w,extent,gid in cases:
        for policy in POLICIES:
            result=simulate_prefix(spv,dict(input_words=w,output_extent=extent,gid=gid,pack_policy=policy))
            report["prefix"].append(dict(id=name,scenario=dict(input_words=w,output_extent=extent,gid=gid,pack_policy=policy),result=result))
            if name=="valid":require(result["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" and len(result["packs"])==10,"valid_prefix")
            else:require(result["status"]=="HOST_PREFIX_RETURNED","negative_prefix_return")
            if ":"in name:require(result["packs"]==[],"raw_nonfinite_before_ANY_pack")
    require(negative["status"]!=0 and negative["errors"]>0 and negative["spirv"]["bytes"]==0,"invalid_compile_retained")
    report["status"]="HOST_COMPILE_TOPOLOGY_PREFIX_ONLY"
    return report
