"""Independent receipt verifier: no imports of core/backend/compiler."""
from pathlib import Path
import base64,hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-SPIRV-GRAPH-HOST-001-CODEX.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def capture(t):
    raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"] and t["rc"]==0 and not t["timed_out"]
    return json.loads(raw)
def lists(v):
    if isinstance(v,tuple):return [lists(x) for x in v]
    if isinstance(v,list):return [lists(x) for x in v]
    return v
def main():
    r=json.loads((ROOT/RECEIPT).read_bytes());pins=r["code_doc_sha256"]
    assert len(pins)==105
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r["initial_failure"]["rc"]==1 and "mutation unexpectedly accepted:truncated" in r["initial_failure"]["stderr"]
    assert "unclosed_function" not in r["initial_core_source"]
    assert r["compiler_calls"]==r["new_RN_operations"]==0 and r["GPU_executed"]is False
    s=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001-CODEX.json").read_bytes())
    sd=capture(s["test_run"])["data"];bd=sd["compiles"]["positive"]["spirv"]
    raw=zlib.decompress(base64.b64decode(bd["zlib_base64"]));assert sha(raw)==bd["sha256"] and len(raw)==7280
    w=struct.unpack("<%dI"%(len(raw)//4),raw);ops=[];i=5
    while i<len(w):
        count=w[i]>>16;assert count and i+count<=len(w)
        ops.append((i,w[i]&65535,w[i+1:i+count]));i+=count
    assert ops[-1][1]==56
    # Independent ID-level expansion of this one sealed compiler output, not expected_edges().
    stat={a[1]:(pos,op,a) for pos,op,a in ops if op in (129,131)}
    helper_ids=[17,21,25,29,33,37]
    expanded=[(240,x) for x in helper_ids]+[(247,x) for x in helper_ids]+[(None,253)]+[(260,x) for x in helper_ids]+[(None,266)]+[(273,x) for x in helper_ids]
    # Explicit independent topology catches source swaps even if captured values coincide.
    S=lambda x:["source",x];N=lambda x:["node",x];NEG=lambda x:["neg",S(x)]
    edge=[
      ("+",S("S0.hi"),NEG("S1.hi")),("-",N(0),S("S0.hi")),("-",N(0),N(1)),("-",NEG("S1.hi"),N(1)),("-",S("S0.hi"),N(2)),("+",N(4),N(3)),
      ("+",S("S0.lo"),NEG("S1.lo")),("-",N(6),S("S0.lo")),("-",N(6),N(7)),("-",NEG("S1.lo"),N(7)),("-",S("S0.lo"),N(8)),("+",N(10),N(9)),
      ("+",N(5),N(6)),("+",N(0),N(12)),("-",N(13),N(0)),("-",N(13),N(14)),("-",N(12),N(14)),("-",N(0),N(15)),("+",N(17),N(16)),
      ("+",N(18),N(11)),("+",N(13),N(19)),("-",N(20),N(13)),("-",N(20),N(21)),("-",N(19),N(21)),("-",N(13),N(22)),("+",N(24),N(23))]
    t=capture(r["test_run"]);assert t["status"]=="PASS" and t["tests"]==5
    data=t["data"];v=data["result"];assert v["status"]=="HOST_STATIC_GRAPH_MATCH_ONLY"
    graph=v["graph"];assert len(graph["nodes"])==26 and graph["helper_calls"]==[240,247,260,273]
    nc={a[0] for pos,op,a in ops if op==71 and a[1]==42}
    for index,(node,(ctx,result_id),(op,left,right)) in enumerate(zip(graph["nodes"],expanded,edge)):
        pos,opcode,args=stat[result_id]
        assert node==dict(op=op,a=left,b=right,result_id=result_id,word_offset=pos,call_context=[] if ctx is None else [ctx],float_width=64,NoContraction=True)
        assert opcode==(129 if op=="+" else 131) and result_id in nc and args[0]==6
    assert graph["source_order"]==["S0.hi","S0.lo","S1.hi","S1.lo"]
    assert graph["egress"]=={str(k):["limb",N(node),limb] for k,node,limb in [(4,20,0),(5,20,1),(6,25,0),(7,25,1)]}
    # Source pack, limbs, ext-set and output stores are independently read from the sealed binary.
    assert [a for p,o,a in ops if o==12 and a[3]in(59,65)]==[(6,130,1,59,129),(6,139,1,59,138),(6,147,1,59,146),(6,156,1,59,155),(128,278,1,65,277),(128,282,1,65,281)]
    assert [a for p,o,a in ops if o==80]==[(128,129,124,127),(128,138,134,137),(128,146,142,145),(128,155,151,154),(8,40,38,39)]
    assert [a for p,o,a in ops if o==62 and a[0]in(286,289,292,295)]==[(286,285),(289,288),(292,291),(295,294)]
    native=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json").read_bytes());nd=capture(native["test_run"])["data"]
    assert v["preserved_parent_census"]==dict(shader_requests=57,shader_STOP=53,native_requests=46,native_STOP=42)
    assert len(sd["results"])==57 and len(nd["results"])==46
    assert set(v["cases"])=={"parent_oblique","parent_direction_scaled","parent_shared_ref1000","parent_tiny_gap_2m60"}
    for case,c in v["cases"].items():
        n=nd["results"][case];rows=n["rows"];trace=n["trace"]["nodes"]
        words={s["record_id"]+"."+part:s[part]["word_le_hex"] for s in rows[:2] for part in ("hi","lo")}
        def bits(ref):
            tag,x=ref
            if tag=="source":return words[x]
            if tag=="node":return trace[x]["y"]
            assert tag=="neg";b=bytearray.fromhex(bits(x));b[7]^=128;return b.hex()
        assert len(trace)==26
        for (op,a,b),event in zip(edge,trace):assert (op,bits(a),bits(b))==(event["op"],event["a"],event["b"])
        assert c==dict(nodes_matched=26,hi_word=rows[2]["hi_word"],lo_word=rows[2]["lo_word"],new_RN_operations=0)
        assert rows[2]["hi_word"]==trace[20]["y"] and rows[2]["lo_word"]==trace[25]["y"]
    expected={"add_to_sub","remove_NoContraction","source_limb_swap","source_pair_swap","egress_limb_swap","unknown_used_operation","float32","wrong_ext_set","truncated","bad_magic","captured_operand_fault"}
    assert set(data["negatives"])==expected
    for name,c in data["negatives"].items():
        assert c["status"]=="STOP" and c["reason"]
        if "binary_hex" in c:
            b=bytes.fromhex(c["binary_hex"]);assert b!=raw and sha(b)==c["binary_sha256"]
    assert data["negatives"]["truncated"]["reason"]=="unclosed_function"
    assert data["wrong_model"]["status"]=="STOP" and data["wrong_model"]["graph"]is None and data["wrong_model"]["cases"]=={}
    for obj in(v,data["wrong_model"]):
        assert all(obj[k]is False for k in("GPU_executed","GPU_launch_allowed","native_promotion_allowed","physical_field_certified","control_flow_certified"))
        assert obj["compiler_calls"]==obj["new_RN_operations"]==obj["frozen_producer_replays"]==0
        assert obj["full_costs"]=="UNMEASURED_NOT_ZERO"
    assert graph["control_flow_certified"]is False and graph["GPU_RNE_certified"]is False
    print(json.dumps(dict(status="PASS",pins=105,nodes=26,cases=4,captured_edges=104,binary_mutations=10,trace_faults=1,model_STOP=1,initial_failure_retained=True,compiler_calls=0,new_RN_operations=0,GPU_executed=False,control_flow_certified=False),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
