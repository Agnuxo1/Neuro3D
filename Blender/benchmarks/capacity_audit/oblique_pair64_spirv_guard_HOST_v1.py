"""Pinned SPIR-V prefix control-flow HOST model, not a Vulkan interpreter."""
from pathlib import Path
import base64,hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-pair64-spirv-guard-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-SPIRV-GRAPH-HOST-001-CODEX.json"
PSHA="e67fd10f27a812c51aee1cde4937eb3e6cf50bd64cec277a46df3507bace71fb"
SHADER="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001-CODEX.json"
BSHA="18a062e49d58800efa0c7aa677339e46e8fcc9a95e919b29a78c6f3ef579b6b3"
LIMIT_BITS=0x4270000000000000 # finite positive 2^40; never a new bound
EXP_MASK=0x7ff0000000000000
FRAC_MASK=(1<<52)-1
ABS_MASK=(1<<63)-1
POLICIES=("BIT_PRESERVE_DIAGNOSTIC","UNSPECIFIED_TO_POSITIVE_ZERO")
def require(x,why):
    if not x:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def captured(t):
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1048577)
    require(len(raw)<=1048576 and z.eof and not z.unused_data and not z.unconsumed_tail,"capture_extent")
    require(len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"] and t["rc"]==0 and t["timed_out"]is False,"capture_identity")
    return json.loads(raw)["data"]
def retained():
    b=(ROOT/PARENT).read_bytes();require(sha(b)==PSHA,"parent_identity");r=json.loads(b)
    require(len(r["code_doc_sha256"])==105 and r["status"]=="HOST_STATIC_GRAPH_MATCH_ONLY","parent_PASS")
    for path,h in r["code_doc_sha256"].items():require(sha((ROOT/path).read_bytes())==h,"pin:"+path)
    d=captured(json.loads((ROOT/SHADER).read_bytes())["test_run"])
    raw=zlib.decompress(base64.b64decode(d["compiles"]["positive"]["spirv"]["zlib_base64"],validate=True))
    require(len(raw)==7280 and sha(raw)==BSHA,"sealed_binary")
    return raw,d
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
def simulate(raw,q):
    """Diagnostic scenarios only. IEEE bit behavior is an explicit model assumption."""
    require(type(q)is dict and set(q)=={"input_words","output_extent","gid","pack_policy"},"closed_scenario")
    words=q["input_words"];require(type(words)is list and len(words)<=64 and all(type(x)is int and 0<=x<2**32 for x in words),"uint32_words")
    require(type(q["output_extent"])is int and 0<=q["output_extent"]<=64,"output_extent")
    require(type(q["gid"])is list and len(q["gid"])==3 and all(type(x)is int and 0<=x<2**32 for x in q["gid"]),"gid")
    require(q["pack_policy"]in POLICIES,"explicit_pack_policy")
    v,bind,builtin,ext,blocks=decode(raw)
    pointers={k:("buffer",b,()) for k,b in bind.items()}
    pointers.update({k:("builtin",b,()) for k,b in builtin.items()})
    mem={};reads=[];writes=[];packs=[];branches=[];labels=[];previous=None;current=next(iter(blocks))
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
            elif op==171:
                x,y=value(a[2]),value(a[3]);v[a[1]]=tuple(u!=t for u,t in zip(x,y)) if type(x)is tuple else x!=y
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
                return dict(status="HOST_PREFIX_REACHED_ARITHMETIC" if op==57 else "HOST_PREFIX_RETURNED",terminal_word_offset=pos,terminal_label=current,labels=labels,branches=branches,input_reads=reads,output_writes=writes,packs=packs,pack_policy=q["pack_policy"],GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,new_RN_operations=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")
            else:raise ValueError("unsupported_prefix_opcode:"+str(op))
        require(target is not None,"no_terminator");previous,current=current,target
    raise ValueError("step_budget")
def scenarios(shader):
    base_words=list(struct.unpack("<12I",bytes.fromhex(shader["results"]["parent_oblique"]["packet"]["input_hex"])))
    def scenario(words=None,out=8,gid=None,policy=POLICIES[0]):return dict(input_words=list(base_words if words is None else words),output_extent=out,gid=[0,0,0] if gid is None else gid,pack_policy=policy)
    cases={}
    for case in("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60"):
        cases[case]=scenario(list(struct.unpack("<12I",bytes.fromhex(shader["results"][case]["packet"]["input_hex"]))))
    for axis in range(3):
        g=[0,0,0];g[axis]=1;cases["gid_"+str(axis)]=scenario(gid=g)
    for n in(0,11,13):cases["input_extent_"+str(n)]=scenario((base_words+[0])[:n])
    for n in(0,7,9):cases["output_extent_"+str(n)]=scenario(out=n)
    for k in range(4):
        w=list(base_words);w[k]^=1;cases["header_"+str(k)]=scenario(w)
    for component in range(4):
        for tag,bits in(("limit",LIMIT_BITS),("over",LIMIT_BITS+1),("negative_limit",LIMIT_BITS|(1<<63)),("negative_over",(LIMIT_BITS+1)|(1<<63)),("negative_zero",1<<63),("subnormal",1)):
            w=list(base_words);i=4+2*component;w[i]=bits&0xffffffff;w[i+1]=bits>>32
            cases["component_"+str(component)+"_"+tag]=scenario(w)
        for tag,bits in(("nan",0x7ff8000000000001),("inf",0x7ff0000000000000),("negative_inf",0xfff0000000000000)):
            w=list(base_words);i=4+2*component;w[i]=bits&0xffffffff;w[i+1]=bits>>32
            cases["component_"+str(component)+"_"+tag+"_ideal"]=scenario(w)
            cases["component_"+str(component)+"_"+tag+"_unspecified0"]=scenario(w,policy=POLICIES[1])
    return cases
def audit(*,model):
    out=dict(model=MODEL,status="STOP",reason=None,scenarios={},results={},counterexamples=[],GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,native_promotion_allowed=False,physical_field_certified=False,new_RN_operations=0,compiler_calls=0,frozen_producer_replays=0,full_costs="UNMEASURED_NOT_ZERO",JEV="LOCAL_FALLBACK_SECURITY_BLOCKED_NO_RETRY")
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        raw,s=retained();cases=scenarios(s)
        for name,q in cases.items():
            v=simulate(raw,q);out["scenarios"][name]=q;out["results"][name]=v
            if name.endswith("_unspecified0"):
                require(v["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" and any(x["raw_nonfinite"] and x["unspecified_choice_used"] for x in v["packs"]),"counterexample_retained")
                out["counterexamples"].append(name)
        require(len(cases)==65 and len(out["counterexamples"])==12,"scenario_census")
        out["status"]="HOST_AUDIT_COMPLETE_RAW_NONFINITE_GUARD_UNPROVEN"
        out["promotion"]="STOP";out["promotion_reason"]="Post-pack isnan/isinf cannot prove original raw words finite: PackDouble2x32 nonfinite result unspecified. Finite HOST packets only; raw-bit pre-pack validation artifact required."
        out["parent_shader_requests"]=len(s["results"]);out["parent_shader_STOP"]=sum(v["status"]=="STOP" for v in s["results"].values())
    except (ValueError,KeyError,TypeError,OSError,struct.error,zlib.error,UnicodeError) as e:
        out["reason"]=str(e);out["scenarios"]={};out["results"]={};out["counterexamples"]=[]
    return out
