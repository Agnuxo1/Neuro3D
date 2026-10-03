"""Capture-only bit/rational native graph oracle; sealed scenes, no old suite replays."""
from fractions import Fraction as F
from pathlib import Path
import copy,json,hashlib,struct,zlib,base64,runpy
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-FRAME-CPU64-001-CODEX.json"
PSHA="d17a781897aeef1289d0e1c0682462e5f9263e8c8a7f1ecf2bd26170acb2603a"
MODEL="oblique-scene-pair64-recenter-CPU-v1"
POLICY="ALL15_EXACT_PAIR_WORDS_COMMON_SOURCE0_CONSTANT_KEEP_RADII"
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
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==181436 and hashlib.sha256(raw).hexdigest()==PSHA
    receipt=json.loads(raw);data=capture(receipt["test_run"])["evidence"]
    assert capture(receipt["independent_pre"])["status"]=="PASS"
    assert len(data["records"])==6
    return receipt,{x["parent_name"]:x for x in data["records"]}
def wordbits(w):
    assert type(w)is str and len(w)==16 and bytes.fromhex(w).hex()==w
    return int.from_bytes(bytes.fromhex(w),"little")
def frac(w,allow_subnormal=False):
    b=wordbits(w);sign=-1 if b>>63 else 1;e=(b>>52)&2047;m=b&((1<<52)-1)
    assert e!=2047
    if e==0:
        assert m==0 or allow_subnormal
        return sign*F(m,2**1074)
    return sign*F((1<<52)+m)*F(2)**(e-1075)
def neg(w):return (wordbits(w)^(1<<63)).to_bytes(8,"little").hex()
def closest(w,target):
    rn=frac(w)
    if rn==0:assert target==0
    else:
        b=wordbits(w);distance=abs(rn-target)
        for z in (b-1,b+1):
            alt=frac(z.to_bytes(8,"little").hex(),True)
            assert distance<=abs(target-alt)
            assert distance!=abs(target-alt) or b%2==0
def graph(r,a,b):
    nodes=r["trace"]["nodes"];eft=r["trace"]["eft"];i=0;j=0
    def take(x,y,op,name):
        nonlocal i
        n=nodes[i];i+=1
        assert set(n)=={"name","op","a","b","y","error"}
        assert (n["name"],n["op"],n["a"],n["b"])==(name,op,x,y)
        v=frac(x)+frac(y) if op=="+" else frac(x)-frac(y)
        closest(n["y"],v)
        assert n["error"]==pair(abs(frac(n["y"])-v))
        assert all(type(t)is int for t in n["error"])
        return n["y"]
    def twosum(x,y,name):
        nonlocal j
        s=take(x,y,"+",name+"_s");bb=take(s,x,"-",name+"_bb");ab=take(s,bb,"-",name+"_ab")
        db=take(y,bb,"-",name+"_db");da=take(x,ab,"-",name+"_da");ee=take(da,db,"+",name+"_e")
        assert eft[j]==dict(name=name,a=x,b=y,hi=s,lo=ee,residual_exact=True);j+=1
        assert frac(s)+frac(ee)==frac(x)+frac(y)
        return s,ee
    s,e=twosum(a[0],neg(b[0]),"h");t,f=twosum(a[1],neg(b[1]),"l")
    e=take(e,t,"+","e_add");h,g=twosum(s,e,"m");lo=take(g,f,"+","lo_add")
    h,lo=twosum(h,lo,"r")
    assert i==26==len(nodes) and j==4==len(eft)
    assert r["status"]=="CONTROL_ONLY" and r["reason"]is None
    assert r["hi_word_le_hex"]==h and r["lo_word_le_hex"]==lo
    target=frac(a[0])+frac(a[1])-frac(b[0])-frac(b[1]);decoded=frac(h)+frac(lo)
    assert r["target_debug_BU"]==pair(target) and r["decoded_debug_BU"]==pair(decoded)
    assert r["error_abs_BU"]==pair(abs(decoded-target))
    assert r["exact_pair_difference"]is (target==decoded)
    assert r["CPU_native_executed"]is True and r["GPU_executed"]is False and r["native_RN64_operations"]==26
    return decoded,target
def scope(r):
    assert r["backend"]==MODEL and r["predicate_calls"]==0
    for k in ("HOST_recenter_substitution","source_uncertainty_cancelled","physical_visibility_certified","phase_certified","scene_authenticated","GPU_used"):
        assert r[k]is False
    assert r["reference_uncertainty"]=="EXACT_CHOSEN_CONSTANT_NOT_ACTUAL_SOURCE_ERROR"
    assert r["promotion"]=="STOP_DOWNSTREAM_PHYSICAL_GPU" and r["full_costs"]=="UNKNOWN_NOT_ZERO"
