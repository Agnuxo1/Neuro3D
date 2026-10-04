"""New length analysis only; sealed interval/input/reference captures are DATA."""
from pathlib import Path
from fractions import Fraction as F
import base64
import hashlib
import importlib.util
import json
import struct
import sys
import traceback
import zlib

ROOT = Path(__file__).resolve().parents[2]
CORE = "Blender/benchmarks/capacity_audit/oblique_first_segment_length_CPU_v1.py"
PARENT = "coordinacion/respuestas/PRECISION-FIRST-HIT-INTERVAL-CPU-001-CODEX.json"
PSHA = "acbfd299d04df0eeabcda625d579cb1fa16d84834af51a29279dc21ef44d4646"
FIRST = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-FIRST-HIT-SHADERC-001-CODEX.json"
FSHA = "47499ec5c242c118fd9357226837c25686826df2b42d0d40510c7bbd8e2e5338"
GI = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
GSHA = "f4814286200766db8494df3f99ff7653d7cf038bd1f51cd34491206a0537016b"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def captured(w):
    assert w["rc"] == 0 and not w["timed_out"]
    decoder = zlib.decompressobj()
    b = decoder.decompress(base64.b64decode(w["stdout_zlib_base64"], validate=True), 1048577)
    assert len(b) <= 1048576 and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data
    assert len(b) == w["stdout_bytes"] and sha(b) == w["stdout_sha256"]
    return json.loads(b)


def sealed(path, expected):
    b = (ROOT/path).read_bytes()
    assert sha(b) == expected, path
    return json.loads(b)


def load_data():
    parent = sealed(PARENT, PSHA)
    pins = dict(parent["code_doc_sha256"])
    pins[PARENT] = PSHA
    assert len(pins) == 402
    for p, h in pins.items():
        assert sha((ROOT/p).read_bytes()) == h, p
    interval = captured(parent["test_run"])
    first = captured(sealed(FIRST, FSHA)["test_run"])
    inputs = {c["id"]: c["result"]["packet"] for c in captured(sealed(GI, GSHA)["test_run"])["evidence"]["positive"]}
    old = {c["case"]: c for c in first["original_cases"]}
    assert len(inputs) == len(old) == len(interval["original_cases"]) == 6
    assert len(interval["prior_nonzero_error_rows_preserved"]) == len(first["retained_precision_failures"]) == 16
    return interval, inputs, old, pins


def pair(values):
    return tuple(F(*x) for x in values)


