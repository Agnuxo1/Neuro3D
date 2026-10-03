"""Contract tests over sealed CPU words; no native phase/geometry/compiler replay."""
from pathlib import Path
import copy,importlib.util,json,struct
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location("egress",ROOT/"Blender/benchmarks/capacity_audit/oblique_total_phase_pair64_egress_HOST_v1.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
    e=m.load_evidence();runs=[];exports=[]
    def run(label,case,raw,reason=None,request=None,model=m.MODEL,origin=m.ORIGIN):
        assert label not in {r["id"]for r in runs}
        req=m.selector(case,e)if request is None else request
        r=m.compare(model,req,raw,origin)
        assert r["reason"]==reason,(label,r["reason"],reason)
        assert r["status"]==("STOP"if reason else "HOST_CPU_TOTAL_PHASE_UNATTESTED_MATCH")
        assert r["rows"]==([]if reason else r["diagnostics"])
        runs.append(dict(id=label,case=case,request=req,model=model,origin=origin,
            raw_type=type(raw).__name__,raw_hex=raw.hex()if type(raw)is bytes else None,result=r))
    valid=[]
    for c,a in e.items():
        r=a["native_result"];ok=r["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY"
        raw=m._packet(a)if ok else b""
        run("sealed_"+c,c,raw,None if ok else "parent_STOP:"+str(r["reason"]))
        exports.append(dict(case=c,request=m.selector(c,e),result=m.export(m.MODEL,m.selector(c,e))))
        assert exports[-1]["result"]==runs[-1]["result"]
        if ok:valid.append(c)
    assert len(e)==46 and len(valid)==11
    c="parent_oblique";raw=m._packet(e[c]);base=m.selector(c,e)
    run("wrong_model",c,raw,"model",model="V2_PROPAGATION_ONLY")
    for origin in("GPU_READBACK","GPU_ATTESTED","CPU_AUTHENTICATED"):
        run("origin_"+origin,c,raw,"unattested_origin_only",origin=origin)
    for key in("native_request_sha256","phase_request_sha256","original_scene_sha256","literal_request_sha256","abi_tag","intent"):
        req=copy.deepcopy(base);req[key]="wrong";run("bad_"+key,c,raw,"selector_identity",request=req)
    req=copy.deepcopy(base);req["abi_tag"]=True;run("boolean_tag",c,raw,"selector_identity",request=req)
    req=copy.deepcopy(base);req["case"]="unknown";run("unknown_case",c,raw,"case",request=req)
    req=copy.deepcopy(base);req["launch_GPU"]=True;run("extra_launch",c,raw,"closed_selector",request=req)
    req=copy.deepcopy(base);del req["intent"];run("missing_intent",c,raw,"closed_selector",request=req)
    run("raw_string",c,"bad","raw_type")
    for label,cut in(("short",raw[:-1]),("long",raw+b"\0"),("V2_extent",raw[:32]),("header_only",raw[:16])):
        run(label,c,cut,"output_extent")
    for j,changed in enumerate((0x4f444632,4,1,0)):
        b=bytearray(raw);b[4*j:4*j+4]=struct.pack("<I",changed);run("header_"+str(j),c,bytes(b),"CPU_total_phase_header")
    for j in range(6):
        for word in(0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001,0xfff0000000000001):
            b=bytearray(raw);b[16+8*j:24+8*j]=word.to_bytes(8,"little")
            run("nonfinite_"+str(j)+"_"+hex(word),c,bytes(b),"raw_nonfinite")
    for j in range(2):
        b=bytearray(raw);b[16+16*j:32+16*j]=bytes(16)
        run("SOURCE_zero_"+str(j),c,bytes(b),"ALL_SOURCE_egress_cap")
        b=bytearray(raw);b[24+16*j:32+16*j]=bytes(8)
        run("SOURCE_hi_only_"+str(j),c,bytes(b),"ALL_SOURCE_egress_cap")
    b=bytearray(raw);b[48:64]=bytes(16);run("relative_zero",c,bytes(b),"relative_egress_cap")
    for j in range(3):
        b=bytearray(raw);b[24+16*j]^=1;run("within_cap_low_bit_"+str(j),c,bytes(b),"native_total_phase_bits")
        assert all(v["fits"]for v in runs[-1]["result"]["diagnostics"])
    b=bytearray(raw);b[16:32],b[32:48]=raw[32:48],raw[16:32]
    run("SOURCE_reordered",c,bytes(b),"ALL_SOURCE_egress_cap")
    packets={}
    for name in valid:packets.setdefault(m._packet(e[name]).hex(),[]).append(name)
    duplicates=[v for v in packets.values()if len(v)>1]
    assert duplicates,"retained_equal_bytes_control"
    witness=duplicates[0][1];run("copied_matching_bytes_NOT_provenance",witness,m._packet(e[duplicates[0][0]]))
    req=m.selector(c,e);req["case"]=witness;run("foreign_selector_not_rebound",witness,raw,"selector_identity",request=req)
    assert len({r["id"]for r in runs})==len(runs)
    print(json.dumps(dict(status="PASS",groups=6,data=dict(evidence=e,runs=runs,exports=exports,
        duplicate_byte_classes=duplicates,producer_replays=0,RN64_operations=0,compiler_calls=0)),sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
