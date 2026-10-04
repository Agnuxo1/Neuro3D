"""New interval tests only; retained captures are data, old producers not imported."""
from pathlib import Path
from fractions import Fraction as F
import base64
import hashlib
import importlib.util
import json
import math
import struct
import sys
import traceback
import zlib

ROOT = Path(__file__).resolve().parents[2]
CORE = "Blender/benchmarks/capacity_audit/oblique_first_hit_interval_CPU_v1.py"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-FIRST-HIT-SHADERC-001-CODEX.json"
PSHA = "47499ec5c242c118fd9357226837c25686826df2b42d0d40510c7bbd8e2e5338"
GI = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
GSHA = "f4814286200766db8494df3f99ff7653d7cf038bd1f51cd34491206a0537016b"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(w):
    assert w["rc"] == 0 and not w["timed_out"]
    decoder = zlib.decompressobj()
    raw = decoder.decompress(base64.b64decode(w["stdout_zlib_base64"], validate=True), 1048577)
    assert len(raw) <= 1048576 and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
    assert len(raw) == w["stdout_bytes"] and sha(raw) == w["stdout_sha256"]
    return json.loads(raw)


def load_data():
    raw = (ROOT/PARENT).read_bytes()
    assert sha(raw) == PSHA
    parent = json.loads(raw)
    pins = dict(parent["code_doc_sha256"])
    pins[PARENT] = PSHA
    for path, expected in pins.items():
        assert sha((ROOT/path).read_bytes()) == expected, path
    graw = (ROOT/GI).read_bytes()
    assert sha(graw) == GSHA
    packets = {r["id"]: r["result"]["packet"] for r in capture(json.loads(graw)["test_run"])["evidence"]["positive"]}
    prior = capture(parent["test_run"])
    assert len(packets) == 6 and len(prior["retained_precision_failures"]) == 16
    return packets, prior, pins


