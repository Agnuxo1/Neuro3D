"""Own tests: no compiler, old producer imports, geometry or floating arithmetic."""
import importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("own_graph",ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_spirv_graph_HOST_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def mutated(raw,op,predicate,change):
    w=list(struct.unpack("<%dI"%(len(raw)//4),raw));i=5;count=0
    while i<len(w):
        n=w[i]>>16;o=w[i]&65535;a=w[i+1:i+n]
        if o==op and predicate(a):
            change(w,i);count+=1;break
        i+=n
    assert count==1
    return struct.pack("<%dI"%len(w),*w)
def main():
    b,s,n=m.retained();out=m.audit(model=m.MODEL)
    assert out["status"]=="HOST_STATIC_GRAPH_MATCH_ONLY",out["reason"]
    assert len(out["graph"]["nodes"])==26 and len(out["cases"])==4
    assert out["preserved_parent_census"]==dict(shader_requests=57,shader_STOP=53,native_requests=46,native_STOP=42)
    variants={
        "add_to_sub":mutated(b,129,lambda a:True,lambda w,i:w.__setitem__(i,(w[i]&0xffff0000)|131)),
        "remove_NoContraction":mutated(b,71,lambda a:a==[17,42],lambda w,i:w.__setitem__(i+2,0)),
        "source_limb_swap":mutated(b,80,lambda a:a[1]==129,lambda w,i:w.__setitem__(slice(i+3,i+5),[w[i+4],w[i+3]])),
        "source_pair_swap":mutated(b,12,lambda a:a[1]==130,lambda w,i:w.__setitem__(i+5,138)),
        "egress_limb_swap":mutated(b,62,lambda a:a[0]==286,lambda w,i:w.__setitem__(i+2,288)),
        "unknown_used_operation":mutated(b,129,lambda a:a[1]==17,lambda w,i:w.__setitem__(i,(w[i]&0xffff0000)|133)),
        "float32":mutated(b,22,lambda a:a[0]==6,lambda w,i:w.__setitem__(i+2,32)),
        "wrong_ext_set":mutated(b,12,lambda a:a[1]==130,lambda w,i:w.__setitem__(i+3,999)),
        "truncated":b[:-4],
        "bad_magic":bytes(4)+b[4:],
    }
    negatives={}
    for name,v in variants.items():
        try:m.extract(v)
        except (ValueError,KeyError,TypeError,IndexError) as e:
            negatives[name]=dict(status="STOP",reason=str(e),binary_hex=v.hex(),binary_sha256=m.sha(v))
        else:raise AssertionError("mutation unexpectedly accepted:"+name)
    wrong=m.audit(model="old");assert wrong["status"]=="STOP" and wrong["graph"]is None and wrong["cases"]=={}
    fault=json.loads(json.dumps(n["results"]["parent_oblique"]));fault["trace"]["nodes"][0]["a"]="00"*8
    try:m.compare_trace(out["graph"],fault)
    except ValueError as e:negatives["captured_operand_fault"]=dict(status="STOP",reason=str(e))
    else:raise AssertionError("trace fault accepted")
    print(json.dumps(dict(status="PASS",tests=5,data=dict(result=out,negatives=negatives,wrong_model=wrong)),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
