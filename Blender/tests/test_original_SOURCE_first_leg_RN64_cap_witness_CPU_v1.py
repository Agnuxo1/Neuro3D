"""Algebra-only cap witnesses; no root, geometry, or legacy-suite replay."""
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Blender.benchmarks.capacity_audit import original_SOURCE_first_leg_RN64_cap_witness_CPU_v1 as m

records = []


def negative(label, fn):
    try:
        fn()
    except (ValueError, TypeError, KeyError) as ex:
        records.append(dict(kind="NEGATIVE", id=label, reason=str(ex)))
    else:
        raise AssertionError(label)


def test_fixed():
    results = m.run(model=m.MODEL)
    assert len(results) == 28
    active = []
    for r in results:
        assert r["promotion"] == "STOP" and r["native_precision_certified"] is False
        assert r["GPU_used"] is False and r["SOURCE_merged"] is False and r["new_root_evaluations"] == 0
        if r["status"] != "STOP_UPSTREAM_NO_CAP_WITNESS":
            assert r["total_path_cap_failure_proved"] is False and r["phase_certified"] is False
            assert r["native_SOURCE_ingress_error_bound_BU"] is None
            assert r["whole_SOURCE_cap_used_as_diagnostic_NOT_allocated_first_leg_budget"] is True
            assert r["original_cap_observable"] == "GEOMETRIC_INTERVAL_WIDTH_RAD_NOT_NATIVE_ACCURACY"
            assert r["original_width_contract_failure_proved"] is False
            assert r["modeled_RN_point_length_width_BU"] == [0, 1]
            assert r["modeled_pointwise_discrepancy_nonzero_proved"] is True
            active.append(r)
        records.append(dict(kind="FIXED_WITNESS_OR_STOP", result=r))
    assert sum(r["status"] == "TERM_ERROR_ABOVE_LITERAL_WIDTH_SCALE" for r in active) == 6
    assert sum(r["status"] == "TERM_ERROR_BOUND_WITHIN_LITERAL_WIDTH_SCALE" for r in active) == 2
    assert all(r["selection"]["tie_to_even_applied"] is False for r in active)
    for r in active:
        lo, hi = (F(*v) for v in r["signed_first_leg_discrepancy_BU"])
        if r["case"] != "tiny_gap_2m60":
            assert (hi < 0) if r["source_id"] == "S0" else (lo > 0)
            assert F(*r["isolated_phase_term_error_rad"][0]) > F(*r["original_SOURCE_cap_rad"])
        else:
            assert F(*r["isolated_phase_term_error_rad"][1]) <= F(*r["original_SOURCE_cap_rad"])


def test_midpoint_controls():
    lower = F(1)
    upper = lower+F(1, 2**52)
    # Midpoint-squared fits the unchanged 128-bit rational input cap.
    for label, lo, hi in (("even_lower", lower, upper), ("odd_lower", upper, upper+F(1, 2**52))):
        q = ((lo+hi)/2)**2
        out = m.select_root(m.pair(q), [m.pair(lo), m.pair(hi)])
        assert out["tie_to_even_applied"] is True
        assert F(*out["selected_RN64_length_BU"]) == (lo if label == "even_lower" else hi)
        records.append(dict(kind="TIE_CONTROL", id=label, result=out))
    out = m.select_root([1, 1], [m.pair(lower), m.pair(upper)])
    assert out["selected_RN64_length_BU"] == [1, 1]
    bound = m.contrast(out, [[1, 1], [1, 1]], [1, 8], [0, 1])
    assert bound["status"] == "TERM_ERROR_BOUND_WITHIN_LITERAL_WIDTH_SCALE"
    assert bound["isolated_phase_term_error_rad"] == [[0, 1], [0, 1]]
    assert bound["modeled_pointwise_discrepancy_nonzero_proved"] is False
    records.append(dict(kind="EXACT_ZERO_CONTROL", result=bound))


def test_numeric_negatives():
    good = [[1, 1], [4503599627370497, 4503599627370496]]
    for label, q, candidates in (
        ("zero_q", [0, 1], good), ("negative_q", [-1, 1], good),
        ("bool", [True, 1], good), ("zero_den", [1, 0], good),
        ("not_canonical", [2, 2], good), ("capacity", [1, 2**128], good),
        ("reversed", [1, 1], good[::-1]), ("nonadjacent", [1, 1], [[1, 1], [2, 1]]),
        ("off_lattice", [1, 1], [[1, 3], [2, 3]]), ("unbracketed", [3, 1], good),
        ("shape", [1, 1], [])):
        negative(label, lambda q=q, c=candidates: m.select_root(q, c))
    s = m.select_root([1, 1], good)
    for label, geo, wave, cap in (
        ("wrong_geo", [[2, 1], [3, 1]], [1, 1], [1, 1]),
        ("reversed_geo", [[2, 1], [1, 1]], [1, 1], [1, 1]),
        ("zero_wave", [[1, 1], [1, 1]], [0, 1], [1, 1]),
        ("negative_cap", [[1, 1], [1, 1]], [1, 1], [-1, 1])):
        negative(label, lambda g=geo, w=wave, c=cap: m.contrast(s, g, w, c))


def test_binding_negatives():
    d = m.capture(m.GRAPH_RECEIPT, m.GRAPH_SHA)
    g = next(r["result"] for r in d["records"] if r["kind"] == "FIXED_GRAPH_OR_STOP" and r["result"]["status"] == "CONDITIONAL_MODELED_FIRST_LEG_RN64_GRAPH_ONLY")
    inputs = m.capture(m.LITERAL_RECEIPT, m.LITERAL_SHA)["data"]["inputs"]
    lit = {k: inputs[g["case"]][k] for k in ("scene", "request")}
    c = g["modeled_length_interval_BU"]
    for k, v in (("source_id", "S1"), ("native_precision_certified", True), ("source_box_BU", [[[0, 1], [0, 1]]]*3),
                 ("graph", "FMA"), ("primitive_id", True), ("radicand_interval_BU2", [[1, 1], [1, 1]])):
        alt = copy.deepcopy(g)
        alt[k] = v
        negative("sealed_"+k, lambda a=alt: m.compose(a, lit, c, expected_graph_row_sha256=m.digest(g), model=m.MODEL))
        negative("semantic_"+k, lambda a=alt: m.compose(a, lit, c, expected_graph_row_sha256=m.digest(a), model=m.MODEL))
    changed = copy.deepcopy(lit)
    changed["request"]["source_width_caps_rad"][0] = [1, 1]
    negative("cap_lift_query_identity", lambda: m.compose(g, changed, c, expected_graph_row_sha256=m.digest(g), model=m.MODEL))
    negative("parent_pin", lambda: m.capture(m.GRAPH_RECEIPT, "0"*64))
    negative("model", lambda: m.run(model="implicit"))


if __name__ == "__main__":
    for fn in (test_fixed, test_midpoint_controls, test_numeric_negatives, test_binding_negatives):
        fn()
    print(json.dumps(dict(status="PASS", tests=4, records=records), sort_keys=True, allow_nan=False))
