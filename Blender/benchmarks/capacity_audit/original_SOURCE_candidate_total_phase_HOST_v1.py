"""Opt-in HOST diagnostic: captured candidate cycles plus explicit phase overlay.

Never imports/replays a frozen producer or promotes a native path. Original
scene phases remain UNKNOWN; a declared overlay is not physical evidence.
"""
import base64
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[3]
ID = "PRECISION-ORIGINAL-SOURCE-CANDIDATE-TOTAL-PHASE-HOST-001"
MODEL = "original-SOURCE-candidate-total-phase-HOST-v1"
CYCLE_MODEL = "original-SOURCE-candidate-path-cycles-HOST-v1"
CASES = ("oblique", "direction_scaled", "shared_ref1000", "tiny_gap_2m60")
PARENTS = {
    "PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001-CODEX.json":
        "53b739dcaaf08e2bbce9ca81ce7a24b98bc53074357720a4bc9aaaf317aae1fe",
    "PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json":
        "f7a5f99aa2d2f18d68b01ab9c4afe4b1db85bc78c7a6a9228809b3066e46a05b",
    "PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json":
        "139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e",
}
OVERLAY_PARENT = "75d7bece210984fc2c30d761946a7285f1f2bcacce68208b5b44d71e5e85972a"
FLAGS = ("native_precision_certified", "native_length_graph_certified", "length_accuracy_budget_admitted",
         "triangle_hit_certified", "nearest_hit_certified", "launch_exclusion_allowed",
         "full_path_visibility_certified", "GPU_launch_allowed", "phase_certified",
         "detector_connection_certified", "first_leg_native_ALU_certified", "physical_optics_certified",
         "scene_authenticated")


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def rat(v, bits=512):
    need(type(v) is list and len(v) == 2 and all(type(x) is int for x in v), "typed_rational")
    need(v[1] > 0 and max(abs(v[0]).bit_length(), v[1].bit_length()) <= bits, "rational_capacity")
    q = F(*v)
    need([q.numerator, q.denominator] == v, "canonical_rational")
    return q


def pair(q):
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 512, "output_capacity512")
    return [q.numerator, q.denominator]


def interval(v, bits=512):
    need(type(v) is list and len(v) == 2, "interval2")
    a, b = (rat(x, bits) for x in v)
    need(a <= b, "ordered_interval")
    return a, b


def capture(r, *, require_deadline=False):
    t = r["test_run"]
    need(type(t["rc"]) is int and t["rc"] == 0 and t.get("timed_out", False) is False, "capture_exit")
    if require_deadline:
        need(t.get("before_deadline") is True, "capture_deadline")
    raw = zlib.decompress(base64.b64decode(t["stdout_zlib_base64"], validate=True))
    need(type(t["stdout_bytes"]) is int and len(raw) == t["stdout_bytes"] and
         sha(raw) == t["stdout_sha256"], "capture_integrity")
    d = json.loads(raw)
    need(d["status"] == "PASS", "capture_status")
    return d


def retained():
    data = {}
    for name, expected in PARENTS.items():
        raw = (ROOT / "coordinacion/respuestas" / name).read_bytes()
        need(sha(raw) == expected, "parent_receipt_identity")
        r = json.loads(raw)
        for path, h in r["code_doc_sha256"].items():
            need(sha((ROOT / path).read_bytes()) == h, "parent_code_doc_pin")
        data[name] = capture(r, require_deadline="CANDIDATE-PATH-CYCLES" in name)
    cycles = data[next(n for n in data if "CANDIDATE-PATH-CYCLES" in n)]
    rows = [x["result"] for x in cycles["records"] if x["kind"] == "FIXED_PATH_OR_STOP"]
    need(len(rows) == 28, "captured_candidate_census")
    overlays = data[next(n for n in data if "SOURCE-MATERIAL-INTERVAL" in n)]["data"]["runs"]
    geometry = data[next(n for n in data if "COMMON-DETECTOR-LENGTH" in n)]["data"]["inputs"]
    requests = {}
    for case in CASES:
        selected = [x["request"] for x in overlays if x["id"] == "parent_" + case]
        need(len(selected) == 1, "captured_explicit_overlay")
        requests[case] = selected[0]
    return rows, geometry, requests


