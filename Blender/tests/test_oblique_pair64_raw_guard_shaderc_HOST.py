"""Own opt-in V2 tests; only this new source compiled; no GPU/old producer replay."""
from pathlib import Path
import importlib.util,json,struct,base64,zlib
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("own_raw_guard",ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_raw_guard_shaderc_HOST_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
    guard,parent,native=m.retained();results={};selectors={}
    for case in m.GOOD:
        q=m.selector(case);r=m.prepare(q,model=m.MODEL);assert r["status"]=="CPU_RAW_GUARD_V2_PACKET_ONLY",r["reason"]
        p=r["packet"];old=parent["results"][case]["packet"]
        assert bytes.fromhex(p["input_hex"])[4:]==bytes.fromhex(old["input_hex"])[4:]
        assert bytes.fromhex(p["expected_CONTROL_ONLY_hex"])[4:]==bytes.fromhex(old["expected_CONTROL_ONLY_hex"])[4:]
        assert p["retained_CPU_budget"]==old["retained_CPU_budget"] and p["source_literal_caps"]==old["source_literal_caps"]
        results[case]=r;selectors[case]=q
    q=selectors["parent_oblique"]
    bads={"extra_cap":dict(q,cap="override"),"extra_launch":dict(q,launch="GPU"),"missing_rep":{k:v for k,v in q.items() if k!="representation"}}
    for key,value in(("case",True),("case","parent_SOURCE0_cap_zero"),("parent_packet_sha256","0"*64),("original_scene_sha256","0"*64),("literal_request_sha256","0"*64),("shader_sha256","0"*64),("representation","old"),("intent","RUN_GPU")):bads["new_bad_"+key+"_"+str(value)]=dict(q,**{key:value})
    for name,bad in bads.items():
        r=m.prepare(bad,model=m.MODEL);assert r["status"]=="STOP" and r["packet"]is None,name
        results[name]=r;selectors[name]=bad
    with patch.object(m,"retained",side_effect=AssertionError("must not read parent")):
        r=m.prepare(q,model="old")
    assert r["status"]=="STOP";results["new_wrong_model"]=r;selectors["new_wrong_model"]=q
    with patch.object(m.C,"CDLL",side_effect=AssertionError("must not load DLL")):
        try:m.compile_source(b"old shader",model=m.MODEL)
        except ValueError as e:before_DLL_source=str(e)
        else:raise AssertionError("unrelated source")
        try:m.compile_source((ROOT/m.SHADER).read_bytes(),model="old")
        except ValueError as e:before_DLL_model=str(e)
        else:raise AssertionError("old compile model")
    # HOST original-bit ingress rejection is independent of post-pack float classification.
    ingress={}
    for name,s in guard["scenarios"].items():
        words=list(s["input_words"])
        if len(words)==12 and words[0]==0x4f444631:words[0]=m.TAG
        try:
            raw=struct.pack("<%dI"%len(words),*words);v=m.validate_raw_packet(raw)
        except ValueError as e:v=dict(status="STOP",reason=str(e))
        ingress[name]=v
    for name in guard["counterexamples"]:assert ingress[name]["status"]=="STOP"
    source=(ROOT/m.SHADER).read_bytes();positive=m.compile_source(source,model=m.MODEL)
    assert positive["status"]==0 and positive["errors"]==0 and "inspection_failure"not in positive,positive
    raw=zlib.decompress(base64.b64decode(positive["spirv"]["zlib_base64"]))
    audit=m.audit_compiled(raw,model=m.MODEL)
    assert len(audit["results"])==65 and len(audit["trace_matches"])==4
    for name,r in audit["results"].items():
        if name.startswith("component_") and any(t in name for t in("_nan_","_inf_","_negative_inf_")):
            assert r["status"]=="HOST_PREFIX_RETURNED" and r["packs"]==[],name
        assert not any(k>=4 for k,v in r["output_writes"])
    assert len(audit["graph"]["nodes"])==26
    negative=m.compile_source(source+b"\nINVALID_RAW_GUARD_TOKEN\n",model=m.MODEL)
    assert negative["status"]!=0 and negative["errors"]>0 and negative["spirv"]["bytes"]==0 and negative["diagnostics"]
    w=list(struct.unpack("<%dI"%(len(raw)//4),raw));changed=False
    for pos,op,a in m.instructions(raw):
        if op==43 and len(a)==3 and a[2]==0x7ff00000:w[pos+3]=0;changed=True;break
    assert changed
    mutated=struct.pack("<%dI"%len(w),*w)
    try:m.audit_compiled(mutated,model=m.MODEL)
    except ValueError as e:mask_failure=str(e)
    else:raise AssertionError("zero exponent mask accepted")
    # Trace all twelve preserved V1 witnesses side by side, never overwrite V1 failures.
    controls=dict(before_DLL_source=before_DLL_source,before_DLL_model=before_DLL_model,mask_mutation=dict(status="STOP",reason=mask_failure,binary_hex=mutated.hex(),binary_sha256=m.sha(mutated)),old_counterexamples=guard["counterexamples"],ingress=ingress)
    assert len(results)==16 and sum(v["status"]=="STOP" for v in results.values())==12
    print(json.dumps(dict(status="PASS",test_groups=6,data=dict(selectors=selectors,results=results,compiles=dict(positive=positive,negative=negative),audit=audit,controls=controls,total_new_compile_calls=2)),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
