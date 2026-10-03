"""Own guard tests: integer bits/booleans only; no compiler or float operations."""
from pathlib import Path
import importlib.util,json,struct
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("own_guard",ROOT/"Blender/benchmarks/capacity_audit/oblique_pair64_spirv_guard_HOST_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def mutate(raw,offset,index,value):
    w=list(struct.unpack("<%dI"%(len(raw)//4),raw));w[offset+index]=value;return struct.pack("<%dI"%len(w),*w)
def reference(q):
    if q["gid"]!=[0,0,0] or len(q["input_words"])!=12 or q["output_extent"]!=8:return False
    w=q["input_words"]
    if w[:4]!=[0x4f444631,8,2,1]:return False
    for k in range(4,12,2):
        bits=w[k]|(w[k+1]<<32);isnf=((bits>>52)&2047)==2047
        if isnf and q["pack_policy"]=="UNSPECIFIED_TO_POSITIVE_ZERO":bits=0
        if ((bits>>52)&2047)==2047 or (bits&((1<<63)-1))>0x4270000000000000:return False
    return True
def main():
    raw,shader=m.retained();out=m.audit(model=m.MODEL)
    assert out["status"]=="HOST_AUDIT_COMPLETE_RAW_NONFINITE_GUARD_UNPROVEN",out["reason"]
    assert len(out["results"])==65 and len(out["counterexamples"])==12 and out["promotion"]=="STOP"
    for name,r in out["results"].items():
        q=out["scenarios"][name];reached=reference(q)
        assert (r["status"]=="HOST_PREFIX_REACHED_ARITHMETIC")==reached,name
        assert r["terminal_word_offset"]==(1381 if reached else r["terminal_word_offset"])
        assert not any(k>=4 for k,v in r["output_writes"]) # prefix never writes payload or commit tag
        if name.startswith(("gid_","input_extent_","output_extent_")):
            assert r["input_reads"]==[] and r["output_writes"]==[]
        elif name.startswith("header_"):
            assert all(k<4 for k in r["input_reads"]) and r["packs"]==[]
        else:
            assert r["input_reads"]==list(range(12)) and len(r["packs"])==4
        if r["output_writes"]:assert r["output_writes"]==[[0,0],[1,0],[2,2],[3,0]]
    assert sum(r["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" for r in out["results"].values())==32
    # Retain the same nonfinite bit injection under ideal and permitted-to-zero models.
    for key in out["counterexamples"]:
        ideal=key.replace("_unspecified0","_ideal")
        assert out["scenarios"][key]["input_words"]==out["scenarios"][ideal]["input_words"]
        assert out["results"][ideal]["status"]=="HOST_PREFIX_RETURNED"
        assert out["results"][key]["status"]=="HOST_PREFIX_REACHED_ARITHMETIC"
    with patch.object(m,"retained",side_effect=AssertionError("must not read parent")):
        wrong=m.audit(model="legacy")
    assert wrong["status"]=="STOP" and wrong["reason"]=="explicit_model"
    q=out["scenarios"]["parent_oblique"];negative={}
    variants={
        "truncated":raw[:-4],
        "bad_magic":bytes(4)+raw[4:],
        "bad_branch_target":mutate(raw,574,2,999),
        "unknown_prefix_opcode":mutate(raw,967,0,(4<<16)|999),
    }
    for name,b in variants.items():
        try:m.simulate(b,q)
        except (ValueError,KeyError,TypeError,IndexError) as e:negative[name]=dict(status="STOP",reason=str(e),binary_hex=b.hex(),binary_sha256=m.sha(b))
        else:raise AssertionError("bad binary accepted:"+name)
    for name,value in(("unknown_policy","ACTUAL_GPU"),("bool_policy",True)):
        bad=dict(q,pack_policy=value)
        try:m.simulate(raw,bad)
        except ValueError as e:negative[name]=dict(status="STOP",reason=str(e))
        else:raise AssertionError("bad policy accepted")
    # Mutation proof: bypass final header test; sealed binary admission never accepts this variant.
    bypass=mutate(raw,818,2,119)
    bad=out["scenarios"]["header_3"]
    witness=m.simulate(bypass,bad)
    assert witness["status"]=="HOST_PREFIX_REACHED_ARITHMETIC" and not reference(bad)
    print(json.dumps(dict(status="PASS",test_groups=6,data=dict(result=out,negative=negative,wrong_model=wrong,bypass=dict(binary_hex=bypass.hex(),binary_sha256=m.sha(bypass),scenario=bad,result=witness,sealed_admission_allowed=False))),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
