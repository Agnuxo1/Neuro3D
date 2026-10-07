"""Opt-in ray-position enclosure; retained parameters are DATA, not nearest hits.

No triangle queries, previous-contact evaluators, roots, native ingress or GPU.
"""
import base64
import copy
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import zlib
from Blender.benchmarks.capacity_audit import oblique_next_triangle_interval_CPU_v1 as ar
from Blender.benchmarks.capacity_audit import original_SOURCE_query_packet_CPU_v1 as packing

ROOT = Path(__file__).resolve().parents[3]
MODEL = "original-SOURCE-next-position-box-CPU-v1"
PINS = {
    "Blender/benchmarks/capacity_audit/oblique_next_triangle_interval_CPU_v1.py":
        "94173ba4dfd8534a4c3556cc8666e3efc2dba175c475d12a7332c10b441af776",
    "coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-QUERY-PACKET-CPU-001-CODEX.json":
        "5f6b3d0ec64df544fc771044796cd88f62967322a879b10fd74fd012a194d272",
    "coordinacion/respuestas/PRECISION-NEXT-TRIANGLE-INTERVAL-CPU-001-CODEX.json":
        "4e64b185a6ebc131c284270318c8793085f17091a27d7eb7ac36cd287e36445e",
    "coordinacion/respuestas/PRECISION-NEXT-LEDGER-CPU-001-CODEX.json":
        "5319af7a02502d5d4d3816ad897963919b0b5bb58bcf66393dfada1b61cba211",
}
QUERY, TRIANGLE, LEDGER = list(PINS)[1:]
UNITS = "unnormalized_reflected_direction_parameter_NOT_BU_length"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def pair(q):
    return [q.numerator, q.denominator]


def interval(value):
    need(type(value) is list and len(value) == 2, "interval2")
    endpoints = []
    for q in value:
        need(type(q) is list and len(q) == 2 and all(type(x) is int for x in q), "rational2")
        n, d = q
        need(d > 0 and math.gcd(n, d) == 1 and max(abs(n).bit_length(), d.bit_length()) <= 4096,
             "canonical_capacity")
        v = F(n, d)
        need(abs(v) <= 1000000, "input_domain")
        need(ar.round_out(v, False) == v == ar.round_out(v, True), "binary64_endpoints")
        endpoints.append(v)
    need(endpoints[0] <= endpoints[1], "ordered_interval")
    return tuple(endpoints)


def box(value):
    need(type(value) is list and len(value) == 3, "box3")
    return [interval(v) for v in value]


def enclose(point_bounds, direction_bounds, parameter_bounds, *, model):
    """Enclose P+tau*D, not tau as length; no hit/visibility inference.

    Exact box is the hull of the Cartesian polynomial. Binary64 box encloses
    separately rounded multiplication and addition, with no FMA/reassociation.
    """
    need(type(model) is str and model == MODEL, "explicit_model")
    point, direction, parameter = box(point_bounds), box(direction_bounds), interval(parameter_bounds)
    exact, rounded = [], []
    for p, d in zip(point, direction):
        products = [t*v for t in parameter for v in d]
        exact.append([pair(p[0]+min(products)), pair(p[1]+max(products))])
        rounded.append((ar.Interval(*p) + ar.Interval(*parameter)*ar.Interval(*d)).json())
    return dict(model=MODEL, status="CONDITIONAL_RAY_POSITION_BOX_ONLY",
                point_box=copy.deepcopy(point_bounds), direction_box=copy.deepcopy(direction_bounds),
                parameter_interval=copy.deepcopy(parameter_bounds), parameter_units=UNITS,
                exact_ray_position_box_BU=exact, modeled_binary64_position_box_BU=rounded,
                assumptions=["binary64_RNE_per_multiply_then_add", "no_FMA_or_reassociation",
                             "gradual_underflow", "declared_boxes_contain_actual_operands"],
                native_precision_certified=False, native_position_error_bound=None,
                triangle_hit_certified=False, nearest_hit_certified=False,
                launch_exclusion_allowed=False, GPU_launch_allowed=False,
                full_path_visibility_certified=False, phase_certified=False,
                phase_error_bound=None, length_reference_phase_bound=None,
                ignored_primitive_ids=[], origin_offset_applied=False,
                full_costs="UNKNOWN_NOT_ZERO")


def capture(receipt, key):
    cap = receipt[key]
    need(cap["rc"] == 0, "capture_rc")
    if key == "final_capture":
        need(cap["before_deadline"] is True, "capture_deadline")
    else:
        need(cap["timed_out"] is False, "capture_timeout")
    decoder = zlib.decompressobj()
    raw = decoder.decompress(base64.b64decode(cap["stdout_zlib_base64"], validate=True), 2097153)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
         and len(raw) <= 2097152 and len(raw) == cap["stdout_bytes"]
         and hashlib.sha256(raw).hexdigest() == cap["stdout_sha256"], "capture_identity")
    return json.loads(raw)


