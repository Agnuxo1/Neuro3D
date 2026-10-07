"""Algebraic RN64 first-leg cap witnesses from sealed captures; no root replay."""
import base64
import copy
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[3]
ID = "PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-CAP-WITNESS-CPU-001"
MODEL = "original-SOURCE-first-leg-RN64-cap-witness-CPU-v1"
GRAPH_RECEIPT = "PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-GRAPH-HOST-001-CODEX.json"
GRAPH_SHA = "e25bb94201574e0778023a36d5c7db7bb842727fdffda82890aa314ff8ad2262"
LITERAL_RECEIPT = "PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
LITERAL_SHA = "139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
SCOPE = "ISOLATED_FIRST_LEG_UNWRAPPED_PHASE_TERM_NOT_TOTAL_PATH_OR_NATIVE_PHASE"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def pair(v):
    need(max(abs(v.numerator).bit_length(), v.denominator.bit_length()) <= 512, "output_capacity512")
    return [v.numerator, v.denominator]


def rat(v):
    need(type(v) is list and len(v) == 2 and all(type(x) is int for x in v), "typed_rational")
    need(v[1] > 0 and math.gcd(*v) == 1 and max(abs(v[0]).bit_length(), v[1].bit_length()) <= 128, "canonical_capacity128")
    return F(*v)


def successor(v):
    """Normal positive binary64 successor, proven from its integer lattice."""
    need(F(1, 2**126) <= v <= 10**6, "candidate_positive_normal_domain")
    e = v.numerator.bit_length()-v.denominator.bit_length()
    if v < F(2)**e:
        e -= 1
    step = F(2)**(e-52)
    index = v/step
    need(index.denominator == 1 and 2**52 <= index < 2**53, "binary64_candidate_lattice")
    return v+step, index.numerator


def select_root(q_raw, candidates):
    """Select RN sqrt by squared midpoint comparison, never sqrt/isqrt/libm."""
    q = rat(q_raw)
    need(0 < q <= 2**64, "positive_squared_domain")
    need(type(candidates) is list and len(candidates) == 2, "candidate_pair")
    lo, hi = map(rat, candidates)
    nxt, index = successor(lo)
    need(hi == nxt and lo*lo <= q <= hi*hi, "adjacent_root_bracket")
    midpoint_squared = ((lo+hi)/2)**2
    selected = lo if q < midpoint_squared or (q == midpoint_squared and index % 2 == 0) else hi
    return dict(selected_RN64_length_BU=pair(selected), adjacent_candidates_BU=copy.deepcopy(candidates),
                squared_midpoint_BU2=pair(midpoint_squared), squared_input_BU2=copy.deepcopy(q_raw),
                tie_to_even_applied=q == midpoint_squared, new_root_evaluations=0)


