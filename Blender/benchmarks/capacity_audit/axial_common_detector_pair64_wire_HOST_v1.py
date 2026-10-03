"""Opt-in HOST pair64 wire contract. Not a shader, GPU ABI, or physical-field admission."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import base64, hashlib, json, math, re, struct, zlib
ROOT = Path(__file__).resolve().parents[3]
MODEL = "precision-axial-common-detector-pair64-wire-HOST-v1"
ABI = "HOST_LE_U32_PAIR64_PHASE_V1_NOT_GPU_ABI"
PARENT = "coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-TWOFOLD-CPU-001-CODEX.json"
PARENT_SHA = "f1dbec5a319c80cc0457d0e32f848641bf752329ccb3e9db687c9cf3c9520b6b"
KEYS = {"case", "result_sha256", "original_scene_sha256", "literal_request_sha256", "abi", "units"}
FLAGS = ("GPU_executed", "native_promotion_allowed", "physical_scene_authenticated",
         "native_hit_coverage_certified", "length_reference_phase_bound_certified",
         "mirror_material_certified", "full_field_certified",
         "coherent_field_admission_allowed", "interference_phase_certified")
class WireStop(ValueError):
    pass
def require(ok, why):
    if not ok:
        raise WireStop(why)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
def rational(value):
    require(type(value) is list and len(value) == 2 and all(type(x) is int for x in value)
            and value[1] > 0, "typed_rational")
    return F(*value)
def pair(value):
    return [value.numerator, value.denominator]
def ieee(word):
    require(type(word) is int and 0 <= word < 2**64, "typed_IEEE64_word")
    value = struct.unpack("<d", word.to_bytes(8, "little"))[0]
    require(math.isfinite(value), "finite_IEEE64_word")
    return value
def load_retained():
    raw = (ROOT / PARENT).read_bytes()
    require(len(raw) <= 1024*1024 and sha(raw) == PARENT_SHA, "sealed_parent_identity")
    receipt = json.loads(raw)
    require(len(receipt["code_doc_sha256"]) == 62, "complete_parent_pins")
    for name, expected in receipt["code_doc_sha256"].items():
        require(sha((ROOT / name).read_bytes()) == expected, "sealed_dependency_identity")
    run = receipt["test_run"]
    require(run["rc"] == 0 and run["timed_out"] is False, "retained_run_not_PASS")
    stream = zlib.decompressobj()
    data = stream.decompress(base64.b64decode(run["stdout_zlib_base64"], validate=True), 1024*1024+1)
    require(len(data) <= 1024*1024 and stream.eof and not stream.unused_data
            and not stream.unconsumed_tail, "closed_bounded_parent_payload")
    require(len(data) == run["stdout_bytes"] and sha(data) == run["stdout_sha256"], "parent_payload_integrity")
    document = json.loads(data)
    require(document["status"] == "PASS" and document["tests"] == 7, "sealed_suite_identity")
    return document["data"]
def select(case="exact"):
    data = load_retained()
    result = data["results"][case]
    request = data["requests"][case]
    return {"case": case, "result_sha256": digest(result),
            "original_scene_sha256": request.get("original_scene_sha256"),
            "literal_request_sha256": request.get("literal_request_sha256"),
            "abi": ABI, "units": "cycles/rad"}
def resolve(request, model):
    require(type(model) is str and model == MODEL, "explicit_model_required")
    require(type(request) is dict and set(request) == KEYS
            and all(type(x) is str for x in request.values()), "closed_typed_selector")
    require(request["abi"] == ABI and request["units"] == "cycles/rad", "explicit_wire_contract")
    data = load_retained()
    require(request["case"] in data["results"], "retained_case_identity")
    result = data["results"][request["case"]]
    old_request = data["requests"][request["case"]]
    require(request["result_sha256"] == digest(result), "sealed_result_binding")
    require(request["original_scene_sha256"] == old_request["original_scene_sha256"], "original_scene_binding")
    require(request["literal_request_sha256"] == old_request["literal_request_sha256"], "literal_request_binding")
    require(result["status"] == "CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY", "retained_STOP_no_buffer")
    require(result["representation"] == "PAIR_FLOAT64_CPU_NOT_GPU_ABI"
            and all(result[k] is False for k in FLAGS), "retained_CPU_not_native_or_physical")
    require(result["literal_request_sha256"] == request["literal_request_sha256"], "literal_result_binding")
    require(len(result["rows"]) == 2 and result["emitted_sources"] == result["rows"], "ALL_SOURCE_atomic_parent")
    require([(x["source_id"], x["branch_id"]) for x in result["rows"]]
            == [("S0", "S0/mirror"), ("S1", "S1/mirror")]
            and result["relative"]["source_order"] == ["S0", "S1"], "source_branch_order")
    rows = result["rows"] + [result["relative"]]
    words = []
    for row in rows:
        require(type(row["pair_uint64"]) is list and len(row["pair_uint64"]) == 2, "pair64_not_singleword")
        values = [ieee(w) for w in row["pair_uint64"]]
        represented = F(values[0]) + F(values[1])  # exact diagnostic: never RN64 hi+lo
        bound = rational(row["total_cycle_error_bound"])
        require(bound >= 0 and rational(row["total_phase_bound_rad"]) == 8*bound, "retained_phase_bound")
        require(rational(row["budget_rad"]) >= 0 and 8*bound <= rational(row["budget_rad"])
                and row["budget_fits"] is True, "ALL_SOURCE_and_relative_caps")
        require(represented == rational(row["represented_cycles"])
                and abs(represented-rational(row["original_declared_cycles"])) <= bound,
                "retained_pair_enclosure")
        words.extend(row["pair_uint64"])
    return result, words
def expected_envelope(request, result, words):
    limbs = [limb for w in words for limb in (w & 0xffffffff, w >> 32)]
    raw = struct.pack("<12I", *limbs)
    return {"abi": ABI, "model": MODEL, "parent_receipt_sha256": PARENT_SHA,
            "result_sha256": request["result_sha256"],
            "parent_request_sha256": result["request_sha256"],
            "literal_request_sha256": request["literal_request_sha256"],
            "original_scene_sha256": request["original_scene_sha256"],
            "units": "cycles/rad", "endian": "little", "record_count": 3, "record_stride_bytes": 16,
            "payload_bytes": 48, "record_ids": ["S0", "S1", "S0-minus-S1"],
            "branch_ids": ["S0/mirror", "S1/mirror", "relative"],
            "word_layout": ["hi.lo32", "hi.hi32", "lo.lo32", "lo.hi32"],
            "phase_contract_sha256": digest({"rows": result["rows"], "relative": result["relative"]}),
            "payload_hex": raw.hex(), "payload_sha256": sha(raw)}
def output(operation):
    out = {"model": MODEL, "abi": ABI, "operation": operation, "status": "STOP", "reason": None,
           "envelope": None, "decoded_rows": [], "parent_receipt_sha256": PARENT_SHA,
           "phase_arithmetic_RN_executed": 0, "producer_replays": 0, "parameter_encoder_replays": 0,
           "transport_error_cycles": None, "HOST_contract_certified": False,
           "detector_complex_field": None, "detector_power": None, "source_amplitude": None,
           "full_costs": "UNMEASURED_NOT_ZERO"}
    out.update({k: False for k in FLAGS})
    return out
def pack(request, *, model):
    out = output("pack")
    try:
        result, words = resolve(request, model)
        out["envelope"] = expected_envelope(request, result, words)
        out["transport_error_cycles"] = [0, 1]
        out["HOST_contract_certified"] = True
        out["status"] = "HOST_PAIR64_WIRE_PACK_ONLY"
    except (ValueError, TypeError, KeyError, OSError, OverflowError, struct.error, zlib.error) as error:
        out["reason"] = str(error) if isinstance(error, WireStop) else "closed_INPUT:" + type(error).__name__
    return out
def consume(request, envelope, *, model):
    out = output("consume")
    try:
        result, expected_words = resolve(request, model)
        expected = expected_envelope(request, result, expected_words)
        require(type(envelope) is dict and set(envelope) == set(expected), "closed_envelope")
        for key in ("record_count", "record_stride_bytes", "payload_bytes"):
            require(type(envelope[key]) is int, "typed_wire_counts")
        excluded = {"payload_hex", "payload_sha256"}
        require(digest({k: v for k, v in envelope.items() if k not in excluded})
                == digest({k: v for k, v in expected.items() if k not in excluded}), "closed_metadata_binding")
        require(type(envelope["payload_hex"]) is str
                and re.fullmatch("[0-9a-f]{96}", envelope["payload_hex"]) is not None, "canonical_48byte_buffer")
        raw = bytes.fromhex(envelope["payload_hex"])
        require(type(envelope["payload_sha256"]) is str
                and envelope["payload_sha256"] == sha(raw), "payload_sha256")
        limbs = struct.unpack("<12I", raw)
        words = [limbs[i] | (limbs[i+1] << 32) for i in range(0, 12, 2)]
        for word in words:
            ieee(word)
        require(words == expected_words and raw.hex() == expected["payload_hex"], "sealed_word_identity")
        decoded = []
        for i, row in enumerate(result["rows"] + [result["relative"]]):
            hi, lo = words[2*i:2*i+2]
            represented = F(ieee(hi)) + F(ieee(lo))
            require(represented == rational(row["represented_cycles"]), "zero_transport_error")
            decoded.append({"record_id": expected["record_ids"][i], "branch_id": expected["branch_ids"][i],
                            "pair_uint64": [hi, lo], "represented_cycles": pair(represented),
                            "original_declared_cycles": row["original_declared_cycles"],
                            "total_cycle_error_bound": row["total_cycle_error_bound"],
                            "total_phase_bound_rad": row["total_phase_bound_rad"], "budget_rad": row["budget_rad"]})
        # Nothing emitted until every SOURCE, relative pair, metadata, and byte has passed.
        out["decoded_rows"] = deepcopy(decoded)
        out["transport_error_cycles"] = [0, 1]
        out["HOST_contract_certified"] = True
        out["status"] = "HOST_PAIR64_WIRE_ROUNDTRIP_ONLY"
    except (ValueError, TypeError, KeyError, OSError, OverflowError, struct.error, zlib.error) as error:
        out["reason"] = str(error) if isinstance(error, WireStop) else "closed_INPUT:" + type(error).__name__
    return out
