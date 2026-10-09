"""Opt-in modeled SOURCE-to-P RN64 length graph; never native admission.

Captured geometric roots are checked algebraically, not recomputed. Only the
new, explicitly ordered scalar graph gets new root certificates.
"""
import copy
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit import oblique_next_triangle_interval_CPU_v1 as rnd
from Blender.benchmarks.capacity_audit import oblique_trace_endpoint_length_enclosure_HOST_v1 as norm
from Blender.benchmarks.capacity_audit import original_SOURCE_detector_connection_residual_HOST_v1 as retained_io

ID = "PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-GRAPH-HOST-001"
MODEL = "original-SOURCE-first-leg-RN64-graph-HOST-v1"
GRAPH = "sub_xyz; square_xyz; add_xy; add_z; correctly_rounded_sqrt"
ASSUMPTIONS = ["RN64_ties_to_even_every_scalar_operation", "no_FMA_no_reassociation",
               "gradual_underflow", "correctly_rounded_binary64_sqrt",
               "actual_SOURCE_and_P_inside_declared_binary64_boxes",
               "HOST_model_NOT_native_backend_or_SOURCE_ingress_evidence"]
DEPS = {
    retained_io.NORM_PATH: retained_io.NORM_SHA,
    "Blender/benchmarks/capacity_audit/oblique_next_triangle_interval_CPU_v1.py":
        "94173ba4dfd8534a4c3556cc8666e3efc2dba175c475d12a7332c10b441af776",
    "Blender/benchmarks/capacity_audit/original_SOURCE_detector_connection_residual_HOST_v1.py":
        "478e81069c41dbe3b817e7bc010864a6f9af5b03a346e510de062ab9e074480e",
}
need = retained_io.need
digest = retained_io.digest


def pair(q):
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 512, "output_capacity512")
    return [q.numerator, q.denominator]


