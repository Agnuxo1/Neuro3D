"""Scene-owned geometry/query hi-lo transport, without native launch or phase claims.

The v1 numeric ABI covers observed binary64 origins, directions and their
explicit endpoints, source fields, vertices, mode references and wavelength.
All material parameters remain exact binary64 metadata in the trusted manifest;
they are uniformly outside this diagnostic arithmetic profile.

No Blender imports, file reads, historical producer execution or GPU dispatch.
"""
import copy
from fractions import Fraction
import hashlib
import json
import math
import struct

from Blender.benchmarks.capacity_audit import oblique_exact_scalar_hilo32_CPU_v1 as codec

SCHEMA = "neuro3d-scene-hilo-transport-v1"
MODEL = "observed-scene-geometry-query-exact-hilo32-v1"
MAGIC = 0x4E33484C
VERSION = 1
HEADER_WORDS = 32
SCALAR_STRIDE = 8
SOURCE_STRIDE = 32
VERTEX_STRIDE = 8
TRIANGLE_STRIDE = 8
INITIAL_PREVIOUS = 0xFFFFFFFF
BOUNDS_PROPERTY = "neuro3d_direction_bounds"
MAX_OBJECTS = 128
MAX_SOURCES = 8
MAX_VERTICES = 4096
MAX_TRIANGLES = 8192
MAX_SCALARS = 20000
MAX_WIRE_WORDS = 262144
MAX_OUTPUT_RECORDS = 65536
INPUT_CLASSES = {"real_reopened_baseline", "controlled_numeric_scene", "cpu_synthetic_test"}
ROLE = {
    "origin": 1, "raw_direction": 2, "direction_bound": 3, "field": 4,
    "vertex": 5, "mode_origin": 8, "mode_direction": 9, "wavelength": 10,
}
# Roles 6/7 are reserved: transmittance and phase are manifest-only material data.
KIND = {"bs": 0, "mirror": 1, "det": 2, "escape": 3}
SCOPE = {
    "numeric_profile": "observed geometry/query and source fields; no material arithmetic",
    "materials": "original binary64 metadata only, never rounded into this numeric ABI",
    "CPU_exact_transport_verified": True,
    "native_transport_verified": False,
    "native_precision_certified": False,
    "native_original_transport_joins": 0,
    "phase_certified": False,
    "first_hit_certified": False,
    "physical_origin_error_bound": None,
    "phase_error_bound": None,
    "GPU_launch_allowed": False,
}


class TransportRejected(ValueError):
    """Fail-closed input, representation or trusted-manifest mismatch."""


def require(condition, message):
    if not condition:
        raise TransportRejected(message)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _json_copy(value):
    """Normalize containers only; preserve JSON numeric values and signed zero."""
    return json.loads(canonical_json(value))


def _sha(value, label):
    require(type(value) is str and len(value) == 64 and
            all(char in "0123456789abcdef" for char in value), label + ": lowercase SHA256 required")


def _name(value, label):
    require(type(value) is str and 0 < len(value) <= 256, label + ": bounded name required")
    return value


def _number(value, label, *, allow_negative_zero=False):
    require(type(value) in (int, float), label + ": observed binary64 number required")
    try:
        observed = float(value)
        raw = struct.pack("<d", observed)
    except (OverflowError, struct.error) as exc:
        raise TransportRejected(label + ": invalid binary64 value") from exc
    require(math.isfinite(observed), label + ": nonfinite observed value")
    words = list(struct.unpack("<II", raw))
    require(allow_negative_zero or not (observed == 0 and words[1] >> 31),
            label + ": negative zero outside numeric ABI")
    return observed, words, Fraction.from_float(observed)


def _vector(value, label):
    require(type(value) is list and len(value) == 3, label + ": three components required")
    return [_number(item, label + "[" + str(i) + "]")[0] for i, item in enumerate(value)]


def _strict_bounds_json(raw):
    require(type(raw) is str and len(raw.encode("utf-8")) <= 65536,
            "bounded persisted direction bounds JSON required")
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate direction bounds JSON key")
            result[key] = value
        return result
    def bad_constant(value):
        raise TransportRejected("nonfinite direction bounds JSON: " + value)
    try:
        return json.loads(raw, object_pairs_hook=object_pairs, parse_constant=bad_constant)
    except (TypeError, json.JSONDecodeError) as exc:
        raise TransportRejected("invalid persisted direction bounds JSON") from exc