def retained():
    receipts = {}
    for path, sha in PINS.items():
        raw = (ROOT/path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sha, "fixed_pin:"+path)
        if path.endswith(".json"):
            receipts[path] = json.loads(raw)
    r = receipts[QUERY]
    for path, e in r["code_sha256"].items():
        raw = (ROOT/path).read_bytes()
        need(len(raw) == e["bytes"] and hashlib.sha256(raw).hexdigest() == e["sha256"], "query_source_pin")
    dep = r["dependency"]
    need(hashlib.sha256((ROOT/dep["path"]).read_bytes()).hexdigest() == dep["sha256"], "codec_pin")
    q = capture(r, "final_capture")
    need(q["status"] == "PASS", "query_PASS")
    packets = [v["packet"] for v in q["records"] if "packet" in v]
    need(len(packets) == 12, "SOURCE12")
    tri = capture(receipts[TRIANGLE], "test_run")
    ledger = capture(receipts[LEDGER], "test_run")
    # Keep prior failure census as data. No rerun of triangle or ledger producers.
    need(len(tri["new_nonzero_errors_preserved"]) == 72
         and len(tri["prior_nonzero_error_rows_preserved"]) == 16, "retained_failure_census")
    return packets, tri, ledger


def compose(packet, case, source, row, ledger_result, *, model):
    """Caller-conditional composition; parent_receipts=None even if re-sealed."""
    need(type(model) is str and model == MODEL, "explicit_model")
    fixed = packing.audit_packet(packet, expected=packet, model=packing.MODEL)
    slot = fixed["slot"]
    for k in ("case", "input_sha256", "scene_sha256", "query_sha256"):
        need(slot[k] == case[k], "case_binding:"+k)
    need(slot["source_id"] == source["source_id"], "SOURCE_binding")
    need(slot["saved_point_bounds"] == source["point_interval"], "point_binding")
    need(slot["saved_direction_bounds"] == source["reflected_direction_interval"], "direction_binding")
    need(type(row["primitive_id"]) is int and row["primitive_id"] in case["primitive_ids"], "primitive_binding")
    need(slot["previous_primitive_id"] == source["previous_primitive_id"]
         == ledger_result["previous_primitive_id"], "previous_binding")
    previous = [r for r in source["rows"] if r["primitive_id"] == slot["previous_primitive_id"]]
    need(len(previous) == 1 and previous[0]["triangle_words"] == slot["saved_triangle_words"], "previous_geometry_binding")
    matches = [r for r in source["rows"] if r["primitive_id"] == row["primitive_id"]]
    need(len(matches) == 1 and matches[0] == row, "row_binding")
    need(ledger_result["binding"] == [slot[k] for k in
         ("input_sha256", "scene_sha256", "query_sha256", "source_id")], "ledger_binding")
    need(ledger_result["expected_ids"] == case["primitive_ids"], "coverage_binding")
    need(ledger_result["status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES"
         and ledger_result["conditional_first_id"] is None
         and slot["previous_primitive_id"] in ledger_result["unresolved_ids"]
         and ledger_result["ignored_primitive_ids"] == [], "preserve_original_ledger_STOP")
    r = row["result"]
    need(r["parameter_units"] == UNITS and r["status"] in
         ("CONDITIONAL_TRIANGLE_INTERIOR_HIT", "CONDITIONAL_TRIANGLE_MISS",
          "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED"), "retained_row_status_units")
    out = enclose(slot["saved_point_bounds"], slot["saved_direction_bounds"],
                  r["parameter_interval"], model=model)
    out.update(case=slot["case"], source_id=slot["source_id"],
               scene_sha256=slot["scene_sha256"], query_sha256=slot["query_sha256"],
               input_sha256=slot["input_sha256"], source_record_sha256=slot["source_record_sha256"],
               CPU_packet_binding_sha256=fixed["CPU_packet_binding_sha256"],
               primitive_id=row["primitive_id"], previous_primitive_id=slot["previous_primitive_id"],
               upstream_triangle_status=r["status"], upstream_ledger_status=ledger_result["status"],
               conditional_first_id=None, scope="CALLER_CONDITIONAL_CPU_CONTENT_ONLY",
               parent_receipts=None, triangle_geometry_words=copy.deepcopy(row["triangle_words"]))
    return out


def run(*, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    packets, tri, ledger = retained()
    outputs = []
    for case in tri["cases"]:
        for source in case["sources"]:
            candidates = [p for p in packets if p["slot"]["case"] == case["case"]
                          and p["slot"]["source_id"] == source["source_id"]]
            ledgers = [s["result"] for c in ledger["cases"] if c["case"] == case["case"]
                       for s in c["sources"] if s["source_id"] == source["source_id"]]
            need(len(candidates) == len(ledgers) == 1, "fixed_unique_SLOT")
            for row in source["rows"]:
                out = compose(candidates[0], case, source, row, ledgers[0], model=model)
                out["scope"] = "FIXED_CAPTURE_CPU_CONTENT_ONLY_NOT_NATIVE"
                out["parent_receipts"] = {p: PINS[p] for p in (QUERY, TRIANGLE, LEDGER)}
                outputs.append(out)
    need(len(outputs) == 28 and len({(r["case"], r["source_id"], r["primitive_id"])
                                    for r in outputs}) == 28, "fixed28_unique")
    return outputs
