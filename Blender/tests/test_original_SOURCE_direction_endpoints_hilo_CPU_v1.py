"""New SOURCE-tagged transport of saved CPU direction-box endpoints; no native query."""
from pathlib import Path
from fractions import Fraction as F
import base64, copy, hashlib, json, struct, zlib
from Blender.benchmarks.capacity_audit import oblique_exact_scalar_hilo32_CPU_v1 as codec

ROOT = Path(__file__).resolve().parents[2]
PARENT = "coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-POINT-HILO-CPU-001-CODEX.json"
SHA = "e3d4a3e5f431b97fb83e121d4a9f06c9454e9f9849437721a7ed3e9b488fce07"
IDENTITY_FIELDS = (
    "case", "source_id", "scene_sha256", "query_sha256", "input_sha256",
    "previous_primitive_id", "saved_direction_bounds", "saved_point_bounds",
    "saved_triangle_words", "parent_point_CPU_slot_binding_sha256",
    "source_record_sha256", "CPU_declared_transport_error_budget",
    "direction_endpoint_words", "direction_endpoint_wire_hex",
)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def capture(c):
    dec = zlib.decompressobj()
    raw = dec.decompress(base64.b64decode(c["stdout_zlib_base64"], validate=True), 1048577)
    assert dec.eof and not dec.unused_data and not dec.unconsumed_tail
    assert len(raw) <= 1048576 and len(raw) == c["stdout_bytes"]
    assert c["rc"] == 0 and not c["timed_out"]
    assert hashlib.sha256(raw).hexdigest() == c["stdout_sha256"]
    return json.loads(raw)


def identity(row):
    # Fixed CPU-fixture content identity only; not a signature or scene authority.
    return {k: row[k] for k in IDENTITY_FIELDS}


def wire_bounds(words):
    assert len(words) == 12
    return [[codec.pair(codec.decode32(words[4*a+2*e]) +
                        codec.decode32(words[4*a+2*e+1])) for e in range(2)]
            for a in range(3)]


def set_wire(row, words):
    row["direction_endpoint_words"] = words
    row["direction_endpoint_wire_hex"] = struct.pack("<12I", *words).hex()


