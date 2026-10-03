"""Six translated controls with direct failures retained; capture-only exact/word oracle."""
from fractions import Fraction as F
from pathlib import Path
import copy,json,hashlib,zlib,base64,runpy
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-FINITE-INTERVAL-CPU64-001-CODEX.json"
PSHA="ec8345447b4c4eb506900567876ba0f8fd9ea16cbe36470d3a78653a41273807"
MODEL="oblique-common-exact-frame-CPU64-v1"
POLICY="SAME_DECLARED_SOURCE0_NOMINAL_FOR_ALL5POINTS_NOT_PHASE_REFERENCE"
POINTS=("origin","detector","A","B","C")
NAMES=("thin_cross","thin_beyond_end","edge","t0","t1","outside")
def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
def pair(x):return [x.numerator,x.denominator]
def retained():
    raw=(ROOT/PARENT).read_bytes()
    assert len(raw)==221368 and hashlib.sha256(raw).hexdigest()==PSHA
    d=json.loads(raw);c=d["test_run"]
    raw=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]))
    assert len(raw)==c["stdout_bytes"]<=2*1024*1024 and hashlib.sha256(raw).hexdigest()==c["stdout_sha256"]
    cap=json.loads(raw)["evidence"]
    selected={x["parent"]["name"]:x for x in cap["records"] if x["parent"]["name"].endswith("/reverse0/wind0/box1") and x["parent"]["name"].split("/")[0] in NAMES}
    assert len(selected)==6
    return d,selected
def translated(parent):
    s=copy.deepcopy(parent["scene"])
    s["scene_id"]+="/NEW-TRANSLATED2p30"
    s["context"]+="/NEW-TRANSLATED2p30"
    for p in POINTS:
        s["points"][p]["nominal"]=[pair(F(*x)+2**30) for x in s["points"][p]["nominal"]]
    return s
def scene_query(scene,parent):
    return dict(parent["parent"]["query"],snapshot_sha256=digest(scene),context=scene["context"])
def host_record(name,scene,query,oracle):
    raw=oracle["oracle_trace"](scene)
    # Test-only exact oracle identity, NOT a replay of HOST producer, and not a sealed new parent.
    return dict(name=name,scene=scene,query=query,result=dict(trace={k:[pair(x) for x in v] for k,v in raw.items()},status="TEST_ORACLE_ONLY_NOT_PARENT_PRODUCER"))
def verify_capture(data):
    d,allowed=retained()
    assert data["pins"]==dict(d["code_doc_sha256"],**{PARENT:PSHA})
    assert len(data["records"])==6 and {x["parent_name"] for x in data["records"]}==set(allowed)
    native=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_finite_interval_CPU64.py"))
    oracle=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_finite_interval_HOST.py"))
    census={};direct_counts={};lost=0
    for item in data["records"]:
        parent=allowed[item["parent_name"]]
        assert item["parent_record_sha256"]==digest(parent)
        scene=translated(parent);query=scene_query(scene,parent)
        assert item["original_scene"]==scene and item["original_scene_query"]==query
        q=dict(backend=MODEL,policy=POLICY,original_snapshot_sha256=digest(scene),original_scene_query=query)
        assert item["request"]==q
        result=item["result"];frame=result["frame"]
        assert result["backend"]==MODEL and result["HOST_exact_recenter_operations"]==15
        assert result["original_snapshot_sha256"]==digest(scene) and result["request_sha256"]==digest(q)
        for k in ("physical_visibility_certified","phase_certified","scene_authenticated","GPU_used","native_hi_lo_transport","source_uncertainty_cancelled"):
            assert result[k] is False
        assert result["promotion"]=="STOP_PHYSICAL_GPU" and result["full_costs"]=="UNKNOWN_NOT_ZERO"
        assert frame["policy"]==POLICY and frame["geometric_NOT_optical"] is True
        ref=scene["points"]["origin"]["nominal"]
        assert frame["reference"]==ref and frame["reference_uncertainty"]=="EXACT_CHOSEN_CONSTANT_NOT_ACTUAL_SOURCE_ERROR"
        centered=copy.deepcopy(scene)
        centered["scene_id"]+="/COMMON-EXACT-FRAME";centered["context"]+="/COMMON-EXACT-FRAME"
        expected=[]
        for p in POINTS:
            for j,(x,r) in enumerate(zip(scene["points"][p]["nominal"],ref)):
                y=pair(F(*x)-F(*r));centered["points"][p]["nominal"][j]=y
                expected.append(dict(point=p,axis=j,original=x,reference=r,centered=y,
                                     radius=scene["points"][p]["radius"][j]))
        assert frame["ledger"]==expected and frame["scene"]==centered
        for entry in frame["ledger"]:
            for k in ("original","reference","centered","radius"):
                v=entry[k]
                assert type(v) is list and len(v)==2 and all(type(x)is int for x in v)
                assert v[1]>0 and pair(F(*v))==v
        assert all(centered["points"][p]["radius"]==scene["points"][p]["radius"]==parent["scene"]["points"][p]["radius"] for p in POINTS)
        cq=dict(query,snapshot_sha256=digest(centered),context=centered["context"])
        assert frame["scene_query"]==cq and frame["snapshot_sha256"]==digest(centered)
        nq=dict(backend="oblique-finite-interval-CPU64-v1",scene_query=cq,snapshot_sha256=digest(centered))
        assert frame["native_request"]==nq
        # Each interval operation is translation invariant when ONE exact constant is used.
        before=oracle["oracle_trace"](scene);after=oracle["oracle_trace"](centered)
        original={k:tuple(F(*x) for x in v) for k,v in parent["parent"]["result"]["trace"].items()}
        assert before==after==original
        proof=host_record(item["parent_name"]+"/FRAME_ORACLE",centered,cq,oracle)
        nr=dict(scene=centered,request=nq,parent=proof,result=result["native_result"])
        status,calls=native["verify_record"](nr)
        assert result["status"]==status
        assert status==parent["result"]["status"]  # geometry semantics retained, not parent STOP rescue
        direct_q=dict(backend="oblique-finite-interval-CPU64-v1",scene_query=query,snapshot_sha256=digest(scene))
        proof=host_record(item["parent_name"]+"/DIRECT_ORACLE",scene,query,oracle)
        direct=dict(scene=scene,request=direct_q,parent=proof,result=item["direct_result"])
        direct_status,_=native["verify_record"](direct)
        direct_counts[direct_status]=direct_counts.get(direct_status,0)+1
        if item["parent_name"].split("/")[0] in ("thin_cross","thin_beyond_end"):
            assert direct_status=="STOP_UNRESOLVED"  # preserve actual failure to resolve thin feature
            assert status!="STOP_UNRESOLVED"
            # Direct RN casts alias the two endpoint nominal heights; input outward boxes overlap.
            a=item["direct_result"]["ledger"][4]["RN_word"]
            b=item["direct_result"]["ledger"][10]["RN_word"]
            assert a==b
            lost+=1
        census[status]=census.get(status,0)+1
    assert lost==2
    assert len(data["invalid"])==7
    for x in data["invalid"]:
        r=x["result"]
        assert r["status"]=="STOP_INPUT" and r["native_result"] is None
        assert r["GPU_used"] is False and r["native_hi_lo_transport"] is False
    for p,h in data["pins"].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    return dict(status="PASS",controls=6,framed=census,direct=direct_counts,direct_thin_STOP_preserved=2,
                HOST_exact_recenter_operations=90,native_calls=12,native_arithmetic=1848,
                endpoint_casts=360,proof_records=3360,invalid=7,pins=len(data["pins"]),
                original_producer_replays=0,GPU_calls=0,native_hi_lo_transport=False,full_costs="UNKNOWN_NOT_ZERO")
