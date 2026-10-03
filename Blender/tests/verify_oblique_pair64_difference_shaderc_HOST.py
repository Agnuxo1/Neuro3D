"""Independent sealed packets and binary SPIR-V oracle; no producer/compiler imports."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001"
MODEL="precision-oblique-pair64-difference-shaderc-HOST-v1"
REP="OBLIQUE_DIFFERENCE_SHADER_CANDIDATE_NO_GPU_ADMISSION"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json"
PSHA="bb67a76885010c9485415007b1f1b5e7fbe03689812216d464baf21dcf4a9dfb"
SHADER="Blender/benchmarks/capacity_audit/oblique_pair64_difference_v1.comp"
SSHA="8fcc8f6df4f4ef061c94208a43af70797c03f983532d1363f6526360bfc5766d"
DLL="D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll"
DSHA="d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
TAG=0x4f444631
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def unpack64(t):
    assert t["rc"]==0 and t["timed_out"]is False and t["threads"]==t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail
    assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==6;return v["data"]
def binary(v):
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(v["zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail
    assert len(raw)==v["bytes"] and sha(raw)==v["sha256"];return raw
def u32(raw):return [int.from_bytes(raw[i:i+4],"little") for i in range(0,len(raw),4)]
def bytes32(ws):return b"".join(w.to_bytes(4,"little") for w in ws)
def selected(i,parent):
    q=i["selector"];keys={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","representation","shader_sha256","intent"}
    if type(i["model"])is not str or i["model"]!=MODEL or type(q)is not dict or set(q)!=keys:return None
    if not all(type(v)is str for v in q.values()) or (q["representation"],q["shader_sha256"],q["intent"])!=(REP,SSHA,"CPU_PREPARE_COMPILE_ONLY"):return None
    if q["case"]not in parent["results"]:return None
    v=parent["results"][q["case"]]
    if q["parent_result_sha256"]!=digest(v) or v["status"]!="CPU_OBLIQUE_PAIR64_DIFFERENCE_ONLY":return None
    if not all(s["original_scene_sha256"]==q["original_scene_sha256"] and s["literal_request_sha256"]==q["literal_request_sha256"] for s in v["rows"]):return None
    return v
def reflect(raw):
    assert len(raw)>=20 and len(raw)%4==0;w=u32(raw);assert w[0]==0x07230203 and w[4]==0
    i=5;caps=[];bind={};stride={};offset={};ints={};floats={};arrays={};structs={};pointers={};variables={};arith=[];noc=set();calls=[];functions=[];modes=[];entries=[];neg=0
    while i<len(w):
        n=w[i]>>16;op=w[i]&65535;assert n>0 and i+n<=len(w);a=w[i+1:i+n]
        if op==17:caps.append(a[0])
        if op==21:ints[a[0]]=a[1:]
        if op==22:floats[a[0]]=a[1]
        if op==29:arrays[a[0]]=a[1]
        if op==30:structs[a[0]]=a[1:]
        if op==32:pointers[a[0]]=a[2]
        if op==59:variables[a[1]]=a[0]
        if op in (129,131):arith.append((op,a[0],a[1]))
        if op==127:neg+=1
        if op==54:functions.append(a[1])
        if op==57:calls.append(a[2])
        if op==15:entries.append(a)
        if op==16:modes.append(a)
        if op==71:
            if a[1]==42:noc.add(a[0])
            if a[1]==33:bind[a[0]]=a[2]
            if a[1]==6:stride[a[0]]=a[2]
        if op==72 and a[2]==35:offset[(a[0],a[1])]=a[3]
        i+=n
    assert sorted(caps)==[1,10] and set(floats.values())=={64}
    assert len(arith)==8 and sum(op==129 for op,_,_ in arith)==4
    assert all(floats.get(t)==64 and rid in noc for _,t,rid in arith)
    assert len(calls)==4 and len(set(calls))==1 and calls[0]in functions and len(functions)==2 and neg==2
    assert sorted(bind.values())==[0,1] and len(bind)==2
    for var,binding in bind.items():
        st=pointers[variables[var]];assert len(structs[st])==1 and offset[(st,0)]==0
        arr=structs[st][0];assert stride[arr]==4 and ints[arrays[arr]]==[32,0]
    assert any(a[0]==5 and bytes32([a[2]])==b"main" for a in entries) and any(a[1:]==[17,1,1,1] for a in modes)
    return dict(capabilities=caps,float_widths=[64],static_FAdd=4,static_FSub=4,NoContraction_arithmetic_nodes=8,
        TwoSum_function_calls=4,source_graph_operations_per_valid_invocation=26,sign_negations=2,bindings=[0,1],
        array_strides=list(stride.values()),LocalSize=[1,1,1],SPIRV_Tools_validated=False,GPU_executed=False,
        GPU_RNE_certified=False,GPU_denorm_certified=False)
def main():
    r=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes())
    assert r["id"]==ID and r["model"]==MODEL and r["status"]=="CPU_COMPILED_CANDIDATE_NO_GPU"
    assert len(r["code_doc_sha256"])==100
    for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
    raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PSHA;pr=json.loads(raw)
    assert len(pr["code_doc_sha256"])==93 and all(r["code_doc_sha256"][p]==h for p,h in pr["code_doc_sha256"].items())
    source=(ROOT/SHADER).read_bytes();assert sha(source)==SSHA and sha(Path(DLL).read_bytes())==DSHA
    parent=unpack64(pr["test_run"]);data=unpack64(r["test_run"]);assert len(data["inputs"])==len(data["results"])==57
    good=bad=0
    for name,i in data["inputs"].items():
        v=data["results"][name];old=selected(i,parent)
        assert all(v[k]is False for k in ("GPU_executed","GPU_launch_allowed","GPU_semantics_certified","physical_field_certified","native_promotion_allowed"))
        assert v["new_RN_operations"]==v["frozen_producer_replays"]==0 and v["full_costs"]=="UNMEASURED_NOT_ZERO"
        if old is None:
            bad+=1;assert v["status"]=="STOP" and v["packet"]is None;continue
        good+=1;assert v["status"]=="CPU_SHADER_CANDIDATE_PACKET_ONLY";p=v["packet"];rows=old["rows"]
        payload=b"".join(bytes.fromhex(s[k]["word_le_hex"]) for s in rows[:2] for k in ("hi","lo"))
        expected=bytes.fromhex(rows[2]["hi_word"]+rows[2]["lo_word"])
        assert p["input_hex"]==(bytes32([TAG,8,2,1])+payload).hex()
        assert p["expected_CONTROL_ONLY_hex"]==(bytes32([TAG,4,2,1])+expected).hex()
        assert (p["input_bytes"],p["output_bytes"],p["total_SSBO_bytes"],p["expected_HOST_bytes"])==(48,32,80,32)
        assert (p["work_sources"],p["work_relative_outputs"])==(2,1)
        assert p["retained_CPU_budget"]==rows[2] and p["source_literal_caps"]==[s["literal_cap_rad"] for s in rows[:2]]
        assert p["scene_sha256"]==i["selector"]["original_scene_sha256"] and p["literal_sha256"]==i["selector"]["literal_request_sha256"]
        assert p["shader_sha256"]==SSHA and p["GPU_launch_allowed"]is False and p["execution_status"]=="NOT_EXECUTED"
    assert (good,bad)==(4,53) and set(parent["results"]).issubset(data["results"])
    cs=data["compiles"];assert set(cs)=={"positive","syntax_negative"}
    reflections={}
    for name,c in cs.items():
        assert c["GPU_executed"]is c["GPU_launch_allowed"]is False and c["compiler_sha256"]==DSHA and c["compiler_bytes"]==4478464
        assert (c["target_env"],c["target_version"],c["shader_kind"],c["entry_point"],c["optimization"])==(0,4194304,2,"main",0)
        src=binary(c["source"]);spv=binary(c["spirv"])
        if name=="positive":
            assert src==source and c["status"]==c["errors"]==0 and "inspection_failure"not in c
            reflections[name]=reflect(spv);assert reflections[name]==c["inspection"]
        else:assert src==source+b"\nINVALID_OBLIQUE_TOKEN\n" and c["status"]!=0 and c["errors"]>0 and c["diagnostics"] and spv==b""
    assert data["controls"]==dict(parent_shader_read_rejects=3,before_DLL_load_rejects=2,structural_rejects=4)
    initial=unpack64(r["initial_test_run"])
    assert len(initial["inputs"])==56 and r["independent_pre_commit_FAILURE"]["rc"]==1
    assert 'checked("wrong_model",q,"old")' in r["initial_test_source"]
    assert binary(initial["compiles"]["positive"]["source"])==source
    assert binary(initial["compiles"]["positive"]["spirv"])==binary(cs["positive"]["spirv"])
    assert initial["compiles"]["syntax_negative"]["status"]!=0
    print(json.dumps(dict(status="PASS",pins=100,requests=57,CPU_packets=good,STOP=bad,new_compile_calls=2,
        total_new_compile_calls=4,retained_initial_oracle_FAIL=True,
        new_RN_operations=0,GPU_executed=False,GPU_launch_allowed=False,SPIRV=reflections),sort_keys=True))
if __name__=="__main__":main()
