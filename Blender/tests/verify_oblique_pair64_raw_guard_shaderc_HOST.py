"""Independent new V2 binary/guard/reference/packet/graph verifier; no core imports."""
from pathlib import Path
import base64,hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-RAW-GUARD-SHADERC-001-CODEX.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def capture(t):
    raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True));assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"] and t["rc"]==0 and not t["timed_out"];return json.loads(raw)
def packed(p):
    raw=zlib.decompress(base64.b64decode(p["zlib_base64"],validate=True));assert len(raw)==p["bytes"] and sha(raw)==p["sha256"];return raw
def decode(raw):
    w=struct.unpack("<%dI"%(len(raw)//4),raw);assert w[0]==0x07230203 and w[1]==0x10000 and w[4]==0
    i=5;ops=[]
    while i<len(w):
        n=w[i]>>16;assert n and i+n<=len(w);ops.append((i,w[i]&65535,w[i+1:i+n]));i+=n
    assert ops[-1][1]==56;return ops
def expected(q,ops):
    words=q["input_words"];w=(words+[0]*12)[:12]
    rawbits=[w[k]|(w[k+1]<<32) for k in range(4,12,2)]
    raw_nf=[((x>>52)&2047)==2047 for x in rawbits]
    is_nonfinite=lambda x:(x>>52)&2047==2047
    bits=rawbits # nonfinite must return BEFORE any pack
    isnan=[is_nonfinite(x) and bool(x&0xfffffffffffff) for x in bits]
    isinf=[is_nonfinite(x) and not x&0xfffffffffffff for x in bits]
    over=[(x&0x7fffffffffffffff)>0x4270000000000000 for x in bits]
    header=[w[k]!=[0x4f444632,8,2,1][k] for k in range(4)]
    nf=any(isnan) or any(isinf)
    cond={53:q["gid"]!=[0,0,0],66:len(words)==12,77:len(words)!=12 or q["output_extent"]!=8,
          95:not header[0],103:not any(header[:2]),110:not any(header[:3]),117:any(header),
          127:not raw_nf[0],136:not any(raw_nf[:2]),145:not any(raw_nf[:3]),153:any(raw_nf),
          191:not isnan[0],197:not any(isnan[:2]),203:not any(isnan[:3]),209:not any(isnan),
          215:not(any(isnan) or isinf[0]),221:not(any(isnan) or any(isinf[:2])),227:not(any(isnan) or any(isinf[:3])),
          233:not nf,241:not(nf or over[0]),248:not(nf or any(over[:2])),255:not(nf or any(over[:3])),261:nf or any(over)}
    # Independent CFG traversal driven by direct input predicates, not SSA interpretation.
    blocks={};active=False;label=None
    for pos,op,a in ops:
        if op==54:active=a[1]==4
        elif op==56:active=False
        elif active:
            if op==248:label=a[0];blocks[label]=[]
            elif label is not None:blocks[label].append((pos,op,a))
    labels=[];branches=[];current=5
    for step in range(128):
        assert current not in labels;labels.append(current);block=blocks[current]
        call=next((t for t in block if t[1]==57),None)
        if call is not None:terminal=call;break
        pos,op,a=block[-1]
        if op==253:terminal=(pos,op,a);break
        if op==249:current=a[0]
        else:
            assert op==250 and a[0]in cond
            target=a[1] if cond[a[0]] else a[2]
            branches.append(dict(word_offset=pos,label=current,condition_id=a[0],condition=cond[a[0]],target=target));current=target
    else:raise AssertionError("budget")
    valid_sizes=q["gid"]==[0,0,0] and len(words)==12 and q["output_extent"]==8
    reached=valid_sizes and not any(header) and not nf and not any(over)
    assert (terminal[1]==57)==reached
    checks=[]
    if not valid_sizes:reads=[];writes=[];packs=[]
    else:
        writes=[[0,0],[1,0],[2,2],[3,0]]
        if any(header):
            reads=list(range(header.index(True)+1));packs=[]
        else:
            stop=raw_nf.index(True)+1 if any(raw_nf) else 4
            reads=list(range(4))+[5+2*j for j in range(stop)]
            checks=[dict(word_offset=pos,raw_high_word=w[5+2*j],mask=0x7ff00000,result=w[5+2*j]&0x7ff00000) for j,pos in enumerate((841,874,918,962)[:stop])]
            if any(raw_nf):packs=[]
            else:
                reads+=list(range(4,12))
                packs=[dict(result_id=rid,original_bits_le=x.to_bytes(8,"little").hex(),modeled_bits_le=x.to_bytes(8,"little").hex(),raw_nonfinite=False,unspecified_choice_used=False) for rid,x in zip((165,173,180,188),rawbits)]
    return dict(status="HOST_PREFIX_REACHED_ARITHMETIC" if reached else "HOST_PREFIX_RETURNED",terminal_word_offset=terminal[0],terminal_label=current,labels=labels,branches=branches,input_reads=reads,output_writes=writes,packs=packs,raw_exponent_checks=checks,pack_policy=q["pack_policy"],GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,new_RN_operations=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")

def main():
    r=json.loads((ROOT/RECEIPT).read_bytes());assert len(r["code_doc_sha256"])==116
    for path,h in r["code_doc_sha256"].items():assert sha((ROOT/path).read_bytes())==h,path
    suite=capture(r["test_run"]);assert suite["status"]=="PASS" and suite["test_groups"]==6
    d=suite["data"];assert d["total_new_compile_calls"]==r["total_new_compile_calls"]==2
    parent=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-SPIRV-GUARD-HOST-001-CODEX.json").read_bytes())
    pd=capture(parent["test_run"])["data"]["result"]
    assert parent["promotion"]=="STOP" and len(pd["counterexamples"])==12 and len(pd["scenarios"])==65
    previous=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001-CODEX.json").read_bytes());sd=capture(previous["test_run"])["data"]
    pos=d["compiles"]["positive"];neg=d["compiles"]["negative"]
    source=packed(pos["source"]);raw=packed(pos["spirv"]);ops=decode(raw)
    assert source==(ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_raw_guard_v2.comp").read_bytes()
    assert sha(source)=="277a94ba2d223a2e2d06052037c6ef549b04270748a3678501ecd2da4446b70f" and len(source)==2221
    assert len(raw)==7952 and sha(raw)=="b7ce7b270d930b67b20a89945b7ae4b9c581ece1b072148beb8f98a7fc2b6ad8"
    assert pos["status"]==pos["errors"]==0 and "inspection_failure"not in pos
    assert neg["status"]==2 and neg["errors"]==1 and packed(neg["spirv"])==b"" and neg["diagnostics"]
    assert packed(neg["source"])==source+b"\nINVALID_RAW_GUARD_TOKEN\n"
    for c in(pos,neg):
        assert (c["target_env"],c["target_version"],c["shader_kind"],c["entry_point"],c["optimization"])==(0,4194304,2,"main",0)
        assert c["compiler_sha256"]=="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b" and c["compiler_bytes"]==4478464 and c["compiler_version"]=="UNKNOWN_LOCAL_HASH_IDENTITY"
        assert c["GPU_executed"]is False and c["GPU_launch_allowed"]is False and c["full_costs"]=="UNMEASURED_NOT_ZERO"
    # Exact compiled unsigned raw high-word chains BEFORE pack59; no floating classification needed.
    const={a[1]:a[2] for p,o,a in ops if o==43 and len(a)==3}
    access={a[1]:a[2:] for p,o,a in ops if o==65};loads={a[1]:a[2] for p,o,a in ops if o==61}
    AND=[(p,a) for p,o,a in ops if o==199];eq=[a for p,o,a in ops if o==170]
    assert len(AND)==len(eq)==4
    for j,((p,a),e) in enumerate(zip(AND,eq)):
        assert a[0]==43 and e[2]==a[1] and e[3]==a[3] and const[a[3]]==0x7ff00000
        ptr=access[loads[a[2]]];assert ptr[0]==60 and [const[k] for k in ptr[1:]]==[0,5+2*j]
    packops=[(p,a) for p,o,a in ops if o==12 and a[3]==59];assert len(packops)==4 and max(p for p,a in AND)<min(p for p,a in packops)
    # Independently source pair component order from input word access chains.
    vectors={a[1]:a[2:] for p,o,a in ops if o==80}
    for j,(p,a) in enumerate(packops):
        pair=vectors[a[4]];indices=[]
        for value in pair:
            ptr=access[loads[value]];assert ptr[0]==60 and const[ptr[1]]==0;indices.append(const[ptr[2]])
        assert indices==[4+2*j,5+2*j]
    arith={a[1]:(p,o,a) for p,o,a in ops if o in(129,131)};nc={a[0] for p,o,a in ops if o==71 and a[1]==42}
    assert len(arith)==8 and all(a[0]==6 and uid in nc for uid,(p,o,a) in arith.items())
    calls=[a[1] for p,o,a in ops if o==57];assert calls==[272,279,292,305]
    audit=d["audit"];assert audit["status"]=="HOST_V2_RAW_GUARD_GRAPH_ONLY" and set(audit["scenarios"])==set(pd["scenarios"])
    for name,q in audit["scenarios"].items():
        old=pd["scenarios"][name];copy=json.loads(json.dumps(old))
        if copy["input_words"] and copy["input_words"][0]==0x4f444631:copy["input_words"][0]=0x4f444632
        assert q==copy and audit["results"][name]==expected(q,ops),name
    assert sum(v["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" for v in audit["results"].values())==20
    assert sum(v["status"]=="HOST_PREFIX_RETURNED" for v in audit["results"].values())==45
    for name in pd["counterexamples"]:
        assert pd["results"][name]["status"]=="HOST_PREFIX_REACHED_ARITHMETIC"
        assert audit["results"][name]["status"]=="HOST_PREFIX_RETURNED" and audit["results"][name]["packs"]==[]
    assert audit["parent_counterexamples_preserved"]==pd["counterexamples"]
    assert len(d["results"])==16 and sum(v["status"]=="STOP" for v in d["results"].values())==12
    for case in("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60"):
        result=d["results"][case];p=result["packet"];old=sd["results"][case]["packet"];q=d["selectors"][case]
        assert result["status"]=="CPU_RAW_GUARD_V2_PACKET_ONLY"
        assert p["input_hex"]==(struct.pack("<I",0x4f444632)+bytes.fromhex(old["input_hex"])[4:]).hex()
        assert p["expected_CONTROL_ONLY_hex"]==(struct.pack("<I",0x4f444632)+bytes.fromhex(old["expected_CONTROL_ONLY_hex"])[4:]).hex()
        assert p["retained_CPU_budget"]==old["retained_CPU_budget"] and p["source_literal_caps"]==old["source_literal_caps"]
        assert p["scene_sha256"]==q["original_scene_sha256"]==old["scene_sha256"] and p["literal_sha256"]==q["literal_request_sha256"]==old["literal_sha256"]
        assert digest(old)==p["parent_packet_sha256"]==q["parent_packet_sha256"]
        assert p["input_bytes"]==48 and p["output_bytes"]==32 and p["total_SSBO_bytes"]==80 and p["expected_HOST_bytes"]==32
        assert p["ABI_tag"]==0x4f444632 and p["shader_sha256"]=="277a94ba2d223a2e2d06052037c6ef549b04270748a3678501ecd2da4446b70f" and p["GPU_launch_allowed"]is False and p["execution_status"]=="NOT_EXECUTED"
    for name,v in d["results"].items():
        assert v["GPU_executed"]is False and v["GPU_launch_allowed"]is False and v["GPU_guard_certified"]is False and v["native_promotion_allowed"]is False and v["physical_field_certified"]is False and v["new_RN_operations"]==0
        if name not in("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60"):assert v["status"]=="STOP" and v["packet"]is None and v["reason"]
    # Immutable old graph topology and native operand bit events, not CPU recomputation.
    graphparent=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-SPIRV-GRAPH-HOST-001-CODEX.json").read_bytes());oldgraph=capture(graphparent["test_run"])["data"]["result"]["graph"]
    graph=audit["graph"];assert len(graph["nodes"])==26 and graph["helper_calls"]==calls
    assert [(v["op"],v["a"],v["b"]) for v in graph["nodes"]]==[(v["op"],v["a"],v["b"]) for v in oldgraph["nodes"]]
    helper=[17,21,25,29,33,37];expanded=[(calls[0],x) for x in helper]+[(calls[1],x) for x in helper]+[(None,285)]+[(calls[2],x) for x in helper]+[(None,298)]+[(calls[3],x) for x in helper]
    for node,(ctx,uid) in zip(graph["nodes"],expanded):
        p,o,a=arith[uid];assert node["result_id"]==uid and node["word_offset"]==p and node["call_context"]==([] if ctx is None else [ctx]) and node["float_width"]==64 and node["NoContraction"]is True and node["op"]==("+" if o==129 else "-")
    assert graph["egress"]==oldgraph["egress"] and graph["source_order"]==oldgraph["source_order"]
    native=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json").read_bytes());nd=capture(native["test_run"])["data"]
    for case,c in audit["trace_matches"].items():
        n=nd["results"][case];events=n["trace"]["nodes"];rows=n["rows"];sourcebits={s["record_id"]+"."+part:s[part]["word_le_hex"] for s in rows[:2] for part in("hi","lo")}
        def bits(ref):
            tag,x=ref
            if tag=="source":return sourcebits[x]
            if tag=="node":return events[x]["y"]
            assert tag=="neg";b=bytearray.fromhex(bits(x));b[7]^=128;return b.hex()
        for node,event in zip(graph["nodes"],events):assert (node["op"],bits(node["a"]),bits(node["b"]))==(event["op"],event["a"],event["b"])
        assert c==dict(nodes_matched=26,hi_word=rows[2]["hi_word"],lo_word=rows[2]["lo_word"],new_RN_operations=0)
    control=d["controls"];assert control["before_DLL_model"]=="explicit_compile_model" and control["before_DLL_source"]=="only_new_source_or_negative"
    mask=control["mask_mutation"];mut=bytes.fromhex(mask["binary_hex"]);assert mask["status"]=="STOP" and mask["reason"]=="V2_entry_census" and sha(mut)==mask["binary_sha256"]
    constant_positions=[p for p,o,a in ops if o==43 and len(a)==3 and a[2]==0x7ff00000]
    assert constant_positions==[416]
    expected_mutation=bytearray(raw);struct.pack_into("<I",expected_mutation,4*(constant_positions[0]+3),0)
    assert mut==bytes(expected_mutation)
    for name,v in control["ingress"].items():
        q=audit["scenarios"][name];w=q["input_words"]
        good=len(w)==12 and w[:4]==[0x4f444632,8,2,1] and all(((w[k+1]>>20)&2047)!=2047 and ((w[k]|(w[k+1]<<32))&0x7fffffffffffffff)<=0x4270000000000000 for k in range(4,12,2))
        assert (v["status"]=="HOST_RAW_FINITE_DOMAIN_ONLY")==good,name
    assert audit["GPU_guard_certified"]is False and audit["GPU_launch_allowed"]is False and audit["new_RN_operations"]==0 and audit["compiler_calls_in_this_audit"]==0
    assert audit["parent_shader_requests"]==57 and audit["parent_shader_STOP"]==53 and r["GPU_executed"]is False and r["GPU_launch_allowed"]is False
    print(json.dumps(dict(status="PASS",pins=116,new_compile_calls=2,HOST_requests=16,HOST_packets=4,HOST_STOP=12,scenarios=65,modeled_entry=20,modeled_returns=45,old_counterexamples_preserved=12,nonfinite_prepack_rejections=24,nodes=26,native_edges=104,GPU_executed=False,GPU_guard_certified=False),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
