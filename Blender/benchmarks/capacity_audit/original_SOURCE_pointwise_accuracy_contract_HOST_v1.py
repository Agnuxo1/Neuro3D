"""Opt-in pointwise budget gate over sealed CPU witnesses, not native admission."""
import base64
import copy
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[3]
ID = "PRECISION-ORIGINAL-SOURCE-POINTWISE-ACCURACY-CONTRACT-HOST-001"
MODEL = "original-SOURCE-pointwise-accuracy-contract-HOST-v1"
WITNESS = "PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-CAP-WITNESS-CPU-001-CODEX.json"
WITNESS_SHA = "0611221f8b72ba5637f19679af2785fb1674b391653916372a014ee5d9bc70c7"
LITERAL = "PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
LITERAL_SHA = "139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
OBSERVABLE = "ABS_ERROR_RN64_FIRST_LEG_VS_EXACT_DECLARED_SOURCE_TO_P_NORM"
BACKEND = "CPU_HYPOTHETICAL_RN64_GRAPH_NOT_NATIVE_BACKEND"
SCOPE = "ISOLATED_FIRST_LEG_UNWRAPPED_PHASE_TERM_NOT_TOTAL_PATH_OR_NATIVE_PHASE"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def rational(value):
    need(type(value) is list and len(value) == 2 and all(type(x) is int for x in value), "typed_rational")
    need(value[1] > 0 and math.gcd(*value) == 1 and
         max(abs(value[0]).bit_length(), value[1].bit_length()) <= 128, "canonical_capacity128")
    return F(*value)


def pair(value):
    need(max(abs(value.numerator).bit_length(), value.denominator.bit_length()) <= 512, "output_capacity512")
    return [value.numerator, value.denominator]


def captured(name, expected):
    raw = (ROOT/"coordinacion/respuestas"/name).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected, "receipt_pin")
    receipt = json.loads(raw)
    for path, pin in receipt["code_doc_sha256"].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == pin, "code_doc_pin")
    cap = receipt["test_run"]
    need(type(cap["rc"]) is int and cap["rc"] == 0 and cap.get("timed_out", False) is False, "capture_exit")
    if name == WITNESS:
        need(cap["before_deadline"] is True, "capture_deadline")
    data = zlib.decompress(base64.b64decode(cap["stdout_zlib_base64"], validate=True))
    need(len(data) == cap["stdout_bytes"] and hashlib.sha256(data).hexdigest() == cap["stdout_sha256"], "capture_seal")
    result = json.loads(data)
    need(result["status"] == "PASS", "capture_PASS")
    return result


def snapshot():
    """Read existing captures only; no producer, sqrt, or prior test execution."""
    rows = [v["result"] for v in captured(WITNESS, WITNESS_SHA)["records"]
            if v["kind"] == "FIXED_WITNESS_OR_STOP"]
    need(len(rows) == 28, "census28")
    literals = captured(LITERAL, LITERAL_SHA)["data"]["inputs"]
    return rows, literals


def declared_contract(row, literal, length_budget, phase_budget):
    """Caller explicitly allocates new modeled budgets; never inherit width caps."""
    return dict(schema=MODEL, evidence_receipt_sha256=WITNESS_SHA, evidence_row_sha256=digest(row),
                scene_sha256=row["scene_sha256"], query_sha256=row["query_sha256"], source_id=row["source_id"],
                backend=BACKEND, observable=OBSERVABLE, phase_observable=SCOPE, units="BU",
                reference_BU=copy.deepcopy(literal["request"]["reference_BU"]),
                wavelength_BU=copy.deepcopy(literal["request"]["lambda_BU"]),
                budget_provenance="CALLER_EXPLICIT_MODEL_ONLY_NOT_ORIGINAL_SCENE_REQUIREMENT",
                length_accuracy_budget_BU=copy.deepcopy(length_budget),
                isolated_phase_accuracy_budget_rad=copy.deepcopy(phase_budget))


def classify(bounds, budget):
    need(type(bounds) is tuple and len(bounds) == 2 and all(type(v) is F for v in bounds) and
         0 <= bounds[0] <= bounds[1], "ordered_nonnegative_fraction_bounds")
    if budget is None:
        return "STOP_UNALLOCATED_POINTWISE_BUDGET"
    allocated = rational(budget)
    need(allocated >= 0, "nonnegative_accuracy_budget")
    if bounds[1] <= allocated:
        return "MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET"
    if bounds[0] > allocated:
        return "MODEL_ERROR_EXCEEDS_EXPLICIT_POINTWISE_BUDGET"
    return "STOP_POINTWISE_BOUND_STRADDLES_BUDGET"