def contrast(selection, geometric_length, wavelength, cap):
    need(type(selection) is dict and digest(selection) == digest(select_root(
        selection["squared_input_BU2"], selection["adjacent_candidates_BU"])), "closed_algebraic_selection")
    need(type(geometric_length) is list and len(geometric_length) == 2, "geometric_interval")
    lo, hi = map(rat, geometric_length)
    need(0 <= lo <= hi, "ordered_geometric_interval")
    rn, q = rat(selection["selected_RN64_length_BU"]), rat(selection["squared_input_BU2"])
    need(lo*lo <= q <= hi*hi, "captured_geometric_root_inequalities")
    wave, cap_value = rat(wavelength), rat(cap)
    need(wave > 0 and cap_value >= 0, "positive_lambda_nonnegative_cap")
    signed = (rn-hi, rn-lo)
    lower = F(0) if signed[0] <= 0 <= signed[1] else min(abs(v) for v in signed)
    upper = max(abs(v) for v in signed)
    # Strict 6 < 2*pi < 8; conservative bounds, never encoded phase.
    lower_rad, upper_rad = 6*lower/wave, 8*upper/wave
    status = "TERM_ERROR_ABOVE_LITERAL_WIDTH_SCALE" if lower_rad > cap_value else (
        "TERM_ERROR_BOUND_WITHIN_LITERAL_WIDTH_SCALE" if upper_rad <= cap_value else "STOP_WIDTH_SCALE_COMPARISON_UNRESOLVED")
    return dict(status=status, scope=SCOPE, signed_first_leg_discrepancy_BU=[pair(v) for v in signed],
                absolute_first_leg_discrepancy_BU=[pair(lower), pair(upper)],
                isolated_phase_term_error_rad=[pair(lower_rad), pair(upper_rad)],
                original_SOURCE_cap_rad=copy.deepcopy(cap), wavelength_BU=copy.deepcopy(wavelength),
                original_cap_observable="GEOMETRIC_INTERVAL_WIDTH_RAD_NOT_NATIVE_ACCURACY",
                original_width_contract_failure_proved=False,
                modeled_RN_point_length_interval_BU=[pair(rn), pair(rn)],
                modeled_RN_point_length_width_BU=[0, 1],
                formal_deterministic_term_uncertainty_width_rad=[0, 1],
                point_width_does_not_bound_pointwise_discrepancy=True,
                modeled_pointwise_discrepancy_nonzero_proved=rn*rn != q,
                whole_SOURCE_cap_used_as_diagnostic_NOT_allocated_first_leg_budget=True,
                first_leg_native_accuracy_budget_BU=None, native_SOURCE_ingress_error_bound_BU=None,
                native_precision_certified=False, phase_certified=False, total_path_cap_failure_proved=False,
                cancellation_with_other_terms_excluded=False, GPU_used=False, Bpy_used=False, RT_used=False,
                promotion="STOP", SOURCE_merged=False, full_costs="UNKNOWN_NOT_ZERO",
                JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")


def capture(name, expected):
    raw = (ROOT/"coordinacion/respuestas"/name).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected, "parent_receipt_pin")
    r = json.loads(raw)
    for path, h in r["code_doc_sha256"].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == h, "parent_code_doc_pin")
    c = r["test_run"]
    need(type(c["rc"]) is int and c["rc"] == 0 and c.get("timed_out", False) is False, "capture_exit")
    if name == GRAPH_RECEIPT:
        need(c["before_deadline"] is True, "capture_deadline")
    b = zlib.decompress(base64.b64decode(c["stdout_zlib_base64"], validate=True))
    need(len(b) == c["stdout_bytes"] and hashlib.sha256(b).hexdigest() == c["stdout_sha256"], "capture_integrity")
    d = json.loads(b)
    need(d["status"] == "PASS", "capture_PASS")
    return d


