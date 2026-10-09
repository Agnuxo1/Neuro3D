"""Opt-in CPU-only candidate packing; NOT a native ABI or launch permission.

Layout: point 6 uint32 + direction endpoints 12 uint32 + previous primitive
1 uint32 = 76 little-endian bytes. SOURCE identity stays in the envelope.
"""
import copy
import hashlib
import json
import struct
from Blender.benchmarks.capacity_audit import oblique_exact_scalar_hilo32_CPU_v1 as codec

MODEL = "original-SOURCE-query-packet-CPU-candidate-v1"
IDENTITY = ("case", "source_id", "scene_sha256", "query_sha256", "input_sha256",
            "previous_primitive_id", "saved_point_bounds", "saved_direction_bounds",
            "saved_triangle_words", "source_record_sha256")
FALSE = ("GPU_launch_allowed", "launch_exclusion_allowed", "native_precision_certified",
         "phase_certified", "binding_authenticated", "native_ABI_certified")
KEYS = {"model", "slot", "point_binding_sha256", "direction_binding_sha256",
        "query_words", "wire_hex", "wire_sha256", "CPU_packet_binding_sha256",
        "phase_error_bound", "native_origin_box_bound", "full_costs", *FALSE}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def hashword(value):
    require(type(value) is str and len(value) == 64 and
            all(c in "0123456789abcdef" for c in value), "lowercase SHA256 required")


def words(value, count):
    require(type(value) is list and len(value) == count, "fixed word count required")
    for word in value:
        require(type(word) is int and 0 <= word <= 0xffffffff, "uint32 required")


def decoded(words_in, axes, endpoints):
    return [[codec.pair(codec.decode32(words_in[2*(a*endpoints+e)]) +
                        codec.decode32(words_in[2*(a*endpoints+e)+1]))
             for e in range(endpoints)] for a in range(axes)]


def binding(packet):
    return digest({k: packet[k] for k in ("model", "slot", "point_binding_sha256",
                                          "direction_binding_sha256", "wire_hex")})


def validate_slot_wire(slot, query):
    """Internal typed consistency, independent of a caller-supplied expected value."""
    require(type(slot) is dict and set(slot) == set(IDENTITY), "closed slot schema required")
    words(query, 19)
    require(type(slot["case"]) is str and 0 < len(slot["case"]) <= 128, "case label required")
    require(type(slot["source_id"]) is str and slot["source_id"] in ("S0", "S1"), "SOURCE label required")
    for key in ("scene_sha256", "query_sha256", "input_sha256", "source_record_sha256"):
        hashword(slot[key])
    previous = slot["previous_primitive_id"]
    require(type(previous) is int and 0 <= previous <= 0xffffffff and
            previous == query[18], "previous primitive does not match wire")
    for key in ("saved_point_bounds", "saved_direction_bounds"):
        box = slot[key]
        require(type(box) is list and len(box) == 3, "three-axis box required")
        for endpoints in box:
            require(type(endpoints) is list and len(endpoints) == 2, "two endpoints required")
            lo, hi = map(codec.rational, endpoints)  # Reject bools/noncanonical fractions.
            require(lo <= hi, "reversed saved interval")
    points = decoded(query[:6], 3, 1)
    require([[v[0], v[0]] for v in points] == slot["saved_point_bounds"], "point/slot contradiction")
    require(decoded(query[6:18], 3, 2) == slot["saved_direction_bounds"], "direction/slot contradiction")
    triangles = slot["saved_triangle_words"]
    require(type(triangles) is list and len(triangles) == 3, "three triangle vertices required")
    for vertex in triangles:
        words(vertex, 3)
        require(all(((w >> 23) & 255) != 255 for w in vertex), "finite triangle metadata required")


