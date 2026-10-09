"""Exact fail-closed first-hit selector for the scene hi/lo ABI (CPU reference).

All numeric geometry comes from the v1 hi/lo packet. Each hi/lo binary32 pair is
decoded exactly as an integer scaled by 2**149. Moller-Trumbore determinants and
numerators therefore use integers only: no epsilon, origin bias or float division.
This module is a CPU reference and packet/fixture builder, not GPU evidence.
"""
from __future__ import annotations

import hashlib
import json
import struct

from Blender.benchmarks.capacity_audit import scene_hilo_transport_v1 as transport

MODEL = "robust-first-hit-exact-scaled512-v1"
SCALE_BITS = 149
I512_MIN = -(1 << 511)
I512_MAX = (1 << 511) - 1

STATUS = {
    "SELECT": 1,
    "MISS": 2,
    "TRUE_TIE": 3,
    "BOUNDARY": 4,
    "CONTACT": 5,
    "COPLANAR": 6,
    "INVALID_GEOMETRY": 7,
    "NUMERIC_OVERFLOW": 8,
}
DEPARTURE = {None: 0, "mirror": 1, "t": 2, "r": 3}


class ExactRejected(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ExactRejected(message)


def i512(value, label="signed512"):
    require(type(value) is int and I512_MIN <= value <= I512_MAX, label + " overflow/type")
    return value


def decode32_scaled149(word):
    require(type(word) is int and 0 <= word <= 0xFFFFFFFF, "uint32 scalar word required")
    sign = -1 if word >> 31 else 1
    exponent = (word >> 23) & 0xFF
    mantissa = word & 0x7FFFFF
    require(exponent != 0xFF and not (exponent == 0 and mantissa), "nonfinite/subnormal binary32")
    if exponent == 0:
        return 0
    return i512(sign * ((mantissa | 0x800000) << (exponent - 1)), "decoded scalar")


def decode_pair(pair):
    require(type(pair) in (tuple, list) and len(pair) == 2, "hi/lo pair required")
    return i512(decode32_scaled149(pair[0]) + decode32_scaled149(pair[1]), "hi/lo sum")


def unpack_words(wire):
    require(type(wire) is bytes and len(wire) % 4 == 0, "word-aligned wire required")
    return list(struct.unpack("<%dI" % (len(wire) // 4), wire))


def packet_bytes(packet):
    require(type(packet) is dict and packet.get("schema") == transport.SCHEMA, "scene hi/lo packet required")
    raw = bytes.fromhex(packet["wire_hex"])
    require(hashlib.sha256(raw).hexdigest() == packet["manifest"]["wire_sha256"], "wire hash mismatch")
    return raw


def scalar(words, layout, index):
    require(0 <= index < layout["scalar_count"], "scalar index")
    base = layout["scalar_offset"] + index * layout["scalar_stride"]
    return decode_pair(words[base:base + 2])


def source(words, layout, index):
    require(0 <= index < layout["source_count"], "source index")
    base = layout["source_offset"] + index * layout["source_stride"]
    require(words[base] == index and words[base + 1] == transport.INITIAL_PREVIOUS, "source record identity")
    return (
        tuple(scalar(words, layout, words[base + 2 + axis]) for axis in range(3)),
        tuple(scalar(words, layout, words[base + 5 + axis]) for axis in range(3)),
    )


def vertex(words, layout, index):
    require(0 <= index < layout["vertex_count"], "vertex index")
    base = layout["vertex_offset"] + index * layout["vertex_stride"]
    require(words[base] == index, "vertex record identity")
    return tuple(scalar(words, layout, words[base + 3 + axis]) for axis in range(3))


def triangle_record(words, layout, index):
    require(0 <= index < layout["triangle_count"], "triangle index")
    base = layout["triangle_offset"] + index * layout["triangle_stride"]
    require(words[base] == index, "triangle record identity")
    return {
        "primitive_id": words[base],
        "object_ordinal": words[base + 1],
        "face_index": words[base + 2],
        "vertices": tuple(words[base + 3:base + 6]),
        "kind": words[base + 6],
    }


def sub3(a, b):
    return tuple(i512(x - y, "vector subtraction") for x, y in zip(a, b))


def cross3(a, b):
    return (
        i512(i512(a[1] * b[2], "cross product") - i512(a[2] * b[1], "cross product"), "cross subtract"),
        i512(i512(a[2] * b[0], "cross product") - i512(a[0] * b[2], "cross product"), "cross subtract"),
        i512(i512(a[0] * b[1], "cross product") - i512(a[1] * b[0], "cross product"), "cross subtract"),
    )


def dot3(a, b):
    p = [i512(x * y, "dot product") for x, y in zip(a, b)]
    return i512(i512(p[0] + p[1], "dot add") + p[2], "dot add")


def iszero3(v):
    return v[0] == 0 and v[1] == 0 and v[2] == 0


def candidate(words, layout, origin, direction, tri_index):
    record = triangle_record(words, layout, tri_index)
    a, b, c = (vertex(words, layout, idx) for idx in record["vertices"])
    e1, e2 = sub3(b, a), sub3(c, a)
    normal = cross3(e1, e2)
    if iszero3(normal):
        return dict(record, class_="degenerate")
    p = cross3(direction, e2)
    det = dot3(e1, p)
    rel = sub3(origin, a)
    if det == 0:
        plane = dot3(rel, normal)
        return dict(record, class_="coplanar" if plane == 0 else "parallel")
    q = cross3(rel, e1)
    u = dot3(rel, p)
    v = dot3(direction, q)
    t = dot3(e2, q)
    if det < 0:
        det, u, v, t = -det, -u, -v, -t
    det, u, v, t = (i512(x, "sign normalization") for x in (det, u, v, t))
    uv = i512(u + v, "u+v")
    if t < 0 or u < 0 or v < 0 or uv > det:
        return dict(record, class_="outside")
    common = dict(record, numerator=t, denominator=det, u_num=u, v_num=v, normal=normal)
    if t == 0:
        return dict(common, class_="contact")
    if u == 0 or v == 0 or uv == det:
        return dict(common, class_="boundary")
    return dict(common, class_="interior")


def compare_fraction(a_num, a_den, b_num, b_den):
    left, right = a_num * b_den, b_num * a_den
    return -1 if left < right else (1 if left > right else 0)


def select(packet, source_index, *, previous_primitive=None, departure_event=None):
    wire = packet_bytes(packet)
    words = unpack_words(wire)
    layout = packet["manifest"]["abi"]
    require(words[:3] == [transport.MAGIC, transport.VERSION, transport.HEADER_WORDS], "ABI header")
    require(words[3] == len(words), "ABI length")
    require(layout["triangle_count"] <= 64, "point-5 pilot supports <=64 primitives")
    origin, direction = source(words, layout, source_index)
    require(not iszero3(direction), "nonzero direction")
    if previous_primitive is None:
        require(departure_event is None, "departure event without previous primitive")
    else:
        require(type(previous_primitive) is int and 0 <= previous_primitive < layout["triangle_count"],
                "previous primitive")
        require(departure_event in ("mirror", "t", "r"), "valid departure event")
    positives, contact_ids = [], []
    excluded_previous = 0
    coplanar, degenerate = [], []
    for tri in range(layout["triangle_count"]):
        row = candidate(words, layout, origin, direction, tri)
        kind = row["class_"]
        if kind == "degenerate":
            degenerate.append(tri)
        elif kind == "coplanar":
            coplanar.append(tri)
        elif kind == "contact":
            if previous_primitive == tri and departure_event in ("mirror", "t", "r"):
                excluded_previous += 1
            else:
                contact_ids.append(tri)
        elif kind in ("boundary", "interior"):
            positives.append(row)
    base = {
        "model": MODEL, "source_index": source_index, "previous_primitive": previous_primitive,
        "departure_event": departure_event, "excluded_previous_contacts": excluded_previous,
        "contact_primitive_ids": contact_ids, "coplanar_primitive_ids": coplanar,
        "degenerate_primitive_ids": degenerate,
    }
    if degenerate:
        return dict(base, status="INVALID_GEOMETRY", status_code=STATUS["INVALID_GEOMETRY"],
                    selected_primitive=None, selected_object=None, tie_primitive_ids=[], t=None)
    if coplanar:
        return dict(base, status="COPLANAR", status_code=STATUS["COPLANAR"],
                    selected_primitive=None, selected_object=None, tie_primitive_ids=[], t=None)
    if contact_ids:
        return dict(base, status="CONTACT", status_code=STATUS["CONTACT"],
                    selected_primitive=None, selected_object=None, tie_primitive_ids=sorted(contact_ids), t=[0, 1])
    if not positives:
        return dict(base, status="MISS", status_code=STATUS["MISS"],
                    selected_primitive=None, selected_object=None, tie_primitive_ids=[], t=None)
    best = positives[0]
    ties = [best]
    for row in positives[1:]:
        relation = compare_fraction(row["numerator"], row["denominator"],
                                    best["numerator"], best["denominator"])
        if relation < 0:
            best, ties = row, [row]
        elif relation == 0:
            ties.append(row)
    if len(ties) > 1:
        winner = min(ties, key=lambda row: row["primitive_id"])
        def parallel(a, b):
            return (a[0]*b[1] == a[1]*b[0] and
                    a[0]*b[2] == a[2]*b[0] and
                    a[1]*b[2] == a[2]*b[1])
        equivalent = all(row["object_ordinal"] == winner["object_ordinal"] and
                         parallel(row["normal"], winner["normal"]) for row in ties)
        if not equivalent:
            return dict(base, status="TRUE_TIE", status_code=STATUS["TRUE_TIE"],
                        selected_primitive=winner["primitive_id"], selected_object=winner["object_ordinal"],
                        tie_primitive_ids=sorted(row["primitive_id"] for row in ties),
                        equivalent_surface_tie=False,
                        t=[winner["numerator"], winner["denominator"]])
        return dict(base, status="SELECT", status_code=STATUS["SELECT"],
                    selected_primitive=winner["primitive_id"], selected_object=winner["object_ordinal"],
                    tie_primitive_ids=sorted(row["primitive_id"] for row in ties),
                    equivalent_surface_tie=True,
                    t=[winner["numerator"], winner["denominator"]])
    if best["class_"] == "boundary":
        return dict(base, status="BOUNDARY", status_code=STATUS["BOUNDARY"],
                    selected_primitive=best["primitive_id"], selected_object=best["object_ordinal"],
                    tie_primitive_ids=[best["primitive_id"]], equivalent_surface_tie=False,
                    t=[best["numerator"], best["denominator"]])
    return dict(base, status="SELECT", status_code=STATUS["SELECT"],
                selected_primitive=best["primitive_id"], selected_object=best["object_ordinal"],
                tie_primitive_ids=[best["primitive_id"]], equivalent_surface_tie=False,
                t=[best["numerator"], best["denominator"]])


def object_primitive(packet, object_id):
    manifest = packet["manifest"]
    rows = [row for row in manifest["objects"] if row["id"] == object_id]
    require(len(rows) == 1 and rows[0]["triangle_count"] == 1, "single-triangle object required")
    return rows[0]["first_triangle"]


def make_snapshot(objects, sources, *, wavelength=0.125):
    return {
        "schema": "exp005-readback-v2", "lambda_BU": float(wavelength),
        "objects": objects, "sources": sources, "undeclared_meshes": [],
    }


def source_row(position, direction, sid="S0"):
    return {"id": sid, "position_BU": list(position), "direction": list(direction),
            "field_reim": [1.0, 0.0]}


def mirror(vertices, faces=((0, 1, 2),)):
    return {"kind": "mirror", "phase_rad": 0.0,
            "vertices_world_BU": [list(v) for v in vertices],
            "faces": [list(face) for face in faces]}


def synthetic_packet(snapshot, *, label):
    canonical = transport.canonical_json(snapshot)
    provenance = {
        "input_class": "cpu_synthetic_test",
        "blend_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "blender_version": "synthetic-no-blender",
        "scene_name": "point5-" + label,
        "view_layer_name": "synthetic",
    }
    return transport.build_packet(snapshot, provenance=provenance)
