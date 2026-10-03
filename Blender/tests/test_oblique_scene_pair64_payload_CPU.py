"""Independent typed manifest, word identity and original-box rational proof."""
from pathlib import Path
from fractions import Fraction as F
import ast,json,hashlib,copy,runpy,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
old=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_consumer_ABI_static.py"))
capture,digest,pair,pf=(old[n]for n in ("capture","digest","pair","pf"))
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-CONSUMER-ABI-STATIC-001-CODEX.json"
PSHA="438b21c4affc14c6050e4ce5e856f0518dad5d95ce6ea5e8cc04f4beaf09d137"
ROOT_PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001-CODEX.json"
ROOT_SHA="6ef5e1e46e9e9f37c4c7051d064598191e76c93737325dc3683e4aeb3e082eef"
MODEL="oblique-scene-pair64-payload-CPU-v1"
POLICY="EXPLICIT_ROOT64_PRE_WIRE_BYTES_NOT_PAIR32_REPAIR_OR_ENGINE"


def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==265694 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==307 and pins[ROOT_PARENT]==ROOT_SHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    da=capture(r["test_run"])["evidence"];abi={x["id"]:x for x in da["records"]}
    raw=(ROOT/ROOT_PARENT).read_bytes();assert len(raw)==168330 and hashlib.sha256(raw).hexdigest()==ROOT_SHA
    dr=capture(json.loads(raw)["test_run"])["evidence"];native={x["id"]:x for x in dr["records"]}
    _,_,ref,orig,_,_=old["retained"]()
    assert set(abi)==set(native)==set(ref)==set(orig)and len(abi)==16
    pins[PARENT]=PSHA
    return abi,native,ref,orig,pins,da,dr


