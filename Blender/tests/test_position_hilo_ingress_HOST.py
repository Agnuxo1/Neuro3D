"""Frozen capture reuse; receiver controls without any encoder or geometry replay."""
import base64,inspect,json,sys,struct
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_hilo_ingress_HOST_v1 as m

def main():
    e,pins=m.retained();runs=[]
    def run(label,q,raw,expected,model=m.MODEL,reason=None):
        r=m._receive(model,q,raw,e);assert r["status"]==expected,(label,r)
        if reason is not None:assert r["reason"]==reason,(label,r)
        if expected=="STOP":
            assert r["rows"]==[]and r["received_geometry"]is None and r["radii_BU"]is None and not r["frame_verified"]
            assert all(v==0 for v in r["HOST_cost"].values()),(label,r)
        assert all(r[k]is False for k in("GPU_launch_allowed","GPU_executed","scene_authenticated","uncertainty_authenticated",
            "full_visibility_certified","phase_certified","physical_field_certified","object_wide_skip","previous_zero_exemption"))
        assert r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"and r["epsilon_BU"]==[0,1]
        runs.append(dict(id=label,model=model,request=q,frame_base64=base64.b64encode(raw).decode()if type(raw)is bytes else None,
            frame_kind=type(raw).__name__,result=r))
        return r
    for record,x in e.items():
        q=m.selector(record,e);blocked=x["result"]["status"]=="STOP";raw=None if blocked else m.frame(record,e)
        run("retained:"+record,q,raw,"STOP"if blocked else "HOST_POSITION_FRAME_MATCH_UNATTESTED",
            reason="parent_STOP_not_rescued"if blocked else None)
    record="HOST_HILO32:synthetic:xy:0:outside_2m60";q=m.selector(record,e);raw=m.frame(record,e)
    for key in q:
        bad=dict(q);bad[key]="wrong";run("selector:"+key,bad,raw,"STOP")
    for label,bad in(("extra",dict(q,extra="x")),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool_mode",dict(q,mode=True))):
        run("selector:"+label,bad,raw,"STOP")
    run("wrong_model",q,raw,"STOP",model="GPU",reason="explicit_model")
    for label,b in(("missing",None),("bytearray",bytearray(raw)),("truncated",raw[:-1]),("trailing",raw+b"\x00"),("raw_legacy",raw[m.HEADER_BYTES:])):
        run("extent:"+label,q,b,"STOP",reason="strict_frame_type_extent")
    for i in(0,8,12,16,48,80):
        b=bytearray(raw);b[i]^=1;run("header:"+str(i),q,bytes(b),"STOP",reason="explicit_header_original_record_mode")
    for i in range(30):
        b=bytearray(raw);b[m.HEADER_BYTES+4*i]^=1
        run("word:"+str(i),q,bytes(b),"STOP")
    for name,w in(("inf",0x7f800000),("ninf",0xff800000),("qnan",0x7fc00000),("snan",0x7f800001),("subnormal",1)):
        b=bytearray(raw);struct.pack_into("<I",b,m.HEADER_BYTES,w)
        run("nonfinite:"+name,q,bytes(b),"STOP",reason="all_normal_or_zero_words")
    words=list(struct.unpack("<30I",raw[m.HEADER_BYTES:]))
    hi_only=raw[:m.HEADER_BYTES]+struct.pack("<15I",*words[::2])
    run("dropped_lows",q,hi_only,"STOP",reason="strict_frame_type_extent")
    swapped=[v for i in range(0,30,2)for v in(words[i+1],words[i])]
    run("swapped_limbs",q,raw[:m.HEADER_BYTES]+struct.pack("<30I",*swapped),"STOP",reason="sealed_payload_bytes")
    signed=words.copy();zero=next(i for i,w in enumerate(words)if w==0);signed[zero]=0x80000000
    run("equal_value_wrong_signed_zero",q,raw[:m.HEADER_BYTES]+struct.pack("<30I",*signed),"STOP",reason="sealed_payload_bytes")
    other=next(k for k,x in e.items()if x["result"]["status"]!="STOP"and x["request"]["case"].startswith("sealed:")==False and
        x["result"]["rows"][0]["original_geometry"]["context"]!=e[record]["result"]["rows"][0]["original_geometry"]["context"])
    otherraw=m.frame(other,e);assert otherraw[:m.HEADER_BYTES]!=raw[:m.HEADER_BYTES]
    run("cross_context_whole_frame",q,otherraw,"STOP")
    # Same header with another valid payload: identity, not just finite-value tests.
    other=next(k for k in e if k.startswith("HOST_HILO32:")and e[k]["result"]["status"]!="STOP"and m.frame(k,e)[m.HEADER_BYTES:]!=raw[m.HEADER_BYTES:])
    run("cross_valid_payload",q,raw[:m.HEADER_BYTES]+m.frame(other,e)[m.HEADER_BYTES:],"STOP",reason="sealed_payload_bytes")
    blocked=next(k for k,x in e.items()if x["result"].get("reason")=="encoding_exhausts_separator")
    z=e[blocked]["result"]["diagnostics"][0]["packet_words"];bq=m.selector(blocked,e)
    attempted=m.header(bq)+struct.pack("<15I",*z)
    run("blocked_diagnostic_not_admitted",bq,attempted,"STOP",reason="parent_STOP_not_rescued")
    public=m.receive(m.MODEL,q,raw);assert public==next(x["result"]for x in runs if x["id"]=="retained:"+record)
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.receive(m.MODEL,q,raw);m.retained=saved
    assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"and missing["rows"]==[]
    assert list(inspect.signature(m.receive).parameters)==["model","request","raw_frame"]
    totals={k:sum(x["result"]["HOST_cost"][k]for x in runs)for k in public["HOST_cost"]}
    assert totals==dict(exact_word_decodes=2880,exact_reconstructions=1080,original_error_differences=1800,frame_matches=120,certificate_reuses=120)
    assert len(runs)==222 and sum(x["result"]["status"]!="STOP"for x in runs)==120
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,public=public,missing=missing,main_cost=totals,
        pins=len(pins),census=dict(main=len(runs),HOST_match=120,STOP=len(runs)-120,parent_STOP=40,mutation_STOP=len(runs)-160),
        GPU_executed=False,compiler_calls=0,producer_replays=0)),sort_keys=True))
if __name__=="__main__":main()
