"""New graph controls and sealed SOURCE contrasts; no legacy suite replay."""
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Blender.benchmarks.capacity_audit import original_SOURCE_first_leg_RN64_graph_HOST_v1 as m

records = []


def point(x, y=0, z=0):
    return [[[F(v).numerator, F(v).denominator]]*2 for v in (x, y, z)]


def check(out):
    assert out["promotion"] == "STOP" and out["SOURCE_merged"] is False
    assert all(out[k] is False for k in m.retained_io.FLAGS)
    assert out["native_SOURCE_ingress_error_bound_BU"] is None
    assert out["native_first_leg_error_bound_BU"] is None and out["native_phase_error_bound_rad"] is None
    assert out["GPU_used"] is False and out["Bpy_used"] is False and out["RT_used"] is False
    assert out["old_root_replays"] == out["frozen_producer_replays"] == 0
    assert out["source_phase"] is None and out["material_phase"] is None


def enclose(a, b, **kwargs):
    return m.enclose(a, b, source_id=kwargs.get("source_id", "S0"),
                     units=kwargs.get("units", "BU"), model=kwargs.get("model", m.MODEL))


def rejected(label, fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError) as ex:
        records.append(dict(kind="NEGATIVE", id=label, reason=str(ex)))
    else:
        raise AssertionError("accepted:"+label)


def test_fixed():
    rows, literals = m.retained_io.retained()
    outputs = m.run(model=m.MODEL)
    assert len(outputs) == 28
    valid = []
    for row, out in zip(rows, outputs):
        check(out)
        assert out["source_id"] == row["source_id"]
        assert out["captured_SOURCE_row_sha256"] == m.digest(row)
        if row["cycles_interval"] is None:
            assert out["status"] == "STOP_UPSTREAM_NO_FIRST_LEG_GRAPH"
            assert out["costs"]["new_integer_root_certificates"] == 0
        else:
            assert out["status"] == "CONDITIONAL_MODELED_FIRST_LEG_RN64_GRAPH_ONLY"
            assert out["costs"] == dict(new_modeled_scalar_operations=9, new_integer_root_certificates=2)
            assert out["captured_geometric_root_inequalities_verified"] == 2
            assert out["captured_candidate_cycles_left_unchanged"] is True
            assert F(*out["conditional_graph_vs_geometric_allowance_BU"]) > 0
            valid.append(out)
        records.append(dict(kind="FIXED_GRAPH_OR_STOP", result=out))
    assert len(valid) == 8 and len({(v["case"], v["source_id"]) for v in valid}) == 8
    # Changing the reference changes the sealed query, not this first-leg graph.
    for sid in ("S0", "S1"):
        a = next(v for v in valid if v["case"] == "oblique" and v["source_id"] == sid)
        b = next(v for v in valid if v["case"] == "shared_ref1000" and v["source_id"] == sid)
        assert a["query_sha256"] != b["query_sha256"]
        assert a["modeled_length_interval_BU"] == b["modeled_length_interval_BU"]


def test_graph_controls():
    cases = [("zero", point(0), point(0), F(0)),
             ("345", point(0), point(3, 4), F(5)),
             ("negative", point(3, 4), point(0), F(5)),
             ("irrational", point(0), point(1, 1), None),
             ("below_root_grid", point(0), point(F(1, 2**100)), None),
             ("coordinate_domain_edge", point(-10**6), point(10**6), F(2*10**6))]
    for label, a, b, exact in cases:
        out = enclose(a, b)
        check(out)
        lo, hi = (F(*v) for v in out["modeled_length_interval_BU"])
        if exact is not None:
            assert lo == hi == exact
        if label == "below_root_grid":
            assert lo == 0 and hi == F(1, 2**96) and hi > F(1, 2**100)
        records.append(dict(kind="GRAPH_CONTROL", id=label, result=out))
    crossing = point(0)
    crossing[0] = [[-1, 1], [1, 1]]
    out = enclose(point(0), crossing)
    assert out["squared_intervals_BU2"][0] == [[0, 1], [1, 1]]
    assert out["modeled_length_interval_BU"] == [[0, 1], [1, 1]]
    check(out)
    records.append(dict(kind="GRAPH_CONTROL", id="square_dependency_crossing_zero", result=out))
    # Lost low contribution must survive in the interval even without FMA.
    out = enclose(point(0), point(1, F(1, 2**27)))
    assert tuple(F(*v) for v in out["radicand_interval_BU2"]) == (F(1), F(1)+F(1, 2**52))
    records.append(dict(kind="GRAPH_CONTROL", id="rounding_small_addend", result=out))