def assess(row, literal, contract, *, expected_row_sha256):
    need(type(row) is dict and digest(row) == expected_row_sha256, "sealed_row")
    fixed, _ = snapshot()
    need(any(digest(value) == expected_row_sha256 for value in fixed), "fixed_parent_row_membership")
    need(row["status"] in ("TERM_ERROR_ABOVE_LITERAL_WIDTH_SCALE", "TERM_ERROR_BOUND_WITHIN_LITERAL_WIDTH_SCALE",
                           "STOP_WIDTH_SCALE_COMPARISON_UNRESOLVED"), "active_witness_only")
    need(row["promotion"] == "STOP" and row["native_precision_certified"] is False and
         row["GPU_used"] is False and row["phase_certified"] is False and row["SOURCE_merged"] is False,
         "modeled_not_native")
    scene, request = literal["scene"], literal["request"]
    need(digest(scene) == row["scene_sha256"] == request["original_scene_sha256"] and
         digest(request) == row["query_sha256"], "scene_query_binding")
    need(type(contract) is dict and set(contract) == set(declared_contract(row, literal, None, None)), "closed_schema")
    expected = declared_contract(row, literal, contract["length_accuracy_budget_BU"], contract["isolated_phase_accuracy_budget_rad"])
    need(digest(contract) == digest(expected), "observable_backend_reference_SOURCE_binding")
    need(scene["units"] == contract["units"] == "BU" and row["scope"] == SCOPE, "units_scope")
    wave = rational(contract["wavelength_BU"])
    rational(contract["reference_BU"])
    need(wave > 0 and row["wavelength_BU"] == contract["wavelength_BU"], "positive_same_lambda")
    # Signed discrepancy endpoints are sealed outputs, not uncertainty width.
    lo, hi = map(rational, row["signed_first_leg_discrepancy_BU"])
    need(lo <= hi, "ordered_discrepancy")
    lower = F(0) if lo <= 0 <= hi else min(abs(lo), abs(hi))
    upper = max(abs(lo), abs(hi))
    bounds = (lower, upper)
    phase = (6*lower/wave, 8*upper/wave)  # 6 < 2*pi < 8, isolated term only.
    need(row["absolute_first_leg_discrepancy_BU"] == list(map(pair, bounds)) and
         row["isolated_phase_term_error_rad"] == list(map(pair, phase)), "sealed_bound_consistency")
    length_status = classify(bounds, contract["length_accuracy_budget_BU"])
    phase_status = classify(phase, contract["isolated_phase_accuracy_budget_rad"])
    statuses = (length_status, phase_status)
    status = ("STOP_UNALLOCATED_POINTWISE_BUDGET" if any("UNALLOCATED" in s for s in statuses) else
              "MODEL_ERROR_EXCEEDS_EXPLICIT_POINTWISE_BUDGET" if any("EXCEEDS" in s for s in statuses) else
              "STOP_POINTWISE_BOUND_STRADDLES_BUDGET" if any("STRADDLES" in s for s in statuses) else
              "MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET")
    return dict(status=status, length_status=length_status, isolated_phase_status=phase_status,
                contract=copy.deepcopy(contract), contract_sha256=digest(contract),
                evidence_row_sha256=expected_row_sha256, absolute_error_BU=list(map(pair, bounds)),
                isolated_phase_error_rad=list(map(pair, phase)),
                original_width_cap_used_as_accuracy_budget=False, native_admission="STOP_MISSING_NATIVE_EVIDENCE",
                native_missing=["backend_GRAPH_and_ABI_identity", "SOURCE_and_P_ingress_error",
                                "native_ALU_reference_lambda_phase_error_and_allocations", "complete_path_geometry_coverage",
                                "separate_SOURCE_material_phase", "per_job_guard_deadline_and_equal_work_full_costs"],
                native_precision_certified=False, native_accuracy_budget_admitted=False, phase_certified=False,
                total_path_error_bound_rad=None, native_SOURCE_ingress_error_bound_BU=None,
                SOURCE_merged=False, promotion="STOP", GPU_used=False, Bpy_used=False, RT_used=False,
                old_producer_replays=0, new_root_evaluations=0, full_costs="UNKNOWN_NOT_ZERO",
                JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
