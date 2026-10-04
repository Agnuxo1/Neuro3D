"""Retained HOST bytes as data only; no trace/encoder/native imports."""
from pathlib import Path
import sys,json,copy,struct
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks/capacity_audit"))
import oblique_trace_output_ABI_partition_HOST_v1 as m

def safe(r):
    assert all(r[k]is False for k in m.FALSE) and r["phase_error_bound"]is None
    assert r["old_numeric_replays"]==r["new_intersections"]==r["new_root_calls"]==r["new_phase_operations"]==0

def reseal(p):
    b=bytes.fromhex(p["buffer_hex"]);p["manifest"]["buffer_sha256"]=m.sha(b)
    p["manifest"]["buffer_bytes"]=len(b);p["manifest_sha256"]=m.digest(p["manifest"])

def main():
    originals,pins=m.load_context();ev=dict(positive=[],negative=[],partition_negative=[],public=[],JSON_negative=[])
    for case,original in sorted(originals.items()):
        p=original["packet"];r=m.validate(case,p,m.PARTITION,original);safe(r)
        assert r["layout_verified"] and r["new_word_classifications"]==84
        assert r["retained_contact_status"]=="STOP_NONEXACT_TRACE_OUTPUT"
        seg=r["SOURCE_partitions"];b=bytes.fromhex(p["buffer_hex"])
        assert bytes.fromhex(r["header_hex"]+seg[0]["raw_hex"]+seg[1]["raw_hex"])==b
        assert seg[0]["offset_bytes"]==32 and seg[1]["offset_bytes"]==200
        assert all(v["length_bytes"]==168 and len(v["fields"])==21 for v in seg)
        ev["positive"].append(dict(case=case,result=r))
    case="oblique";orig=originals[case];ref=orig["packet"]
    edits=[
        ("SOURCE_reverse",lambda p:p["manifest"].update(source_ids=["S1","S0"])),
        ("query",lambda p:p["manifest"].update(query_sha256="0"*64)),
        ("scene",lambda p:p["manifest"].update(scene_sha256="0"*64)),
        ("input_hash",lambda p:p["manifest"].update(input_buffer_sha256="0"*64)),
        ("radii_forged",lambda p:next(v for v in p["manifest"]["fields"]if v["radius"]!=[0,1]).update(radius=[0,1])),
        ("fields_reverse",lambda p:p["manifest"]["fields"].reverse()),
        ("word_bool",lambda p:p["manifest"]["fields"][0]["word_pair"].__setitem__(0,True)),
        ("header_bool",lambda p:p["manifest"].update(header_bytes=True)),
        ("source_count_float",lambda p:p["manifest"].update(source_field_count=21.0)),
        ("contact_forged",lambda p:p["manifest"].update(exact_contact_allowed=True)),
        ("SOURCE_path",lambda p:p["manifest"]["fields"][0].update(path="S1/false")),
        ("extra_key",lambda p:p.update(phase_error_bound=0))]
    for label,fn in edits:
        p=copy.deepcopy(ref);fn(p);reseal(p);assert m.digest(p)!=m.digest(ref)
        r=m.validate(case,p,m.PARTITION,orig);safe(r);assert not r["layout_verified"],label
        ev["negative"].append(dict(id=label,result=r))
    loindex=next(i for i,f in enumerate(ref["manifest"]["fields"])if f["word_pair"][1]!=0)
    for label,offset,value in (("NaN",32,0x7fc00000),("Inf",32,0x7f800000),
        ("subnormal",32,1),("negative_zero",32,0x80000000),("header_reserved",28,1),
        ("drop_lo",32+8*loindex+4,0)):
        p=copy.deepcopy(ref);b=bytearray.fromhex(p["buffer_hex"]);struct.pack_into("<I",b,offset,value);p["buffer_hex"]=b.hex()
        if offset>=32:
            i=(offset-32)//8;word=((offset-32)%8)//4;p["manifest"]["fields"][i]["word_pair"][word]=value
        reseal(p);assert p!=ref
        r=m.validate(case,p,m.PARTITION,orig);safe(r);assert not r["layout_verified"],label
        ev["negative"].append(dict(id=label,result=r))
    for label,transform in (("truncated",lambda b:b[:-4]),("extra",lambda b:b+b"\0"*4),
        ("SOURCE_raw_swap",lambda b:b[:32]+b[200:]+b[32:200])):
        p=copy.deepcopy(ref);p["buffer_hex"]=transform(bytes.fromhex(p["buffer_hex"])).hex();reseal(p)
        r=m.validate(case,p,m.PARTITION,orig);safe(r);assert not r["layout_verified"],label
        ev["negative"].append(dict(id=label,result=r))
    for label,parts in (("naive_half184",[
        dict(m.PARTITION[0],offset_bytes=0,length_bytes=184),dict(m.PARTITION[1],offset_bytes=184,length_bytes=184)]),
        ("SOURCE_reverse",list(reversed(m.PARTITION))),("offset_bool",[dict(m.PARTITION[0],offset_bytes=True),m.PARTITION[1]])):
        r=m.validate(case,ref,parts,orig);safe(r);assert not r["layout_verified"]
        ev["partition_negative"].append(dict(id=label,result=r))
    for label,c,p in (("original",case,ref),("other_case",next(k for k in originals if k!=case),ref),("bool_case",True,ref)):
        r=m.inspect(c,p);safe(r);assert r["layout_verified"]is (label=="original")
        r.pop("dependency_pins",None);ev["public"].append(dict(id=label,result=r))
    for label,raw in (("duplicate",b'{"x":1,"x":2}'),("Inf",b'{"x":Infinity}'),("overflow",b'{"x":1e309}')):
        try:m.parse(raw)
        except ValueError as ex:reason=str(ex)
        else:raise AssertionError(label)
        ev["JSON_negative"].append(dict(id=label,reason=reason))
    print(json.dumps(dict(status="PASS",pins=pins,evidence=ev,summary=dict(
        original_cases=6,SOURCE_partitions=12,header_bytes=32,SOURCE_bytes=168,
        output_bytes_each=368,fields=252,original_word_classifications=504,
        negative_packets=len(ev["negative"]),negative_partitions=3,public_checks=3,JSON_STOPS=3,
        source_fields_inferred=0,exact_contact_admitted=0,old_numeric_replays=0,GPU_used=False,
        phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO")),sort_keys=True,allow_nan=False))

if __name__=="__main__":main()