def _provenance(value, bounds):
    require(type(value) is dict, "explicit provenance required")
    required = {"input_class", "blend_sha256", "blender_version", "scene_name", "view_layer_name"}
    optional = {"blend_path", "direction_bounds_property", "direction_bounds_json"}
    require(required <= set(value) <= required | optional, "closed provenance schema required")
    require(value["input_class"] in INPUT_CLASSES, "explicit supported input class required")
    _sha(value["blend_sha256"], "blend_sha256")
    for key in ("blender_version", "scene_name", "view_layer_name"):
        _name(value[key], key)
    if "blend_path" in value:
        require(type(value["blend_path"]) is str and 0 < len(value["blend_path"]) <= 4096,
                "bounded blend_path required")
    bound_keys = {"direction_bounds_property", "direction_bounds_json"}
    if bounds is None:
        require(not (bound_keys & set(value)), "bounds provenance without observed bounds")
        return None
    require(bound_keys <= set(value) and value["direction_bounds_property"] == BOUNDS_PROPERTY,
            "persisted namespaced bounds provenance required")
    parsed = _strict_bounds_json(value["direction_bounds_json"])
    require(canonical_json(parsed) == canonical_json(bounds),
            "persisted bounds JSON differs from supplied bounds")
    return {
        "property": BOUNDS_PROPERTY,
        "stored_json_sha256": hashlib.sha256(value["direction_bounds_json"].encode("utf-8")).hexdigest(),
        "parsed_sha256": digest(parsed),
        "scope": "observed explicit endpoints, not an authenticated physical uncertainty bound",
    }


def _layout(scalars, sources, vertices, triangles, objects, wavelength_index):
    source_offset = HEADER_WORDS + scalars * SCALAR_STRIDE
    vertex_offset = source_offset + sources * SOURCE_STRIDE
    triangle_offset = vertex_offset + vertices * VERTEX_STRIDE
    total = triangle_offset + triangles * TRIANGLE_STRIDE
    require(total <= MAX_WIRE_WORDS, "wire word limit exceeded")
    require(sources * vertices + sources + 2 * triangles <= MAX_OUTPUT_RECORDS,
            "diagnostic output record limit exceeded")
    return {
        "header_words": HEADER_WORDS, "total_words": total,
        "scalar_count": scalars, "scalar_offset": HEADER_WORDS, "scalar_stride": SCALAR_STRIDE,
        "source_count": sources, "source_offset": source_offset, "source_stride": SOURCE_STRIDE,
        "vertex_count": vertices, "vertex_offset": vertex_offset, "vertex_stride": VERTEX_STRIDE,
        "triangle_count": triangles, "triangle_offset": triangle_offset, "triangle_stride": TRIANGLE_STRIDE,
        "object_count": objects, "wavelength_scalar_index": wavelength_index,
        "endianness": "little", "word_type": "uint32",
    }


def _header(layout):
    return [
        MAGIC, VERSION, HEADER_WORDS, layout["total_words"],
        layout["scalar_count"], layout["scalar_offset"], SCALAR_STRIDE,
        layout["source_count"], layout["source_offset"], SOURCE_STRIDE,
        layout["vertex_count"], layout["vertex_offset"], VERTEX_STRIDE,
        layout["triangle_count"], layout["triangle_offset"], TRIANGLE_STRIDE,
        layout["object_count"], layout["wavelength_scalar_index"], 0,
    ] + [0] * 13


