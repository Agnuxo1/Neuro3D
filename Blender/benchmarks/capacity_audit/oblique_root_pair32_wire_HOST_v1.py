"""Sealed native-pair independent float32 wire; HOST composition, NOT Bpy/shader."""
from pathlib import Path
from fractions import Fraction as F
import json, struct
import oblique_root_hilo_correction_CPU64_v1 as prior
ROOT = Path(__file__).resolve().parents[3]
MODEL = "oblique-root-pair32-wire-HOST-v1"
POLICY = "SEALED_NATIVE_PAIR_INDEPENDENT_COMPONENT_RN32_WIRE_HOST_COMPOSITION"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001-CODEX.json"
PSHA = "6ef5e1e46e9e9f37c4c7051d064598191e76c93737325dc3683e4aeb3e082eef"
require,sha,capture,digest,pair = prior.require,prior.sha,prior.capture,prior.digest,prior.pair


def retained():
    raw = (ROOT/PARENT).read_bytes()
    require(len(raw) == 168330 and sha(raw) == PSHA, "parent_seal")
    r = json.loads(raw);pins = dict(r["code_doc_sha256"])
    require(len(pins) == 292, "parent_pins")
    for p,h in pins.items():
        require(sha((ROOT/p).read_bytes()) == h, "dependency:"+p)
    require(capture(r["independent_pre"])["status"] == "PASS", "parent_oracle")
    d = capture(r["test_run"])["evidence"]
    e = {x["id"]:x for x in d["records"]}
    _,_,reference,orig,_,_ = prior.retained()
    require(set(e) == set(reference) == set(orig) and len(e) == 16, "closed_records")
    pins[PARENT] = PSHA
    return e,reference,orig,pins,d


def rational(p):
    require(type(p) is list and len(p) == 2 and all(type(x) is int for x in p)
            and p[1] > 0, "canonical_rational")
    q = F(*p)
    require(pair(q) == p, "canonical_rational")
    return q


def decode64(w):
    x = prior.exp.decode(w)
    require(abs(x) <= 2**33, "source_component_bound33")
    return x


def wire(words, squared, inherited_bound):
    out = dict(status="STOP_INPUT",reason=None,input_words=words,exact_squared=squared,
        inherited_bound=inherited_bound,cast_ledger=[],partial_packet_hex="",packet_hex=None,
        decoded_words64=None,RN32_casts=0,packet_decode_calls=0,decoded_components=0,
        Q64=None,Q32=None,signed_transport_error=None,transport_error_bound=None,
        composed_length_error_bound=None,HOST_enclosure=None,drop_lo_simulation=None,
        new_products=0,new_sums=0,new_sqrt_calls=0,retained_numeric_replays=0,
        full_costs="UNKNOWN_NOT_ZERO")
    try:
        require(type(words) is list and len(words) == 2, "pair2_input")
        xs = [decode64(w) for w in words]
        S,B = rational(squared),rational(inherited_bound)
        Q = sum((F.from_float(x) for x in xs),F(0))
        require(0 < Q <= 2**33 and 0 < S <= 2**66 and B >= 0 and Q-B > 0
                and (Q-B)**2 <= S <= (Q+B)**2, "inherited_enclosure")
        out["Q64"] = pair(Q)
        chunks = []
        for i,x in enumerate(xs):
            raw = struct.pack("<f",x) # ONLY independent RN32: no HOST residual injection.
            chunks.append(raw)
            out["RN32_casts"] += 1
            out["partial_packet_hex"] = b"".join(chunks).hex()
            out["cast_ledger"].append(dict(index=i,input_word64=words[i],output_word32=raw.hex()))
            u = int.from_bytes(raw,"little");exponent = (u>>23)&255;mantissa = u&((1<<23)-1)
            require(exponent != 255 and (exponent != 0 or mantissa == 0)
                    and (exponent != 0 or mantissa != 0 or x == 0.0),
                    "target_normal_zero_no_underflow:"+str(i))
        packet = b"".join(chunks)
        decoded = struct.unpack("<ff",packet) # CPU format decode, NOT FP32 ALU addition.
        out.update(packet_decode_calls=1,decoded_components=2,
                   decoded_words64=[struct.pack("<d",v).hex() for v in decoded])
        q = sum((F.from_float(v) for v in decoded),F(0))
        E = Q-q;budget = B+abs(E)
        require(q-budget > 0 and (q-budget)**2 <= S <= (q+budget)**2, "composed_enclosure")
        single = F.from_float(decoded[0]);lost = q-single;single_budget = budget+abs(lost)
        require(single-single_budget > 0 and (single-single_budget)**2 <= S <= (single+single_budget)**2,
                "drop_lo_composed_enclosure")
        out.update(status="CPU_FORMAT_PAIR32_HOST_BOUND_ONLY",reason="independent_RN32_not_engine",
            packet_hex=packet.hex(),Q32=pair(q),signed_transport_error=pair(E),
            transport_error_bound=pair(abs(E)),composed_length_error_bound=pair(budget),
            HOST_enclosure=[pair(q-budget),pair(q+budget)],
            drop_lo_simulation=dict(scope="SIMULATED_CONSUMER_DROPS_LO_NOT_BPY_SHADER",
                nominal_single=pair(single),signed_discarded_low=pair(lost),
                composed_length_error_bound=pair(single_budget),
                HOST_enclosure=[pair(single-single_budget),pair(single+single_budget)],
                extra_RN32_casts=0))
    except (ValueError,TypeError,OverflowError,KeyError,struct.error) as ex:
        out["reason"] = str(ex)
    return out


