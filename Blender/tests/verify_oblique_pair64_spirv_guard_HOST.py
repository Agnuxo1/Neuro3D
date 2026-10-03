"""Independent sealed prefix/branch-trace audit: no core/compiler/backend import."""
from pathlib import Path
import base64,hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-SPIRV-GUARD-HOST-001-CODEX.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def capture(t):
    raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"] and t["rc"]==0 and not t["timed_out"]
    return json.loads(raw)
def decode(raw):
    w=struct.unpack("<%dI"%(len(raw)//4),raw);assert w[0]==0x07230203
    i=5;ops=[]
    while i<len(w):
        n=w[i]>>16;assert n and i+n<=len(w);ops.append((i,w[i]&65535,w[i+1:i+n]));i+=n
    return ops
def expected(q,ops):
    words=q["input_words"];w=(words+[0]*12)[:12]
    rawbits=[w[k]|(w[k+1]<<32) for k in range(4,12,2)]
    is_nonfinite=lambda x:(x>>52)&2047==2047
    bits=[0 if is_nonfinite(x) and q["pack_policy"]=="UNSPECIFIED_TO_POSITIVE_ZERO" else x for x in rawbits]
    isnan=[is_nonfinite(x) and bool(x&0xfffffffffffff) for x in bits]
    isinf=[is_nonfinite(x) and not x&0xfffffffffffff for x in bits]
    over=[(x&0x7fffffffffffffff)>0x4270000000000000 for x in bits]
    header=[w[k]!=[0x4f444631,8,2,1][k] for k in range(4)]
    nf=any(isnan) or any(isinf)
    cond={53:q["gid"]!=[0,0,0],66:len(words)==12,77:len(words)!=12 or q["output_extent"]!=8,
          95:not header[0],103:not any(header[:2]),110:not any(header[:3]),117:any(header),
          159:not isnan[0],165:not any(isnan[:2]),171:not any(isnan[:3]),177:not any(isnan),
          183:not(any(isnan) or isinf[0]),189:not(any(isnan) or any(isinf[:2])),195:not(any(isnan) or any(isinf[:3])),
          201:not nf,209:not(nf or over[0]),216:not(nf or any(over[:2])),223:not(nf or any(over[:3])),229:nf or any(over)}
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
    if not valid_sizes:reads=[];writes=[];packs=[]
    else:
        writes=[[0,0],[1,0],[2,2],[3,0]]
        if any(header):
            reads=list(range(header.index(True)+1));packs=[]
        else:
            reads=list(range(12));packs=[dict(result_id=rid,original_bits_le=x.to_bytes(8,"little").hex(),modeled_bits_le=y.to_bytes(8,"little").hex(),raw_nonfinite=is_nonfinite(x),unspecified_choice_used=is_nonfinite(x) and y==0) for rid,x,y in zip((130,139,147,156),rawbits,bits)]
    return dict(status="HOST_PREFIX_REACHED_ARITHMETIC" if reached else "HOST_PREFIX_RETURNED",terminal_word_offset=terminal[0],terminal_label=current,labels=labels,branches=branches,input_reads=reads,output_writes=writes,packs=packs,pack_policy=q["pack_policy"],GPU_executed=False,GPU_launch_allowed=False,GPU_guard_certified=False,new_RN_operations=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")
def main():
    r=json.loads((ROOT/RECEIPT).read_bytes());assert len(r["code_doc_sha256"])==110
    for path,h in r["code_doc_sha256"].items():assert sha((ROOT/path).read_bytes())==h,path
    t=capture(r["test_run"]);assert t["status"]=="PASS" and t["test_groups"]==6
    data=t["data"];v=data["result"];assert v["status"]=="HOST_AUDIT_COMPLETE_RAW_NONFINITE_GUARD_UNPROVEN" and v["promotion"]=="STOP"
    assert v["GPU_executed"]is False and v["GPU_launch_allowed"]is False and v["GPU_guard_certified"]is False and v["native_promotion_allowed"]is False and v["physical_field_certified"]is False
    assert v["new_RN_operations"]==v["compiler_calls"]==v["frozen_producer_replays"]==0 and v["full_costs"]=="UNMEASURED_NOT_ZERO"
    s=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001-CODEX.json").read_bytes());sd=capture(s["test_run"])["data"]
    b=zlib.decompress(base64.b64decode(sd["compiles"]["positive"]["spirv"]["zlib_base64"]));assert len(b)==7280 and sha(b)=="18a062e49d58800efa0c7aa677339e46e8fcc9a95e919b29a78c6f3ef579b6b3"
    ops=decode(b);assert ops[-1][1]==56
    # Sealed main has twelve post-pack checks and NO pre-pack raw bit classification.
    prefix=[(p,o,a) for p,o,a in ops if 476<=p<1381]
    assert [(o,a[1]) for p,o,a in prefix if o in(156,157)]==[(156,158),(156,163),(156,169),(156,175),(157,181),(157,187),(157,193),(157,199)]
    assert [a[1] for p,o,a in prefix if o==186]==[207,214,221,228]
    assert min(p for p,o,a in prefix if o in(156,157))>max(p for p,o,a in prefix if o==12 and a[3]==59)
    assert all(o not in(129,131) for p,o,a in prefix)
    assert len(v["scenarios"])==len(v["results"])==65
    # Exact expected scenario IDs prevent duplicate/census masquerading.
    keys={"parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60"}
    keys|={"gid_"+str(k) for k in range(3)}
    keys|={"input_extent_"+str(k) for k in(0,11,13)}
    keys|={"output_extent_"+str(k) for k in(0,7,9)}
    keys|={"header_"+str(k) for k in range(4)}
    keys|={"component_"+str(k)+"_"+tag for k in range(4) for tag in("limit","over","negative_limit","negative_over","negative_zero","subnormal")}
    keys|={"component_"+str(k)+"_"+tag+"_"+policy for k in range(4) for tag in("nan","inf","negative_inf") for policy in("ideal","unspecified0")}
    assert set(v["scenarios"])==set(v["results"])==keys
    for name,q in v["scenarios"].items():assert v["results"][name]==expected(q,ops),name
    for name in("parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60"):
        assert struct.pack("<12I",*v["scenarios"][name]["input_words"]).hex()==sd["results"][name]["packet"]["input_hex"]
    assert sum(x["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" for x in v["results"].values())==32
    assert sum(x["status"]=="HOST_PREFIX_RETURNED" for x in v["results"].values())==33
    counter=[name for name in sorted(keys) if name.endswith("_unspecified0")]
    assert sorted(v["counterexamples"])==counter and len(counter)==12
    for key in counter:
        ideal=key.replace("_unspecified0","_ideal")
        assert v["scenarios"][key]["input_words"]==v["scenarios"][ideal]["input_words"]
        assert v["results"][key]["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" and v["results"][ideal]["status"]=="HOST_PREFIX_RETURNED"
        assert sum(x["unspecified_choice_used"] for x in v["results"][key]["packs"])==1
    assert set(data["negative"])=={"truncated","bad_magic","bad_branch_target","unknown_prefix_opcode","unknown_policy","bool_policy"}
    for name,x in data["negative"].items():
        assert x["status"]=="STOP" and x["reason"]
        if "binary_hex"in x:
            raw=bytes.fromhex(x["binary_hex"]);assert raw!=b and sha(raw)==x["binary_sha256"]
    wrong=data["wrong_model"];assert wrong["status"]=="STOP" and wrong["reason"]=="explicit_model" and wrong["results"]=={} and wrong["scenarios"]=={}
    breach=data["bypass"];mut=bytes.fromhex(breach["binary_hex"]);assert sha(mut)==breach["binary_sha256"] and mut!=b and breach["sealed_admission_allowed"]is False
    witness=json.loads(json.dumps(v["results"]["parent_oblique"]))
    changed=[branch for branch in witness["branches"] if branch["condition_id"]==117]
    assert len(changed)==1 and changed[0]["target"]==119 and changed[0]["condition"]is False
    changed[0]["condition"]=True
    assert breach["result"]==witness
    # Specific mutation changes only target118→119 at final header conditional, all other bytes intact.
    assert [(i,x,y) for i,(x,y) in enumerate(zip(b,mut)) if x!=y]==[(3280,118,119)]
    assert breach["scenario"]==v["scenarios"]["header_3"] and v["results"]["header_3"]["status"]=="HOST_PREFIX_RETURNED"
    assert v["parent_shader_requests"]==57 and v["parent_shader_STOP"]==53
    assert r["GPU_executed"]is False and r["new_RN_operations"]==r["compiler_calls"]==0 and r["promotion"]=="STOP"
    print(json.dumps(dict(status="PASS",pins=110,scenarios=65,modeled_arithmetic_entry=32,modeled_early_returns=33,conditional_nonfinite_counterexamples=12,negative_controls=7,header_bypass_mutations=1,GPU_guard_certified=False,promotion="STOP",new_RN_operations=0,compiler_calls=0,GPU_executed=False),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
