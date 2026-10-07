"""Opt-in CPU previous-contact condition with non-singleton direction boxes.

Uses only pure arithmetic from retained helpers, not their contact evaluators.
No native exclusion, next-hit selection, launch or phase certification.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path
import zlib
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit import oblique_transport_contact_plane_CPU_v1 as ar
from Blender.benchmarks.capacity_audit import oblique_transport_contact_interior_CPU_v1 as affine
from Blender.benchmarks.capacity_audit import original_SOURCE_query_packet_CPU_v1 as packing

ROOT = Path(__file__).resolve().parents[3]
MODEL = "original-SOURCE-previous-contact-direction-box-CPU-v1"
PARENT = "coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-QUERY-PACKET-CPU-001-CODEX.json"
PSHA = "5f6b3d0ec64df544fc771044796cd88f62967322a879b10fd74fd012a194d272"
ARITHMETIC_PINS = {
    "Blender/benchmarks/capacity_audit/oblique_transport_contact_plane_CPU_v1.py":
        "ab3060ad3664842a834e600f81c1caa19da08adff445f3f6fbdb00382a5b0572",
    "Blender/benchmarks/capacity_audit/oblique_transport_contact_interior_CPU_v1.py":
        "23e0370f9f85a6c1dfa600eb54df5d26ad7104c4702c0a4cadd98d2a900ba022",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def box(value):
    need(type(value) is list and len(value) == 3, "box3")
    result = []
    for axis in value:
        need(type(axis) is list and len(axis) == 2, "axis2")
        lo, hi = map(ar.fraction, axis)
        need(lo <= hi, "ordered_box")
        result.append((lo, hi))
    return result


def condition(point_bounds, direction_bounds, triangle_words, *, model):
    """Mathematical condition for all members of two declared Cartesian boxes."""
    need(type(model) is str and model == MODEL, "explicit_model")
    point, direction = box(point_bounds), box(direction_bounds)
    need(type(triangle_words) is list and len(triangle_words) == 3, "triangle3")
    vertices = []
    for words in triangle_words:
        need(type(words) is list and len(words) == 3, "vertex3")
        vertex = tuple(ar.decode(w) for w in words)
        need(all(not ((w & 0x7f800000) == 0 and (w & 0x7fffff)) for w in words),
             "normal_or_positive_zero_geometry_only")
        vertices.append(vertex)
    a, b, c = vertices
    e1, e2 = ar.sub(b, a), ar.sub(c, a)
    normal = ar.cross(e1, e2)
    out = dict(model=MODEL, status="STOP_DEGENERATE_PLANE", normal_exact=None,
               point_box=copy.deepcopy(point_bounds), direction_box=copy.deepcopy(direction_bounds),
               plane_residual_interval=None, denominator_interval=None,
               plane_parameter_interval=None, barycentric_intervals=None,
               CPU_strict_interior_contact_for_all_directions=False,
               native_point_budget_authenticated=False, native_direction_budget_authenticated=False,
               native_precision_certified=False, launch_exclusion_allowed=False,
               nearest_hit_certified=False, GPU_launch_allowed=False, phase_certified=False,
               phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO",
               ignored_primitive_ids=[], origin_offset_applied=False,
               parameter_units="original_unnormalized_direction_parameter_NOT_BU_length")
    if not any(normal):
        return out
    out["normal_exact"] = [ar.pair(x) for x in normal]
    residual = affine.affine_interval(normal, -ar.dot(normal, a), point)
    denominator = affine.affine_interval(normal, F(0), direction)
    out.update(plane_residual_interval=[ar.pair(x) for x in residual],
               denominator_interval=[ar.pair(x) for x in denominator])
    if denominator[0] <= 0 <= denominator[1]:
        return dict(out, status="STOP_DIRECTION_PLANE_DENOMINATOR_ZERO_POSSIBLE")
    if residual != (F(0), F(0)):
        return dict(out, status="STOP_POINT_BOX_NOT_IDENTICALLY_ON_PREVIOUS_PLANE")
    # R identically zero and n.d excludes zero for EVERY direction: tau=0.
    # This preserves, rather than authorizes ignoring, the previous contact.
    out["plane_parameter_interval"] = [[0, 1], [0, 1]]
    g11, g12, g22 = ar.dot(e1, e1), ar.dot(e1, e2), ar.dot(e2, e2)
    gram = g11 * g22 - g12 * g12
    need(gram > 0, "positive_Gram_for_nondegenerate_plane")
    u = tuple((g22*x - g12*y) / gram for x, y in zip(e1, e2))
    v = tuple((g11*y - g12*x) / gram for x, y in zip(e1, e2))
    ou, ov = -ar.dot(u, a), -ar.dot(v, a)
    w, ow = tuple(-x-y for x, y in zip(u, v)), F(1)-ou-ov
    need(all(x+y+z == 0 for x, y, z in zip(u, v, w)) and ou+ov+ow == 1,
         "affine_partition_identity")
    intervals = [affine.affine_interval(coef, off, point)
                 for coef, off in ((u, ou), (v, ov), (w, ow))]
    out["barycentric_intervals"] = [[ar.pair(x) for x in interval] for interval in intervals]
    if all(lo > 0 for lo, hi in intervals):
        out.update(status="CPU_STRICT_PREVIOUS_CONTACT_ALL_DECLARED_DIRECTIONS_ONLY",
                   CPU_strict_interior_contact_for_all_directions=True)
    else:
        out["status"] = "STOP_PREVIOUS_TRIANGLE_NOT_STRICT_INTERIOR"
    return out


def retained_packets():
    for path, expected in ARITHMETIC_PINS.items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
             "fixed_pure_arithmetic:" + path)
    raw = (ROOT / PARENT).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PSHA, "fixed_candidate_receipt")
    r = json.loads(raw)
    dependency = r["dependency"]
    need(hashlib.sha256((ROOT / dependency["path"]).read_bytes()).hexdigest()
         == dependency["sha256"], "fixed_candidate_codec_dependency")
    for path, entry in r["code_sha256"].items():
        data = (ROOT / path).read_bytes()
        need(len(data) == entry["bytes"] and hashlib.sha256(data).hexdigest() == entry["sha256"],
             "fixed_candidate_source:" + path)
    cap = r["final_capture"]
    need(cap["rc"] == 0 and cap["before_deadline"] is True, "completed_candidate_capture")
    decoder = zlib.decompressobj()
    data = decoder.decompress(base64.b64decode(cap["stdout_zlib_base64"], validate=True), 1048577)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
         and len(data) <= 1048576 and len(data) == cap["stdout_bytes"]
         and hashlib.sha256(data).hexdigest() == cap["stdout_sha256"], "candidate_capture_identity")
    body = json.loads(data)
    need(body["status"] == "PASS", "candidate_capture_PASS")
    packets = [r["packet"] for r in body["records"] if "packet" in r]
    need(len(packets) == 12 and len({(p["slot"]["case"], p["slot"]["source_id"])
                                   for p in packets}) == 12, "SOURCE12_unique")
    return packets


def evaluate_packet(packet, *, model):
    """Caller-conditional CPU content only; use run for fixed captured slots."""
    need(type(model) is str and model == MODEL, "explicit_model")
    # Internal consistency is not external authentication.
    fixed = packing.audit_packet(packet, expected=packet, model=packing.MODEL)
    slot = fixed["slot"]
    result = condition(slot["saved_point_bounds"], slot["saved_direction_bounds"],
                       slot["saved_triangle_words"], model=model)
    result.update(slot=copy.deepcopy(slot), CPU_packet_binding_sha256=fixed["CPU_packet_binding_sha256"],
                  parent_receipt_sha256=None, scene_authenticated=False, SOURCE_authenticated=False,
                  scope="CALLER_CONDITIONAL_CPU_CONTENT_ONLY")
    return result


def run(case, source_id, *, model):
    need(type(model) is str and model == MODEL, "explicit_model")
    need(type(case) is str and type(source_id) is str, "literal_case_SOURCE")
    found = [p for p in retained_packets()
             if p["slot"]["case"] == case and p["slot"]["source_id"] == source_id]
    need(len(found) == 1, "unique_fixed_case_SOURCE")
    out = evaluate_packet(found[0], model=model)
    out["scope"] = "FIXED_CAPTURE_CPU_CONTENT_ONLY_NOT_NATIVE"
    out["parent_receipt_sha256"] = PSHA
    return out
