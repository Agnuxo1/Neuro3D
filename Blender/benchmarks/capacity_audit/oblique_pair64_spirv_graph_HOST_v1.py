"""Sealed HOST static dataflow audit; NOT a control-flow or GPU interpreter."""
from pathlib import Path
import base64, hashlib, json, struct, zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-pair64-spirv-graph-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001-CODEX.json"
PSHA="f46a947f771cb4ccbdd1b1e8279642a7187b78a43c8d5f2ef52dfa06406b27e3"
NATIVE="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json"
NSHA="bb67a76885010c9485415007b1f1b5e7fbe03689812216d464baf21dcf4a9dfb"
BSHA="18a062e49d58800efa0c7aa677339e46e8fcc9a95e919b29a78c6f3ef579b6b3"
CASES=("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60")
def require(x, why):
    if not x: raise ValueError(why)
def sha(x): return hashlib.sha256(x).hexdigest()
def unpack_capture(t):
    z=zlib.decompressobj()
    raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1048577)
    require(len(raw)<=1048576 and z.eof and not z.unused_data and not z.unconsumed_tail,"capture_extent")
    require(len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"],"capture_identity")
    require(t["rc"]==0 and t["timed_out"]is False,"capture_PASS")
    return json.loads(raw)["data"]
def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PSHA,"parent_identity")
    p=json.loads(raw);require(len(p["code_doc_sha256"])==100,"parent_pins")
    for f,h in p["code_doc_sha256"].items(): require(sha((ROOT/f).read_bytes())==h,"pin:"+f)
    native=(ROOT/NATIVE).read_bytes();require(sha(native)==NSHA,"native_identity")
    s=unpack_capture(p["test_run"]);n=unpack_capture(json.loads(native)["test_run"])
    b=zlib.decompress(base64.b64decode(s["compiles"]["positive"]["spirv"]["zlib_base64"],validate=True))
    require(len(b)==7280 and sha(b)==BSHA,"sealed_binary")
    return b,s,n
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
def extract(raw):
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
def audit(*,model):
    out=dict(model=MODEL,status="STOP",reason=None,graph=None,cases={},GPU_executed=False,GPU_launch_allowed=False,native_promotion_allowed=False,physical_field_certified=False,new_RN_operations=0,compiler_calls=0,frozen_producer_replays=0,control_flow_certified=False,full_costs="UNMEASURED_NOT_ZERO")
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        b,s,n=retained();g=extract(b)
        for case in CASES:
            require(n["results"][case]["status"]=="CPU_OBLIQUE_PAIR64_DIFFERENCE_ONLY","native_retained_status")
            out["cases"][case]=compare_trace(g,n["results"][case])
        out["graph"]=g;out["status"]="HOST_STATIC_GRAPH_MATCH_ONLY"
        out["preserved_parent_census"]=dict(shader_requests=len(s["results"]),shader_STOP=sum(v["status"]=="STOP" for v in s["results"].values()),native_requests=len(n["results"]),native_STOP=sum(v["status"]=="STOP" for v in n["results"].values()))
    except (ValueError,KeyError,TypeError,OSError,struct.error,zlib.error,UnicodeError) as e:
        out["reason"]=str(e);out["graph"]=None;out["cases"]={}
    return out