def base():
    return dict(model=MODEL, status="STOP", reason=None, rows=[], diagnostics=[], promotion="STOP",
                native_promotion_allowed=False, GPU_launch_allowed=False, GPU_used=False,
                phase_certified=False, native_phase_error_bound=None, material_authenticated=False,
                SOURCE_merged=False, old_ideal_relative_interval_used=False,
                amplitude=None, field=None, power=None, full_costs="UNKNOWN_NOT_ZERO",
                JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY", source_phase=None, material_phase=None,
                original_scene_phase_status="UNKNOWN_NOT_ZERO", backend="HOST_RATIONAL_DIAGNOSTIC_ONLY")


def evaluate(rows, literal, overlay, *, expected_row_sha256s, model):
    """Closed binding, independent SOURCE intervals; ALL caps before rows.

    Caller digests provide local consistency, not scene/physical authentication.
    A single shared coefficient variable cancels in the relative diagnostic;
    SOURCE phase, reference and wavelength uncertainty are not cancelled.
    """
    out = base()
    try:
        need(type(model) is str and model == MODEL, "explicit_model")
        need(type(rows) is list and len(rows) == 2 and type(expected_row_sha256s) is list and
             len(expected_row_sha256s) == 2, "ALL_two_SOURCE")
        need([digest(r) for r in rows] == expected_row_sha256s, "captured_row_binding")
        need(type(literal) is dict and set(literal) == {"scene", "request"}, "closed_literal_context")
        scene, query = literal["scene"], literal["request"]
        scene_sha, query_sha = digest(scene), digest(query)
        need(type(query["root_primitive_id"]) is int and type(query["detector_primitive_id"]) is int,
             "typed_literal_primitives")
        need(query["original_scene_sha256"] == scene_sha and query["source_ids"] == ["S0", "S1"], "literal_binding")
        case = rows[0]["case"]
        for j, r in enumerate(rows):
            need(r["model"] == CYCLE_MODEL and r["status"] == "CONDITIONAL_GEOMETRIC_PATH_CYCLES_ONLY",
                 "conditional_candidate_only")
            need(r["case"] == case and r["source_id"] == "S" + str(j) and
                 r["scene_sha256"] == scene_sha and r["query_sha256"] == query_sha, "SOURCE_scene_query_identity")
            need(all(r[f] is False for f in FLAGS) and r["SOURCE_merged"] is False and
                 r["origin_offset_applied"] is False and r["ignored_primitive_ids"] == [] and
                 r["conditional_first_id"] is None and r["upstream_ledger_status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES",
                 "upstream_native_STOP")
            need(type(r["previous_primitive_id"]) is int and r["previous_primitive_id"] == query["root_primitive_id"] == 1 and
                 type(r["primitive_id"]) is int and r["primitive_id"] == query["detector_primitive_id"] == 0,
                 "path_primitive_identity")
            need(r["reference_scope"] == "GEOMETRIC_TWO_SEGMENT_PATH" and r["units"] == "BU" and
                 r["result_units"] == "unwrapped_cycles_NOT_radians", "candidate_units_scope")
            need(r["reference_BU"] == [query["reference_BU"]]*2 and
                 r["wavelength_BU"] == [query["lambda_BU"]]*2, "literal_reference_wavelength")
            lo, hi = interval(r["cycles_interval"])
            need(rat(r["cycles_width"]) == hi-lo, "captured_width")
            need(r["source_phase"] is None and r["material_phase"] is None, "original_phase_unknown")
        if overlay is None:
            out.update(reason="UNKNOWN_SOURCE_MATERIAL_PHASE_NOT_ZERO", status="STOP_ORIGINAL_PHASE_UNKNOWN")
            return out
        need(type(overlay) is dict and set(overlay) == {"case", "parent_receipt_sha256", "original_scene_sha256",
             "literal_request_sha256", "overlay", "units", "authentication", "sources", "material"}, "closed_overlay")
        need(overlay["case"] == "parent_" + case and overlay["parent_receipt_sha256"] == OVERLAY_PARENT and
             overlay["original_scene_sha256"] == scene_sha and overlay["literal_request_sha256"] == query_sha,
             "overlay_scene_query_parent")
        need(overlay["overlay"] == "NEW_DECLARED_PHASE_OVERLAY" and
             overlay["authentication"] == "DECLARED_NOT_PHYSICALLY_AUTHENTICATED" and
             overlay["units"] == {"phase": "cycles", "cap": "rad"}, "explicit_declared_overlay")
        sources = overlay["sources"]
        need(type(sources) is list and len(sources) == 2, "ALL_SOURCE_overlay")
        gamma = []
        for j, s in enumerate(sources):
            need(type(s) is dict and set(s) == {"record_id", "branch_id", "phase_interval_cycles"} and
                 s["record_id"] == "S"+str(j) and s["branch_id"] == "S"+str(j)+"/mirror", "SOURCE_branch_order")
            gamma.append(interval(s["phase_interval_cycles"], 256))
        m = overlay["material"]
        need(type(m) is dict and set(m) == {"object_id", "primitive_id", "profile", "phase_interval_cycles"}, "closed_material")
        need(type(m["primitive_id"]) is int and m["primitive_id"] == 1 and
             m["profile"] == "DECLARED_COMPLETE_SHARED_COEFFICIENT_PHASE_CYCLES", "shared_complete_coefficient")
        primitive = [t for t in scene["triangles"] if t["primitive_id"] == 1]
        need(len(primitive) == 1 and primitive[0]["object_id"] == m["object_id"] == "oblique_common_fixture", "material_object")
        mu = interval(m["phase_interval_cycles"], 256)
        need(all(abs(x) <= 10**6 for iv in (*gamma, mu) for x in iv), "phase_magnitude")
        prop = [interval(r["cycles_interval"]) for r in rows]
        totals = [(p[0]+g[0]+mu[0], p[1]+g[1]+mu[1]) for p, g in zip(prop, gamma)]
        relative = (prop[0][0]-prop[1][1]+gamma[0][0]-gamma[1][1],
                    prop[0][1]-prop[1][0]+gamma[0][1]-gamma[1][0])
        caps = query["source_width_caps_rad"]
        need(type(caps) is list and len(caps) == 2, "ALL_SOURCE_caps")
        cap_values = [rat(c, 256) for c in (*caps, query["relative_width_cap_rad"])]
        need(all(c > 0 for c in cap_values), "positive_literal_caps")
        for j, (bounds, cap) in enumerate(zip((*totals, relative), cap_values)):
            lo, hi = bounds
            # About the exact HOST midpoint only: 2*pi<8 => radius<=4*width.
            # This is NOT a bound about any emitted/encoded/native phase value.
            mid = (lo+hi)/2
            rad = 4*(hi-lo)
            out["diagnostics"].append(dict(record_id="S"+str(j) if j < 2 else "S0-minus-S1",
                interval_cycles=[pair(lo), pair(hi)], HOST_midpoint_cycles=pair(mid),
                conditional_HOST_radius_bound_rad=pair(rad), literal_cap_rad=pair(cap), fits=rad <= cap,
                shared_material_cancellation="DECLARED_SAME_VARIABLE_ONLY" if j == 2 else "NONE"))
        out.update(overlay_sha256=digest(overlay), SOURCE_row_sha256s=copy.deepcopy(expected_row_sha256s),
                   case=case, scene_sha256=scene_sha, query_sha256=query_sha,
                   source_phase=copy.deepcopy(sources), material_phase=copy.deepcopy(m))
        if not all(x["fits"] for x in out["diagnostics"][:2]):
            out.update(status="STOP_ALL_SOURCE_DIAGNOSTIC_CAP", reason="ALL_SOURCE_before_relative")
        elif not out["diagnostics"][2]["fits"]:
            out.update(status="STOP_RELATIVE_DIAGNOSTIC_CAP", reason="relative_literal_cap")
        else:
            out.update(status="CONDITIONAL_HOST_OVERLAY_CAPS_ONLY", rows=copy.deepcopy(out["diagnostics"]))
    except (ValueError, TypeError, KeyError, IndexError, OverflowError) as ex:
        out.update(status="STOP_INPUT", reason=str(ex), rows=[])
    return out


def run(*, model):
    need(model == MODEL and type(model) is str, "explicit_model")
    rows, geometry, requests = retained()
    runs = []
    for case in CASES:
        selected = [r for r in rows if r["case"] == case and r["status"] == "CONDITIONAL_GEOMETRIC_PATH_CYCLES_ONLY"]
        selected.sort(key=lambda r: r["source_id"])
        need(len(selected) == 2, "ALL_captured_SOURCE_candidates")
        literal = {k: geometry[case][k] for k in ("scene", "request")}
        expected = [digest(r) for r in selected]
        for mode, overlay in (("ORIGINAL_UNKNOWN", None), ("EXISTING_DECLARED_OVERLAY", requests[case])):
            result = evaluate(selected, literal, overlay, expected_row_sha256s=expected, model=model)
            runs.append(dict(case=case, mode=mode, result=result))
    return dict(runs=runs, captured_candidate_rows=28, captured_conditional_cycle_rows=8,
                upstream_STOP_rows_preserved=20, parent_receipts_sha256=copy.deepcopy(PARENTS),
                geometry_queries=0, root_evaluations=0, frozen_producer_replays=0)
