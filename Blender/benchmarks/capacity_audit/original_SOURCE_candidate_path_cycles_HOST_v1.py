"""Opt-in geometric broken-line cycles, conditional on SOURCE/P/Q boxes.

No ideal length transplant, phase evaluator, material model or path admission.
"""
import base64
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from Blender.benchmarks.capacity_audit import oblique_trace_endpoint_length_enclosure_HOST_v1 as norm

ROOT = Path(__file__).resolve().parents[3]
MODEL = "original-SOURCE-candidate-path-cycles-HOST-v1"
ID = "PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001"
PARENTS = {
    "PRECISION-ORIGINAL-SOURCE-NEXT-CHORD-LENGTH-CPU-001-CODEX.json":
        "73aa493db7344763bfc814b9298327e25c96b802ffcba5fdea0c5a87db4b3366",
    "PRECISION-OBLIQUE-TRACE-ENDPOINT-LENGTH-ENCLOSURE-HOST-001-CODEX.json":
        "1bf7f82103218e14d04eec0c630531bfe040f9978c843e7981a7bfb8b3502d9a",
    "PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json":
        "139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e",
}
NORM_PATH = "Blender/benchmarks/capacity_audit/oblique_trace_endpoint_length_enclosure_HOST_v1.py"
NORM_SHA = "8f3b77dba20a755754f1c0da4bc9b779d35056a02240b6602d0c7d1d34d330e8"
CONTEXT = ("case", "source_id", "scene_sha256", "query_sha256", "input_sha256",
           "source_record_sha256", "CPU_packet_binding_sha256", "primitive_id", "previous_primitive_id")
FLAGS = ("native_precision_certified", "native_length_graph_certified", "length_accuracy_budget_admitted",
         "triangle_hit_certified", "nearest_hit_certified", "launch_exclusion_allowed",
         "full_path_visibility_certified", "GPU_launch_allowed", "phase_certified")


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def interval(value):
    need(type(value) is list and len(value) == 2, "interval2")
    lo, hi = map(norm.rat, value)
    need(lo <= hi, "ordered_interval")
    return lo, hi


def box(value):
    need(type(value) is list and len(value) == 3, "box3")
    b = [interval(v) for v in value]
    need(all(max(abs(x), abs(y)) <= 1000000 for x, y in b), "coordinate_domain")
    return b


