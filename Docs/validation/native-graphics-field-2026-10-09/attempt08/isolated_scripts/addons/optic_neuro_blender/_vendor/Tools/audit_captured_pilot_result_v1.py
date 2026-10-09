"""Independent categorical and exact local-ledger audit; no producer imports.

Checks branching coverage and represented local path arithmetic. Does not
independently solve all nearest-hit queries or certify floating-point fields.
"""
from fractions import Fraction as F
import math


def need(condition, message):
    if not condition:
        raise ValueError(message)


def decode(value):
    if isinstance(value, dict):
        if set(value) == {"numerator", "denominator"}:
            need(type(value["numerator"]) is int and type(value["denominator"]) is int and value["denominator"] > 0,
                 "invalid rational wire")
            return F(value["numerator"], value["denominator"])
        return {key: decode(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decode(item) for item in value]
    return value


def vec(value):
    need(isinstance(value, (list, tuple)) and len(value) == 3, "three exact coordinates required")
    need(all(isinstance(v, (int, F)) and not isinstance(v, bool) for v in value), "exact rational coordinates required")
    return tuple(F(v) for v in value)


def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def dot(a, b): return sum((x * y for x, y in zip(a, b)), F(0))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def check_triangle(point, vertices):
    a, b, c = map(vec, vertices)
    ab, ac, ap = sub(b, a), sub(c, a), sub(point, a)
    normal = cross(ab, ac)
    need(dot(normal, normal) > 0 and dot(normal, ap) == 0, "hit not on nondegenerate triangle plane")
    aa, cc, av = dot(ab, ab), dot(ac, ac), dot(ab, ac)
    denom = aa * cc - av * av
    u = (cc * dot(ap, ab) - av * dot(ap, ac)) / denom
    v = (aa * dot(ap, ac) - av * dot(ap, ab)) / denom
    need(u >= 0 and v >= 0 and u + v <= 1, "hit outside closed triangle")
    return normal


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def audit_result(scene_wire, result_wire):
    scene, result = decode(scene_wire), decode(result_wire)
    need(result.get("schema") == "neuro3d-exact-multipath-v1" and result.get("backend") == "CPU_FRACTION",
         "unexpected worker schema/backend")
    need(result.get("field_certified") is False, "pilot must not assert a field certificate")
    status = result.get("status")
    need(status in ("COMPLETE", "INCOMPLETE"), "invalid traversal status")
    need(isinstance(result.get("paths"), list) and isinstance(result.get("unresolved"), list), "path ledgers required")
    sources = {s["id"]: s for s in scene["sources"]}
    need(len(sources) == len(scene["sources"]), "unique input sources required")
    objects = scene["objects"]
    ports = {name for name, obj in objects.items() if obj["kind"] in ("det", "escape")}
    need(isinstance(result.get("ports"), list) and len(result["ports"]) == len(ports) and set(result["ports"]) == ports,
         "terminal IDs mismatch")
    need(result.get("wavelength") == scene["lambda_BU"], "wavelength mismatch")
    need(type(result.get("rays")) is int and result["rays"] >= 0, "valid cast count required")
    if status == "INCOMPLETE":
        need(result["unresolved"] and result.get("fields") is None and result.get("powers") is None
             and result.get("output_power") is None, "incomplete result must preserve reasons and null outputs")
        need(all(isinstance(row, dict) and isinstance(row.get("status"), str) and row["status"]
                 for row in result["unresolved"]), "explicit unresolved reasons required")
        return {"status": "VALID_ALGORITHMIC_INCOMPLETE", "primary_metric": 0,
                "unresolved_reasons": sorted({r["status"] for r in result["unresolved"]}),
                "field_certified": False, "exact_local_ledger_verified": False,
                "nearest_hits_independently_verified": False}
    need(not result["unresolved"], "COMPLETE with unresolved branches")
    fields, powers = result.get("fields"), result.get("powers")
    need(isinstance(fields, dict) and isinstance(powers, dict) and set(fields) == set(powers) == ports,
         "every declared terminal needs a finite field/power")
    for name in ports:
        field = fields[name]
        need(isinstance(field, dict) and set(field) == {"real", "imag"} and all(finite(x) for x in field.values()),
             "finite complex terminal field required")
        need(finite(powers[name]) and powers[name] >= 0, "finite nonnegative terminal power required")
    need(finite(result.get("output_power")) and result["output_power"] >= 0, "finite total output power required")
    triangles = []
    for name, obj in objects.items():
        for face in obj["faces"]:
            triangles.append((name, [obj["vertices_world_BU"][i] for i in face]))
    observed, leaves, seen_sources = {}, set(), set()
    for path in result["paths"]:
        sid = path["source_id"]
        need(sid in sources and path["terminal"] in ports, "unknown path source/terminal")
        source = sources[sid]
        need(path["source_reim"] == source["field_reim"], "path source amplitude mismatch")
        need(source["field_reim"] != [0, 0], "zero input path must not be fabricated")
        origin, direction = vec(source["position_BU"]), vec(source["direction"])
        norm2 = dot(direction, direction)
        length, power, phase, turns = F(0), F(1), F(0), 0
        prefix = (sid,)
        need(isinstance(path.get("hits"), list) and path["hits"], "nonempty path hits required")
        for index, hit in enumerate(path["hits"]):
            name, primitive = hit["object_id"], hit["primitive_id"]
            need(name in objects and type(primitive) is int and 0 <= primitive < len(triangles), "invalid hit identity")
            need(triangles[primitive][0] == name, "primitive/object mismatch")
            parameter = hit["parameter"]
            need(isinstance(parameter, (int, F)) and not isinstance(parameter, bool) and parameter > 0, "positive exact hit required")
            point = vec(hit["point"])
            need(vec(hit["direction"]) == direction, "incoming direction mismatch")
            need(point == tuple(o + parameter * d for o, d in zip(origin, direction)), "ray point mismatch")
            normal = check_triangle(point, triangles[primitive][1])
            obj, event = objects[name], hit["event"]
            kind = obj["kind"]
            if kind == "mirror":
                expected = {"mirror"}
                turns = (turns + 2) % 4
                phase += obj["phase_rad"]
            elif kind == "bs":
                tau = obj["power_transmittance"]
                expected = ({"t"} if tau > 0 else set()) | ({"r"} if tau < 1 else set())
                need(event in expected, "invalid/nonzero splitter branch")
                coefficient = tau if event == "t" else 1 - tau
                need(hit.get("coefficient_power") == coefficient, "splitter coefficient mismatch")
                power *= coefficient
                turns = (turns + (event == "r")) % 4
            else:
                expected = {kind}
                need(index == len(path["hits"]) - 1 and path["terminal"] == name, "terminal must end path")
            need(event in expected, "event/optical role mismatch")
            signature = (name, primitive, parameter, point, direction)
            if prefix not in observed:
                observed[prefix] = [signature, expected, set()]
            node = observed[prefix]
            need(node[0] == signature and node[1] == expected, "inconsistent geometry at same path prefix")
            node[2].add(event)
            prefix += (event,)
            length += parameter
            if kind in ("mirror", "bs") and event != "t":
                scale = 2 * dot(direction, normal) / dot(normal, normal)
                direction = tuple(d - scale * n for d, n in zip(direction, normal))
            origin = point
        need(objects[path["terminal"]]["kind"] in ("det", "escape") and hit["event"] in ("det", "escape"),
             "last hit must be terminal")
        need(prefix not in leaves, "duplicate path leaf")
        leaves.add(prefix)
        seen_sources.add(sid)
        axis = vec(objects[path["terminal"]]["mode_direction"])
        need(cross(direction, axis) == (0, 0, 0) and dot(direction, axis) > 0, "terminal mode mismatch")
        reference = vec(objects[path["terminal"]]["mode_origin_BU"])
        numerator = norm2 * length + dot(direction, sub(reference, origin))
        need(all(isinstance(path[key], (int, F)) and not isinstance(path[key], bool) for key in
                 ("direction_norm_squared", "parameter_length", "phase_length_numerator", "power_factor", "mirror_phase"))
             and type(path["quarter_turns"]) is int and 0 <= path["quarter_turns"] <= 3,
             "exact optical ledger scalar types required")
        need(path["direction_norm_squared"] == norm2 and path["parameter_length"] == length and
             path["phase_length_numerator"] == numerator and path["power_factor"] == power and
             path["mirror_phase"] == phase and path["quarter_turns"] == turns, "exact path optical ledger mismatch")
    need(seen_sources == {sid for sid, s in sources.items() if s["field_reim"] != [0, 0]}, "nonzero input source missing")
    need(all(expected == actual for _, expected, actual in observed.values()), "nonzero branch missing from complete tree")
    return {"status": "VALID_COMPLETE_ESTIMATE", "primary_metric": 1, "paths": len(leaves),
            "sources": len(seen_sources), "terminal_count": len(ports), "exact_local_ledger_verified": True,
            "branch_prefix_coverage_verified": True, "nearest_hits_independently_verified": False,
            "field_certified": False, "physical_optics_certified": False}
