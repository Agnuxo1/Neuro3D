"""New opt-in raw exponent V2 shader candidate; CPU compile/model only."""
from pathlib import Path
import base64,ctypes as C,hashlib,json,os,struct,time,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-pair64-raw-guard-shaderc-HOST-v1"
REP="OBLIQUE_RAW_GUARD_V2_CANDIDATE_NOT_GPU_ADMISSION"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-SPIRV-GUARD-HOST-001-CODEX.json"
PSHA="b4eacc9e5b7a3746669b7e834ec0888d32587025bb9e86e51e5d5cf8e8e141ed"
SHADER="Blender/benchmarks/capacity_audit/oblique_pair64_raw_guard_v2.comp"
SHADER_SHA="277a94ba2d223a2e2d06052037c6ef549b04270748a3678501ecd2da4446b70f"
DLL=Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll")
DLL_SHA="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
TAG=0x4f444632
EXP_MASK=0x7ff0000000000000
FRAC_MASK=(1<<52)-1
ABS_MASK=(1<<63)-1
POLICIES=("BIT_PRESERVE_DIAGNOSTIC","UNSPECIFIED_TO_POSITIVE_ZERO")
KEYS={"case","parent_packet_sha256","original_scene_sha256","literal_request_sha256","representation","shader_sha256","intent"}
GOOD=("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60")
def require(x,why):
    if not x:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def packed(raw):return dict(bytes=len(raw),sha256=sha(raw),zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
def captured(t):
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1048577)
    require(len(raw)<=1048576 and z.eof and not z.unused_data and not z.unconsumed_tail,"capture_extent")
    require(len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"] and t["rc"]==0 and t["timed_out"]is False,"capture_identity")
    return json.loads(raw)["data"]
def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    require(len(r["code_doc_sha256"])==110 and r["status"]=="HOST_AUDIT_COMPLETE_RAW_NONFINITE_GUARD_UNPROVEN" and r["promotion"]=="STOP","parent_NOT_PROMOTED")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"pin:"+p)
    guard=captured(r["test_run"])["result"]
    require(len(guard["counterexamples"])==12 and len(guard["scenarios"])==65 and guard["GPU_guard_certified"]is False,"parent_counterexamples_retained")
    shader=captured(json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001-CODEX.json").read_bytes())["test_run"])
    native=captured(json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json").read_bytes())["test_run"])
    return guard,shader,native
def selector(case="parent_oblique"):
    g,s,n=retained();p=s["results"][case]["packet"]
    return dict(case=case,parent_packet_sha256=digest(p),original_scene_sha256=p["scene_sha256"],literal_request_sha256=p["literal_sha256"],representation=REP,shader_sha256=SHADER_SHA,intent="CPU_PREPARE_RAW_GUARD_V2_ONLY")
def validate_raw_packet(raw):
    require(type(raw)is bytes and len(raw)==48,"V2_packet_extent")
    w=struct.unpack("<12I",raw);require(w[:4]==(TAG,8,2,1),"explicit_V2_header")
    for k in range(4,12,2):
        bits=w[k]|(w[k+1]<<32)
        require((bits&EXP_MASK)!=EXP_MASK,"raw_nonfinite_SOURCE_"+str(k))
        require((bits&ABS_MASK)<=0x4270000000000000,"unchanged_source_domain")
    return dict(status="HOST_RAW_FINITE_DOMAIN_ONLY",SOURCE_components=4,GPU_guard_certified=False,scene_authenticated=False)
def prepare(q,*,model):
    out=dict(model=MODEL,status="STOP",reason=None,packet=None,GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,native_promotion_allowed=False,physical_field_certified=False,new_RN_operations=0,frozen_producer_replays=0,full_costs="UNMEASURED_NOT_ZERO")
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        require(type(q)is dict and set(q)==KEYS and all(type(v)is str for v in q.values()),"closed_selector")
        require(q["representation"]==REP and q["intent"]=="CPU_PREPARE_RAW_GUARD_V2_ONLY","explicit_CPU_V2_intent")
        require(q["shader_sha256"]==SHADER_SHA and sha((ROOT/SHADER).read_bytes())==SHADER_SHA,"new_shader_identity")
        g,s,n=retained();require(q["case"]in GOOD,"four_retained_finite_cases")
        parent=s["results"][q["case"]]["packet"]
        require(digest(parent)==q["parent_packet_sha256"] and parent["scene_sha256"]==q["original_scene_sha256"] and parent["literal_sha256"]==q["literal_request_sha256"],"same_scene_literal_packet")
        source=bytes.fromhex(parent["input_hex"]);expect=bytes.fromhex(parent["expected_CONTROL_ONLY_hex"])
        raw=struct.pack("<I",TAG)+source[4:];control=struct.pack("<I",TAG)+expect[4:]
        validate_raw_packet(raw)
        out["packet"]=dict(parent,input_hex=raw.hex(),expected_CONTROL_ONLY_hex=control.hex(),shader_sha256=SHADER_SHA,ABI_tag=TAG,ABI_revision="V2_RAW_EXPONENT_BEFORE_PACK",execution_status="NOT_EXECUTED",GPU_launch_allowed=False,raw_guard_scope="finite SOURCE exponents only, BEFORE packing; finite2^40 bound unchanged",parent_packet_sha256=digest(parent))
        out["status"]="CPU_RAW_GUARD_V2_PACKET_ONLY"
    except (ValueError,TypeError,KeyError,OSError,zlib.error) as e:out["reason"]=str(e)
    return out
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
def expected_edges():
    e=[]
    def add(op,a,b): e.append((op,a,b));return ("node",len(e)-1)
    def two(a,b):
        s=add("+",a,b);bb=add("-",s,a);ab=add("-",s,bb)
        db=add("-",b,bb);da=add("-",a,ab);return s,add("+",da,db)
    h=two(("source","S0.hi"),("neg",("source","S1.hi")))
    l=two(("source","S0.lo"),("neg",("source","S1.lo")))
    m=two(h[0],add("+",h[1],l[0]))
    two(m[0],add("+",m[1],l[1]))
    return e
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
    require(main in funcs and len(funcs)==2 and sorted(bind.values())==[0,1],"closed_entry_bindings")
    nodes=[];outputs={};calls=[];packs=[]
    def run(fid,args=(),ctx=()):
        require(len(ctx)<=1,"no_recursive_calls")
        values={k:("int",v) for k,v in const.items()};ptr={};mem={};params=[]
        for k,v in bind.items():ptr[k]=("buffer",v,())
        def value(k):require(k in values,"unresolved_value:"+str(k));return values[k]
        def read(k):
            require(k in ptr,"unresolved_pointer")
            kind,base,idx=ptr[k]
            if kind=="buffer":
                require(base==0 and len(idx)==2 and idx[0]==0 and 0<=idx[1]<12,"source_pointer")
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
                    names={(4,5):"S0.hi",(6,7):"S0.lo",(8,9):"S1.hi",(10,11):"S1.lo"}
                    require(pair in names,"SOURCE_word_order");values[a[1]]=("source",names[pair]);packs.append(names[pair])
                else:
                    require(v[0]=="node" and a[0]in vectors and ints.get(vectors[a[0]][0])==(32,0) and vectors[a[0]][1]==2,"unpack_type")
                    values[a[1]]=("vector",(("limb",v,0),("limb",v,1)))
            elif op==127:
                require(floats.get(a[0])==64 and a[1]in nc,"negate_float64_precise")
                v=value(a[2]);require(v[0]=="source","source_negation");values[a[1]]=("neg",v)
            elif op in (129,131):
                require(floats.get(a[0])==64 and a[1]in nc,"arithmetic_float64_precise")
                left,right=value(a[2]),value(a[3])
                require(left[0]in ("source","neg","node") and right[0]in ("source","neg","node"),"arithmetic_operands")
                nodes.append(dict(op="+" if op==129 else "-",a=left,b=right,result_id=a[1],word_offset=pos,call_context=ctx,float_width=64,NoContraction=True))
                values[a[1]]=("node",len(nodes)-1)
            elif op==57:
                require(fid==main and len(a)==5,"closed_helper_call");calls.append(a[1])
                values[a[1]]=run(a[2],tuple(read(k) for k in a[3:]),(a[1],))
            elif op==254:
                require(fid!=main and len(params)==2,"helper_return");return value(a[0])
            # Other opcodes, early returns and labels are guard-only/metadata in this pinned binary.
            # No branch feasibility, runtime memory layout or SPIR-V validity is certified.
        require(fid==main,"missing_helper_return")
    run(main)
    require(packs==["S0.hi","S0.lo","S1.hi","S1.lo"] and len(calls)==4,"source_call_order")
    edges=[(n["op"],n["a"],n["b"]) for n in nodes]
    require(edges==expected_edges(),"26node_topology")
    expected={4:("limb",("node",20),0),5:("limb",("node",20),1),6:("limb",("node",25),0),7:("limb",("node",25),1)}
    require({k:v for k,v in outputs.items() if k>=4}==expected,"egress_order")
    return dict(nodes=nodes,source_order=packs,helper_calls=calls,egress={str(k):v for k,v in expected.items()},control_flow_certified=False,GPU_RNE_certified=False)
def compare_trace(g,native):
    rows=native["rows"];trace=native["trace"]["nodes"];require(len(trace)==26,"trace_count")
    source={s["record_id"]+"."+part:s[part]["word_le_hex"] for s in rows[:2] for part in ("hi","lo")}
    def bits(ref):
        tag,x=ref
        if tag=="source":return source[x]
        if tag=="node":return trace[x]["y"]
        require(tag=="neg","trace_reference")
        return (int.from_bytes(bytes.fromhex(bits(x)),"little")^(1<<63)).to_bytes(8,"little").hex()
    for node,t in zip(g["nodes"],trace):
        require((node["op"],bits(node["a"]),bits(node["b"]))==(t["op"],t["a"],t["b"]),"captured_trace_edges")
    require(rows[2]["hi_word"]==trace[20]["y"] and rows[2]["lo_word"]==trace[25]["y"],"captured_egress")
    return dict(nodes_matched=26,hi_word=trace[20]["y"],lo_word=trace[25]["y"],new_RN_operations=0)
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
    for step in range(128):
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

def inspect_spirv(raw):
    graph=extract_graph(raw)
    require(len(graph["nodes"])==26 and len(graph["helper_calls"])==4,"new_graph")
    integer_guards=[(p,a) for p,o,a in instructions(raw) if o==199]
    require(len(integer_guards)==4,"four_raw_exponent_guards")
    return dict(graph=graph,raw_exponent_BitwiseAnd=[dict(word_offset=p,result_id=a[1]) for p,a in integer_guards],GPU_executed=False,GPU_guard_certified=False,SPIRV_Tools_validated=False)
def compile_source(source,*,model):
    require(type(model)is str and model==MODEL,"explicit_compile_model")
    require(type(source)is bytes and len(source)<=65536,"bounded_source")
    base=(ROOT/SHADER).read_bytes();require(sha(base)==SHADER_SHA,"new_shader_identity")
    require(source in (base,base+b"\nINVALID_RAW_GUARD_TOKEN\n"),"only_new_source_or_negative")
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
        start=time.perf_counter();result=run(compiler,source,len(source),2,b"oblique_raw_guard_v2.comp",b"main",options)
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

def audit_compiled(raw,*,model):
    require(type(model)is str and model==MODEL,"explicit_audit_model")
    g,s,n=retained();scenarios={};results={};compare={}
    for name,parent in g["scenarios"].items():
        q=json.loads(json.dumps(parent))
        # ABI migration is explicit; only migrate the old correct tag, not faulty tag controls.
        if q["input_words"] and q["input_words"][0]==0x4f444631:q["input_words"][0]=TAG
        scenarios[name]=q;results[name]=simulate_prefix(raw,q)
    require(sum(v["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" for v in results.values())==20,"V2_entry_census")
    require(sum(v["status"]=="HOST_PREFIX_RETURNED" for v in results.values())==45,"V2_return_census")
    for name in g["counterexamples"]:
        require(results[name]["status"]=="HOST_PREFIX_RETURNED" and results[name]["packs"]==[],"old_counter_rejected_BEFORE_pack")
    graph=extract_graph(raw)
    for case in GOOD:compare[case]=compare_trace(graph,n["results"][case])
    return dict(status="HOST_V2_RAW_GUARD_GRAPH_ONLY",scenarios=scenarios,results=results,graph=graph,trace_matches=compare,parent_counterexamples_preserved=g["counterexamples"],parent_shader_requests=len(s["results"]),parent_shader_STOP=sum(v["status"]=="STOP" for v in s["results"].values()),GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,native_promotion_allowed=False,physical_field_certified=False,new_RN_operations=0,compiler_calls_in_this_audit=0,full_costs="UNMEASURED_NOT_ZERO")