def verify_record(item,success=True):
    s,q,r=item["scene"],item["request"],item["result"];scope(r)
    assert q==dict(backend=MODEL,policy=POLICY,snapshot_sha256=digest(s),scene_query=item["scene_query"],
        packet_hex=q["packet_hex"],packet_sha256=hashlib.sha256(bytes.fromhex(q["packet_hex"])).hexdigest())
    raw=bytes.fromhex(q["packet_hex"]);assert len(raw)==240 and raw.hex()==q["packet_hex"]
    words=[raw[i:i+8].hex() for i in range(0,240,8)]
    for i in range(15):assert frac(words[2*i])+frac(words[2*i+1])==F(*s["points"][POINTS[i//3]]["nominal"][i%3])
    assert r["snapshot_sha256"]==digest(s) and r["request_sha256"]==digest(q)
    assert r["packet_sha256"]==q["packet_sha256"] and r["packet_bytes"]==240 and r["decoded_words"]==30
    assert r["native_RN64_operations"]==26*len(r["ledger"]) and r["native_sign_flips"]==2*len(r["ledger"])
    assert r["native_hi_lo_recenter_executed"]is True
    centered=copy.deepcopy(s);centered["scene_id"]+="/NATIVE-PAIR64";centered["context"]+="/NATIVE-PAIR64"
    output=[]
    for i,entry in enumerate(r["ledger"]):
        n,j=POINTS[i//3],i%3;a=words[2*i:2*i+2];b=words[2*j:2*j+2]
        assert set(entry)=={"point","axis","input_words","reference_words","radius","native_result"}
        assert (entry["point"],entry["axis"],entry["input_words"],entry["reference_words"],entry["radius"])==(n,j,a,b,s["points"][n]["radius"][j])
        y,target=graph(entry["native_result"],a,b)
        assert target==F(*s["points"][n]["nominal"][j])-F(*s["points"]["origin"]["nominal"][j])
        if success:assert y==target
        centered["points"][n]["nominal"][j]=pair(y)
        output+=[entry["native_result"]["hi_word_le_hex"],entry["native_result"]["lo_word_le_hex"]]
    if not success:
        assert r["status"]=="STOP_NATIVE" and r["frame"]is None and len(r["ledger"])==4
        assert r["reason"]=="inexact_native_difference_STOP" and F(*r["ledger"][-1]["native_result"]["error_abs_BU"])==F(1,2**120)
        return
    assert len(r["ledger"])==15 and r["status"]=="CPU_NATIVE_PAIR64_RECENTER_ONLY" and r["reason"]=="EXACT_TRANSPORT_NOT_PREDICATE"
    frame=r["frame"];cq=dict(item["scene_query"],snapshot_sha256=digest(centered),context=centered["context"])
    assert frame==dict(scene=centered,scene_query=cq,snapshot_sha256=digest(centered),
        reference=s["points"]["origin"]["nominal"],coordinate_representation="EXACT_DECODED_NATIVE_PAIR64",output_packet_hex="".join(output))
    assert len(bytes.fromhex(frame["output_packet_hex"]))==240
    assert all(frame["scene"]["points"][n]["radius"]==s["points"][n]["radius"] for n in POINTS)
def verify_capture(data):
    receipt,parents=retained()
    pins=dict(receipt["code_doc_sha256"]);pins[PARENT]=PSHA
    assert data["pins"]==pins
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert len(data["records"])==6 and {x["name"]for x in data["records"]}==set(parents)
    for x in data["records"]:
        old=parents[x["name"]]
        assert x["parent_record_sha256"]==digest(old) and x["scene"]==old["original_scene"] and x["scene_query"]==old["original_scene_query"]
        verify_record(x)
        assert x["retained_direct_status"]==old["direct_result"]["status"]
        # Compare decoded native coordinates with sealed HOST exact frame, no HOST producer call.
        assert x["result"]["frame"]["scene"]["points"]==old["result"]["frame"]["scene"]["points"]
    assert sum(x["retained_direct_status"]=="STOP_UNRESOLVED"for x in data["records"])==5
    badscene=copy.deepcopy(data["records"][0]["scene"])
    badscene["scene_id"]+="/NEW-INEXACT3SCALE";badscene["context"]+="/NEW-INEXACT3SCALE"
    for n in POINTS:badscene["points"][n]["nominal"][0]=pair(F(1)+F(1,2**60))
    badscene["points"]["origin"]["nominal"][0]=[1,2**120]
    assert data["inexact"]["scene"]==badscene
    assert data["inexact"]["scene_query"]==dict(data["records"][0]["scene_query"],context=badscene["context"],snapshot_sha256=digest(badscene))
    verify_record(data["inexact"],False)
    expected=("hi_only","short_packet","packet_hash","phase_policy","snapshot","SOURCE1","nonfinite","noncanonical_hex","inexact_encoding")
    assert tuple(x["name"]for x in data["invalid"])==expected
    base=next(x for x in data["records"] if any(frac(x["request"]["packet_hex"][32*i+16:32*i+32])!=0 for i in range(15)))
    for x in data["invalid"]:
        r=x["result"];scope(r)
        assert r["status"]=="STOP_INPUT" and r["frame"]is None and r["ledger"]==[] and r["native_RN64_operations"]==0 and not r["native_hi_lo_recenter_executed"]
        ss=copy.deepcopy(base["scene"]);qq=copy.deepcopy(base["request"]);name=x["name"]
        why="canonical_packet_identity"
        if name=="hi_only":
            i=next(i for i in range(15) if frac(qq["packet_hex"][32*i+16:32*i+32])!=0)
            qq["packet_hex"]=qq["packet_hex"][:32*i+16]+"0"*16+qq["packet_hex"][32*i+32:]
            why="inexact_pair_input:"+POINTS[i//3]+":"+str(i%3)
        elif name=="short_packet":qq["packet_hex"]=qq["packet_hex"][:-2];why="ALL15_pairs_240bytes"
        elif name=="packet_hash":qq["packet_sha256"]="0"*64
        elif name=="phase_policy":qq["policy"]="OPTICAL_REFERENCE";why="closed_backend_policy"
        elif name=="snapshot":qq["snapshot_sha256"]="0"*64;why="snapshot_binding"
        elif name=="SOURCE1":qq["scene_query"]["source"]="SOURCE1";why="query_snapshot_binding_mismatch"
        elif name=="nonfinite":qq["packet_hex"]="000000000000f07f"+qq["packet_hex"][16:];why="normal_zero_input_words"
        elif name=="noncanonical_hex":qq["packet_hex"]=qq["packet_hex"].upper()
        else:
            ss["scene_id"]+="/NEW-INEXACT-ENCODING";ss["context"]+="/NEW-INEXACT-ENCODING"
            ss["points"]["A"]["nominal"][0]=[1,3]
            query=dict(base["scene_query"],snapshot_sha256=digest(ss),context=ss["context"])
            qq=dict(backend=MODEL,policy=POLICY,snapshot_sha256=digest(ss),scene_query=query,
                packet_hex=x["request"]["packet_hex"],packet_sha256=hashlib.sha256(bytes.fromhex(x["request"]["packet_hex"])).hexdigest())
            assert len(qq["packet_hex"])==480
            for i in range(15):
                value=F(*ss["points"][POINTS[i//3]]["nominal"][i%3])
                hw=qq["packet_hex"][32*i:32*i+16];lw=qq["packet_hex"][32*i+16:32*i+32]
                closest(hw,value);closest(lw,value-frac(hw))
                assert frac(hw)+frac(lw)==value if i!=6 else frac(hw)+frac(lw)!=value
            why="inexact_pair_input:A:0"
        if name in ("hi_only","short_packet","nonfinite","noncanonical_hex"):
            qq["packet_sha256"]=hashlib.sha256(bytes.fromhex(qq["packet_hex"])).hexdigest()
        assert x["scene"]==ss and x["request"]==qq and r["reason"]==x["expected_reason"]==why
    return dict(status="PASS",scenes=6,coordinate_pairs=90,native_RN64_operations=2340,native_sign_flips=180,
        input_packet_bytes=1440,output_packet_bytes=1440,invalid=9,inexact_native_STOP=1,
        inexact_native_operations=104,old_direct_STOP_preserved=5,pins=len(pins),predicate_calls=0,
        retained_suite_replays=0,GPU_calls=0,full_costs="UNKNOWN_NOT_ZERO")
def encode(scene,query):
    # Test preparation only: real float casts + HOST exact residual, NOT native encoding.
    words=[]
    for n in POINTS:
        for x in scene["points"][n]["nominal"]:
            exact=F(*x);hi=float(exact);lo=float(exact-F.from_float(hi))
            words+=[struct.pack("<d",hi).hex(),struct.pack("<d",lo).hex()]
    text="".join(words)
    return dict(backend=MODEL,policy=POLICY,snapshot_sha256=digest(scene),scene_query=query,
        packet_hex=text,packet_sha256=hashlib.sha256(bytes.fromhex(text)).hexdigest())
def run():
    import sys
    sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
    import oblique_scene_pair64_recenter_CPU_v1 as m
    receipt,parents=retained();pins=dict(receipt["code_doc_sha256"]);pins[PARENT]=PSHA
    records=[]
    for name,old in parents.items():
        s=copy.deepcopy(old["original_scene"]);sq=old["original_scene_query"];q=encode(s,sq)
        records.append(dict(name=name,parent_record_sha256=digest(old),scene=s,scene_query=sq,request=q,
            retained_direct_status=old["direct_result"]["status"],result=m.recenter(s,q)))
    first=records[0];s=copy.deepcopy(first["scene"])
    s["scene_id"]+="/NEW-INEXACT3SCALE";s["context"]+="/NEW-INEXACT3SCALE"
    for n in POINTS:s["points"][n]["nominal"][0]=pair(F(1)+F(1,2**60))
    s["points"]["origin"]["nominal"][0]=[1,2**120]
    sq=dict(first["scene_query"],snapshot_sha256=digest(s),context=s["context"]);q=encode(s,sq)
    inexact=dict(scene=s,scene_query=sq,request=q,result=m.recenter(s,q))
    first=next(x for x in records if any(frac(x["request"]["packet_hex"][32*i+16:32*i+32])!=0 for i in range(15)))
    invalid=[]
    for name in ("hi_only","short_packet","packet_hash","phase_policy","snapshot","SOURCE1","nonfinite","noncanonical_hex","inexact_encoding"):
        s=copy.deepcopy(first["scene"]);q=copy.deepcopy(first["request"])
        expected="canonical_packet_identity"
        if name=="hi_only":
            # Alter the low limb of a NONZERO actual pair, reseal bytes only; scene still binds original.
            for i in range(15):
                if frac(q["packet_hex"][32*i+16:32*i+32])!=0:
                    q["packet_hex"]=q["packet_hex"][:32*i+16]+"0"*16+q["packet_hex"][32*i+32:]
                    expected="inexact_pair_input:"+POINTS[i//3]+":"+str(i%3);break
            else:raise AssertionError("need_nonzero_low")
        elif name=="short_packet":q["packet_hex"]=q["packet_hex"][:-2];expected="ALL15_pairs_240bytes"
        elif name=="packet_hash":q["packet_sha256"]="0"*64
        elif name=="phase_policy":q["policy"]="OPTICAL_REFERENCE";expected="closed_backend_policy"
        elif name=="snapshot":q["snapshot_sha256"]="0"*64;expected="snapshot_binding"
        elif name=="SOURCE1":q["scene_query"]["source"]="SOURCE1";expected="query_snapshot_binding_mismatch"
        elif name=="nonfinite":q["packet_hex"]="000000000000f07f"+q["packet_hex"][16:];expected="normal_zero_input_words"
        elif name=="noncanonical_hex":q["packet_hex"]=q["packet_hex"].upper()
        else:
            s["scene_id"]+="/NEW-INEXACT-ENCODING";s["context"]+="/NEW-INEXACT-ENCODING"
            s["points"]["A"]["nominal"][0]=[1,3]
            sq=dict(first["scene_query"],snapshot_sha256=digest(s),context=s["context"]);q=encode(s,sq)
            expected="inexact_pair_input:A:0"
        if name in ("hi_only","short_packet","nonfinite","noncanonical_hex"):
            q["packet_sha256"]=hashlib.sha256(bytes.fromhex(q["packet_hex"])).hexdigest()
        invalid.append(dict(name=name,scene=s,request=q,expected_reason=expected,result=m.recenter(s,q)))
    data=dict(records=records,inexact=inexact,invalid=invalid,pins=pins)
    summary=verify_capture(data);mutations=[]
    for name in ("low_word","native_node","radius_zero","different_reference","claim_phase","claim_predicate","erase_inexact_STOP","HOST_substitution"):
        d=copy.deepcopy(data);r=d["records"][0]["result"]
        if name=="low_word":
            z=r["ledger"][4]["native_result"]["lo_word_le_hex"]
            r["ledger"][4]["native_result"]["lo_word_le_hex"]="000000000000f03f" if z=="0"*16 else "0"*16
        elif name=="native_node":r["ledger"][0]["native_result"]["trace"]["nodes"][0]["y"]="000000000000f03f"
        elif name=="radius_zero":r["frame"]["scene"]["points"]["origin"]["radius"][0]=[0,1]
        elif name=="different_reference":r["ledger"][3]["reference_words"]=["0"*16,"0"*16]
        elif name=="claim_phase":r["phase_certified"]=True
        elif name=="claim_predicate":r["predicate_calls"]=1
        elif name=="erase_inexact_STOP":d["inexact"]["result"]["status"]="CPU_NATIVE_PAIR64_RECENTER_ONLY"
        else:r["HOST_recenter_substitution"]=True
        try:verify_capture(d)
        except (AssertionError,ValueError,KeyError,TypeError):mutations.append(name)
        else:raise AssertionError("mutation_not_rejected:"+name)
    summary["mutations_rejected"]=mutations
    return dict(summary=summary,evidence=data)