def load_core():
    spec = importlib.util.spec_from_file_location("own_new_interval", ROOT/CORE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(report):
    m = load_core()
    packets, prior, pins = load_data()
    report["context_pins"] = pins
    report["original_cases"] = []
    enclosed_hits = 0
    for case in prior["original_cases"]:
        packet = packets[case["case"]]
        raw = bytes.fromhex(packet["buffer_hex"])
        result = m.evaluate(raw)
        assert result["input_sha256"] == packet["manifest"]["buffer_sha256"]
        comparisons = []
        for current, previous in zip(result["sources"], case["sources"]):
            assert current["source_id"] == previous["candidate"]["source_id"]
            for row, exact, rounded in zip(current["rows"], previous["exact_rows"], previous["candidate"]["rows"]):
                assert row["primitive_id"] == exact["primitive_id"] == rounded["primitive_id"]
                if exact["kind"] != "EXACT_HIT":
                    continue
                assert rounded["kind"] == "FLOAT64_HIT_CANDIDATE"
                errors, radii = [], []
                for label, q, bits in zip(("t", "u", "v"), exact["tuv"], rounded["tuv_binary64_le"]):
                    lo, hi = [F(*x) for x in row[label]]
                    reference = F(*q)
                    candidate = F.from_float(struct.unpack("<d", bytes.fromhex(bits))[0])
                    assert lo <= reference <= hi and lo <= candidate <= hi
                    radius = max(abs(candidate-lo), abs(hi-candidate))
                    error = candidate-reference
                    assert abs(error) <= radius
                    errors.append([error.numerator, error.denominator])
                    radii.append([radius.numerator, radius.denominator])
                comparisons.append(dict(source_id=current["source_id"], primitive_id=row["primitive_id"],
                                        signed_errors=errors, candidate_absolute_error_radius=radii,
                                        zero_error=all(F(*e) == 0 for e in errors)))
                enclosed_hits += 1
        report["original_cases"].append(dict(case=case["case"], scene_sha256=packet["manifest"]["scene_sha256"],
                                            query_sha256=packet["manifest"]["query_sha256"], result=result, comparisons=comparisons))
    assert enclosed_hits == 16
    preserved = [dict(case=c["case"], source_id=x["source_id"], primitive_id=x["primitive_id"], errors=x["signed_errors"])
                 for c in report["original_cases"] for x in c["comparisons"] if not x["zero_error"]]
    old = [dict(case=x["case"], source_id=x["source_id"], primitive_id=x["comparison"]["primitive_id"], errors=x["comparison"]["signed_errors"])
           for x in prior["retained_precision_failures"]]
    assert preserved == old
    report["prior_nonzero_error_rows_preserved"] = preserved
    # Independent host RNE and rational checks, not a device numerical test.
    values = [F(0), F(1, 3), -F(1, 3), F(1)+F(1, 2**53), -F(1)-F(1, 2**53),
              F(1, 2**1075), -F(1, 2**1075), m.MAX64]
    values += [F(a, b)*m.power2(e) for a in (-7, -1, 1, 7) for b in (3, 5) for e in (-500, -30, 0, 200)]
    checks = []
    for x in values:
        lo, hi = m.round_out(x, False), m.round_out(x, True)
        host = F.from_float(float(x))
        assert lo <= x <= hi and lo <= host <= hi
        assert m.round_out(lo, False) == lo and m.round_out(hi, True) == hi
        checks.append(dict(input=[x.numerator, x.denominator], interval=[[lo.numerator, lo.denominator], [hi.numerator, hi.denominator]]))
    report["directed_round_checks"] = checks
    raw = bytes.fromhex(packets["oblique"]["buffer_hex"])
    words = list(struct.unpack("<47I", raw))
    mutations = [("short", raw[:-4]), ("extra", raw+b"\0\0\0\0"), ("wrong_type", True)]
    for label, index, value in (("magic", 0, 0), ("version", 2, 2), ("sources", 3, 1), ("n0", 4, 0), ("n65", 4, 65),
                                ("scalars", 5, 0), ("idcount", 6, 1), ("query_id", 7, 1234), ("reserved", 9, 1),
                                ("duplicate", 11, words[10]), ("id_sign", 10, 2**31), ("nan", 12, 0x7fc00001),
                                ("inf", 12, 0x7f800000), ("subnormal", 12, 1), ("negativezero", 12, 0x80000000),
                                ("domain", 12, 0x4b000000), ("lambda0", 45, 0)):
        w = words.copy()
        w[index] = value
        mutations.append((label, struct.pack("<47I", *w)))
    w = words.copy()
    w[15:18] = [0, 0, 0]
    mutations.append(("zero_direction", struct.pack("<47I", *w)))
    report["input_negatives"] = []
    for label, bad in mutations:
        try:
            m.evaluate(bad)
        except ValueError as error:
            report["input_negatives"].append(dict(id=label, reason=str(error)))
        else:
            raise AssertionError("accepted_input:"+label)
    arithmetic = [("overflow", lambda: m.round_out(m.MAX64+1, True)),
                  ("zero_denominator", lambda: m.Interval(F(1))/m.Interval(F(-1), F(1))),
                  ("bool_scalar", lambda: m.Interval(True)), ("round_bool", lambda: m.round_out(True, True))]
    report["arithmetic_negatives"] = []
    for label, action in arithmetic:
        try:
            action()
        except ValueError as error:
            report["arithmetic_negatives"].append(dict(id=label, reason=str(error)))
        else:
            raise AssertionError("accepted_arithmetic:"+label)
    sources, triangles = m.decode(raw)
    origin, direction = sources[0]
    tri = triangles[0][1]
    controls = dict(contact=m.triangle_enclosure(tri[0], direction, tri),
                    degenerate=m.triangle_enclosure(origin, direction, [tri[0]]*3))
    assert controls["contact"]["classification"].startswith("STOP_")
    assert controls["degenerate"]["classification"].startswith("STOP_")
    # Same two surfaces at the same t, distinct IDs: unresolved ordering, no epsilon.
    w = words.copy()
    w[24:33] = w[33:42]
    tied = m.evaluate(struct.pack("<47I", *w))
    assert all(s["selection"].startswith("STOP_") for s in tied["sources"])
    controls["equal_tie"] = tied
    report["fabricated_stage_controls_NOT_original"] = controls
    report["summary"] = dict(original_cases=6, sources=12, triangle_tests=28, enclosed_hit_rows=enclosed_hits,
                              prior_nonzero_rows_preserved=len(preserved), directed_round_checks=len(checks),
                              input_negatives=len(mutations), arithmetic_negatives=len(arithmetic), fabricated_controls=3,
                              context_pins=len(pins), GPU_used=False, compiler_calls=0, old_producer_executions=0,
                              native_precision_certified=False, phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO")
    report["status"] = "PASS_CPU_ENCLOSURES_ONLY_NATIVE_PHASE_STOP"


if __name__ == "__main__":
    report = dict(status="IN_PROGRESS", GPU_used=False, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    try:
        run(report)
    except Exception as error:
        report.update(status="FAIL_RETAINED", error=str(error), traceback=traceback.format_exc())
        print(json.dumps(report, allow_nan=False))
        sys.exit(1)
    print(json.dumps(report, allow_nan=False))