def run():
    raw = (ROOT/PARENT).read_bytes()
    assert len(raw) == 122600 and hashlib.sha256(raw).hexdigest() == SHA
    parent = json.loads(raw)
    pins = dict(parent["code_doc_sha256"])
    assert len(pins) == 452
    pins[PARENT] = SHA
    for path, expected in pins.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    data = capture(parent["test_run"])
    assert data["native_original_transport_joins"] == 0
    original = data["rows"]
    assert len(original) == 12
    rows = []
    encodes = audits = nonzero_lo = 0
    for saved in original:
        bounds = saved["saved_direction_bounds"]
        assert len(bounds) == 3
        widths = [codec.rational(hi)-codec.rational(lo) for lo, hi in bounds]
        assert widths[0] > 0 and widths[1:] == [F(0), F(0)]
        expected_width = F(3, 1 << (51 if saved["case"] == "direction_scaled" else 52))
        assert widths[0] == expected_width
        packets = []
        for axis, endpoints in enumerate(bounds):
            for endpoint, value in enumerate(endpoints):
                packet = codec.encode_scalar(value)
                encodes += 1
                assert codec.audit_packet(packet) == packet
                encodes += 1
                audits += 1
                assert packet["status"] == "EXACT_PAIR_CPU_ONLY"
                assert packet["residual_exact"] == [0, 1]
                assert packet["native_origin_box_bound"] is None
                assert packet["GPU_launch_allowed"] is False
                nonzero_lo += int(packet["lo_word"] != 0)
                packets.append(dict(axis=axis, endpoint=endpoint, packet=packet))
        words = [w for item in packets for w in (
            item["packet"]["hi_word"], item["packet"]["lo_word"])]
        assert wire_bounds(words) == bounds  # Both endpoints, never a midpoint.
        row = {k: copy.deepcopy(saved[k]) for k in (
            "case", "source_id", "scene_sha256", "query_sha256", "input_sha256",
            "previous_primitive_id", "saved_direction_bounds", "saved_point_bounds",
            "saved_triangle_words", "source_record_sha256")}
        row.update(
            parent_point_CPU_slot_binding_sha256=saved["CPU_slot_binding_sha256"],
            CPU_declared_transport_error_budget=[[[0, 1], [0, 1]] for _ in range(3)],
            scalar_endpoint_packets=packets,
            decoded_direction_bounds=wire_bounds(words),
            preserved_axis_widths=[codec.pair(x) for x in widths],
            native_direction_budget_authenticated=False,
            binding_authenticated=False, GPU_launch_allowed=False,
            launch_exclusion_allowed=False, native_precision_certified=False,
            phase_certified=False, phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO")
        set_wire(row, words)
        assert len(bytes.fromhex(row["direction_endpoint_wire_hex"])) == 48
        row["CPU_direction_slot_binding_sha256"] = digest(identity(row))
        rows.append(row)
    kinds = (
        "SOURCE_swap", "scene_substitution", "previous_id_substitution",
        "collapse_to_lower", "collapse_to_upper", "endpoint_order_swap",
        "literal_ideal_singleton_replacement", "budget_substitution",
        "triangle_substitution", "point_substitution",
    )
    negatives = []
    for row in rows:
        for kind in kinds:
            changed = copy.deepcopy(row)
            if kind == "SOURCE_swap":
                changed["source_id"] = "S1" if row["source_id"] == "S0" else "S0"
            elif kind == "scene_substitution":
                changed["scene_sha256"] = "0"*64
            elif kind == "previous_id_substitution":
                changed["previous_primitive_id"] += 1
            elif kind in ("collapse_to_lower", "collapse_to_upper", "endpoint_order_swap"):
                words = changed["direction_endpoint_words"][:]
                if kind == "collapse_to_lower":
                    words[2:4] = words[:2]
                elif kind == "collapse_to_upper":
                    words[:2] = words[2:4]
                else:
                    words[:4] = words[2:4] + words[:2]
                set_wire(changed, words)
                changed["saved_direction_bounds"] = wire_bounds(words)
                assert wire_bounds(words) == changed["saved_direction_bounds"]
            elif kind == "literal_ideal_singleton_replacement":
                # Explicit synthetic control, NOT a normalization calculation.
                set_wire(changed, [0xbf800000, 0, 0xbf800000, 0,
                                   0x3f800000, 0, 0x3f800000, 0, 0, 0, 0, 0])
                changed["saved_direction_bounds"] = wire_bounds(changed["direction_endpoint_words"])
            elif kind == "budget_substitution":
                changed["CPU_declared_transport_error_budget"][0][1] = [1, 1]
            elif kind == "triangle_substitution":
                changed["saved_triangle_words"][0][0] ^= 1
            elif kind == "point_substitution":
                changed["saved_point_bounds"][0] = [[0, 1], [0, 1]]
            changed["CPU_direction_slot_binding_sha256"] = digest(identity(changed))
            assert identity(changed) != identity(row)
            assert changed["CPU_direction_slot_binding_sha256"] != row["CPU_direction_slot_binding_sha256"]
            negatives.append(dict(
                case=row["case"], source_id=row["source_id"], kind=kind,
                candidate_identity=identity(changed),
                candidate_binding_sha256=changed["CPU_direction_slot_binding_sha256"],
                expected_binding_sha256=row["CPU_direction_slot_binding_sha256"],
                status="REJECT_DIFFERENT_FIXED_CPU_DIRECTION_SLOT"))
    groups = {}
    for row in rows:
        groups.setdefault(hashlib.sha256(bytes.fromhex(
            row["direction_endpoint_wire_hex"])).hexdigest(), []).append([row["case"], row["source_id"]])
    assert sorted(map(len, groups.values())) == [2, 10]
    assert len({r["CPU_direction_slot_binding_sha256"] for r in rows}) == 12
    for case in {r["case"] for r in rows}:
        pair = [r for r in rows if r["case"] == case]
        assert sorted(r["source_id"] for r in pair) == ["S0", "S1"]
        assert pair[0]["direction_endpoint_wire_hex"] == pair[1]["direction_endpoint_wire_hex"]
        assert pair[0]["CPU_direction_slot_binding_sha256"] != pair[1]["CPU_direction_slot_binding_sha256"]
    assert encodes == 144 and audits == 72 and nonzero_lo == 24
    assert len(negatives) == 120
    return dict(
        status="PASS_CPU_SAVED_DIRECTION_ENDPOINT_TRANSPORT_ONLY",
        context_pins=pins, rows=rows, fixed_slot_negative_controls=negatives,
        equal_wire_SOURCE_groups=groups,
        summary=dict(source_slots=12, original_cases=6, scalar_endpoint_packets=72,
                     valid_encoder_calls_including_packet_audits=144, internal_RN32_calls=288,
                     packet_consistency_checks=72, nonzero_low_words=24,
                     logical_wire_bytes_per_SOURCE=48, logical_total_wire_bytes_no_dedup=576,
                     distinct_direction_wires=2, distinct_CPU_slot_bindings=12,
                     nonzero_x_widths_preserved=12, fixed_slot_negative_controls=120,
                     context_pins=453),
        native_original_transport_joins=0, native_direction_budget_authenticated=False,
        GPU_used=False, Bpy_used=False, RT_used=False, native_precision_certified=False,
        GPU_launch_allowed=False, launch_exclusion_allowed=False,
        phase_certified=False, phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO",
        new_geometric_evaluations=0, original_query_replays=0, compiler_calls=0,
        old_runner_or_producer_executions=0,
        prior_zero_error_gate=parent["prior_zero_error_gate"])


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