def base():
    out = dict(model=MODEL, status="STOP", promotion="STOP", SOURCE_merged=False,
               native_SOURCE_ingress_error_bound_BU=None, native_first_leg_error_bound_BU=None,
               native_phase_error_bound_rad=None, first_leg_accuracy_budget_BU=None,
               source_phase=None, material_phase=None, amplitude=None, field=None, power=None,
               full_costs="UNKNOWN_NOT_ZERO", GPU_used=False, Bpy_used=False, RT_used=False,
               old_root_replays=0, frozen_producer_replays=0,
               costs=dict(new_modeled_scalar_operations=0, new_integer_root_certificates=0),
               JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    out.update({k: False for k in retained_io.FLAGS})
    return out


def box(raw):
    need(type(raw) is list and len(raw) == 3, "box3")
    result = []
    for v in raw:
        lo, hi = retained_io.interval(v)
        need(max(abs(lo), abs(hi)) <= 10**6, "coordinate_domain")
        need(all(rnd.round_out(x, False) == x == rnd.round_out(x, True) for x in (lo, hi)),
             "binary64_endpoint_required")
        result.append(rnd.Interval(lo, hi))
    return result


def square(v):
    # x*x has one operand dependency: an interval crossing zero has min 0.
    lo = F(0) if v.lo <= 0 <= v.hi else min(v.lo*v.lo, v.hi*v.hi)
    return rnd.Interval.outward(lo, max(v.lo*v.lo, v.hi*v.hi))


def enclose(source_box_BU, previous_P_box_BU, *, source_id, units, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    need(type(source_id) is str and source_id in ("S0", "S1"), "SOURCE_identity")
    need(type(units) is str and units == "BU", "same_BU_not_meters")
    a, b = box(source_box_BU), box(previous_P_box_BU)
    differences = [y-x for x, y in zip(a, b)]
    squares = [square(v) for v in differences]
    xy = squares[0]+squares[1]
    q = xy+squares[2]
    out = base()
    lower = norm.sqrt_certificate(q.lo, out["costs"])
    upper = norm.sqrt_certificate(q.hi, out["costs"])
    # floor64(lower certificate) <= RN64(sqrt(actual q)) <= ceil64(upper).
    length = rnd.Interval.outward(F(*lower["lower_BU"]), F(*upper["upper_BU"]))
    out["costs"]["new_modeled_scalar_operations"] = 9
    out.update(status="CONDITIONAL_MODELED_FIRST_LEG_RN64_GRAPH_ONLY", source_id=source_id,
               units="BU", graph=GRAPH, assumptions=list(ASSUMPTIONS),
               source_box_BU=copy.deepcopy(source_box_BU), previous_P_box_BU=copy.deepcopy(previous_P_box_BU),
               difference_intervals_BU=[v.json() for v in differences],
               squared_intervals_BU2=[v.json() for v in squares],
               add_xy_interval_BU2=xy.json(), radicand_interval_BU2=q.json(),
               root_lower_certificate=lower, root_upper_certificate=upper,
               modeled_length_interval_BU=length.json(), modeled_length_width_BU=pair(length.hi-length.lo),
               sqrt_certificate_fraction_bits=96, root_grid_uncertainty_included=True,
               native_graph_identity_verified=False, native_SOURCE_ingress_status="UNKNOWN_NOT_ZERO",
               SOURCE_input_box_scope="DECLARED_VALUES_NOT_NATIVE_INGRESS_ERROR_BUDGET",
               ideal_t_times_D_length_used=False, candidate_cycles_replaced=False,
               phase_budget_transferred=False, encoded_phase_evaluated=False)
    return out


def verify_geometric_capture(seg, a, b):
    """Check stored squares and root inequalities; never call sqrt/isqrt here."""
    need(type(seg) is dict and len(seg["components"]) == 3, "captured_norm3")
    sqlo = sqhi = F(0)
    for c, x, y in zip(seg["components"], a, b):
        lo, hi = y.lo-x.hi, y.hi-x.lo
        need(c["difference_BU"] == [pair(lo), pair(hi)], "captured_difference_binding")
        l = F(0) if lo <= 0 <= hi else min(lo*lo, hi*hi)
        h = max(lo*lo, hi*hi)
        need(c["squared_BU2"] == [pair(l), pair(h)], "captured_square_binding")
        sqlo += l
        sqhi += h
    need(seg["squared_BU2"] == [pair(sqlo), pair(sqhi)], "captured_sum_binding")
    for cert, q in zip((seg["root_lower_certificate"], seg["root_upper_certificate"]), (sqlo, sqhi)):
        k = cert["floor_scaled_root"]
        need(type(k) is int and k >= 0 and cert["fraction_bits"] == 96, "captured_root_type_grid")
        n, d = q.numerator << 192, q.denominator
        need(cert["squared"] == pair(q) and cert["scaled_numerator"] == n and
             cert["scaled_denominator"] == d and k*k*d <= n < (k+1)*(k+1)*d, "captured_root_inequalities")
        exact = k*k*d == n
        need(cert["exact"] is exact and cert["lower_BU"] == pair(F(k, 2**96)) and
             cert["upper_BU"] == pair(F(k+int(not exact), 2**96)), "captured_root_endpoints")
    need(seg["length_BU"] == [seg["root_lower_certificate"]["lower_BU"],
                              seg["root_upper_certificate"]["upper_BU"]], "captured_length_binding")
    return tuple(F(*v) for v in seg["length_BU"])


def compose(row, literal, *, expected_row_sha256, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    need(type(row) is dict and digest(row) == expected_row_sha256, "captured_SOURCE_row_binding")
    need(row["model"] == retained_io.CYCLE_MODEL and row["source_id"] in ("S0", "S1"), "candidate_model_SOURCE")
    need(all(row[k] is False for k in retained_io.FLAGS) and row["SOURCE_merged"] is False and
         row["upstream_ledger_status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES" and
         row["origin_offset_applied"] is False and row["ignored_primitive_ids"] == [] and
         row["conditional_first_id"] is None, "upstream_STOP_preserved")
    context = {k: copy.deepcopy(row[k]) for k in retained_io.CONTEXT}
    context.update(captured_SOURCE_row_sha256=expected_row_sha256,
                   upstream_cycle_status=row["status"], upstream_ledger_status=row["upstream_ledger_status"])
    if row["cycles_interval"] is None:
        need(row["status"] in ("STOP_NO_CONDITIONAL_FORWARD_PATH", "STOP_MISSING_LITERAL_REFERENCE_WAVELENGTH_CONTEXT"), "known_upstream_STOP")
        out = base()
        out.update(context, status="STOP_UPSTREAM_NO_FIRST_LEG_GRAPH")
        return out
    need(row["status"] == "CONDITIONAL_GEOMETRIC_PATH_CYCLES_ONLY", "conditional_cycle_status")
    need(type(literal) is dict and set(literal) == {"scene", "request"}, "closed_literal_context")
    scene, query = literal["scene"], literal["request"]
    need(digest(scene) == query["original_scene_sha256"] == row["scene_sha256"] and
         digest(query) == row["query_sha256"], "scene_query_identity")
    need(query["source_ids"] == ["S0", "S1"] and row["units"] == "BU" and
         scene["units"] == "BU", "literal_SOURCE_units")
    sources = [s for s in scene["sources"] if s["id"] == row["source_id"]]
    need(len(sources) == 1 and row["source_origin_box_BU"] == [[v, v] for v in sources[0]["position_BU"]], "literal_SOURCE_origin")
    need(type(row["primitive_id"]) is int and type(row["previous_primitive_id"]) is int and
         row["primitive_id"] == query["detector_primitive_id"] == 0 and
         row["previous_primitive_id"] == query["root_primitive_id"] == 1, "literal_primitives")
    need(row["reference_BU"] == [query["reference_BU"]]*2 and
         row["wavelength_BU"] == [query["lambda_BU"]]*2 and row["source_phase"] is None and
         row["material_phase"] is None, "literal_reference_wavelength_original_phase")
    a, b = box(row["source_origin_box_BU"]), box(row["previous_point_box_BU"])
    geo_lo, geo_hi = verify_geometric_capture(row["new_first_segment"], a, b)
    out = enclose(row["source_origin_box_BU"], row["previous_point_box_BU"],
                  source_id=row["source_id"], units="BU", model=MODEL)
    lo, hi = (F(*v) for v in out["modeled_length_interval_BU"])
    allowance = max(abs(lo-geo_hi), abs(hi-geo_lo))
    out.update(context, captured_geometric_first_length_BU=copy.deepcopy(row["new_first_segment"]["length_BU"]),
               conditional_graph_vs_geometric_allowance_BU=pair(allowance),
               allowance_scope="CARTESIAN_INTERVAL_CONTRAST_NOT_NATIVE_ALU_ERROR_OR_PHASE_BUDGET",
               captured_geometric_root_inequalities_verified=2,
               captured_candidate_cycles_left_unchanged=True)
    return out


def run(*, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    for path, h in DEPS.items():
        need(retained_io.sha((retained_io.ROOT/path).read_bytes()) == h, "pure_dependency_pin")
    rows, literals = retained_io.retained()  # sealed reads only; no producer run.
    outputs = []
    for row in rows:
        out = compose(row, literals.get(row["case"]), expected_row_sha256=digest(row), model=MODEL)
        out["parent_receipts_sha256"] = copy.deepcopy(retained_io.PARENTS)
        outputs.append(out)
    return outputs
