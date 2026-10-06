"""Focused CPU-only tests of the new scene transport ABI.

Fixtures here are synthetic Python objects, never evidence of a reopened Blender
scene or native execution. The independent oracle uses struct IEEE decoding and
Fraction; it does not call the codec's decoder, rounding or audit functions.
"""
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from Blender.benchmarks.capacity_audit import scene_hilo_transport_v1 as transport


def fixture():
    return {
        "schema": "exp005-readback-v2", "lambda_BU": 0.125,
        "objects": {
            "a.bs": {"kind": "bs", "power_transmittance": 0.2,
                     "vertices_world_BU": [[0.5, -1, -1], [0.5, 1, -1], [0.5, 0, 1]],
                     "faces": [[0, 1, 2]]},
            "b.mirror": {"kind": "mirror", "phase_rad": 0.2,
                         "vertices_world_BU": [[1, 0, 0], [1, 1, 0], [1, 0, 1]],
                         "faces": [[0, 1, 2]]},
            "c.det": {"kind": "det", "mode_origin_BU": [2, 0, 0], "mode_direction": [1, 0, 0],
                      "vertices_world_BU": [[2, 0, 0], [2, 1, 0], [2, 0, 1]], "faces": [[0, 1, 2]]},
        },
        "sources": [
            {"id": "source.A", "position_BU": [-1, 0, 0], "direction": [1, 0, 0], "field_reim": [1, 0]},
            {"id": "source.B", "position_BU": [0, -1, 0], "direction": [0, 1, 0], "field_reim": [0, 1]},
        ],
        "undeclared_meshes": [],
        "evaluated_optics_checked": True,
        "evaluated_optical_ids": ["a.bs", "b.mirror", "c.det"],
        "evaluation_scope": "synthetic CPU fixture, not a Blender execution",
    }


def provenance():
    return {"input_class": "cpu_synthetic_test", "blend_sha256": "1" * 64,
            "blender_version": "CPU fixture only", "scene_name": "synthetic",
            "view_layer_name": "synthetic"}


def controlled():
    snapshot, origin = fixture(), provenance()
    snapshot["sources"][0]["position_BU"][0] = 1.0 + 2.0**-30
    snapshot["sources"][0]["direction"][0] = 1.0 + 2.0**-31
    snapshot["sources"][1]["position_BU"][0] = 2.0**-60
    bounds = {"source.A": [[1.0 + 2.0**-32, 1.0 + 2.0**-30], [0, 0], [0, 0]]}
    snapshot[transport.BOUNDS_PROPERTY] = bounds
    origin.update(direction_bounds_property=transport.BOUNDS_PROPERTY,
                  direction_bounds_json=json.dumps(bounds, indent=2))
    return snapshot, origin


def decode32(word):
    value = struct.unpack("<f", struct.pack("<I", word))[0]
    if not math.isfinite(value):
        raise AssertionError("Independent oracle encountered nonfinite float32")
    return Fraction.from_float(value)


