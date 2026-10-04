"""New point/reflection computation only; retained intersection captures are data."""
from pathlib import Path
from fractions import Fraction as F
import ast
import base64
import hashlib
import importlib.util
import json
import struct
import sys
import traceback
import zlib

ROOT = Path(__file__).resolve().parents[2]
CORE = "Blender/benchmarks/capacity_audit/oblique_first_hit_reflection_interval_CPU_v1.py"
PARENT = "coordinacion/respuestas/PRECISION-FIRST-SEGMENT-LENGTH-CPU-001-CODEX.json"
PSHA = "9e760690052121564d748ea504f2028f536ce616121fe9f5f2e8b70e9364866c"
PREVIOUS = "Blender/benchmarks/capacity_audit/oblique_first_hit_interval_CPU_v1.py"
ISHA = "96aec84e42054dd4a8b38f774ba6d85ee959ab5a15b53ed72fca12750c375563"
INTERVAL = "coordinacion/respuestas/PRECISION-FIRST-HIT-INTERVAL-CPU-001-CODEX.json"
FIRST = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-FIRST-HIT-SHADERC-001-CODEX.json"
GI = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def captured(w):
    assert w["rc"] == 0 and not w["timed_out"]
    decoder = zlib.decompressobj()
    raw = decoder.decompress(base64.b64decode(w["stdout_zlib_base64"], validate=True), 1048577)
    assert len(raw) <= 1048576 and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
    assert sha(raw) == w["stdout_sha256"] and len(raw) == w["stdout_bytes"]
    return json.loads(raw)


def load_data():
    b = (ROOT/PARENT).read_bytes()
    assert sha(b) == PSHA
    parent = json.loads(b)
    pins = dict(parent["code_doc_sha256"])
    pins[PARENT] = PSHA
    assert len(pins) == 406
    for p, h in pins.items():
        assert sha((ROOT/p).read_bytes()) == h, p
    assert sha((ROOT/PREVIOUS).read_bytes()) == ISHA
    read = lambda p: json.loads((ROOT/p).read_bytes())
    interval = captured(read(INTERVAL)["test_run"])
    first = captured(read(FIRST)["test_run"])
    inputs = {x["id"]: x["result"]["packet"] for x in captured(read(GI)["test_run"])["evidence"]["positive"]}
    assert len(inputs) == len(interval["original_cases"]) == 6
    return interval, {c["case"]: c for c in first["original_cases"]}, inputs, pins


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return (a[0]*b[0]+a[1]*b[1])+a[2]*b[2]


def pair(v):
    return tuple(F(*x) for x in v)


