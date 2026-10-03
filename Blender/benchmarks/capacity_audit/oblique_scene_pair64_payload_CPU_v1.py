"""Opt-in typed scene ROOT64 payload producer/parser; no floating computation."""
from pathlib import Path
import json
import oblique_consumer_ABI_static_v1 as previous
import oblique_root_pair32_wire_HOST_v1 as native_input
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-scene-pair64-payload-CPU-v1"
POLICY="EXPLICIT_ROOT64_PRE_WIRE_BYTES_NOT_PAIR32_REPAIR_OR_ENGINE"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-CONSUMER-ABI-STATIC-001-CODEX.json"
PSHA="438b21c4affc14c6050e4ce5e856f0518dad5d95ce6ea5e8cc04f4beaf09d137"
ROOT_PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001-CODEX.json"
ROOT_SHA="6ef5e1e46e9e9f37c4c7051d064598191e76c93737325dc3683e4aeb3e082eef"
require,sha,capture,digest=previous.require,previous.sha,previous.capture,previous.digest


def retained():
    raw=(ROOT/PARENT).read_bytes()
    require(len(raw)==265694 and sha(raw)==PSHA,"parent_seal")
    receipt=json.loads(raw);pins=dict(receipt["code_doc_sha256"])
    require(len(pins)==307,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(receipt["independent_pre"])["status"]=="PASS","parent_oracle")
    d=capture(receipt["test_run"])["evidence"];abi={x["id"]:x for x in d["records"]}
    native,ref,orig,_,root_capture=native_input.retained()
    require(set(abi)==set(native)==set(ref)==set(orig)and len(abi)==16,"closed_records")
    require(pins.get(ROOT_PARENT)==ROOT_SHA,"explicit_root_parent")
    pins[PARENT]=PSHA
    return abi,native,ref,orig,pins,d,root_capture


def selector(k,abi,native,ref,orig):
    o=orig[k];query=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        ABI_record_sha256=digest(abi[k]),native_root_receipt_sha256=ROOT_SHA,
        native_root_record_sha256=digest(native[k]),reference_record_sha256=digest(ref[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),
        original_query_sha256=digest(query))


def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,envelope=None,HOST_roundtrip=None,
        pair_hex_builds=0,byte_decode_calls=0,integer_word_reads=0,float_decode_calls=0,
        RN_nodes_executed=0,new_products=0,new_sums=0,new_sqrt_calls=0,
        retained_numeric_replays=0,native_length=None,phase_error_bound=None,
        phase_certified=False,wavelength_known=False,scene_engine_admitted=False,
        GPU_used=False,Bpy_used=False,shader_used=False,foreign_source_executed=False,
        source_uncertainty_cancelled=False,physical_reference_certified=False,
        full_costs="UNKNOWN_NOT_ZERO",scope="CPU_TYPED_ROOT64_LENGTH_BOUND_BYTES_HOST_PARSER_ONLY",
        promotion="STOP_REAL_PAIR64_CONSUMER_SCENE_PHASE_GUARD_AND_COSTS")