def selector(k,abi,native,ref,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        ABI_record_sha256=digest(abi[k]),native_root_receipt_sha256=ROOT_SHA,
        native_root_record_sha256=digest(native[k]),reference_record_sha256=digest(ref[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q))


def scope(r):
    assert r["backend"]==MODEL and r["scope"]=="CPU_TYPED_ROOT64_LENGTH_BOUND_BYTES_HOST_PARSER_ONLY"
    assert r["promotion"]=="STOP_REAL_PAIR64_CONSUMER_SCENE_PHASE_GUARD_AND_COSTS"
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["native_length"]is None and r["phase_error_bound"]is None
    for p in ("float_decode_calls","RN_nodes_executed","new_products","new_sums","new_sqrt_calls","retained_numeric_replays"):
        assert r[p]==0,p
    for p in ("phase_certified","wavelength_known","scene_engine_admitted","GPU_used","Bpy_used","shader_used",
              "foreign_source_executed","source_uncertainty_cancelled","physical_reference_certified"):assert r[p]is False,p


def proof_envelope(v,k,q,abi,native,ref,orig):
    n=native[k]["result"];a=abi[k]["result"];z=n["diagnostic"];rz=ref[k]["result"]["diagnostic"]
    assert n["status"]=="CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY"
    assert a["status"]=="STATIC_CONSUMER_ABI_UNBOUND"and a["upstream_status"]=="STOP_SCALAR_PAIR_CONSUMPTION_LOSS"
    assert rz["original_scene"]==orig[k]["scene"]and rz["original_query"]==orig[k]["scene_query"]
    words=[];certs=[]
    for i,x in enumerate(z["corrections"]):
        b,r=x["bound"],x["result"];assert b==("lower","upper")[i]and r["status"]=="CPU64_NATIVE_ROOT_PAIR_HOST_BOUND_ONLY"
        hi,lo=r["root_pair_words"];Q=pf(hi)+pf(lo);S=F(*r["exact_squared"]);B=F(*r["length_error_bound"])
        for w in (hi,lo):
            u=int.from_bytes(bytes.fromhex(w),"little");e=(u>>52)&2047
            assert e!=2047 and (e!=0 or pf(w)==0)and abs(pf(w))<=2**33
        assert pair(Q)==r["candidate_sum"]and B>=0 and Q-B>0 and (Q-B)**2<=S<=(Q+B)**2
        assert r["HOST_enclosure"]==[pair(Q-B),pair(Q+B)]and r["exact_squared"]==rz["extrema"]["squared"][i]
        words.extend([hi,lo]);certs.append(dict(bound=b,exact_squared=r["exact_squared"],
            retained_exact_pair_sum=pair(Q),retained_length_error_bound=r["length_error_bound"],
            retained_HOST_enclosure=r["HOST_enclosure"]))
    payload="".join(words);assert len(payload)==64
    expected=dict(schema=MODEL,version=1,artifact_kind="scene_length_lower_upper_bounds",
        provenance_branch=POLICY,endianness="little",word_type="IEEE754_BINARY64",
        word_order=["lower_hi","lower_lo","upper_hi","upper_lo"],pair_bytes=16,pair_count=2,
        payload_bytes=32,payload_hex=payload,
        payload_hex_ASCII_sha256=hashlib.sha256(payload.encode("ascii")).hexdigest(),selector_sha256=digest(q),
        original_snapshot_sha256=q["original_snapshot_sha256"],original_query_sha256=q["original_query_sha256"],
        original_record_sha256=q["original_record_sha256"],reference_record_sha256=q["reference_record_sha256"],
        native_root_receipt_sha256=ROOT_SHA,native_root_record_sha256=q["native_root_record_sha256"],
        ABI_receipt_sha256=PSHA,ABI_record_sha256=q["ABI_record_sha256"],source="SOURCE0",detector="DETECTOR0",
        units="scene_length",source_uncertainty_cancelled=False,legacy_ABI_status=a["status"],
        legacy_scalar_gate=a["upstream_status"],retained_canonical_status=n["retained_canonical_status"],
        certificates=certs,consumer_binding_proven=False,phase_error_bound=None,wavelength_known=False)
    assert v==expected
    return words


def no_foreign_execution_static():
    paths=("Blender/benchmarks/capacity_audit/oblique_scene_pair64_payload_CPU_v1.py",
           "Blender/tests/test_oblique_scene_pair64_payload_CPU.py")
    for path in paths:
        t=ast.parse((ROOT/path).read_text(encoding="utf-8"))
        for n in ast.walk(t):
            if isinstance(n,ast.Call):
                assert not(isinstance(n.func,ast.Name)and n.func.id in ("eval","exec"))
                if isinstance(n.func,ast.Attribute):
                    assert n.func.attr not in ("pack","unpack","dispatch","sqrt","write_bytes","write_text")
    return True


def verify_capture(d,verify_parent=True):
    abi,native,ref,orig,pins,parent,_=retained()
    if verify_parent:old["verify_capture"](parent)
    assert d["pins"]==pins and len(pins)==308 and no_foreign_execution_static()
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(abi)
    eligible=stops=decodes=builds=0;meta=[]
    for x in d["records"]:
        k=x["id"];q=selector(k,abi,native,ref,orig);assert x["request"]==q
        r=x["result"];scope(r);n=native[k]["result"];a=abi[k]["result"]
        assert r["request_sha256"]==digest(q)and r["native_upstream_status"]==n["status"]
        assert r["retained_ABI_status"]==a["status"]and r["retained_canonical_status"]==n["retained_canonical_status"]
        if n["status"]!="CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"
            assert r["envelope"]is None and r["HOST_roundtrip"]is None
            assert r["pair_hex_builds"]==r["byte_decode_calls"]==r["integer_word_reads"]==0;stops+=1;continue
        assert r["status"]=="CPU_HOST_PAIR64_LENGTH_BYTES_ONLY"and r["reason"]=="producer_and_HOST_parser_not_scene_engine"
        words=proof_envelope(r["envelope"],k,q,abi,native,ref,orig)
        assert r["HOST_roundtrip"]==dict(payload_bytes=32,word_hex=words,payload_hex="".join(words),
                                       consumer="OWN_HOST_TYPED_PARSER_NO_NUMERIC_RECOMPOSITION")
        assert (r["pair_hex_builds"],r["byte_decode_calls"],r["integer_word_reads"])==(2,1,4)
        eligible+=1;decodes+=1;builds+=2
        meta.append(dict(id=k,payload_hex=r["envelope"]["payload_hex"],pair_words=[words[:2],words[2:]],
            max_retained_bound=str(max(F(*v["retained_length_error_bound"])for v in r["envelope"]["certificates"]))))
    assert (eligible,stops,decodes,builds)==(2,14,2,4)
    assert len(d["invalid_selectors"])==8
    for x in d["invalid_selectors"]:
        r=x["result"];scope(r)
        assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"
        assert r["envelope"]is None and r["HOST_roundtrip"]is None
        assert r["pair_hex_builds"]==r["byte_decode_calls"]==r["integer_word_reads"]==0
    assert len(d["invalid_envelopes"])==8
    for x in d["invalid_envelopes"]:
        r=x["result"];scope(r)
        assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_typed_envelope"
        assert r["envelope"]is None and r["HOST_roundtrip"]is None
        assert r["pair_hex_builds"]==2 and r["byte_decode_calls"]==r["integer_word_reads"]==0
        builds+=2
    assert builds==20
    return dict(status="PASS",eligible_scenes=2,upstream_STOP=14,scene_engine_admitted=0,
        source_branch="NATIVE_ROOT64_PRE_WIRE_EXPLICIT",pair64_payloads=4,total_payload_bytes=64,
        valid_pair_hex_builds=4,total_pair_hex_builds=20,byte_decode_calls=2,integer_word_reads=8,
        float_decode_calls=0,new_RN_operations=0,new_products=0,new_sqrt_calls=0,retained_numeric_replays=0,
        selectors_rejected=8,typed_envelopes_rejected=8,inherited_pins=308,by_scene=meta)


def mutations(d):
    k=next(i for i,x in enumerate(d["records"])if x["result"]["envelope"]is not None);rejected=0
    for n in range(8):
        a=copy.deepcopy(d);r=a["records"][k]["result"];v=r["envelope"]
        if n==0:v["pair_bytes"]=8
        elif n==1:v["word_type"]="IEEE754_BINARY32"
        elif n==2:v["certificates"][0]["retained_length_error_bound"]=[0,1]
        elif n==3:v["source_uncertainty_cancelled"]=True
        elif n==4:v["native_root_record_sha256"]="0"*64
        elif n==5:v["payload_hex"]=v["payload_hex"][:32]+"0"*32
        elif n==6:r["HOST_roundtrip"]["word_hex"][1]="0000000000000000"
        else:r["scene_engine_admitted"]=True
        try:verify_capture(a,verify_parent=False)
        except (AssertionError,ValueError,TypeError,KeyError,IndexError):rejected+=1
        else:raise AssertionError("mutation_accepted:"+str(n))
    return rejected


def run():
    import oblique_scene_pair64_payload_CPU_v1 as c
    abi,native,ref,orig,pins,_,_=c.retained();records=[]
    for k in abi:
        q=c.selector(k,abi,native,ref,orig)
        records.append(dict(id=k,request=q,result=c._audit(q,abi,native,ref,orig)))
    x=next(x for x in records if x["result"]["envelope"]is not None);q=x["request"];env=x["result"]["envelope"]
    invalid=[]
    for key in ("policy","backend","ABI_record_sha256","native_root_receipt_sha256","native_root_record_sha256",
                "original_snapshot_sha256","original_query_sha256","reference_record_sha256"):
        bad=dict(q);bad[key]="unsealed_or_pair32_repair"
        invalid.append(dict(request=bad,result=c._audit(bad,abi,native,ref,orig)))
    typed=[]
    for n in range(8):
        bad=copy.deepcopy(env)
        if n==0:bad["pair_bytes"]=8
        elif n==1:bad["word_type"]="IEEE754_BINARY32"
        elif n==2:bad["artifact_kind"]="phase_scalar64"
        elif n==3:bad["artifact_kind"]="EFT_difference_two_pairs"
        elif n==4:bad["payload_hex"]=bad["payload_hex"][:32]
        elif n==5:bad["version"]=True
        elif n==6:bad["wavelength_known"]=True
        else:bad["certificates"][0]["retained_length_error_bound"]=[0,1]
        typed.append(dict(envelope=bad,result=c._audit(q,abi,native,ref,orig,bad)))
    d=dict(records=records,invalid_selectors=invalid,invalid_envelopes=typed,pins=pins)
    summary=verify_capture(d);summary["mutations_rejected"]=mutations(d)
    assert summary["mutations_rejected"]==8
    print(json.dumps(dict(status="PASS",summary=summary,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