def run(report):
    interval, first, inputs, pins = load_data()
    report["context_pins"] = pins
    names = {"require", "power2", "MAX64", "round_out", "Interval", "scalar32", "sub", "cross", "dot"}
    def subtrees(path):
        nodes = {}
        for n in ast.parse((ROOT/path).read_text(encoding="utf-8")).body:
            name = getattr(n, "name", None)
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
                name = n.targets[0].id
            if name in names:
                nodes[name] = ast.dump(n, include_attributes=False)
        return nodes
    assert subtrees(CORE) == subtrees(PREVIOUS) and len(subtrees(CORE)) == 9
    spec = importlib.util.spec_from_file_location("own_new_reflection", ROOT/CORE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    report["pure_arithmetic_AST_copies"] = dict(count=9, source_sha256=ISHA, old_evaluator_executed=False)
    report["cases"] = []
    nonzero = []
    for case in interval["original_cases"]:
        name = case["case"]
        packet = inputs[name]
        raw = bytes.fromhex(packet["buffer_hex"])
        w = struct.unpack("<%dI" % (len(raw)//4), raw)
        n, base = w[4], 10+w[4]
        assert sha(raw) == case["result"]["input_sha256"] == packet["manifest"]["buffer_sha256"]
        sources = []
        for sid, source in enumerate(case["result"]["sources"]):
            assert source["source_id"] == "S"+str(sid) and source["selection"] == "CONDITIONAL_UNIQUE_FIRST_HIT"
            pid = source["chosen_primitive_id"]
            i = list(w[10:10+n]).index(pid)
            bounds = next(r["t"] for r in source["rows"] if r["primitive_id"] == pid)
            origin = tuple(w[base+6*sid:base+6*sid+3])
            direction = tuple(w[base+6*sid+3:base+6*sid+6])
            vertices = tuple(tuple(w[base+12+9*i+j:base+15+9*i+j]) for j in (0, 3, 6))
            result = m.enclose(origin, direction, vertices, pair(bounds))
            assert result["status"] == "CONDITIONAL_POINT_REFLECTION_ENCLOSURE"
            # Original binary32 promoted exactly; new CPU FLOAT64 graph, not native evidence.
            vals = lambda words: tuple(struct.unpack("<f", struct.pack("<I", x))[0] for x in words)
            of, df = vals(origin), vals(direction)
            af, bf, cf = [vals(v) for v in vertices]
            nf = cross(sub(bf, af), sub(cf, af))
            factorf = (2.0*dot(df, nf))/dot(nf, nf)
            rf = tuple(d-factorf*x for d, x in zip(df, nf))
            previous = first[name]["sources"][sid]
            tref = F(*next(r["tuv"][0] for r in previous["exact_rows"] if r["primitive_id"] == pid))
            tc = struct.unpack("<d", bytes.fromhex(previous["candidate"]["tuv_binary64_le"][0]))[0]
            pf = tuple(o+tc*d for o, d in zip(of, df))
            oq, dq = [tuple(F.from_float(x) for x in v) for v in (of, df)]
            aq, bq, cq = [tuple(F.from_float(x) for x in v) for v in (af, bf, cf)]
            nq = cross(sub(bq, aq), sub(cq, aq))
            fq = 2*dot(dq, nq)/dot(nq, nq)
            rq = tuple(d-fq*x for d, x in zip(dq, nq))
            pq = tuple(o+tref*d for o, d in zip(oq, dq))
            errors = {}
            for label, expected, actual in (("point", pq, pf), ("reflected_direction", rq, rf), ("normal", nq, nf)):
                intervals = result[label+"_interval"]
                rows = []
                for axis, (ex, value, bound) in enumerate(zip(expected, actual, intervals)):
                    lo, hi = pair(bound)
                    candidate = F.from_float(value)
                    assert lo <= ex <= hi and lo <= candidate <= hi
                    error = candidate-ex
                    radius = max(abs(candidate-lo), abs(hi-candidate))
                    assert abs(error) <= radius
                    rows.append(dict(axis=axis, exact=[ex.numerator, ex.denominator], candidate_binary64_le=struct.pack("<d", value).hex(),
                                     signed_error=[error.numerator, error.denominator], error_radius=[radius.numerator, radius.denominator]))
                    if error:
                        nonzero.append(dict(case=name, source_id="S"+str(sid), field=label, axis=axis, signed_error=[error.numerator, error.denominator]))
                errors[label] = rows
            assert pair(result["plane_residual_interval"])[0] <= 0 <= pair(result["plane_residual_interval"])[1]
            assert result["contact_status"] == "STOP_PLANE_CONTACT_ZERO_POSSIBLE" and not result["exact_contact_allowed"]
            sources.append(dict(source_id="S"+str(sid), primitive_id=pid, t_interval=bounds,
                                result=result, CPU_new_graph_vs_exact=errors))
        report["cases"].append(dict(case=name, input_sha256=sha(raw), scene_sha256=packet["manifest"]["scene_sha256"],
                                  query_sha256=packet["manifest"]["query_sha256"], sources=sources))
    report["new_nonzero_errors_preserved"] = nonzero
    report["prior_nonzero_error_rows_preserved_as_data"] = interval["prior_nonzero_error_rows_preserved"]
    assert len(report["prior_nonzero_error_rows_preserved_as_data"]) == 16
    word = lambda x: struct.unpack("<I", struct.pack("<f", x))[0]
    vector = lambda x: tuple(word(y) for y in x)
    o, d = vector((0, 0, 1)), vector((0, 0, -1))
    tri = tuple(vector(v) for v in ((-1, -1, 0), (1, -1, 0), (0, 1, 0)))
    base = m.enclose(o, d, tri, (F(1), F(1)))
    reversed_face = m.enclose(o, d, (tri[0], tri[2], tri[1]), (F(1), F(1)))
    assert base["reflected_direction_interval"] == reversed_face["reflected_direction_interval"]
    zero_normal = m.enclose(o, d, (tri[0],)*3, (F(1), F(1)))
    assert zero_normal["status"] == "STOP_NORMAL_SQUARED_ZERO_POSSIBLE"
    inconsistent = m.enclose(o, d, tri, (F(2), F(2)))
    assert inconsistent["contact_status"] == "STOP_UPSTREAM_SURFACE_INCONSISTENT"
    report["fabricated_controls"] = dict(normal_reversal=[base, reversed_face], degenerate=zero_normal, inconsistent_t=inconsistent,
                                          origin="FABRICATED_NOT_ORIGINAL_SCENE_OR_GPU")
    bad = [("bool_word", lambda: m.enclose((True, 0, 0), d, tri, (F(1), F(1)))),
           ("nan_word", lambda: m.enclose((0x7fc00001, 0, 0), d, tri, (F(1), F(1)))),
           ("subnormal", lambda: m.enclose((1, 0, 0), d, tri, (F(1), F(1)))),
           ("negative_zero", lambda: m.enclose((0x80000000, 0, 0), d, tri, (F(1), F(1)))),
           ("word_over", lambda: m.enclose((2**32, 0, 0), d, tri, (F(1), F(1)))),
           ("domain", lambda: m.enclose((0x4b000000, 0, 0), d, tri, (F(1), F(1)))),
           ("zero_direction", lambda: m.enclose(o, (0, 0, 0), tri, (F(1), F(1)))),
           ("bad_triangle", lambda: m.enclose(o, d, list(tri), (F(1), F(1)))),
           ("t_bool", lambda: m.enclose(o, d, tri, (True, F(1)))),
           ("t_contact", lambda: m.enclose(o, d, tri, (F(0), F(1)))),
           ("t_reverse", lambda: m.enclose(o, d, tri, (F(2), F(1)))),
           ("t_capacity", lambda: m.enclose(o, d, tri, (F(1), F(1 << 4097))))]
    report["negatives"] = []
    for label, action in bad:
        try:
            action()
        except ValueError as error:
            report["negatives"].append(dict(id=label, reason=str(error)))
        else:
            raise AssertionError("accepted_negative:"+label)
    report["summary"] = dict(cases=6, sources=12, point_coordinates=36, reflected_coordinates=36, normal_coordinates=36,
                              prior_nonzero_rows_preserved=16, new_nonzero_coordinates=len(nonzero), negatives=len(bad),
                              fabricated_controls=3, arithmetic_AST_copies=9, context_pins=406, intersection_replays=0,
                              old_producer_executions=0, compiler_calls=0, GPU_used=False, native_precision_certified=False,
                              exact_contact_allowed=False, phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO")
    report["status"] = "PASS_CPU_POINT_REFLECTION_ENCLOSURES_ONLY_CONTACT_NATIVE_PHASE_STOP"


if __name__ == "__main__":
    report = dict(status="IN_PROGRESS", GPU_used=False, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    try:
        run(report)
    except Exception as error:
        report.update(status="FAIL_RETAINED", error=str(error), traceback=traceback.format_exc())
        print(json.dumps(report, allow_nan=False))
        sys.exit(1)
    print(json.dumps(report, allow_nan=False))