def expected_envelope(k,q,abi,native,ref,orig):
    n=native[k]["result"];a=abi[k]["result"];z=n["diagnostic"];r=ref[k]["result"]["diagnostic"]
    require(n["status"]=="CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY","native_root_eligible")
    require(a["status"]=="STATIC_CONSUMER_ABI_UNBOUND"and
            a["upstream_status"]=="STOP_SCALAR_PAIR_CONSUMPTION_LOSS","legacy_STOP_preserved")
    require(r["original_scene"]==orig[k]["scene"]and r["original_query"]==orig[k]["scene_query"],
            "same_original_box")
    bounds=[];packets=[]
    require(len(z["corrections"])==2,"two_bounds")
    for i,x in enumerate(z["corrections"]):
        v=x["result"];words=v["root_pair_words"]
        require(x["bound"]==("lower","upper")[i]and v["status"]=="CPU64_NATIVE_ROOT_PAIR_HOST_BOUND_ONLY",
                "bound_status")
        require(type(words)is list and len(words)==2 and all(type(w)is str and len(w)==16
                    and all(c in "0123456789abcdef"for c in w)for w in words),"canonical_pair64_hex")
        require(v["exact_squared"]==r["extrema"]["squared"][i],"same_original_squared")
        packets.append("".join(words)) # Preserve words, no rounding, renormalization, decoding or sum.
        bounds.append(dict(bound=x["bound"],exact_squared=v["exact_squared"],
            retained_exact_pair_sum=v["candidate_sum"],retained_length_error_bound=v["length_error_bound"],
            retained_HOST_enclosure=v["HOST_enclosure"]))
    payload="".join(packets)
    require(len(payload)==64,"payload32_bytes")
    return dict(schema=MODEL,version=1,artifact_kind="scene_length_lower_upper_bounds",
        provenance_branch=POLICY,endianness="little",word_type="IEEE754_BINARY64",
        word_order=["lower_hi","lower_lo","upper_hi","upper_lo"],pair_bytes=16,pair_count=2,
        payload_bytes=32,payload_hex=payload,
        payload_hex_ASCII_sha256=sha(payload.encode("ascii")),selector_sha256=digest(q),
        original_snapshot_sha256=q["original_snapshot_sha256"],original_query_sha256=q["original_query_sha256"],
        original_record_sha256=q["original_record_sha256"],reference_record_sha256=q["reference_record_sha256"],
        native_root_receipt_sha256=ROOT_SHA,native_root_record_sha256=q["native_root_record_sha256"],
        ABI_receipt_sha256=PSHA,ABI_record_sha256=q["ABI_record_sha256"],
        source="SOURCE0",detector="DETECTOR0",units="scene_length",
        source_uncertainty_cancelled=False,legacy_ABI_status=a["status"],
        legacy_scalar_gate=a["upstream_status"],retained_canonical_status=n["retained_canonical_status"],
        certificates=bounds,consumer_binding_proven=False,phase_error_bound=None,wavelength_known=False)


def _audit(q,abi,native,ref,orig,incoming=None):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in abi,"closed_record")
        k=q["record_id"]
        require(q==selector(k,abi,native,ref,orig)and all(type(v)is str for v in q.values()),"closed_selector")
        n=native[k]["result"];a=abi[k]["result"]
        out.update(request_sha256=digest(q),native_upstream_status=n["status"],
                   retained_ABI_status=a["status"],retained_canonical_status=n["retained_canonical_status"])
        if n["status"]!="CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        env=expected_envelope(k,q,abi,native,ref,orig)
        out["pair_hex_builds"]=2
        require(incoming is None or (type(incoming)is dict and digest(incoming)==digest(env)
                                    and incoming==env),"closed_typed_envelope")
        out["envelope"]=env
        # Only own HOST parser consumes these bytes. NOT any frozen shader ABI.
        raw=bytes.fromhex(env["payload_hex"]);out["byte_decode_calls"]=1
        require(len(raw)==32,"payload32_bytes")
        words=[]
        for i in range(4):
            chunk=raw[8*i:8*i+8];word=int.from_bytes(chunk,"little");out["integer_word_reads"]+=1
            exponent=(word>>52)&2047;mantissa=word&((1<<52)-1)
            require(exponent!=2047 and (exponent!=0 or mantissa==0),"normal_zero_word:"+str(i))
            words.append(chunk.hex())
        require(words==[w for x in n["diagnostic"]["corrections"]for w in x["result"]["root_pair_words"]],
                "exact_word_roundtrip")
        out.update(HOST_roundtrip=dict(payload_bytes=32,word_hex=words,
                    payload_hex=raw.hex(),consumer="OWN_HOST_TYPED_PARSER_NO_NUMERIC_RECOMPOSITION"),
            status="CPU_HOST_PAIR64_LENGTH_BYTES_ONLY",reason="producer_and_HOST_parser_not_scene_engine")
    except (ValueError,TypeError,KeyError,IndexError,OSError)as ex:out["reason"]=str(ex)
    return out


def audit(q,incoming=None):
    try:
        abi,native,ref,orig,_,_,_=retained()
        return _audit(q,abi,native,ref,orig,incoming)
    except (ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]=str(ex);return out
