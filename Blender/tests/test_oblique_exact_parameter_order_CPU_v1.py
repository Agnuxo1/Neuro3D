"""Focused new exact CPU method; read pinned prior capture, never execute old producer."""
from pathlib import Path
from fractions import Fraction as F
import base64, hashlib, importlib.util, json, struct, zlib

ROOT = Path(__file__).resolve().parents[2]
PARENT = "coordinacion/respuestas/PRECISION-THIN-GAP-FALSE-TIE-CPU-001-CODEX.json"
PARENT_SHA = "406ce6757503aa41cfc0aa6f42b4f550a401ef675294df460100f5f67501dfac"
CORE = "Blender/benchmarks/capacity_audit/oblique_exact_parameter_order_CPU_v1.py"


def run():
    raw = (ROOT/PARENT).read_bytes()
    assert len(raw) == 120733 and hashlib.sha256(raw).hexdigest() == PARENT_SHA
    parent = json.loads(raw)
    pins = dict(parent["code_doc_sha256"]); pins[PARENT] = PARENT_SHA
    for p, h in pins.items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p
    cap = parent["test_run"]
    decoder = zlib.decompressobj()
    payload = decoder.decompress(base64.b64decode(cap["stdout_zlib_base64"], validate=True), 1048577)
    assert len(payload) <= 1048576 and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
    assert cap["rc"] == 0 and not cap["timed_out"]
    assert len(payload) == cap["stdout_bytes"] and hashlib.sha256(payload).hexdigest() == cap["stdout_sha256"]
    old = json.loads(payload)
    spec = importlib.util.spec_from_file_location("own_exact_parameter_cpu", ROOT/CORE)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    evidence = []
    for case in old["cases"]:
        original = list(struct.unpack("<24I", bytes.fromhex(case["raw_word_bundle_hex"])))
        gap = F(*case["gap_BU"])
        for rotation in range(3):
            for swap in (False, True):
                for winding in (False, True):
                    vectors = [original[i:i+3] for i in range(0, 24, 3)]
                    vectors = [v[rotation:]+v[:rotation] for v in vectors]
                    if winding:
                        vectors[3], vectors[4] = vectors[4], vectors[3]
                        vectors[6], vectors[7] = vectors[7], vectors[6]
                    if swap:
                        vectors[2:5], vectors[5:8] = vectors[5:8], vectors[2:5]
                    words = [w for v in vectors for w in v]
                    result = m.audit_raw_stage(words)
                    if gap:
                        chosen = int(swap)
                        assert result["status"] == "UNIQUE_TWO_TRIANGLES_CPU_ONLY"
                        assert result["candidate_index"] == chosen
                        expected = [gap, F(1), F(1)]
                        expected = expected[rotation:] + expected[:rotation]
                        assert result["exact_candidate_point"] == [m.pair(x) for x in expected]
                        assert F(*result["triangles"][chosen]["t"]) == 1-gap
                    else:
                        assert result["status"] == "STOP_EXACT_TIE"
                        assert result["candidate_index"] is None and result["exact_candidate_point"] is None
                    for flag in ("GPU_launch_allowed","launch_exclusion_allowed","native_precision_certified",
                                 "nearest_hit_certified","full_path_visibility_certified","phase_certified",
                                 "transport_hilo_implemented"):
                        assert result[flag] is False
                    evidence.append({"case":case["label"],"rotation":rotation,"swap":swap,
                                     "winding":winding,"raw_words":words,"result":result})
    base = list(struct.unpack("<24I", bytes.fromhex(old["cases"][0]["raw_word_bundle_hex"])))
    invalid = [[],base[:-1],base+[0],str(base),dict(enumerate(base))]
    for word in (True, 1.0, -1, 1<<32, 0x7f800000, 0x7fc00001, 1, 0x80000000, 0x7f7fffff):
        q = base.copy(); q[6] = word; invalid.append(q)
    q = base.copy(); q[3:6] = [0,0,0]; invalid.append(q)
    for words in invalid:
        try:
            m.audit_raw_stage(words)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid data admitted")
    stops = []
    for kind in ("degenerate", "parallel", "contact", "boundary", "miss"):
        words = base.copy()
        if kind == "degenerate": words[9:12] = words[6:9]
        if kind == "parallel": words[3:6] = [0,0x3f800000,0]
        if kind == "contact": words[:3] = [words[6],0x3f800000,0x3f800000]
        if kind == "boundary": words[1] = 0
        if kind == "miss": words[1] = 0x41000000
        result = m.audit_raw_stage(words)
        assert result["candidate_index"] is None and result["exact_candidate_point"] is None
        assert result["status"] == ("MISS_TWO_TRIANGLES_CPU_ONLY" if kind == "miss" else "STOP_UNRESOLVED_TRIANGLE")
        stops.append({"kind":kind,"raw_words":words,"result":result})
    first = m.audit_raw_stage(base); first["triangles"][0]["point"][0][0] = 123
    assert m.audit_raw_stage(base)["exact_candidate_point"][0] == [1,1<<60]
    assert old["zero_error_gate"] == parent["zero_error_gate"]
    assert old["prior_scalar_errors"] == 72 and old["prior_error_rows"] == 16 and old["prior_contact_STOP"] == 12
    return {"status":"PASS_EXACT_TWO_TRIANGLES_CPU_ORDER_ONLY_NO_NATIVE_PROMOTION",
            "context_pins":pins,"evidence":evidence,"negative_cases":stops,
            "variants":len(evidence),"unique":36,"genuine_tie_STOP":12,
            "malformed_rejections":len(invalid),"geometric_negative_controls":len(stops),
            "independent_return_mutation_check":True,
            "prior_zero_error_gate":old["zero_error_gate"],"prior_scalar_errors":72,
            "prior_error_rows":16,"prior_contact_STOP":12,"GPU_used":False,"Bpy_used":False,
            "RT_used":False,"old_producer_executions":0,"original_scene_queries_replayed":0,
            "phase_error_bound":None,"full_costs":"UNKNOWN_NOT_ZERO"}

if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True))
