"""CPU emulated scalar32 projection gate; NOT native ALU32/Bpy/shader."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import oblique_root_pair32_wire_HOST_v1 as prior
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-scalar32-consumer-gate-CPU-v1"
POLICY="EMULATED_RN64_ADD_THEN_RN32_PRESERVE_SEALED_PAIR_SUM_EXACTLY"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-PAIR32-WIRE-HOST-001-CODEX.json"
PSHA="580b012d7921d0130852fa082de6e5cc8bdd066340c790d9849fb381355fc111"
require,sha,capture,digest,pair=prior.require,prior.sha,prior.capture,prior.digest,prior.pair


def retained():
    raw=(ROOT/PARENT).read_bytes()
    require(len(raw)==159924 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);require(len(pins)==296,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    d=capture(r["test_run"])["evidence"];e={x["id"]:x for x in d["records"]}
    _,reference,orig,_,_=prior.retained()
    require(set(e)==set(reference)==set(orig)and len(e)==16,"closed_records")
    pins[PARENT]=PSHA
    return e,reference,orig,pins,d


def project(packet,squared,bound):
    out=dict(status="STOP_INPUT",reason=None,input_packet=packet,exact_squared=squared,
        inherited_bound=bound,RN64_adds=0,RN32_casts=0,input_decode_calls=0,output_decode_calls=0,
        decoded_components=0,ledger=None,candidate_word32=None,scalar_word32=None,
        exact_pair_sum=None,HOST_signed_intermediate_error=None,scalar_value=None,
        signed_projection_error=None,projection_error_bound=None,composed_length_error_bound=None,
        HOST_enclosure=None,exact_projection_preserved=None,new_products=0,native_ALU32_sums=0,
        new_sqrt_calls=0,retained_numeric_replays=0,full_costs="UNKNOWN_NOT_ZERO",
        scope="CPU_RN64_ADD_RN32_CAST_EMULATION_NOT_NATIVE_ALU32")
    try:
        require(type(packet)is str and len(packet)==16,"packet8_input")
        raw=bytes.fromhex(packet);require(raw.hex()==packet,"canonical_packet")
        for i in range(2):
            u=int.from_bytes(raw[4*i:4*i+4],"little");exponent=(u>>23)&255;mantissa=u&((1<<23)-1)
            require(exponent!=255 and (exponent!=0 or mantissa==0),"input_normal_zero:"+str(i))
        a,b=struct.unpack("<ff",raw)
        out.update(input_decode_calls=1,decoded_components=2)
        require(abs(a)<=2**33 and abs(b)<=2**33,"component_bound33")
        S,B=prior.rational(squared),prior.rational(bound)
        Q=F.from_float(a)+F.from_float(b)
        require(0<Q<=2**33 and 0<S<=2**66 and B>=0 and Q-B>0
                and (Q-B)**2<=S<=(Q+B)**2,"inherited_enclosure")
        out["exact_pair_sum"]=pair(Q)
        v=a+b # Actual Python binary64 addition. NOT a native binary32 ALU.
        ledger=dict(a_word32=raw[:4].hex(),b_word32=raw[4:].hex(),
                    intermediate_word64=struct.pack("<d",v).hex(),candidate_word32=None)
        out.update(ledger=ledger,RN64_adds=1,HOST_signed_intermediate_error=pair(Q-F.from_float(v)))
        candidate=struct.pack("<f",v)
        ledger["candidate_word32"]=candidate.hex()
        out.update(RN32_casts=1,candidate_word32=candidate.hex())
        u=int.from_bytes(candidate,"little");exponent=(u>>23)&255;mantissa=u&((1<<23)-1)
        require(exponent!=255 and (exponent!=0 or mantissa==0)and not(exponent==0 and mantissa==0),
                "target_positive_normal_no_underflow")
        scalar=struct.unpack("<f",candidate)[0]
        out.update(output_decode_calls=1,decoded_components=3)
        T=F.from_float(scalar);E=Q-T;C=B+abs(E)
        require(T-C>0 and (T-C)**2<=S<=(T+C)**2,"composed_enclosure")
        out.update(scalar_value=pair(T),signed_projection_error=pair(E),
            projection_error_bound=pair(abs(E)),composed_length_error_bound=pair(C),
            HOST_enclosure=[pair(T-C),pair(T+C)],exact_projection_preserved=E==0)
        if E!=0:
            out.update(status="STOP_PROJECTION_LOSS",reason="nonzero_scalar_projection_loss")
        else:
            out.update(status="CPU_EMULATED_SCALAR32_EXACT_PAIR_PROJECTION_ONLY",
                       reason="exact_emulated_projection_not_scene_engine",scalar_word32=candidate.hex())
    except (ValueError,TypeError,KeyError,OverflowError,struct.error)as ex:out["reason"]=str(ex)
    return out


def selector(k,e,reference,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),reference_record_sha256=digest(reference[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),
        original_query_sha256=digest(q))


def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,RN64_adds=0,
        RN32_casts=0,input_decode_calls=0,output_decode_calls=0,decoded_components=0,
        new_products=0,native_ALU32_sums=0,new_sqrt_calls=0,retained_numeric_replays=0,
        native_length=None,phase_error_bound=None,phase_certified=False,wavelength_known=False,
        physical_reference_certified=False,GPU_used=False,Bpy_used=False,shader_used=False,
        source_uncertainty_cancelled=False,full_costs="UNKNOWN_NOT_ZERO",
        promotion="STOP_SCALAR_LOSS_REAL_CONSUMER_SCENE_PHASE_PHYSICAL_GPU",
        scope="CPU_EMULATED_SCALAR_PROJECTION_GATE_ORIGINAL_BOX_NOT_ENGINE")


def _audit(q,e,reference,orig):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        k=q["record_id"]
        require(q==selector(k,e,reference,orig)and all(type(v)is str for v in q.values()),"closed_selector")
        p=e[k]["result"]
        out.update(request_sha256=digest(q),upstream_status=p["status"],
                   retained_canonical_status=p["retained_canonical_status"])
        if p["status"]!="CPU_PAIR32_WIRE_HOST_ORIGINAL_BOX_BOUND_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        z,o=reference[k]["result"]["diagnostic"],orig[k]
        require(z["original_scene"]==o["scene"]and z["original_query"]==o["scene_query"],"original_box_binding")
        attempts=[]
        out["diagnostic"]=dict(attempts=attempts,original_snapshot_sha256=digest(o["scene"]),
                              source="SOURCE0",detector="DETECTOR0",units="scene_length")
        for i,x in enumerate(p["diagnostic"]["packets"]):
            r=x["result"]
            require(r["exact_squared"]==z["extrema"]["squared"][i],"same_original_squared")
            v=project(r["packet_hex"],r["exact_squared"],r["composed_length_error_bound"])
            attempts.append(dict(bound=x["bound"],result=v))
            for n in ("RN64_adds","RN32_casts","input_decode_calls","output_decode_calls","decoded_components"):out[n]+=v[n]
            require(v["status"]in ("STOP_PROJECTION_LOSS","CPU_EMULATED_SCALAR32_EXACT_PAIR_PROJECTION_ONLY"),
                    "scalar_attempt_unavailable")
        a,b=(x["result"]for x in attempts)
        low,high=F(*a["HOST_enclosure"][0]),F(*b["HOST_enclosure"][1])
        nominal=[F(*x["scalar_value"])for x in (a,b)]
        rw=F(*z["reference_width"]);C=max(F(*x["composed_length_error_bound"])for x in (a,b))
        lost=sum(x["status"]=="STOP_PROJECTION_LOSS"for x in (a,b))
        out["diagnostic"].update(HOST_scalar_length_interval=[pair(low),pair(high)],interval_width=pair(high-low),
            nominal_scalar_interval=[pair(x)for x in nominal],nominal_scalar_width=pair(nominal[1]-nominal[0]),
            reference_interval=z["reference_interval"],reference_width=z["reference_width"],
            width_over_reference=pair((high-low)/rw),max_composed_length_error_bound=pair(C),
            error_bound_over_reference_width=pair(C/rw),scalar_attempts_rejected=lost,
            retained_wire_interval_width=p["diagnostic"]["interval_width"],HOST_ratio_divisions=2)
        out.update(status="STOP_SCALAR_PAIR_CONSUMPTION_LOSS"if lost else "CPU_EMULATED_SCALAR_PAIR_EXACT_ONLY",
                   reason="pair_information_not_preserved"if lost else "emulated_exact_not_native_engine")
    except (ValueError,TypeError,KeyError,IndexError,OSError,OverflowError)as ex:out["reason"]=str(ex)
    return out


def audit(q):
    try:e,reference,orig,_,_=retained()
    except (ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _audit(q,e,reference,orig)