def compose(g, literal, candidates, *, expected_graph_row_sha256, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    need(type(g) is dict and digest(g) == expected_graph_row_sha256, "captured_graph_row_binding")
    need(g["model"] == "original-SOURCE-first-leg-RN64-graph-HOST-v1" and
         g["graph"] == "sub_xyz; square_xyz; add_xy; add_z; correctly_rounded_sqrt" and
         g["status"] == "CONDITIONAL_MODELED_FIRST_LEG_RN64_GRAPH_ONLY" and
         g["source_id"] in ("S0", "S1") and g["promotion"] == "STOP" and
         g["native_precision_certified"] is False and g["phase_certified"] is False and
         g["first_leg_native_ALU_certified"] is False and g["SOURCE_merged"] is False, "conditional_native_STOP")
    scene, query = literal["scene"], literal["request"]
    need(digest(scene) == query["original_scene_sha256"] == g["scene_sha256"] and
         digest(query) == g["query_sha256"], "scene_query_binding")
    need(scene["units"] == g["units"] == "BU" and query["source_ids"] == ["S0", "S1"], "literal_SOURCE_units")
    sources = [s for s in scene["sources"] if s["id"] == g["source_id"]]
    need(len(sources) == 1 and g["source_box_BU"] == [[v, v] for v in sources[0]["position_BU"]], "literal_SOURCE_origin")
    need(type(g["primitive_id"]) is int and type(g["previous_primitive_id"]) is int and
         g["primitive_id"] == query["detector_primitive_id"] == 0 and
         g["previous_primitive_id"] == query["root_primitive_id"] == 1 and
         g["upstream_ledger_status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES", "literal_primitives_upstream_STOP")
    need(all(v[0] == v[1] for v in g["source_box_BU"]+g["previous_P_box_BU"]), "singleton_declared_endpoints")
    # Algebraic exactness of pre-sqrt graph at these singleton inputs.
    delta = [rat(b[0])-rat(a[0]) for a, b in zip(g["source_box_BU"], g["previous_P_box_BU"])]
    squares = [d*d for d in delta]
    need(g["difference_intervals_BU"] == [[pair(d)]*2 for d in delta] and
         g["squared_intervals_BU2"] == [[pair(s)]*2 for s in squares], "captured_exact_sub_square")
    q = sum(squares, F(0))
    for v in delta+squares+[squares[0]+squares[1], q]:
        if v != 0:
            successor(abs(v))  # representable result: exact RN pre-sqrt op.
    need(g["add_xy_interval_BU2"] == [pair(squares[0]+squares[1])]*2 and
         g["radicand_interval_BU2"] == [pair(q)]*2, "captured_exact_sum")
    s = select_root(pair(q), candidates)
    j = query["source_ids"].index(g["source_id"])
    out = contrast(s, g["captured_geometric_first_length_BU"], query["lambda_BU"], query["source_width_caps_rad"][j])
    out.update(selection=s, model=MODEL, case=g["case"], source_id=g["source_id"],
               scene_sha256=g["scene_sha256"], query_sha256=g["query_sha256"],
               input_sha256=g["input_sha256"], captured_graph_row_sha256=expected_graph_row_sha256,
               candidates_scope="ADJACENT_DYADIC_BRACKET_PROVED_ALGEBRAICALLY_NOT_NATIVE_OBSERVATION",
               native_GRAPH_identity_verified=False, old_root_replays=0, new_root_evaluations=0)
    return out


def run(*, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    gd = capture(GRAPH_RECEIPT, GRAPH_SHA)
    inputs = capture(LITERAL_RECEIPT, LITERAL_SHA)["data"]["inputs"]
    rows = [r["result"] for r in gd["records"] if r["kind"] == "FIXED_GRAPH_OR_STOP"]
    need(len(rows) == 28, "captured_census28")
    base_candidates = {r["source_id"]: r["modeled_length_interval_BU"] for r in rows
                       if r["case"] == "oblique" and r["status"] == "CONDITIONAL_MODELED_FIRST_LEG_RN64_GRAPH_ONLY"}
    need(set(base_candidates) == {"S0", "S1"}, "base_SOURCE_brackets")
    outputs = []
    for g in rows:
        if g["status"] == "STOP_UPSTREAM_NO_FIRST_LEG_GRAPH":
            outputs.append(dict(status="STOP_UPSTREAM_NO_CAP_WITNESS", case=g["case"], source_id=g["source_id"],
                                captured_graph_row_sha256=digest(g), promotion="STOP", native_precision_certified=False,
                                GPU_used=False, Bpy_used=False, RT_used=False, phase_certified=False,
                                total_path_cap_failure_proved=False, full_costs="UNKNOWN_NOT_ZERO",
                                native_SOURCE_ingress_error_bound_BU=None, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY",
                                new_root_evaluations=0, SOURCE_merged=False))
            continue
        candidates = base_candidates[g["source_id"]]
        if g["case"] == "tiny_gap_2m60":
            # Exact dyadic scale of an existing bracket, NOT a sqrt replay.
            candidates = [pair(rat(v)/2**60) for v in candidates]
        out = compose(g, {k: inputs[g["case"]][k] for k in ("scene", "request")}, candidates,
                      expected_graph_row_sha256=digest(g), model=MODEL)
        out["dyadic_candidate_scale"] = [1, 2**60] if g["case"] == "tiny_gap_2m60" else [1, 1]
        outputs.append(out)
    return outputs
