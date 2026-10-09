"""Explicit modeled accuracy allocations, unknowns, and immutable context gates."""
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Blender.benchmarks.capacity_audit import original_SOURCE_pointwise_accuracy_contract_HOST_v1 as m

records = []


def negative(label, fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError) as exc:
        records.append(dict(kind="NEGATIVE", id=label, reason=str(exc)))
    else:
        raise AssertionError(label)


def test_fixed_allocations():
    rows, literals = m.snapshot()
    for row in rows:
        if row["status"] == "STOP_UPSTREAM_NO_CAP_WITNESS":
            records.append(dict(kind="UPSTREAM_STOP_PRESERVED", evidence_row_sha256=m.digest(row)))
            continue
        literal = literals[row["case"]]
        for label, length, phase in (("unallocated", None, None), ("tight", [1, 2**80], [1, 2**80]),
                                     ("loose", [1, 2**50], [1, 2**40])):
            contract = m.declared_contract(row, literal, length, phase)
            result = m.assess(row, literal, contract, expected_row_sha256=m.digest(row))
            expected = ("STOP_UNALLOCATED_POINTWISE_BUDGET" if label == "unallocated" else
                        "MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET" if label == "loose" or row["case"] == "tiny_gap_2m60" else
                        "MODEL_ERROR_EXCEEDS_EXPLICIT_POINTWISE_BUDGET")
            assert result["status"] == expected
            assert result["native_admission"] == "STOP_MISSING_NATIVE_EVIDENCE"
            assert not result["native_accuracy_budget_admitted"] and not result["original_width_cap_used_as_accuracy_budget"]
            records.append(dict(kind="FIXED_EXPLICIT_ALLOCATION", label=label, case=row["case"], source_id=row["source_id"], result=result))


def test_boundaries_and_unknown():
    for label, bounds, budget, expected in (
        ("upper_equal", (F(1), F(2)), [2, 1], "MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET"),
        ("lower_equal", (F(1), F(2)), [1, 1], "STOP_POINTWISE_BOUND_STRADDLES_BUDGET"),
        ("strict_exceeds", (F(1), F(2)), [0, 1], "MODEL_ERROR_EXCEEDS_EXPLICIT_POINTWISE_BUDGET"),
        ("zero_exact", (F(0), F(0)), [0, 1], "MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET"),
        ("zero_not_unknown", (F(0), F(0)), None, "STOP_UNALLOCATED_POINTWISE_BUDGET")):
        assert m.classify(bounds, budget) == expected
        records.append(dict(kind="BOUNDARY_CONTROL", id=label, status=expected))
    rows, literals = m.snapshot()
    row = next(r for r in rows if r["case"] == "oblique" and "scene_sha256" in r)
    lit = literals[row["case"]]
    for label, a, b in (("missing_length", None, [1, 1]), ("missing_phase", [1, 1], None)):
        result = m.assess(row, lit, m.declared_contract(row, lit, a, b), expected_row_sha256=m.digest(row))
        assert result["status"] == "STOP_UNALLOCATED_POINTWISE_BUDGET"
        records.append(dict(kind="PARTIAL_ALLOCATION_STOP", id=label, result=result))


def test_schema_and_context_rejections():
    rows, literals = m.snapshot()
    row = next(r for r in rows if r["case"] == "oblique" and "scene_sha256" in r)
    lit = literals[row["case"]]
    contract = m.declared_contract(row, lit, [1, 1], [1, 1])
    for key, value in (("backend", "CUDA_RN64"), ("observable", "GEOMETRIC_INTERVAL_WIDTH"),
                       ("phase_observable", "TOTAL_PATH_PHASE"), ("source_id", "S1"), ("units", "m"),
                       ("reference_BU", [1000, 1]), ("wavelength_BU", [1, 4]),
                       ("evidence_receipt_sha256", "0"*64), ("evidence_row_sha256", "0"*64),
                       ("query_sha256", "0"*64), ("schema", "implicit"),
                       ("budget_provenance", "INHERITED_ORIGINAL_WIDTH_CAP")):
        alt = copy.deepcopy(contract); alt[key] = value
        negative(key, lambda alt=alt: m.assess(row, lit, alt, expected_row_sha256=m.digest(row)))
    for value in ([True, 1], [1, 0], [2, 2], [-1, 1], [1, 2**128], 0):
        alt = copy.deepcopy(contract); alt["length_accuracy_budget_BU"] = value
        negative("malformed_budget_"+str(value), lambda alt=alt: m.assess(row, lit, alt, expected_row_sha256=m.digest(row)))
    for op in ("extra", "missing"):
        alt = copy.deepcopy(contract)
        if op == "extra": alt["native_SOURCE_ingress_error_bound_BU"] = [0, 1]
        else: del alt["isolated_phase_accuracy_budget_rad"]
        negative(op, lambda alt=alt: m.assess(row, lit, alt, expected_row_sha256=m.digest(row)))
    alt = copy.deepcopy(row); alt["signed_first_leg_discrepancy_BU"] = [[0, 1], [0, 1]]
    negative("edited_witness", lambda: m.assess(alt, lit, contract, expected_row_sha256=m.digest(row)))
    resealed = m.declared_contract(alt, lit, [1, 1], [1, 1])
    negative("caller_resealed_witness", lambda: m.assess(alt, lit, resealed, expected_row_sha256=m.digest(alt)))
    negative("same_scene_different_query", lambda: m.assess(row, literals["shared_ref1000"], contract, expected_row_sha256=m.digest(row)))
    negative("wrong_parent_pin", lambda: m.captured(m.WITNESS, "0"*64))
    alt = copy.deepcopy(contract); alt["isolated_phase_accuracy_budget_rad"] = [True, 1]
    negative("malformed_phase_budget", lambda: m.assess(row, lit, alt, expected_row_sha256=m.digest(row)))
    for bad in ((F(2), F(1)), (F(-1), F(0)), (0, 1), [F(0), F(1)]):
        negative("malformed_bounds_"+str(bad), lambda bad=bad: m.classify(bad, [1, 1]))


def test_contract_copy_isolation():
    rows, literals = m.snapshot()
    row = next(r for r in rows if "scene_sha256" in r)
    lit = literals[row["case"]]
    contract = m.declared_contract(row, lit, [1, 1], [1, 1])
    before = m.digest([row, lit, contract])
    result = m.assess(row, lit, contract, expected_row_sha256=m.digest(row))
    result["contract"]["reference_BU"][0] += 1
    result["absolute_error_BU"][0][0] = 0
    assert m.digest([row, lit, contract]) == before
    records.append(dict(kind="COPY_ISOLATION", unchanged_input_sha256=before))


if __name__ == "__main__":
    for fn in (test_fixed_allocations, test_boundaries_and_unknown, test_schema_and_context_rejections, test_contract_copy_isolation):
        fn()
    print(json.dumps(dict(status="PASS", tests=4, records=records), sort_keys=True, allow_nan=False))