def test_input_negatives():
    bad = [None, [], point(0)[:2], [point(0)[0]],
           [[[1, 3], [1, 3]], *point(0)[1:]],
           [[[1, 1], [0, 1]], *point(0)[1:]],
           [[[True, 1], [True, 1]], *point(0)[1:]],
           [[[0, 2], [0, 2]], *point(0)[1:]],
           [[[0, 0], [0, 0]], *point(0)[1:]],
           [[[1, -1], [1, -1]], *point(0)[1:]],
           point(10**6+1), point(F(1, 2**128))]
    for i, value in enumerate(bad):
        rejected("SOURCE_shape_domain_"+str(i), lambda v=value: enclose(v, point(0)))
        rejected("P_shape_domain_"+str(i), lambda v=value: enclose(point(0), v))
    for k, v in (("source_id", True), ("source_id", "S2"), ("units", "m"), ("model", "implicit")):
        rejected(k+str(v), lambda k=k, v=v: enclose(point(0), point(0), **{k: v}))


def test_binding_negatives():
    rows, literals = m.retained_io.retained()
    row = next(r for r in rows if r["cycles_interval"] is not None)
    literal = literals[row["case"]]
    mutations = [("source_id", "S1"), ("scene_sha256", "0"*64),
                 ("query_sha256", "0"*64), ("primitive_id", True),
                 ("previous_primitive_id", 0), ("native_precision_certified", True),
                 ("SOURCE_merged", True), ("origin_offset_applied", True),
                 ("source_origin_box_BU", point(0)), ("source_phase", [0, 1])]
    for k, v in mutations:
        altered = copy.deepcopy(row)
        altered[k] = v
        rejected("sealed_"+k, lambda a=altered: m.compose(a, literal, expected_row_sha256=m.digest(row), model=m.MODEL))
        rejected("contract_"+k, lambda a=altered: m.compose(a, literal, expected_row_sha256=m.digest(a), model=m.MODEL))
    for key in ("floor_scaled_root", "scaled_numerator", "scaled_denominator", "lower_BU", "exact"):
        altered = copy.deepcopy(row)
        cert = altered["new_first_segment"]["root_lower_certificate"]
        cert[key] = [0, 1] if key == "lower_BU" else (not cert[key] if key == "exact" else cert[key]+1)
        rejected("captured_root_"+key, lambda a=altered: m.compose(a, literal, expected_row_sha256=m.digest(a), model=m.MODEL))
    rejected("literal_context_missing", lambda: m.compose(row, None, expected_row_sha256=m.digest(row), model=m.MODEL))
    changed = copy.deepcopy(literal)
    changed["request"]["reference_BU"] = [999, 1]
    rejected("same_scene_other_query", lambda: m.compose(row, changed, expected_row_sha256=m.digest(row), model=m.MODEL))
    with patch.dict(m.DEPS, {next(iter(m.DEPS)): "0"*64}):
        rejected("dependency_pin", lambda: m.run(model=m.MODEL))


def test_no_alias():
    a, b = point(0), point(3, 4)
    before = copy.deepcopy((a, b))
    out = enclose(a, b)
    assert (a, b) == before
    snapshot = copy.deepcopy(out)
    out["source_box_BU"][0][0][0] = 99
    out["assumptions"].append("changed")
    assert (a, b) == before and "changed" not in m.ASSUMPTIONS
    records.append(dict(kind="NO_ALIAS", status="PASS", result=snapshot))


if __name__ == "__main__":
    for fn in (test_fixed, test_graph_controls, test_input_negatives, test_binding_negatives, test_no_alias):
        fn()
    print(json.dumps(dict(status="PASS", tests=5, records=records), sort_keys=True, allow_nan=False))