def make_packet(point, direction, *, model):
    require(type(model) is str and model == MODEL, "explicit CPU candidate model required")
    require(type(point) is dict and type(direction) is dict, "two retained rows required")
    try:
        require(all(point[k] == direction[k] for k in IDENTITY), "point/direction slot mismatch")
        slot = copy.deepcopy({k: point[k] for k in IDENTITY})
        require(type(slot["case"]) is str and 0 < len(slot["case"]) <= 128, "case label required")
        require(slot["source_id"] in ("S0", "S1"), "SOURCE label required")
        for key in ("scene_sha256", "query_sha256", "input_sha256", "source_record_sha256"):
            hashword(slot[key])
        pb, db = point["CPU_slot_binding_sha256"], direction["CPU_direction_slot_binding_sha256"]
        hashword(pb); hashword(db)
        require(direction["parent_point_CPU_slot_binding_sha256"] == pb, "parent point binding mismatch")
        for row in (point, direction):
            for key in ("GPU_launch_allowed", "launch_exclusion_allowed", "phase_certified",
                        "binding_authenticated"):
                require(row[key] is False, "CPU rows cannot grant permission")
        pw, dw = point["point_words"], direction["direction_endpoint_words"]
        words(pw, 6); words(dw, 12)
        require(struct.pack("<6I", *pw).hex() == point["point_wire_hex"], "point wire mismatch")
        require(struct.pack("<12I", *dw).hex() == direction["direction_endpoint_wire_hex"], "direction wire mismatch")
        actual_p = decoded(pw, 3, 1)
        require([[v[0], v[0]] for v in actual_p] == slot["saved_point_bounds"], "point bounds mismatch")
        actual_d = decoded(dw, 3, 2)
        require(actual_d == slot["saved_direction_bounds"], "direction endpoints mismatch")
        for lo, hi in actual_d:
            require(codec.rational(lo) <= codec.rational(hi), "reversed direction interval")
        previous = slot["previous_primitive_id"]
        require(type(previous) is int and 0 <= previous <= 0xffffffff, "previous primitive uint32 required")
    except (KeyError, TypeError, struct.error) as exc:
        raise ValueError("missing or malformed CPU row") from exc
    query = list(pw) + list(dw) + [previous]
    validate_slot_wire(slot, query)
    wire = struct.pack("<19I", *query)
    packet = dict(model=MODEL, slot=slot, point_binding_sha256=pb,
                  direction_binding_sha256=db, query_words=query, wire_hex=wire.hex(),
                  wire_sha256=hashlib.sha256(wire).hexdigest(), phase_error_bound=None,
                  native_origin_box_bound=None, full_costs="UNKNOWN_NOT_ZERO",
                  **{key: False for key in FALSE})
    packet["CPU_packet_binding_sha256"] = binding(packet)
    return packet


def audit_packet(packet, *, expected, model):
    """Compare to caller's fixed CPU fixture; expected is NOT trusted native authority."""
    require(type(model) is str and model == MODEL, "explicit CPU candidate model required")
    require(type(packet) is dict and type(expected) is dict and
            set(packet) == set(expected) == KEYS, "closed CPU packet schema required")
    require(packet["model"] == MODEL, "packet model mismatch")
    for key in FALSE:
        require(packet[key] is False and expected[key] is False, "CPU packet cannot grant permission")
    require(packet["phase_error_bound"] is None and packet["native_origin_box_bound"] is None,
            "no native bound allowed in this candidate")
    require(packet["full_costs"] == "UNKNOWN_NOT_ZERO", "costs remain unknown")
    words(packet["query_words"], 19)
    validate_slot_wire(packet["slot"], packet["query_words"])
    hashword(packet["point_binding_sha256"])
    hashword(packet["direction_binding_sha256"])
    wire = struct.pack("<19I", *packet["query_words"])
    require(wire.hex() == packet["wire_hex"] and
            hashlib.sha256(wire).hexdigest() == packet["wire_sha256"], "wire integrity mismatch")
    require(binding(packet) == packet["CPU_packet_binding_sha256"], "CPU content binding mismatch")
    require(packet == expected, "different fixed CPU SOURCE slot")
    return copy.deepcopy(packet)
