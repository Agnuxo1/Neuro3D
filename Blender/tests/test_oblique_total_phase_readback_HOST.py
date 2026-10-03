"""Focused readback controls; no shader/geometry/RN/compiler execution."""
import base64,copy,inspect,json,struct,sys,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_total_phase_readback_HOST_v1 as m
def word(raw,i,bits):
    out=bytearray(raw);out[16+8*i:24+8*i]=bits.to_bytes(8,"little");return bytes(out)
def main():
    e,pins=m.retained();runs=[];control={}
    def check(name,case,inp,out,request=None,model=None,origin=None):
        q=m.selector(case,e)if request is None else request
        r=m._compare(m.MODEL if model is None else model,q,inp,out,m.ORIGIN if origin is None else origin,e)
        runs.append(dict(id=name,case=case,request=q,model=m.MODEL if model is None else model,
            origin=m.ORIGIN if origin is None else origin,input_hex=inp.hex()if type(inp)is bytes else None,
            output_hex=out.hex()if type(out)is bytes else None,input_type=type(inp).__name__,output_type=type(out).__name__,result=r))
        return r
    for case,a in e.items():
        r=check("sealed:"+case,case,a["input"],a["output"])
        if a["input"]is None:
            assert r["status"]=="STOP" and r["reason"].startswith("parent_STOP:") and r["decoded_components"]==0
        else:
            assert r["status"]=="HOST_UNATTESTED_TOTAL_PHASE_MATCH" and r["verified_rows"]==3
            control[case]=r
    case="parent_oblique";inp=e[case]["input"];out=e[case]["output"]
    original=m.number;calls=[]
    def spy(b):calls.append(b.hex());return original(b)
    m.number=spy
    for i in range(6):
        for label,bits in (("inf",0x7ff0000000000000),("ninf",0xfff0000000000000),("qnan",0x7ff8000000000001),("snan",0x7ff0000000000001)):
            calls.clear();r=check("output_nonfinite:"+str(i)+":"+label,case,inp,word(out,i,bits))
            assert r["reason"]=="raw_nonfinite_6" and r["decoded_components"]==0 and calls==[]
    for i in range(10):
        calls.clear();r=check("input_nonfinite:"+str(i),case,word(inp,i,0x7ff8000000000001),out)
        assert r["reason"]=="raw_nonfinite_10" and r["decoded_components"]==0 and calls==[]
    m.number=original
    for side in("input","output"):
        r=check("domain:"+side,case,word(inp,0,0x4270000000000001)if side=="input"else inp,
            word(out,0,0x4270000000000001)if side=="output"else out)
        assert r["reason"]=="raw_domain_"+("10"if side=="input"else "6") and r["decoded_components"]==0
    for side in("input","output"):
        packet=inp if side=="input"else out
        for i in range(4):
            w=list(struct.unpack("<4I",packet[:16]));w[i]^=1;bad=struct.pack("<4I",*w)+packet[16:]
            r=check("header:"+side+":"+str(i),case,bad if side=="input"else inp,bad if side=="output"else out)
            assert r["status"]=="STOP" and r["decoded_components"]==0
        for tag in(0x43545031,0x4f444632):
            bad=struct.pack("<I",tag)+packet[4:]
            r=check("legacy_TAG:"+side+":"+hex(tag),case,bad if side=="input"else inp,bad if side=="output"else out)
            assert r["status"]=="STOP"
        for label,bad in(("short",packet[:-1]),("long",packet+b"\x00"),("empty",b"")):
            r=check("extent:"+side+":"+label,case,bad if side=="input"else inp,bad if side=="output"else out)
            assert r["status"]=="STOP" and r["decoded_components"]==0
    for c in control:
        ii=e[c]["input"];oo=e[c]["output"]
        for j in(1,3,5):
            bits=int.from_bytes(oo[16+8*j:24+8*j],"little");r=check("within_cap_wrong_bits:"+c+":"+str(j),c,ii,word(oo,j,bits+1))
            assert len(r["diagnostics"])==3 and all(v["fits"]for v in r["diagnostics"])
            assert r["reason"]=="native_TOTAL_phase_bits" and r["rows"]==[] and r["verified_rows"]==0
    for i in(0,2,4):
        bits=int.from_bytes(out[16+8*i:24+8*i],"little")
        r=check("over_cap:"+str(i),case,inp,word(out,i,bits+1))
        assert r["reason"]==("relative_readback_cap"if i==4 else "ALL_SOURCE_readback_cap")
    bits=[int.from_bytes(out[16+8*i:24+8*i],"little")for i in(0,2)];ex=[(b>>52)&2047 for b in bits];maximum=max(ex)
    bad=out
    for i,b,x in zip((0,2),bits,ex):bad=word(bad,i,b+(1<<(maximum-x)))
    r=check("same_delta_both_SOURCE_relative_value_unchanged",case,inp,bad)
    assert r["reason"]=="ALL_SOURCE_readback_cap" and not all(v["fits"]for v in r["diagnostics"][:2])
    before=[original(out[16+8*i:24+8*i])+original(out[24+8*i:32+8*i])for i in(0,2)]
    after=[original(bad[16+8*i:24+8*i])+original(bad[24+8*i:32+8*i])for i in(0,2)]
    assert after[0]-before[0]==after[1]-before[1]!=0 and after[0]-after[1]==before[0]-before[1]
    r=check("stale_finite_input",case,word(inp,0,int.from_bytes(inp[16:24],"little")+1),out)
    assert r["reason"]=="sealed_input_bits_before_decode" and r["decoded_components"]==0
    for field in m.selector(case,e):
        q=copy.deepcopy(m.selector(case,e));q[field]="wrong"
        r=check("selector:"+field,case,inp,out,request=q);assert r["reason"]in("closed_case","closed_selector_identity")
    q=dict(m.selector(case,e),extra=True);r=check("selector:extra",case,inp,out,request=q);assert r["reason"]=="closed_selector_identity"
    for label,badin,badout in(("input_bytearray",bytearray(inp),out),("output_bytearray",inp,bytearray(out)),("output_none",inp,None)):
        r=check("type:"+label,case,badin,badout);assert r["status"]=="STOP" and r["decoded_components"]==0
    for label,kwargs in(("wrong_model",dict(model="GPU")),("device_origin_claim",dict(origin="GPU_NATIVE_READBACK"))):
        r=check(label,case,inp,out,**kwargs);assert r["status"]=="STOP" and r["decoded_components"]==0
    assert list(inspect.signature(m.compare).parameters)==["model","request","input_bytes","output_bytes","origin"]
    for x in runs:
        r=x["result"]
        assert not any(r[k]for k in("GPU_launch_allowed","GPU_executed","GPU_guard_certified","device_egress_authenticated",
            "fence_readback_authenticated","scene_authenticated","material_authenticated","native_promotion_allowed","physical_field_certified"))
        assert (r["RN64_operations"],r["producer_replays"],r["compiler_calls"])==(0,0,0)
        if r["status"]=="STOP":assert r["rows"]==[] and r["verified_rows"]==0 and r["output_sha256"]is None
    print(json.dumps(dict(status="PASS",test_groups=4,data=dict(runs=runs,sealed_matches=len(control),parent_STOP=35,
        raw_output_nonfinite_STOP=24,raw_input_nonfinite_STOP=10,within_cap_wrong_bits_STOP=33,ALL_SOURCE_translation_STOP=1,
        compiler_calls=0,RN64_operations=0,producer_replays=0,GPU_executed=False,GPU_launch_allowed=False)),sort_keys=True))
if __name__=="__main__":main()