def selector(k,e,reference,orig):
    o = orig[k];q = o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),reference_record_sha256=digest(reference[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),
        original_query_sha256=digest(q))


def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,
        RN32_casts=0,packet_decode_calls=0,decoded_components=0,new_products=0,new_sums=0,
        new_sqrt_calls=0,retained_numeric_replays=0,native_length=None,phase_error_bound=None,
        phase_certified=False,wavelength_known=False,physical_reference_certified=False,
        GPU_used=False,Bpy_used=False,shader_used=False,source_uncertainty_cancelled=False,
        full_costs="UNKNOWN_NOT_ZERO",promotion="STOP_CONSUMER_BPY_SHADER_SCENE_PHASE_PHYSICAL_GPU",
        scope="CPU_FORMAT_TEST_HOST_COMPOSITION_SEALED_NATIVE_PAIR_ORIGINAL_BOX_ONLY")


def _audit(q,e,reference,orig):
    out = baseline()
    try:
        require(type(q) is dict and type(q.get("record_id")) is str and q["record_id"] in e,"closed_record")
        k = q["record_id"]
        require(q == selector(k,e,reference,orig) and all(type(v) is str for v in q.values()),"closed_selector")
        p = e[k]["result"]
        out.update(request_sha256=digest(q),upstream_status=p["status"],
                   retained_canonical_status=p["retained_canonical_status"])
        if p["status"] != "CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued")
            return out
        z,o = reference[k]["result"]["diagnostic"],orig[k]
        require(z["original_scene"] == o["scene"] and z["original_query"] == o["scene_query"],"original_box_binding")
        packets = []
        out["diagnostic"] = dict(packets=packets,original_snapshot_sha256=digest(o["scene"]),
                                 source="SOURCE0",detector="DETECTOR0",units="scene_length")
        for i,c in enumerate(p["diagnostic"]["corrections"]):
            r = c["result"]
            require(r["exact_squared"] == z["extrema"]["squared"][i],"same_original_squared")
            v = wire(r["root_pair_words"],r["exact_squared"],r["length_error_bound"])
            packets.append(dict(bound=c["bound"],result=v))
            for n in ("RN32_casts","packet_decode_calls","decoded_components"):out[n] += v[n]
            require(v["status"] == "CPU_FORMAT_PAIR32_HOST_BOUND_ONLY","wire_STOP")
        a,b = (x["result"] for x in packets)
        low,high = F(*a["HOST_enclosure"][0]),F(*b["HOST_enclosure"][1])
        rw = F(*z["reference_width"]);B = max(F(*v["composed_length_error_bound"]) for v in (a,b))
        nominals = [F(*v["drop_lo_simulation"]["nominal_single"]) for v in (a,b)]
        slo,shi = F(*a["drop_lo_simulation"]["HOST_enclosure"][0]),F(*b["drop_lo_simulation"]["HOST_enclosure"][1])
        out["diagnostic"].update(HOST_wire_length_interval=[pair(low),pair(high)],interval_width=pair(high-low),
            reference_interval=z["reference_interval"],reference_width=z["reference_width"],
            width_over_reference=pair((high-low)/rw),max_composed_length_error_bound=pair(B),
            error_bound_over_reference_width=pair(B/rw),
            drop_lo_nominal_interval=[pair(v) for v in nominals],drop_lo_nominal_width=pair(nominals[1]-nominals[0]),
            drop_lo_HOST_interval=[pair(slo),pair(shi)],drop_lo_HOST_width=pair(shi-slo),
            HOST_ratio_divisions=2)
        out.update(status="CPU_PAIR32_WIRE_HOST_ORIGINAL_BOX_BOUND_ONLY",reason="wire_format_not_scene_consumer")
    except (ValueError,TypeError,KeyError,IndexError,OSError,OverflowError) as ex:
        out["reason"] = str(ex)
    return out


def audit(q):
    try:e,reference,orig,_,_ = retained()
    except (ValueError,TypeError,KeyError,OSError) as ex:
        out = baseline();out["reason"] = "evidence_integrity:"+str(ex);return out
    return _audit(q,e,reference,orig)
