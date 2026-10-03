"""Seal/byte/interval oracle only; upstream graphs not replayed; helper not a scene."""
from fractions import Fraction as F
from pathlib import Path
import json,hashlib,copy,runpy,base64,zlib
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-CPU-001-CODEX.json"
PSHA="813fd728006a90adb40f99d1eb49aa3523f8f63bf61edca7775e332dc57106ea"
MODEL="oblique-pair64-interval-consumer-CPU-v1"
POLICY="EXACT_BOTH_LIMBS_THEN_OUTWARD_BOX_CAST_KEEP_ALL_RADII"
POINTS=("origin","detector","A","B","C")
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def pair(x):return [x.numerator,x.denominator]
def capture(c):
    assert c["rc"]==0 and c["timed_out"]is False
    zz=zlib.decompressobj();raw=zz.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),2*1024*1024+1)
    assert zz.eof and not zz.unused_data and not zz.unconsumed_tail
    assert len(raw)==c["stdout_bytes"]<=2*1024*1024 and hashlib.sha256(raw).hexdigest()==c["stdout_sha256"]
    return json.loads(raw)
def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==84149 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);d=capture(r["test_run"])["evidence"]
    assert capture(r["independent_pre"])["status"]=="PASS"
    e={"scene:"+x["name"]:x for x in d["records"]};e["native_inexact"]=d["inexact"]
    e.update({"input:"+x["name"]:x for x in d["invalid"]});assert len(e)==16
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return r,e,pins,d
def selector(record,e):
    x=e[record];frame=x["result"]["frame"];text=frame["output_packet_hex"] if frame else ""
    query=x.get("scene_query",x["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,parent_receipt_sha256=PSHA,record_id=record,
        parent_record_sha256=digest(x),original_snapshot_sha256=digest(x["scene"]),
        original_query_sha256=digest(query),input_request_sha256=digest(x["request"]),
        output_packet_hex=text,output_packet_sha256=hashlib.sha256(bytes.fromhex(text)).hexdigest())
def scope(r):
    assert r["backend"]==MODEL and r["new_transport_graph_calls"]==r["retained_suite_replays"]==0
    for k in ("scalar_RN_limb_collapse","physical_visibility_certified","phase_certified","scene_authenticated","GPU_used","source_uncertainty_cancelled"):assert r[k]is False
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO" and r["promotion"]=="STOP_PHYSICAL_GPU"
    assert r["decode_scope"]=="HOST_EXACT_WORD_DECODE_PLUS_NATIVE_CPU64_INTERVALS"
def verify_capture(data):
    receipt,e,pins,parent_data=retained()
    assert data["pins"]==pins
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    # Pure upstream oracle rechecks sealed graph/capture; no native producer.
    upstream=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_scene_pair64_recenter_CPU64.py"))
    assert upstream["verify_capture"](parent_data)["status"]=="PASS"
    native=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_finite_interval_CPU64.py"))
    exact=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_finite_interval_HOST.py"))
    frac=native["fraction"];counts={};calls=0
    assert len(data["records"])==16 and {x["id"]for x in data["records"]}==set(e)
    for row in data["records"]:
        x=e[row["id"]];q=selector(row["id"],e);r=row["result"];scope(r)
        assert row["request"]==q and row["parent_record_sha256"]==digest(x)
        assert r["parent_record_sha256"]==digest(x) and r["parent_receipt_sha256"]==PSHA
        assert r["original_snapshot_sha256"]==digest(x["scene"]) and r["request_sha256"]==digest(q)
        assert r["upstream_status"]==x["result"]["status"] and r["upstream_reason"]==x["result"]["reason"]
        if x["result"]["status"]!="CPU_NATIVE_PAIR64_RECENTER_ONLY":
            assert r["status"]=="STOP_UPSTREAM" and r["reason"]=="sealed_upstream_STOP_not_rescued"
            assert r["frame"]is None and r["native_result"]is None and r["predicate_calls"]==0
            assert r["packet_bytes"]==r["word_decodes"]==r["exact_pair_decodes"]==0
            continue
        assert r["reason"]=="sealed_native_packet_outward_predicate"
        assert r["predicate_calls"]==1 and r["packet_bytes"]==240 and r["word_decodes"]==30 and r["exact_pair_decodes"]==15
        frame=r["frame"];old=x["result"]["frame"];s=frame["scene"]
        assert s==old["scene"] and frame["scene_query"]==old["scene_query"]
        assert frame["snapshot_sha256"]==digest(s)==old["snapshot_sha256"] and frame["reference"]==old["reference"]
        text=q["output_packet_hex"];expected=[]
        for i in range(15):
            n,j=POINTS[i//3],i%3;hw=text[32*i:32*i+16];lw=text[32*i+16:32*i+32]
            v=frac(hw)+frac(lw);rad=x["scene"]["points"][n]["radius"][j]
            assert v==F(*s["points"][n]["nominal"][j])==F(*x["scene"]["points"][n]["nominal"][j])-F(*x["scene"]["points"]["origin"]["nominal"][j])
            assert rad==s["points"][n]["radius"][j]
            expected.append(dict(point=n,axis=j,hi_word=hw,lo_word=lw,decoded=pair(v),radius=rad))
        assert frame["decode_ledger"]==expected
        nq=dict(backend="oblique-finite-interval-CPU64-v1",scene_query=old["scene_query"],snapshot_sha256=digest(s))
        assert frame["native_request"]==nq
        trace=exact["oracle_trace"](s);original=exact["oracle_trace"](x["scene"])
        assert trace==original # common constant geometry, never optical/phase cancellation
        parent=dict(scene=s,query=old["scene_query"],result=dict(trace={k:[pair(v)for v in iv]for k,iv in trace.items()},status="TEST_ORACLE_ONLY_NOT_PARENT_PRODUCER"))
        status,neighbors=native["verify_record"](dict(scene=s,request=nq,parent=parent,result=r["native_result"]))
        assert r["status"]==status;calls+=neighbors;counts[status]=counts.get(status,0)+1
    assert counts=={"CPU64_DECLARED_BOX_INTERIOR_CROSS":1,"CPU64_DECLARED_BOX_DISJOINT":2,"STOP_UNRESOLVED":3}
    assert len(data["invalid"])==8
    base=next(k for k in e if k.startswith("scene:"));q0=selector(base,e)
    names=("backend","policy","parent_receipt_sha256","original_snapshot_sha256","input_request_sha256","output_packet_sha256","output_packet_hex","extra_radius")
    assert tuple(x["id"]for x in data["invalid"])==names
    for item in data["invalid"]:
        q=copy.deepcopy(q0)
        if item["id"]=="extra_radius":q["radius_override"]="0"
        elif item["id"]=="output_packet_hex":q["output_packet_hex"]="0"*480
        else:q[item["id"]]="wrong"
        assert item["request"]==q
        r=item["result"];scope(r)
        assert r["status"]=="STOP_INPUT" and r["reason"]=="closed_selector"
        assert r["native_result"]is None and r["frame"]is None and r["predicate_calls"]==0 and r["word_decodes"]==0
    assert len(data["helpers"])==3
    helper_calls=0
    for h,sign in zip(data["helpers"],(1,-1,0)):
        assert h["label"]=="NEW_BYTE_CONTROL_NOT_SCENE_NOT_NATIVE_GRAPH"
        words=({"hi":"000000000000f03f","lo":"000000000000303c"} if sign==1 else
            {"hi":"000000000000f0bf","lo":"00000000000030bc"} if sign==-1 else
            {"hi":"000000000000f03f","lo":"0"*16})
        assert h["words"]==words
        value=frac(words["hi"])+frac(words["lo"]);rad=F(1,2**66) if sign else F(0)
        assert h["decoded"]==pair(value) and h["radius"]==pair(rad) and h["hi_only_loss"]==pair(abs(value-frac(words["hi"])))
        if sign:assert F(*h["hi_only_loss"])==F(1,2**60)
        assert len(h["ledger"])==2
        for node,direction,t in zip(h["ledger"],("lo","hi"),(value-rad,value+rad)):
            assert node["op"]=="cast" and node["operands"]==[] and node["exact"]==pair(t) and node["direction"]==direction
            v,n=native["verify_round"](node);helper_calls+=n
            assert v<=t if direction=="lo" else v>=t
        assert h["interval_words"]==[v["output_word"]for v in h["ledger"]]
        if sign:assert frac(h["interval_words"][0])<frac(h["interval_words"][1]) # error charged, not high-only exact
        assert h["costs"]==dict(native_arithmetic=0,endpoint_casts=2,nextafter_calls=sum(2*(F(*n["exact"])!=0)+int(n["nextafter"])for n in h["ledger"]),
            sign_flips=0,exact_audit_fraction_operations="UNMEASURED_NOT_ZERO",total_cost="UNKNOWN_NOT_ZERO")
    return dict(status="PASS",counts=counts,upstream_STOP=10,selector_STOP=8,packet_bytes=1440,
        word_decodes=180,exact_pair_decodes=90,predicate_calls=6,new_transport_graph_calls=0,
        predicate_native_arithmetic=924,predicate_endpoint_casts=180,predicate_proof_records=1680,
        predicate_nextafter_calls=calls,helper_casts=6,helper_nextafter_calls=helper_calls,pins=len(pins),
        GPU_calls=0,retained_suite_replays=0,full_costs="UNKNOWN_NOT_ZERO")
def run():
    import sys
    sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
    import oblique_pair64_interval_consumer_CPU_v1 as m
    receipt,e,pins,parent_data=retained()
    actual,actual_pins=m.retained();assert actual==e and actual_pins==pins
    rows=[]
    for key,x in e.items():
        q=m.selector(key,e)
        rows.append(dict(id=key,request=q,parent_record_sha256=digest(x),result=m._consume(q,e)))
    base=next(k for k in e if k.startswith("scene:"));q0=m.selector(base,e);invalid=[]
    for key in ("backend","policy","parent_receipt_sha256","original_snapshot_sha256","input_request_sha256","output_packet_sha256","output_packet_hex","extra_radius"):
        q=copy.deepcopy(q0)
        if key=="extra_radius":q["radius_override"]="0"
        elif key=="output_packet_hex":q["output_packet_hex"]="0"*480
        else:q[key]="wrong"
        invalid.append(dict(id=key,request=q,result=m._consume(q,e)))
    helpers=[]
    for sign in (1,-1,0):
        words=({"hi":"000000000000f03f","lo":"000000000000303c"} if sign==1 else
            {"hi":"000000000000f0bf","lo":"00000000000030bc"} if sign==-1 else
            {"hi":"000000000000f03f","lo":"0"*16})
        x=m.decode_pair(words["hi"],words["lo"]);rad=F(1,2**66) if sign else F(0)
        a=m.cpu.Outward();interval=[a.cast(x-rad,"lo"),a.cast(x+rad,"hi")]
        helpers.append(dict(label="NEW_BYTE_CONTROL_NOT_SCENE_NOT_NATIVE_GRAPH",words=words,decoded=pair(x),
            radius=pair(rad),hi_only_loss=pair(abs(x-m.decode_word(words["hi"]))),
            interval_words=list(map(m.cpu.word,interval)),ledger=a.ledger,costs=a.costs()))
    data=dict(records=rows,invalid=invalid,helpers=helpers,pins=pins)
    summary=verify_capture(data);mutations=[]
    for name in ("low_bytes","source_radius","parent_STOP_rescue","contact_rescue","omit_cast_error","claim_phase","claim_GPU","hide_cost"):
        d=copy.deepcopy(data);r=d["records"][0]["result"]
        if name=="low_bytes":r["frame"]["decode_ledger"][0]["lo_word"]="000000000000f03f"
        elif name=="source_radius":r["frame"]["scene"]["points"]["origin"]["radius"][0]=[0,1]
        elif name=="parent_STOP_rescue":next(x for x in d["records"] if x["id"]=="native_inexact")["result"]["status"]="CPU64_DECLARED_BOX_INTERIOR_CROSS"
        elif name=="contact_rescue":next(x for x in d["records"] if x["id"].startswith("scene:edge/"))["result"]["status"]="CPU64_DECLARED_BOX_INTERIOR_CROSS"
        elif name=="omit_cast_error":d["helpers"][0]["ledger"][1]["output_word"]=d["helpers"][0]["words"]["hi"]
        elif name=="claim_phase":r["phase_certified"]=True
        elif name=="claim_GPU":r["GPU_used"]=True
        else:r["native_result"]["costs"]["endpoint_casts"]=0
        try:verify_capture(d)
        except (AssertionError,KeyError,TypeError,ValueError):mutations.append(name)
        else:raise AssertionError("mutation_not_rejected:"+name)
    summary["mutations_rejected"]=mutations
    return dict(summary=summary,evidence=data)