def words_of(packet):
    wire = bytes.fromhex(packet["wire_hex"])
    return list(struct.unpack("<" + str(len(wire) // 4) + "I", wire))


def reseal_wire(packet, words):
    changed = copy.deepcopy(packet)
    wire = struct.pack("<" + str(len(words)) + "I", *words)
    changed["wire_hex"] = wire.hex()
    changed["manifest"]["wire_sha256"] = hashlib.sha256(wire).hexdigest()
    changed["manifest"]["wire_bytes"] = len(wire)
    return changed


class Tests(unittest.TestCase):
    def make(self, snapshot=None, origin=None):
        return transport.build_packet(snapshot or fixture(), provenance=origin or provenance())

    def assert_rejected(self, packet, trusted):
        with self.assertRaises(ValueError):
            transport.admit_for_upload(packet, trusted_manifest=trusted)

    def independent_values(self, packet):
        manifest = packet["manifest"]
        snapshot, bounds = manifest["snapshot"], manifest["direction_bounds"] or {}
        object_order = sorted(snapshot["objects"])
        raw = words_of(packet)
        layout = manifest["abi"]
        expected_scalars = []
        # Build the reference from observed source/geometry data, not audit rationals.
        for source_index, source in enumerate(snapshot["sources"]):
            intervals = bounds.get(source["id"], [[v, v] for v in source["direction"]])
            for role, values, endpoint in (
                ("origin", source["position_BU"], 0),
                ("raw_direction", source["direction"], 0),
                ("direction_bound", [v[0] for v in intervals], 0),
                ("direction_bound", [v[1] for v in intervals], 1),
                ("field", source["field_reim"], 0),
            ):
                expected_scalars.extend((role, source_index, 0, axis, endpoint, float(value))
                                        for axis, value in enumerate(values))
        for object_index, name in enumerate(object_order):
            obj = snapshot["objects"][name]
            for vertex_index, vertex in enumerate(obj["vertices_world_BU"]):
                expected_scalars.extend(("vertex", object_index, vertex_index, axis, 0, float(value))
                                        for axis, value in enumerate(vertex))
            if obj["kind"] in ("det", "escape"):
                for key, role in (("mode_origin_BU", "mode_origin"), ("mode_direction", "mode_direction")):
                    expected_scalars.extend((role, object_index, 0, axis, 0, float(value))
                                            for axis, value in enumerate(obj[key]))
        expected_scalars.append(("wavelength", 0xFFFFFFFF, 0, 0, 0, float(snapshot["lambda_BU"])))
        self.assertEqual(layout["scalar_count"], len(expected_scalars))
        decoded = []
        for index, (role, owner, element, component, endpoint, observed) in enumerate(expected_scalars):
            offset = layout["scalar_offset"] + index * 8
            hi, lo, actual_role, actual_owner, actual_element, actual_component, actual_endpoint, reserved = raw[offset:offset + 8]
            self.assertEqual((actual_role, actual_owner, actual_element, actual_component, actual_endpoint, reserved),
                             (transport.ROLE[role], owner, element, component, endpoint, 0))
            value = decode32(hi) + decode32(lo)
            self.assertEqual(value, Fraction.from_float(observed))
            audit = manifest["scalars"][index]
            self.assertEqual(audit["observed_binary64_words"], list(struct.unpack("<II", struct.pack("<d", observed))))
            self.assertEqual(Fraction(*audit["exact_input"]), value)
            self.assertEqual(audit["residual_exact"], [0, 1])
            decoded.append(value)
        return decoded

    def test_complete_packet_and_independent_scalar_oracle(self):
        packet = self.make()
        manifest = packet["manifest"]
        raw = transport.admit_for_upload(packet, trusted_manifest=copy.deepcopy(manifest))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest["wire_sha256"])
        self.assertEqual(len(raw), manifest["abi"]["total_words"] * 4)
        self.independent_values(packet)
        self.assertEqual((manifest["abi"]["source_count"], manifest["abi"]["vertex_count"],
                          manifest["abi"]["triangle_count"], manifest["abi"]["object_count"]), (2, 9, 3, 3))
        for source_index, record in enumerate(manifest["source_records"]):
            self.assertEqual(len(record), 32)
            self.assertEqual(record[:2], [source_index, 0xFFFFFFFF])
            self.assertEqual(record[16:], [0] * 16)
        for record in manifest["triangle_records"]:
            self.assertEqual(record[7], 0)
            vertices = [manifest["vertex_records"][index] for index in record[3:6]]
            self.assertTrue(all(vertex[1] == record[1] for vertex in vertices))
            self.assertEqual(len({vertex[0] for vertex in vertices}), 3)
        summary = transport.audit_packet(packet, trusted_manifest=manifest)
        self.assertEqual(summary["status"], "PASS")
        self.assertFalse(summary["native_transport_verified"])
        self.assertFalse(summary["GPU_launch_allowed"])
        self.assertFalse(manifest["scope"]["phase_certified"])
        self.assertIsNone(manifest["scope"]["physical_origin_error_bound"])

    def test_material_metadata_retains_nonrepresentable_values_uniformly(self):
        packet = self.make()
        roles = {record["role"] for record in packet["manifest"]["scalars"]}
        self.assertNotIn("phase", roles)
        self.assertNotIn("transmittance", roles)
        for metadata in packet["manifest"]["material_binary64_metadata"]:
            for key, record in metadata["parameters"].items():
                observed = packet["manifest"]["snapshot"]["objects"][metadata["object_id"]][key]
                self.assertEqual(record["binary64_words"], list(struct.unpack("<II", struct.pack("<d", observed))))
                self.assertFalse(record["numeric_ABI"])
        changed_snapshot = fixture()
        changed_snapshot["objects"]["b.mirror"]["phase_rad"] = 0.3
        changed = self.make(changed_snapshot)
        self.assertEqual(changed["wire_hex"], packet["wire_hex"])
        self.assert_rejected(changed, packet["manifest"])

    def test_controlled_low_components_and_nonzero_intervals(self):
        snapshot, origin = controlled()
        packet = self.make(snapshot, origin)
        decoded = self.independent_values(packet)
        manifest = packet["manifest"]
        self.assertTrue(any(record["lo_word"] != 0 for record in manifest["scalars"]))
        source = manifest["source_records"][0]
        width = decoded[source[11]] - decoded[source[8]]
        self.assertEqual(width, Fraction(3, 2**32))
        self.assertGreater(width, 0)
        self.assertEqual(manifest["direction_bounds_provenance"]["stored_json_sha256"],
                         hashlib.sha256(origin["direction_bounds_json"].encode()).hexdigest())
        # A metadata-free source still gets an observed singleton, not a guessed box.
        second = manifest["source_records"][1]
        self.assertEqual([decoded[i] for i in second[8:11]], [decoded[i] for i in second[11:14]])

    def test_future_native_delta_requires_pair64_not_float64_collapse(self):
        snapshot, origin = controlled()
        packet = self.make(snapshot, origin)
        decoded = self.independent_values(packet)
        manifest = packet["manifest"]
        source_index = manifest["source_records"][1][2]
        vertex = next(record for record in manifest["vertex_records"] if record[1] == 1 and record[2] == 0)
        exact = decoded[vertex[3]] - decoded[source_index]
        self.assertEqual(exact, Fraction(1) - Fraction(1, 2**60))
        self.assertNotEqual(Fraction.from_float(float(exact)), exact)
        self.assertEqual(Fraction.from_float(1.0) + Fraction.from_float(-2.0**-60), exact)
        # CPU construction of the mathematical witness is not a native test.
        self.assertFalse(manifest["scope"]["native_transport_verified"])

    def test_resealed_zero_low_and_component_swap_rejected(self):
        snapshot, origin = controlled()
        packet = self.make(snapshot, origin)
        for mutation in ("zero_low", "swap_limbs"):
            words = words_of(packet)
            index = next(record["index"] for record in packet["manifest"]["scalars"] if record["lo_word"])
            offset = packet["manifest"]["abi"]["scalar_offset"] + index * 8
            if mutation == "zero_low":
                words[offset + 1] = 0
            else:
                words[offset], words[offset + 1] = words[offset + 1], words[offset]
            self.assert_rejected(reseal_wire(packet, words), packet["manifest"])

    def test_resealed_identity_substitutions_rejected_even_with_equal_wire(self):
        packet = self.make()
        snapshot = fixture()
        snapshot["sources"][0]["id"], snapshot["sources"][1]["id"] = (
            snapshot["sources"][1]["id"], snapshot["sources"][0]["id"])
        changed = self.make(snapshot)
        self.assertEqual(changed["wire_hex"], packet["wire_hex"])
        self.assert_rejected(changed, packet["manifest"])
        other_provenance = provenance()
        other_provenance["blend_sha256"] = "2" * 64
        self.assert_rejected(self.make(origin=other_provenance), packet["manifest"])

    def test_resealed_bounds_collapse_rejected_against_fixed_manifest(self):
        snapshot, origin = controlled()
        packet = self.make(snapshot, origin)
        raw = snapshot["sources"][0]["direction"][0]
        snapshot[transport.BOUNDS_PROPERTY]["source.A"][0] = [raw, raw]
        origin["direction_bounds_json"] = json.dumps(snapshot[transport.BOUNDS_PROPERTY])
        changed = self.make(snapshot, origin)
        self.assert_rejected(changed, packet["manifest"])

    def test_header_counts_endian_padding_previous_and_triangle_corruption(self):
        packet = self.make()
        original = words_of(packet)
        layout = packet["manifest"]["abi"]
        mutations = []
        for index, value in ((3, original[3] + 1), (4, original[4] + 1), (6, 7), (18, 1),
                             (layout["source_offset"] + 1, 0),
                             (layout["triangle_offset"] + 3, 0xFFFFFFFF)):
            words = original[:]
            words[index] = value
            mutations.append(words)
        mutations.extend((original[:-1], original + [0]))
        for words in mutations:
            self.assert_rejected(reseal_wire(packet, words), packet["manifest"])
        wrong_endian = copy.deepcopy(packet)
        wire = struct.pack(">" + str(len(original)) + "I", *original)
        wrong_endian["wire_hex"] = wire.hex()
        wrong_endian["manifest"]["wire_sha256"] = hashlib.sha256(wire).hexdigest()
        self.assert_rejected(wrong_endian, packet["manifest"])

    def test_selected_numeric_domain_failures(self):
        for value in (0.1, 2.0**-149, float("nan"), float("inf"), -0.0, True, 1000001):
            with self.subTest(value=repr(value)):
                snapshot = fixture()
                snapshot["sources"][0]["position_BU"][0] = value
                with self.assertRaises(ValueError):
                    self.make(snapshot)
        for path in ("field", "vertex", "lambda"):
            snapshot = fixture()
            if path == "field":
                snapshot["sources"][0]["field_reim"][0] = 0.1
            elif path == "vertex":
                snapshot["objects"]["b.mirror"]["vertices_world_BU"][0][0] = 0.1
            else:
                snapshot["lambda_BU"] = 0.126
            with self.assertRaisesRegex(ValueError, "STOP_NONZERO_RESIDUAL"):
                self.make(snapshot)

    def test_reversed_noncontaining_unknown_and_unbound_intervals(self):
        for kind in ("reverse", "noncontaining", "unknown", "raw_json_mismatch", "missing_provenance"):
            snapshot, origin = controlled()
            bounds = snapshot[transport.BOUNDS_PROPERTY]
            if kind == "reverse":
                bounds["source.A"][0].reverse()
            elif kind == "noncontaining":
                bounds["source.A"][0] = [2, 2]
            elif kind == "unknown":
                bounds["foreign"] = bounds["source.A"]
            elif kind == "missing_provenance":
                del origin["direction_bounds_json"]
            if kind not in ("raw_json_mismatch", "missing_provenance"):
                origin["direction_bounds_json"] = json.dumps(bounds)
            if kind == "raw_json_mismatch":
                bounds["source.A"][0][1] = 1.0 + 2.0**-29
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.make(snapshot, origin)

    def test_geometry_and_source_completeness_rejections(self):
        for kind in ("quad", "bad_index", "duplicate_index", "missing_terminal_mode",
                     "duplicate_source", "undeclared_mesh", "zero_direction", "previous_in_source"):
            snapshot = fixture()
            if kind == "quad":
                snapshot["objects"]["b.mirror"]["faces"][0] = [0, 1, 2, 0]
            elif kind == "bad_index":
                snapshot["objects"]["b.mirror"]["faces"][0][0] = 10
            elif kind == "duplicate_index":
                snapshot["objects"]["b.mirror"]["faces"][0] = [0, 1, 1]
            elif kind == "missing_terminal_mode":
                del snapshot["objects"]["c.det"]["mode_direction"]
            elif kind == "duplicate_source":
                snapshot["sources"][1]["id"] = snapshot["sources"][0]["id"]
            elif kind == "undeclared_mesh":
                snapshot["undeclared_meshes"] = ["user.mesh"]
            elif kind == "zero_direction":
                snapshot["sources"][0]["direction"] = [0, 0, 0]
            else:
                snapshot["sources"][0]["previous_primitive_id"] = 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.make(snapshot)

    def test_degenerate_coordinate_geometry_is_preserved_without_hit_claim(self):
        snapshot = fixture()
        snapshot["objects"]["b.mirror"]["vertices_world_BU"] = [[1, 0, 0]] * 3
        packet = self.make(snapshot)
        values = self.independent_values(packet)
        vertices = [record for record in packet["manifest"]["vertex_records"] if record[1] == 1]
        self.assertEqual([[values[index] for index in vertex[3:6]] for vertex in vertices],
                         [[Fraction(1), Fraction(0), Fraction(0)]] * 3)
        self.assertFalse(packet["manifest"]["scope"]["first_hit_certified"])
        transport.admit_for_upload(packet, trusted_manifest=packet["manifest"])

    def test_claimed_reopened_input_requires_evaluated_scene_evidence(self):
        snapshot, origin = fixture(), provenance()
        origin["input_class"] = "real_reopened_baseline"
        snapshot["evaluated_optics_checked"] = False
        with self.assertRaisesRegex(ValueError, "evaluated optics"):
            self.make(snapshot, origin)
        snapshot["evaluated_optics_checked"] = True
        snapshot["evaluated_optical_ids"] = ["a.bs"]
        with self.assertRaisesRegex(ValueError, "evaluated optics"):
            self.make(snapshot, origin)

    def test_sorted_serialized_manifest_is_reproducible_without_input_mutation(self):
        snapshot, origin = controlled()
        original_snapshot, original_origin = copy.deepcopy(snapshot), copy.deepcopy(origin)
        packet = self.make(snapshot, origin)
        saved = json.loads(json.dumps(packet, sort_keys=True, allow_nan=False))
        transport.admit_for_upload(saved, trusted_manifest=copy.deepcopy(saved["manifest"]))
        self.assertEqual(snapshot, original_snapshot)
        self.assertEqual(origin, original_origin)
        # Caller mutation does not rewrite the already-built packet.
        snapshot["sources"][0]["position_BU"][0] = 12
        self.assertNotEqual(snapshot, packet["manifest"]["snapshot"])

    def test_packet_and_provenance_schemas_are_closed(self):
        packet = self.make()
        changed = copy.deepcopy(packet)
        changed["GPU_launch_allowed"] = True
        self.assert_rejected(changed, packet["manifest"])
        origin = provenance()
        origin["trusted_native_scene"] = True
        with self.assertRaisesRegex(ValueError, "provenance schema"):
            self.make(origin=origin)

    def test_duplicate_persisted_json_keys_are_rejected(self):
        snapshot, origin = controlled()
        raw_value = json.dumps(snapshot[transport.BOUNDS_PROPERTY]["source.A"])
        origin["direction_bounds_json"] = '{"source.A":' + raw_value + ',"source.A":' + raw_value + '}'
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.make(snapshot, origin)


if __name__ == "__main__":
    unittest.main(verbosity=2)
