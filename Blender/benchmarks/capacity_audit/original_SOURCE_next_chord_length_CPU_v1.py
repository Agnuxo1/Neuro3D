"""Opt-in HOST rational norms from modeled next-position boxes, not selected paths."""
import base64
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from Blender.benchmarks.capacity_audit import oblique_trace_endpoint_length_enclosure_HOST_v1 as norm

ROOT = Path(__file__).resolve().parents[3]
MODEL = "original-SOURCE-next-chord-length-CPU-v1"
PARENT = "coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-NEXT-POSITION-BOX-CPU-001-CODEX.json"
PSHA = "2f55ba29b624ddddef68b1e28ec8b50f23d85eaec6ffb6b9cd6c39e668528b29"
NORM = "Blender/benchmarks/capacity_audit/oblique_trace_endpoint_length_enclosure_HOST_v1.py"
NSHA = "8f3b77dba20a755754f1c0da4bc9b779d35056a02240b6602d0c7d1d34d330e8"
CONTEXT = ("case", "source_id", "scene_sha256", "query_sha256", "input_sha256",
           "source_record_sha256", "CPU_packet_binding_sha256", "primitive_id", "previous_primitive_id")


def need(ok, why):
    if not ok:
        raise ValueError(why)


def box(value):
    need(type(value) is list and len(value) == 3, "box3")
    result = []
    for axis in value:
        need(type(axis) is list and len(axis) == 2, "axis2")
        lo, hi = map(norm.rat, axis)
        need(lo <= hi and max(abs(lo), abs(hi)) <= 1000000, "ordered_bounded_box")
        result.append((lo, hi))
    return result


def enclose(point_bounds, next_position_bounds, *, model):
    """Exact norm hull for independent endpoint boxes, with fixed 96-bit roots.

    No native length ALU model. Loss of P/Q correlation is conservative, even
    when both boxes describe the same uncertain contact point.
    """
    need(type(model) is str and model == MODEL, "explicit_model")
    point, target = box(point_bounds), box(next_position_bounds)
    costs = dict(new_interval_segment_norms=0, new_integer_root_certificates=0)
    chord = norm.segment(point, target, costs)
    return dict(model=MODEL, status="CONDITIONAL_CHORD_LENGTH_BOX_ONLY",
                point_box=copy.deepcopy(point_bounds),
                modeled_next_position_box_BU=copy.deepcopy(next_position_bounds),
                chord=chord, costs=costs, root_fraction_bits=norm.BITS,
                scope="CALLER_CONDITIONAL_ENDPOINT_BOXES_ONLY", parent_receipt_sha256=None,
                units=dict(displacement="BU", squared="BU2", length="BU"),
                assumptions=["actual_start_in_declared_P_box", "actual_end_in_declared_modeled_Q_box",
                             "independent_boxes_conservative_correlation_loss",
                             "HOST_exact_rational_norm_and_integer_root_certificates_NOT_native_length_ALU"],
                native_precision_certified=False, native_length_graph_certified=False,
                length_accuracy_budget_admitted=False, native_length_error_bound=None,
                triangle_hit_certified=False, nearest_hit_certified=False,
                launch_exclusion_allowed=False, full_path_visibility_certified=False,
                GPU_launch_allowed=False, phase_certified=False,
                phase_error_bound=None, length_reference_phase_bound=None,
                ignored_primitive_ids=[], origin_offset_applied=False,
                SOURCE_merged=False, full_costs="UNKNOWN_NOT_ZERO")


def compose(row, *, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    need(row["model"] == "original-SOURCE-next-position-box-CPU-v1"
         and row["status"] == "CONDITIONAL_RAY_POSITION_BOX_ONLY", "position_contract")
    need(row["upstream_ledger_status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES"
         and row["conditional_first_id"] is None, "keep_ledger_STOP")
    need(row["ignored_primitive_ids"] == [] and row["origin_offset_applied"] is False, "keep_previous_contact")
    need(row["upstream_triangle_status"] in ("CONDITIONAL_TRIANGLE_INTERIOR_HIT",
         "CONDITIONAL_TRIANGLE_MISS", "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED"), "triangle_status")
    for flag in ("native_precision_certified", "triangle_hit_certified", "nearest_hit_certified",
                 "launch_exclusion_allowed", "GPU_launch_allowed", "full_path_visibility_certified", "phase_certified"):
        need(row[flag] is False, "no_upstream_promotion:"+flag)
    need(row["source_id"] in ("S0", "S1") and type(row["source_id"]) is str, "SOURCE_identity")
    for key in ("primitive_id", "previous_primitive_id"):
        need(type(row[key]) is int and 0 <= row[key] < 2**32, "typed_primitive")
    out = enclose(row["point_box"], row["modeled_binary64_position_box_BU"], model=model)
    out.update({key: copy.deepcopy(row[key]) for key in CONTEXT})
    out.update(upstream_triangle_status=row["upstream_triangle_status"],
               upstream_ledger_status=row["upstream_ledger_status"], conditional_first_id=None,
               scope="CALLER_CONDITIONAL_POSITION_CONTENT_ONLY")
    return out


def retained():
    raw = (ROOT/PARENT).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PSHA, "fixed_position_receipt")
    need(hashlib.sha256((ROOT/NORM).read_bytes()).hexdigest() == NSHA, "fixed_pure_norm_helper")
    r = json.loads(raw)
    cap = r["test_run"]
    need(type(cap["rc"]) is int and cap["rc"] == 0 and cap["before_deadline"] is True, "completed_position_capture")
    for path, e in cap["sources"].items():
        b = (ROOT/path).read_bytes()
        need(len(b) == e["bytes"] and hashlib.sha256(b).hexdigest() == e["sha256"], "position_source_pin")
    decoder = zlib.decompressobj()
    b = decoder.decompress(base64.b64decode(cap["stdout_zlib_base64"], validate=True), 2097153)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
         and len(b) <= 2097152 and len(b) == cap["stdout_bytes"]
         and hashlib.sha256(b).hexdigest() == cap["stdout_sha256"], "position_capture_identity")
    d = json.loads(b)
    need(d["status"] == "PASS" and len(d["records"]) == 67, "position_PASS67")
    rows = [x["result"] for x in d["records"] if x["kind"] == "FIXED_POSITION"]
    need(len(rows) == 28 and len({(x["case"], x["source_id"], x["primitive_id"])
                                  for x in rows}) == 28, "unique_fixed28")
    return rows


def run(*, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    rows = retained()
    results = []
    for row in rows:
        out = compose(row, model=model)
        out.update(scope="FIXED_CAPTURE_CPU_CONTENT_ONLY_NOT_NATIVE", parent_receipt_sha256=PSHA)
        results.append(out)
    return results