def base():
    out = dict(model=MODEL, status="STOP_INPUT", cycles_interval=None,
               phase_error_bound=None, native_length_error_bound=None,
               SOURCE_merged=False, origin_offset_applied=False, ignored_primitive_ids=[],
               conditional_first_id=None, full_costs="UNKNOWN_NOT_ZERO",
               source_phase=None, material_phase=None, amplitude=None, field=None, power=None,
               detector_connection_certified=False, first_leg_native_ALU_certified=False,
               physical_optics_certified=False, scene_authenticated=False,
               parent_receipts_sha256=None, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    out.update({f: False for f in FLAGS})
    return out


def enclose(length_BU, reference_BU, wavelength_BU, *, source_id, units, reference_scope, model):
    """Exact HOST Cartesian quotient (L-R)/lambda; unwrapped cycles, not radians.

    Positive wavelength interval is mandatory. No cancellation/correlation
    credit between SOURCEs or a common reference, no modulo reduction.
    """
    need(type(model) is str and model == MODEL, "explicit_model")
    need(type(source_id) is str and source_id in ("S0", "S1"), "SOURCE_identity")
    need(units == "BU" and type(units) is str, "same_declared_BU_NOT_meters")
    need(reference_scope == "GEOMETRIC_TWO_SEGMENT_PATH" and type(reference_scope) is str,
         "total_geometric_path_reference_only")
    length, ref, wave = map(interval, (length_BU, reference_BU, wavelength_BU))
    need(length[0] >= 0 and wave[0] > 0, "nonnegative_length_positive_wavelength")
    delta = (length[0]-ref[1], length[1]-ref[0])
    corners = [a/b for a in delta for b in wave]
    bounds = [min(corners), max(corners)]
    # New arithmetic is bounded too; never increase existing rational/root caps.
    width = bounds[1]-bounds[0]
    need(all(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 512
             for q in (*delta, *corners, width)), "cycle_capacity512")
    out = base()
    out.update(status="CONDITIONAL_GEOMETRIC_PATH_CYCLES_ONLY", source_id=source_id,
               length_BU=copy.deepcopy(length_BU), reference_BU=copy.deepcopy(reference_BU),
               wavelength_BU=copy.deepcopy(wavelength_BU),
               length_minus_reference_BU=[norm.pair(q) for q in delta],
               cycles_interval=[norm.pair(q) for q in bounds],
               cycles_width=norm.pair(width),
               units="BU", result_units="unwrapped_cycles_NOT_radians", reference_scope=reference_scope,
               scope="CALLER_CONDITIONAL_GEOMETRIC_LENGTH_REFERENCE_WAVELENGTH_BOXES_ONLY",
               assumptions=["actual_geometric_two_segment_length_inside_L",
                            "actual_reference_and_positive_wavelength_inside_declared_intervals",
                            "homogeneous_geometric_diagnostic_NOT_optical_path_integral",
                            "HOST_exact_quotient_NOT_native_ALU_or_phase_reduction"])
    return out


def verify_chord(row):
    """Verify captured norm bounds with integer inequalities, no root evaluation."""
    p, q = box(row["point_box"]), box(row["modeled_next_position_box_BU"])
    sqlo = F(0); sqhi = F(0)
    for a, b in zip(p, q):
        lo, hi = b[0]-a[1], b[1]-a[0]
        sqlo += F(0) if lo <= 0 <= hi else min(lo*lo, hi*hi)
        sqhi += max(lo*lo, hi*hi)
    chord = row["chord"]
    need(chord["squared_BU2"] == [norm.pair(sqlo), norm.pair(sqhi)], "chord_squared_binding")
    for squared, key in zip((sqlo, sqhi), ("root_lower_certificate", "root_upper_certificate")):
        c = chord[key]; k = c["floor_scaled_root"]
        need(type(k) is int and k >= 0 and c["fraction_bits"] == 96, "fixed_root96")
        n, d = squared.numerator << 192, squared.denominator
        need(k*k*d <= n < (k+1)*(k+1)*d, "captured_integer_root_inequality")
        exact = k*k*d == n
        need(c["squared"] == norm.pair(squared) and c["scaled_numerator"] == n
             and c["scaled_denominator"] == d and c["exact"] is exact, "root_context")
        need(c["lower_BU"] == norm.pair(F(k, 2**96))
             and c["upper_BU"] == norm.pair(F(k+int(not exact), 2**96)), "root_bounds")
    need(chord["length_BU"] == [chord["root_lower_certificate"]["lower_BU"],
                                chord["root_upper_certificate"]["upper_BU"]], "length_binding")
    return interval(chord["length_BU"])


def compose(row, literal, endpoint, *, expected_context, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    need(type(expected_context) is dict and set(expected_context) == set(CONTEXT), "closed_expected_context")
    need(all(type(row[k]) is type(expected_context[k]) and row[k] == expected_context[k]
             for k in CONTEXT), "SOURCE_candidate_context_binding_NOT_authentication")
    need(row["model"] == "original-SOURCE-next-chord-length-CPU-v1"
         and row["status"] == "CONDITIONAL_CHORD_LENGTH_BOX_ONLY", "chord_contract")
    need(row["upstream_ledger_status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES"
         and row["conditional_first_id"] is None, "keep_ledger_STOP")
    need(row["ignored_primitive_ids"] == [] and row["origin_offset_applied"] is False
         and row["SOURCE_merged"] is False, "keep_contact_and_SOURCE")
    need(row["units"] == dict(displacement="BU", length="BU", squared="BU2")
         and row["root_fraction_bits"] == 96, "chord_units_root_resolution")
    need(all(row[f] is False for f in FLAGS), "no_upstream_promotion")
    sid = row["source_id"]
    need(type(sid) is str and sid in ("S0", "S1"), "SOURCE_identity")
    for k in ("primitive_id", "previous_primitive_id"):
        need(type(row[k]) is int and 0 <= row[k] < 2**32, "typed_primitive")
    out = base(); out.update({k: copy.deepcopy(row[k]) for k in CONTEXT})
    out.update(upstream_ledger_status=row["upstream_ledger_status"],
               upstream_triangle_status=row["upstream_triangle_status"])
    state = row["upstream_triangle_status"]
    need(state in ("CONDITIONAL_TRIANGLE_INTERIOR_HIT", "CONDITIONAL_TRIANGLE_MISS",
                   "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED"), "triangle_contract")
    if state != "CONDITIONAL_TRIANGLE_INTERIOR_HIT":
        out.update(status="STOP_NO_CONDITIONAL_FORWARD_PATH", reason=state)
        return out
    if literal is None:
        out.update(status="STOP_MISSING_LITERAL_REFERENCE_WAVELENGTH_CONTEXT")
        return out
    need(literal["model"] == "precision-oblique-common-detector-length-CPU-v1", "literal_contract")
    scene, request = literal["scene"], literal["request"]
    need(scene["units"] == "BU" and scene["schema"] == "precision-oblique-declared-scene-v1", "scene_units_schema")
    need(digest(scene) == row["scene_sha256"] == request["original_scene_sha256"]
         and digest(request) == row["query_sha256"], "exact_scene_query_NOT_scene_only")
    need(request["source_ids"] == ["S0", "S1"]
         and [s["id"] for s in scene["sources"]] == ["S0", "S1"], "separate_SOURCE_order")
    need(endpoint["status"] == "HOST_DECLARED_LENGTH_ENCLOSURE_ONLY", "endpoint_contract")
    need(endpoint["scene_sha256"] == row["scene_sha256"]
         and endpoint["query_sha256"] == row["query_sha256"]
         and endpoint["input_buffer_sha256"] == row["input_sha256"], "exact_endpoint_context")
    need([s["source_id"] for s in endpoint["SOURCE_results"]] == ["S0", "S1"], "endpoint_SOURCE_order")
    i = 0 if sid == "S0" else 1
    source = scene["sources"][i]
    srcbox = [[copy.deepcopy(v), copy.deepcopy(v)] for v in source["position_BU"]]
    saved = endpoint["SOURCE_results"][i]
    need(saved["endpoint_boxes"][0] == srcbox and saved["endpoint_boxes"][1] == row["point_box"],
         "SOURCE_and_previous_point_box_binding")
    need(saved["coverage"]["primary_primitive_id"] == row["previous_primitive_id"] == request["root_primitive_id"]
         and row["primitive_id"] == request["detector_primitive_id"], "candidate_primitive_binding")
    # No old ideal first length or old endpoint norm reused. New first chord
    # is conditional on the declared SOURCE point and the SAME modeled P box.
    last = verify_chord(row)
    costs = dict(new_interval_segment_norms=0, new_integer_root_certificates=0)
    first = norm.segment(box(srcbox), box(row["point_box"]), costs)
    total = [F(*first["length_BU"][j])+last[j] for j in range(2)]
    wave, ref = request["lambda_BU"], request["reference_BU"]
    out.update(enclose([norm.pair(v) for v in total], [copy.deepcopy(ref), copy.deepcopy(ref)],
                       [copy.deepcopy(wave), copy.deepcopy(wave)], source_id=sid, units="BU",
                       reference_scope="GEOMETRIC_TWO_SEGMENT_PATH", model=model))
    out.update(source_origin_box_BU=srcbox, previous_point_box_BU=copy.deepcopy(row["point_box"]),
               candidate_next_point_box_BU=copy.deepcopy(row["modeled_next_position_box_BU"]),
               new_first_segment=first, retained_next_segment_length_BU=copy.deepcopy(row["chord"]["length_BU"]),
               costs=costs, captured_chord_root_inequalities_verified=2,
               retained_chord_sha256=digest(row["chord"]), literal_input_sha256=digest(literal),
               scope="CPU_CONDITIONAL_SOURCE_P_Q_BROKEN_LINE_NOT_ADMITTED_DETECTOR_PATH",
               first_segment_model="NEW_ENDPOINT_NORM_NOT_IDEAL_T_TIMES_DIRECTION",
               reference_wavelength_model="DECLARED_EXACT_GEOMETRIC_REQUEST_NOT_NATIVE_INGRESS_BUDGET",
               root_fraction_bits=96, old_ideal_lengths_used=False,
               upstream_ledger_status=row["upstream_ledger_status"], upstream_triangle_status=state)
    return out


def capture(receipt):
    c = receipt["test_run"]
    need(type(c["rc"]) is int and c["rc"] == 0, "completed_capture")
    need(c["before_deadline"] is True if "before_deadline" in c else c.get("timed_out") is False,
         "capture_deadline")
    need("timed_out" not in c or c["timed_out"] is False, "capture_timeout")
    if "stdout_zlib_base64" in c:
        decoder = zlib.decompressobj()
        b = decoder.decompress(base64.b64decode(c["stdout_zlib_base64"], validate=True), 2097153)
        need(decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data, "single_capture")
    else:
        b = c["stdout"].encode()
    need(len(b) <= 2097152 and len(b) == c["stdout_bytes"]
         and hashlib.sha256(b).hexdigest() == c["stdout_sha256"], "capture_identity")
    return json.loads(b)


def retained():
    parents = []
    need(hashlib.sha256((ROOT/NORM_PATH).read_bytes()).hexdigest() == NORM_SHA, "pure_norm_pin")
    for name, sha in PARENTS.items():
        raw = (ROOT/"coordinacion/respuestas"/name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sha, "parent_pin:"+name)
        receipt = json.loads(raw)
        for path, p in receipt.get("code_doc_sha256", {}).items():
            need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == p, "ancestral_pin:"+path)
        for path, p in receipt["test_run"].get("sources", {}).items():
            raw_source = (ROOT/path).read_bytes()
            need(len(raw_source) == p["bytes"] and hashlib.sha256(raw_source).hexdigest() == p["sha256"], "source_pin")
        parents.append(capture(receipt))
    chord, endpoint, literal = parents
    need(chord["status"] == endpoint["status"] == "PASS", "parent_PASS")
    rows = [r["result"] for r in chord["records"] if r["kind"] == "FIXED_LENGTH"]
    need(len(rows) == 28 and len({(r["case"], r["source_id"], r["primitive_id"]) for r in rows}) == 28, "fixed28")
    endpoints = {r["id"]: r["result"] for r in endpoint["evidence"]["positive"]}
    need(len(endpoints) == 6, "endpoint6")
    literals = {k: literal["data"]["inputs"][k] for k in
                ("direction_scaled", "oblique", "shared_ref1000", "tiny_gap_2m60")}
    return rows, literals, endpoints


def run(*, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    rows, literals, endpoints = retained()
    outputs = []
    for row in rows:
        out = compose(row, literals.get(row["case"]), endpoints[row["case"]],
                      expected_context={k: row[k] for k in CONTEXT}, model=model)
        out["parent_receipts_sha256"] = copy.deepcopy(PARENTS)
        outputs.append(out)
    return outputs
