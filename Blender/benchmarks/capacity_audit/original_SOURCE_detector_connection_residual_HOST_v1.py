"""Conditional detector residual from captured propagated Q boxes, not native closure.

Only new norms of Q minus the explicit detector point are evaluated. Frozen
ray/position/chord/phase producers are never executed or rewritten.
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
ID = "PRECISION-ORIGINAL-SOURCE-DETECTOR-CONNECTION-RESIDUAL-HOST-001"
MODEL = "original-SOURCE-detector-connection-residual-HOST-v1"
CYCLE_MODEL = "original-SOURCE-candidate-path-cycles-HOST-v1"
NORM_PATH = "Blender/benchmarks/capacity_audit/oblique_trace_endpoint_length_enclosure_HOST_v1.py"
NORM_SHA = "8f3b77dba20a755754f1c0da4bc9b779d35056a02240b6602d0c7d1d34d330e8"
PARENTS = {
    "PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001-CODEX.json":
        "53b739dcaaf08e2bbce9ca81ce7a24b98bc53074357720a4bc9aaaf317aae1fe",
    "PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json":
        "139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e",
}
CONTEXT = ("case", "source_id", "scene_sha256", "query_sha256", "input_sha256",
           "source_record_sha256", "CPU_packet_binding_sha256", "primitive_id", "previous_primitive_id")
FLAGS = ("native_precision_certified", "native_length_graph_certified", "length_accuracy_budget_admitted",
         "triangle_hit_certified", "nearest_hit_certified", "launch_exclusion_allowed",
         "full_path_visibility_certified", "GPU_launch_allowed", "phase_certified",
         "first_leg_native_ALU_certified", "detector_connection_certified", "physical_optics_certified",
         "scene_authenticated")


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(v):
    return sha(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def bounded_pair(q):
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 512, "output_capacity512")
    return [q.numerator, q.denominator]


def interval(v):
    need(type(v) is list and len(v) == 2, "interval2")
    a, b = map(norm.rat, v)
    need(a <= b, "ordered_interval")
    return a, b


def base():
    out = dict(model=MODEL, status="STOP", promotion="STOP", reason=None,
               native_promotion_allowed=False, SOURCE_merged=False, phase_certified=False,
               GPU_used=False, Bpy_used=False, RT_used=False, original_detector_connection_budget_BU=None,
               native_detector_error_bound_BU=None, native_phase_error_bound_rad=None,
               full_costs="UNKNOWN_NOT_ZERO", amplitude=None, field=None, power=None,
               source_phase=None, material_phase=None, costs=dict(new_interval_segment_norms=0,
               new_integer_root_certificates=0), JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    out.update({k: False for k in FLAGS})
    return out


def enclose(candidate_Q_box_BU, literal_detector_point_BU, wavelength_BU, *, source_id, units, model):
    """Exact HOST box distance and conditional reverse-triangle allowance.

    For fixed P and the SAME actual positive lambda, replacing Q by detector D
    changes |Q-P| by at most |Q-D|. No Q replacement or cap admission is done.
    """
    need(type(model) is str and model == MODEL, "explicit_model")
    need(type(source_id) is str and source_id in ("S0", "S1"), "SOURCE_identity")
    need(type(units) is str and units == "BU", "same_BU_not_meters")
    need(type(candidate_Q_box_BU) is list and len(candidate_Q_box_BU) == 3, "candidate_box3")
    need(type(literal_detector_point_BU) is list and len(literal_detector_point_BU) == 3, "detector_point3")
    qbox = [interval(v) for v in candidate_Q_box_BU]
    detector = [norm.rat(v) for v in literal_detector_point_BU]
    need(all(abs(v) <= 10**6 for iv in qbox for v in iv) and all(abs(v) <= 10**6 for v in detector), "coordinate_domain")
    wave = interval(wavelength_BU)
    need(wave[0] > 0, "positive_wavelength")
    out = base()
    cost = out["costs"]
    residual = norm.segment([(d, d) for d in detector], qbox, cost)
    delta_hi = F(*residual["length_BU"][1])
    cycles_allowance = delta_hi/wave[0]
    rad_allowance = 8*cycles_allowance  # 2*pi<8; NOT encoded/native error.
    contains = all(a <= d <= b for (a, b), d in zip(qbox, detector))
    exact_equal = all(a == b == d for (a, b), d in zip(qbox, detector))
    # A real HOST box corner, not evidence it occurs in a correlated/native ray.
    corner = [max((a, b), key=lambda v: abs(v-d)) for (a, b), d in zip(qbox, detector)]
    witness_sq = sum(((v-d)**2 for v, d in zip(corner, detector)), F(0))
    out.update(status="CONDITIONAL_DETECTOR_RESIDUAL_ONLY", source_id=source_id, units="BU",
               candidate_Q_box_BU=copy.deepcopy(candidate_Q_box_BU),
               literal_detector_point_BU=copy.deepcopy(literal_detector_point_BU),
               wavelength_BU=copy.deepcopy(wavelength_BU), residual=residual,
               detector_point_in_candidate_box=contains,
               ALL_candidate_box_points_equal_literal_detector=exact_equal,
               max_distance_box_witness_Q_BU=[bounded_pair(v) for v in corner],
               max_distance_box_witness_squared_BU2=bounded_pair(witness_sq),
               conditional_geometric_Q_replacement_allowance_BU=residual["length_BU"][1],
               conditional_Q_replacement_allowance_cycles=bounded_pair(cycles_allowance),
               conditional_Q_replacement_allowance_rad=bounded_pair(rad_allowance),
               allowance_scope="SAME_P_REFERENCE_ACTUAL_WAVELENGTH_GEOMETRIC_LENGTH_ONLY_NOT_TOTAL_PHASE_ERROR",
               actual_Q_replaced=False, cap_budget_admitted=False, original_budget_status="UNKNOWN_NOT_ZERO",
               encoded_phase_evaluated=False, frozen_producer_replays=0, old_root_replays=0,
               assumptions=["actual_Q_inside_caller_box", "same_P_in_both_geometric_last_legs",
                            "same_actual_reference_and_positive_wavelength", "homogeneous_geometric_path_NOT_optical_integral",
                            "HOST_cartesian_box_NOT_native_ALU_or_correlated_trajectory"])
    return out


def compose(row, literal, *, expected_row_sha256, model):
    need(model == MODEL and type(model) is str, "explicit_model")
    need(type(row) is dict and digest(row) == expected_row_sha256, "captured_SOURCE_row_binding")
    need(row["model"] == CYCLE_MODEL and type(row["source_id"]) is str and row["source_id"] in ("S0", "S1"), "candidate_model_SOURCE")
    need(all(row[f] is False for f in FLAGS) and row["SOURCE_merged"] is False and
         row["origin_offset_applied"] is False and row["ignored_primitive_ids"] == [] and
         row["conditional_first_id"] is None and row["upstream_ledger_status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES",
         "upstream_STOP_preserved")
    need(type(row["primitive_id"]) is int and type(row["previous_primitive_id"]) is int, "typed_primitive_ids")
    out = base()
    out.update({k: copy.deepcopy(row[k]) for k in CONTEXT})
    out.update(upstream_ledger_status=row["upstream_ledger_status"],
               upstream_cycle_status=row["status"], captured_SOURCE_row_sha256=expected_row_sha256)
    if row["cycles_interval"] is None:
        need(row["status"] in ("STOP_NO_CONDITIONAL_FORWARD_PATH", "STOP_MISSING_LITERAL_REFERENCE_WAVELENGTH_CONTEXT"), "known_upstream_STOP")
        out.update(status="STOP_UPSTREAM_NO_DETECTOR_RESIDUAL", reason=row["status"])
        return out
    need(row["status"] == "CONDITIONAL_GEOMETRIC_PATH_CYCLES_ONLY", "conditional_cycle_status")
    need(type(literal) is dict and set(literal) == {"scene", "request"}, "closed_literal_context")
    scene, query = literal["scene"], literal["request"]
    need(digest(scene) == query["original_scene_sha256"] == row["scene_sha256"] and
         digest(query) == row["query_sha256"], "SOURCE_scene_query_identity")
    need(query["source_ids"] == ["S0", "S1"] and type(query["root_primitive_id"]) is int and
         type(query["detector_primitive_id"]) is int and
         query["detector_primitive_id"] == row["primitive_id"] == 0 and
         query["root_primitive_id"] == row["previous_primitive_id"] == 1, "literal_path_primitives")
    need(row["units"] == "BU" and row["reference_scope"] == "GEOMETRIC_TWO_SEGMENT_PATH" and
         row["result_units"] == "unwrapped_cycles_NOT_radians" and
         row["reference_BU"] == [query["reference_BU"]]*2 and
         row["wavelength_BU"] == [query["lambda_BU"]]*2, "literal_units_reference_wavelength")
    need(row["source_phase"] is None and row["material_phase"] is None, "phase_original_unknown")
    residual = enclose(row["candidate_next_point_box_BU"], query["detector_point_BU"], row["wavelength_BU"],
                       source_id=row["source_id"], units="BU", model=MODEL)
    out.update(residual)
    out.update({k: copy.deepcopy(row[k]) for k in CONTEXT})
    out.update(upstream_ledger_status=row["upstream_ledger_status"], upstream_cycle_status=row["status"],
               captured_SOURCE_row_sha256=expected_row_sha256)
    return out


def capture(r, *, require_deadline=False):
    c = r["test_run"]
    need(type(c["rc"]) is int and c["rc"] == 0 and c.get("timed_out", False) is False, "capture_exit")
    if require_deadline:
        need(c.get("before_deadline") is True, "capture_deadline")
    raw = zlib.decompress(base64.b64decode(c["stdout_zlib_base64"], validate=True))
    need(type(c["stdout_bytes"]) is int and len(raw) == c["stdout_bytes"] and sha(raw) == c["stdout_sha256"], "capture_integrity")
    d = json.loads(raw)
    need(d["status"] == "PASS", "capture_status")
    return d


def retained():
    need(sha((ROOT/NORM_PATH).read_bytes()) == NORM_SHA, "pure_norm_pin")
    data = {}
    for name, expected in PARENTS.items():
        raw = (ROOT/"coordinacion/respuestas"/name).read_bytes()
        need(sha(raw) == expected, "parent_receipt_pin")
        r = json.loads(raw)
        for p, h in r["code_doc_sha256"].items():
            need(sha((ROOT/p).read_bytes()) == h, "parent_code_doc_pin")
        data[name] = capture(r, require_deadline="CANDIDATE-PATH-CYCLES" in name)
    cd = data[next(n for n in data if "CANDIDATE-PATH-CYCLES" in n)]
    rows = [x["result"] for x in cd["records"] if x["kind"] == "FIXED_PATH_OR_STOP"]
    need(len(rows) == 28, "captured_census28")
    geometry = data[next(n for n in data if "COMMON-DETECTOR-LENGTH" in n)]["data"]["inputs"]
    return rows, {k: {v: g[v] for v in ("scene", "request")} for k, g in geometry.items()}


def run(*, model):
    need(model == MODEL and type(model) is str, "explicit_model")
    rows, literals = retained()
    outputs = []
    for row in rows:
        out = compose(row, literals.get(row["case"]), expected_row_sha256=digest(row), model=MODEL)
        out["parent_receipts_sha256"] = copy.deepcopy(PARENTS)
        outputs.append(out)
    return outputs