def run():
    import sys
    sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
    import oblique_common_frame_CPU64_v1 as m
    import oblique_finite_interval_CPU64_v1 as cpu
    d,allowed=retained();pins=dict(d["code_doc_sha256"]);pins[PARENT]=PSHA
    records=[]
    for name,parent in allowed.items():
        scene=translated(parent);query=scene_query(scene,parent)
        q=m.request(scene,query)
        records.append(dict(parent_name=name,parent_record_sha256=digest(parent),
                            original_scene=scene,original_scene_query=query,request=q,
                            direct_result=cpu.classify(scene,dict(backend=cpu.MODEL,scene_query=query,snapshot_sha256=digest(scene))),
                            result=m.classify(scene,q)))
    base=records[0];invalid=[]
    for name,change in [
        ("unknown_backend",lambda s,q:q.__setitem__("backend","GPU")),
        ("optical_reference",lambda s,q:q.__setitem__("policy","OPTICAL_REFERENCE")),
        ("stale_snapshot",lambda s,q:q.__setitem__("original_snapshot_sha256","0"*64)),
        ("SOURCE1",lambda s,q:q["original_scene_query"].__setitem__("source","SOURCE1")),
        ("missing_radius",lambda s,q:s["points"]["origin"].pop("radius")),
        ("extra_zero_source_error",lambda s,q:q.__setitem__("source_error",0)),
        ("uncertain_reference_override",lambda s,q:q.__setitem__("reference",[0,0,0]))]:
        s,q=copy.deepcopy(base["original_scene"]),copy.deepcopy(base["request"]);change(s,q)
        if name=="missing_radius":
            q["original_snapshot_sha256"]=digest(s);q["original_scene_query"]["snapshot_sha256"]=digest(s)
        invalid.append(dict(name=name,result=m.classify(s,q)))
    data=dict(records=records,invalid=invalid,pins=pins)
    summary=verify_capture(data)
    mutants=[]
    for name in ("omit_source_radius","different_reference","cancel_source_error","claim_native_hilo","claim_phase","shrink_native_box","erase_direct_STOP","recenter_nominal_float"):
        a=copy.deepcopy(data);r=a["records"][0]["result"]
        if name=="omit_source_radius":r["frame"]["scene"]["points"]["origin"]["radius"][0]=[0,1]
        elif name=="different_reference":r["frame"]["ledger"][3]["reference"]=[0,1]
        elif name=="cancel_source_error":r["source_uncertainty_cancelled"]=True
        elif name=="claim_native_hilo":r["native_hi_lo_transport"]=True
        elif name=="claim_phase":r["phase_certified"]=True
        elif name=="shrink_native_box":r["native_result"]["input_boxes"]["origin"][0][0]="0"*16
        elif name=="erase_direct_STOP":
            next(x for x in a["records"] if x["parent_name"].startswith("thin_cross/"))["direct_result"]["status"]="CPU64_DECLARED_BOX_INTERIOR_CROSS"
        else:r["frame"]["ledger"][0]["original"]=[float(F(*r["frame"]["ledger"][0]["original"])),1]
        try:verify_capture(a)
        except (AssertionError,ValueError,TypeError,KeyError):mutants.append(name)
        else:raise AssertionError("mutation_not_rejected/"+name)
    summary["mutations_rejected"]=mutants
    return dict(summary=summary,evidence=data)