def build_packet(snapshot, *, provenance, direction_bounds=None):
    """Encode a complete observed snapshot; no precomputed intersections or hits.

    Provenance is supplied by the independently controlled Blender reader.
    This function checks consistency; a caller-created hash is not authentication.
    Initial scene-owned sources always use the explicitly versioned no-previous
    sentinel. Historical SOURCE continuation packets are not accepted here.
    """
    require(type(snapshot) is dict and type(provenance) is dict, "snapshot and provenance objects required")
    snap = _json_copy(snapshot)
    prov = _json_copy(provenance)
    embedded = snap.get(BOUNDS_PROPERTY)
    if embedded is not None:
        require(direction_bounds is None or canonical_json(direction_bounds) == canonical_json(embedded),
                "two conflicting direction bounds inputs")
        direction_bounds = embedded
    bounds = None if direction_bounds is None else _json_copy(direction_bounds)
    bounds_provenance = _provenance(prov, bounds)
    require(snap.get("schema") in ("exp005-readback-v1", "exp005-readback-v2"),
            "explicit exp005 readback schema required")
    require(snap.get("undeclared_meshes") == [], "complete declared mesh set required")
    objects = snap.get("objects")
    sources = snap.get("sources")
    require(type(objects) is dict and 1 <= len(objects) <= MAX_OBJECTS, "bounded nonempty object map required")
    require(type(sources) is list and 1 <= len(sources) <= MAX_SOURCES, "bounded nonempty source list required")
    object_order = sorted(_name(name, "object ID") for name in objects)
    if prov["input_class"] != "cpu_synthetic_test":
        require(snap.get("evaluated_optics_checked") is True and
                snap.get("evaluated_optical_ids") == object_order,
                "real scene requires complete evaluated optics readback")
    source_order = []
    for source in sources:
        require(type(source) is dict and set(source) == {"id", "position_BU", "direction", "field_reim"},
                "closed source schema required")
        source_order.append(_name(source["id"], "source ID"))
    require(len(set(source_order)) == len(source_order), "duplicate source ID")
    if bounds is not None:
        require(type(bounds) is dict and set(bounds) <= set(source_order), "unknown direction bounds source")
    scalars, scalar_words, source_records, vertex_records, triangle_records = [], [], [], [], []
    object_records, material_metadata = [], []

    def scalar(value, role, owner, element, component, endpoint, path):
        observed, original_words, exact = _number(value, path)
        packet = codec.encode_scalar([exact.numerator, exact.denominator])
        require(packet["status"] == "EXACT_PAIR_CPU_ONLY" and packet["residual_exact"] == [0, 1],
                path + ": " + packet["status"])
        require(len(scalars) < MAX_SCALARS, "scalar limit exceeded")
        index = len(scalars)
        record = [packet["hi_word"], packet["lo_word"], ROLE[role], owner,
                  element, component, endpoint, 0]
        scalar_words.extend(record)
        scalars.append({
            "index": index, "role": role, "owner": owner, "element": element,
            "component": component, "endpoint": endpoint, "path": path,
            "observed_binary64_words": original_words,
            "exact_input": [exact.numerator, exact.denominator],
            "hi_word": packet["hi_word"], "lo_word": packet["lo_word"],
            "residual_exact": packet["residual_exact"], "status": packet["status"],
        })
        return index

    for ordinal, source in enumerate(sources):
        sid = source["id"]
        base = "sources[" + str(ordinal) + "]"
        origin = _vector(source["position_BU"], base + ".position_BU")
        raw_direction = _vector(source["direction"], base + ".direction")
        require(any(raw_direction), base + ": nonzero direction required")
        field = source["field_reim"]
        require(type(field) is list and len(field) == 2, base + ": complex pair required")
        axes = bounds.get(sid) if bounds is not None and sid in bounds else [[v, v] for v in raw_direction]
        require(type(axes) is list and len(axes) == 3, sid + ": three direction intervals required")
        for axis, interval in enumerate(axes):
            require(type(interval) is list and len(interval) == 2, sid + ": endpoint pair required")
            lo = _number(interval[0], sid + ".lower")[2]
            hi = _number(interval[1], sid + ".upper")[2]
            raw = Fraction.from_float(raw_direction[axis])
            require(lo <= raw <= hi, sid + ": reversed or non-containing direction interval")
        p = [scalar(value, "origin", ordinal, 0, axis, 0, base + ".position_BU[" + str(axis) + "]")
             for axis, value in enumerate(origin)]
        d = [scalar(value, "raw_direction", ordinal, 0, axis, 0, base + ".direction[" + str(axis) + "]")
             for axis, value in enumerate(raw_direction)]
        lower = [scalar(axes[axis][0], "direction_bound", ordinal, 0, axis, 0,
                        base + ".direction_bounds[" + str(axis) + "].lower") for axis in range(3)]
        upper = [scalar(axes[axis][1], "direction_bound", ordinal, 0, axis, 1,
                        base + ".direction_bounds[" + str(axis) + "].upper") for axis in range(3)]
        amplitudes = [scalar(value, "field", ordinal, 0, component, 0,
                             base + ".field_reim[" + str(component) + "]") for component, value in enumerate(field)]
        source_records.append([ordinal, INITIAL_PREVIOUS] + p + d + lower + upper + amplitudes + [0] * 16)

    for ordinal, name in enumerate(object_order):
        obj = objects[name]
        require(type(obj) is dict and obj.get("kind") in KIND, name + ": optical kind required")
        allowed = {"kind", "vertices_world_BU", "faces", "power_transmittance", "phase_rad",
                   "mode_origin_BU", "mode_direction"}
        require(set(obj) <= allowed and {"kind", "vertices_world_BU", "faces"} <= set(obj),
                name + ": unsupported object fields")
        kind = obj["kind"]
        vertices, faces = obj["vertices_world_BU"], obj["faces"]
        require(type(vertices) is list and vertices and type(faces) is list and faces,
                name + ": nonempty vertices and faces required")
        require(len(vertex_records) + len(vertices) <= MAX_VERTICES, "vertex limit exceeded")
        first_vertex, first_triangle = len(vertex_records), len(triangle_records)
        for local, point in enumerate(vertices):
            values = _vector(point, name + ".vertices[" + str(local) + "]")
            indices = [scalar(value, "vertex", ordinal, local, axis, 0,
                              "objects." + name + ".vertices_world_BU[" + str(local) + "][" + str(axis) + "]")
                       for axis, value in enumerate(values)]
            vertex_records.append([len(vertex_records), ordinal, local] + indices + [0, 0])
        for face_index, face in enumerate(faces):
            require(type(face) is list and len(face) == 3 and len(set(face)) == 3 and
                    all(type(index) is int and 0 <= index < len(vertices) for index in face),
                    name + ": actual triangulated faces required; no silent triangulation")
            require(len(triangle_records) < MAX_TRIANGLES, "triangle limit exceeded")
            triangle_records.append([len(triangle_records), ordinal, face_index] +
                                    [first_vertex + index for index in face] + [KIND[kind], 0])
        metadata = {"object_ordinal": ordinal, "object_id": name, "kind": kind, "parameters": {}}
        if kind == "mirror":
            require("phase_rad" in obj, name + ": explicit mirror phase required")
        if kind == "bs" and snap["schema"] == "exp005-readback-v2":
            require("power_transmittance" in obj, name + ": explicit v2 splitter transmittance required")
        if kind == "bs" and snap["schema"] == "exp005-readback-v1":
            require("power_transmittance" not in obj, name + ": variable splitter requires v2")
            metadata["v1_transmittance_definition"] = "ideal one-half, defined by exp005-readback-v1"
        for key in ("phase_rad", "power_transmittance"):
            if key in obj:
                value, words64, _ = _number(obj[key], name + "." + key, allow_negative_zero=True)
                if key == "power_transmittance":
                    require(0 <= value <= 1, name + ": transmittance outside [0,1]")
                metadata["parameters"][key] = {"binary64_words": words64, "numeric_ABI": False}
        material_metadata.append(metadata)
        mode_indices = {}
        if kind in ("det", "escape"):
            for key, role in (("mode_origin_BU", "mode_origin"), ("mode_direction", "mode_direction")):
                require(key in obj, name + ": terminal " + key + " required")
                values = _vector(obj[key], name + "." + key)
                if key == "mode_direction":
                    require(any(values), name + ": nonzero terminal direction required")
                mode_indices[key] = [scalar(value, role, ordinal, 0, axis, 0,
                                            "objects." + name + "." + key + "[" + str(axis) + "]")
                                     for axis, value in enumerate(values)]
        object_records.append({
            "ordinal": ordinal, "id": name, "kind": kind, "kind_code": KIND[kind],
            "first_vertex": first_vertex, "vertex_count": len(vertices),
            "first_triangle": first_triangle, "triangle_count": len(faces),
            "mode_scalar_indices": mode_indices,
        })

    wavelength = _number(snap.get("lambda_BU"), "lambda_BU")[0]
    require(wavelength > 0, "positive observed wavelength required")
    wavelength_index = scalar(wavelength, "wavelength", INITIAL_PREVIOUS, 0, 0, 0, "lambda_BU")
    layout = _layout(len(scalars), len(source_records), len(vertex_records),
                     len(triangle_records), len(object_records), wavelength_index)
    words = _header(layout) + scalar_words
    for table in (source_records, vertex_records, triangle_records):
        for record in table:
            words.extend(record)
    require(len(words) == layout["total_words"] and
            all(type(word) is int and 0 <= word <= 0xFFFFFFFF for word in words),
            "internal typed ABI mismatch")
    wire = struct.pack("<" + str(len(words)) + "I", *words)
    manifest = {
        "schema": SCHEMA, "model": MODEL, "codec_schema": codec.SCHEMA,
        "abi": layout, "snapshot": snap, "snapshot_sha256": digest(snap),
        "provenance": prov, "direction_bounds": bounds,
        "direction_bounds_provenance": bounds_provenance,
        "source_order": source_order, "object_order": object_order,
        "source_records": source_records, "vertex_records": vertex_records,
        "triangle_records": triangle_records, "objects": object_records,
        "scalars": scalars, "material_binary64_metadata": material_metadata,
        "wire_bytes": len(wire), "wire_sha256": hashlib.sha256(wire).hexdigest(),
        "scope": copy.deepcopy(SCOPE),
    }
    return {"schema": SCHEMA, "manifest": manifest, "wire_hex": wire.hex()}