def run(report):
    spec = importlib.util.spec_from_file_location("own_new_length", ROOT/CORE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    interval, inputs, old, pins = load_data()
    report["context_pins"] = pins
    report["cases"] = []
    for c in interval["original_cases"]:
        name = c["case"]
        packet = inputs[name]
        b = bytes.fromhex(packet["buffer_hex"])
        words = struct.unpack("<%dI" % (len(b)//4), b)
        base = 10+words[4]
        assert c["result"]["input_sha256"] == sha(b) == packet["manifest"]["buffer_sha256"]
        assert c["scene_sha256"] == packet["manifest"]["scene_sha256"] and c["query_sha256"] == packet["manifest"]["query_sha256"]
        sources = []
        for sid, source in enumerate(c["result"]["sources"]):
            assert source["source_id"] == "S"+str(sid)
            assert source["selection"] == "CONDITIONAL_UNIQUE_FIRST_HIT"
            pid = source["chosen_primitive_id"]
            chosen = [r for r in source["rows"] if r["primitive_id"] == pid]
            assert len(chosen) == 1 and chosen[0]["classification"] == "CONDITIONAL_INTERIOR_HIT"
            direction = tuple(words[base+6*sid+3:base+6*sid+6])
            result = module.enclose(direction, pair(chosen[0]["t"]))
            prior = old[name]["sources"][sid]
            exact = next(r for r in prior["exact_rows"] if r["primitive_id"] == pid)
            assert exact["kind"] == "EXACT_HIT"
            t_ref = F(*exact["tuv"][0])
            ns = F(*result["direction_norm_squared"])
            norm_lo, norm_hi = pair(result["direction_norm_interval"])
            length_lo, length_hi = pair(result["length_interval"])
            t_lo, t_hi = pair(chosen[0]["t"])
            assert t_lo <= t_ref <= t_hi and norm_lo**2 <= ns <= norm_hi**2
            assert length_lo**2 <= t_ref**2*ns <= length_hi**2
            assert result["status"] == "CONDITIONAL_LENGTH_ENCLOSURE"
            assert result["normalized"] is False and result["phase_error_bound"] is None
            sources.append(dict(source_id="S"+str(sid), primitive_id=pid, result=result,
                                retained_t_reference=[t_ref.numerator, t_ref.denominator],
                                exact_length_squared=[(t_ref*t_ref*ns).numerator, (t_ref*t_ref*ns).denominator]))
        report["cases"].append(dict(case=name, input_sha256=sha(b), scene_sha256=c["scene_sha256"],
                                  query_sha256=c["query_sha256"], sources=sources))
    report["prior_nonzero_errors_preserved_as_data"] = interval["prior_nonzero_error_rows_preserved"]
    roots = [F(0), F(1), F(4), F(25), F(2), F(1, 3), F(1, 2**300), F(3*10**12)]
    roots += [F(k, den) for k in (1, 2, 7, 31) for den in (3, 5, 17)]
    report["root_checks"] = []
    for value in roots:
        lo, hi = module.root_interval(value)
        assert 0 <= lo <= hi and lo*lo <= value <= hi*hi and hi-lo <= F(1, 2**96)
        report["root_checks"].append(dict(value=[value.numerator, value.denominator], interval=module.pair_json(lo, hi)))
    word = lambda x: struct.unpack("<I", struct.pack("<f", x))[0]
    a = module.enclose(tuple(word(x) for x in (3, 4, 0)), (F(2), F(2)))
    scaled = module.enclose(tuple(word(x) for x in (6, 8, 0)), (F(1), F(1)))
    assert pair(a["length_interval"]) == pair(scaled["length_interval"]) == (F(10), F(10))
    tiny = module.enclose((0x00800000, 0, 0), (F(1), F(1)))
    assert tiny["status"] == "STOP_LENGTH_ZERO_POSSIBLE" and pair(tiny["length_interval"])[0] == 0
    report["fabricated_controls"] = dict(scaled_original_direction=a, doubled_direction_half_t=scaled,
                                          tiny_normal_direction=tiny, origin="FABRICATED_NOT_ORIGINAL_SCENE")
    good = (0x3f800000, 0, 0)
    bad = [("root_bool", lambda: module.root_interval(True)), ("root_negative", lambda: module.root_interval(F(-1))),
           ("root_capacity", lambda: module.root_interval(F(1 << 4097))),
           ("direction_list", lambda: module.enclose(list(good), (F(1), F(2)))),
           ("direction_bool", lambda: module.enclose((True, 0, 0), (F(1), F(2)))),
           ("word_negative", lambda: module.enclose((-1, 0, 0), (F(1), F(2)))),
           ("word_over", lambda: module.enclose((2**32, 0, 0), (F(1), F(2)))),
           ("word_nan", lambda: module.enclose((0x7fc00001, 0, 0), (F(1), F(2)))),
           ("word_inf", lambda: module.enclose((0x7f800000, 0, 0), (F(1), F(2)))),
           ("word_subnormal", lambda: module.enclose((1, 0, 0), (F(1), F(2)))),
           ("word_negzero", lambda: module.enclose((0x80000000, 0, 0), (F(1), F(2)))),
           ("word_domain", lambda: module.enclose((0x4b000000, 0, 0), (F(1), F(2)))),
           ("direction_zero", lambda: module.enclose((0, 0, 0), (F(1), F(2)))),
           ("t_list", lambda: module.enclose(good, [F(1), F(2)])),
           ("t_bool", lambda: module.enclose(good, (True, F(2)))),
           ("t_zero", lambda: module.enclose(good, (F(0), F(1)))),
           ("t_reverse", lambda: module.enclose(good, (F(2), F(1)))),
           ("t_capacity", lambda: module.enclose(good, (F(1), F(1 << 4097))))]
    report["negatives"] = []
    for label, action in bad:
        try:
            action()
        except ValueError as error:
            report["negatives"].append(dict(id=label, reason=str(error)))
        else:
            raise AssertionError("accepted_negative:"+label)
    report["summary"] = dict(cases=6, first_segments=12, root_checks=len(roots), negatives=len(bad), fabricated_controls=3,
                              context_pins=len(pins), prior_nonzero_rows_preserved=16, intersection_replays=0,
                              old_producer_executions=0, compiler_calls=0, GPU_used=False, Bpy_used=False, RT_used=False,
                              native_length_graph_certified=False, phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO")
    report["status"] = "PASS_CPU_IDEAL_FIRST_LENGTH_ONLY_NATIVE_PHASE_STOP"


if __name__ == "__main__":
    report = dict(status="IN_PROGRESS", GPU_used=False, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    try:
        run(report)
    except Exception as error:
        report.update(status="FAIL_RETAINED", error=str(error), traceback=traceback.format_exc())
        print(json.dumps(report, allow_nan=False))
        sys.exit(1)
    print(json.dumps(report, allow_nan=False))