def admit_for_upload(packet, *, trusted_manifest):
    """Return validated bytes, not launch permission or scene authentication.

    trusted_manifest must come from the caller's fixed, independently controlled
    input manifest. Passing the packet's own mutable manifest only checks
    consistency; it cannot establish provenance.
    """
    require(type(packet) is dict and set(packet) == {"schema", "manifest", "wire_hex"} and
            packet["schema"] == SCHEMA, "closed packet schema required")
    require(type(trusted_manifest) is dict and trusted_manifest.get("schema") == SCHEMA,
            "fixed trusted manifest required")
    require(type(packet["wire_hex"]) is str and
            len(packet["wire_hex"]) <= MAX_WIRE_WORDS * 8 and
            len(packet["wire_hex"]) % 8 == 0, "bounded word-aligned wire hex required")
    try:
        wire = bytes.fromhex(packet["wire_hex"])
    except ValueError as exc:
        raise TransportRejected("malformed wire hex") from exc
    require(len(wire) >= HEADER_WORDS * 4 and len(wire) % 4 == 0, "complete ABI header required")
    words = struct.unpack("<" + str(len(wire) // 4) + "I", wire)
    require(words[:3] == (MAGIC, VERSION, HEADER_WORDS), "ABI magic/version/endianness mismatch")
    require(words[3] == len(words), "ABI total word count mismatch")
    require(words[6] == SCALAR_STRIDE and words[9] == SOURCE_STRIDE and
            words[12] == VERTEX_STRIDE and words[15] == TRIANGLE_STRIDE,
            "ABI record stride mismatch")
    require(not any(words[18:32]), "ABI reserved header words must be zero")
    for key in ("snapshot", "provenance", "direction_bounds"):
        require(key in trusted_manifest, "incomplete fixed manifest")
    expected = build_packet(trusted_manifest["snapshot"],
                            provenance=trusted_manifest["provenance"],
                            direction_bounds=trusted_manifest["direction_bounds"])
    require(canonical_json(expected["manifest"]) == canonical_json(trusted_manifest),
            "trusted manifest is inconsistent with its retained inputs")
    require(canonical_json(packet["manifest"]) == canonical_json(trusted_manifest),
            "different fixed manifest or SOURCE/geometry identity")
    require(wire.hex() == expected["wire_hex"], "wire differs from fixed observed scene packet")
    return wire


def audit_packet(packet, *, trusted_manifest):
    """Report CPU consistency only, with native and physical claims kept false."""
    wire = admit_for_upload(packet, trusted_manifest=trusted_manifest)
    return {
        "status": "PASS", "scope": "CPU observed-scene transport consistency only",
        "wire_bytes": len(wire), "wire_sha256": hashlib.sha256(wire).hexdigest(),
        "numeric_scalar_count": trusted_manifest["abi"]["scalar_count"],
        "CPU_exact_transport_verified": True, "native_transport_verified": False,
        "native_precision_certified": False, "phase_certified": False,
        "GPU_launch_allowed": False,
    }
