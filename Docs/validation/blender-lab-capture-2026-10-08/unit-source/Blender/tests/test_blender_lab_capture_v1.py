"""Software admission/integrity checks; no optical or ML experiment is run."""
import copy
import math
from pathlib import Path
import tempfile
import unittest

from Blender.blender_lab import scene_capture_v1 as capture
from Blender.blender_lab.bos_adapter_v1 import collect_bos_diagnostic


class CaptureContractTests(unittest.TestCase):
    def setUp(self):
        self.objects = [{"name": "laser", "evaluated_instance_count": 1},
                        {"name": "detector", "evaluated_instance_count": 1},
                        {"name": "mirror", "evaluated_instance_count": 1,
                         "matrix_world": [[float(v == k).hex() for k in range(4)] for v in range(4)],
                         "custom_properties": {"delay": {"float64_hex": (0.125).hex()}},
                         "optics": {"retardance": {"float64_hex": (0.5).hex()}}}]
        self.network = {"schema": capture.NETWORK_SCHEMA, "model": "fixture-only",
                        "inputs": [{"id": "x", "object": "laser"}],
                        "parameters": [{"id": "w", "object": "mirror",
                                        "path": ["custom_properties", "delay"],
                                        "bounds": [0.0, 1.0], "unit": "BU"}],
                        "detectors": [{"id": "y", "object": "detector"}]}

    def test_float_roundtrip_and_signed_zero(self):
        values = [-0.0, math.nextafter(1.0, math.inf), 1e-300, 1e300]
        for value in values:
            self.assertEqual(float.fromhex(capture.float_hex(value)).hex(), value.hex())

    def test_nonfinite_and_bool_rejected(self):
        for value in (True, float("nan"), float("inf"), float("-inf"), 10**1000):
            with self.assertRaises(capture.CaptureError):
                capture.float_hex(value)

    def test_property_tree_preserves_float_type(self):
        value = {"integer": 3, "float": -0.0, "array": [1.5, "s", True]}
        self.assertEqual(capture.json_value(value)["float"], {"float64_hex": "-0x0.0p+0"})
        self.assertEqual(capture.json_value(value)["integer"], 3)

    def test_parameter_reads_scene_value(self):
        result = capture.resolve_network(self.network, self.objects)
        self.assertEqual(result["parameters"][0]["represented_value_hex"], (0.125).hex())
        self.assertFalse(result["forward_executed"])

    def test_optics_and_matrix_parameter_bindings(self):
        for path, expected in [(["optics", "retardance"], 0.5), (["matrix_world", 0, 0], 1.0)]:
            self.network["parameters"][0]["path"] = path
            result = capture.resolve_network(self.network, self.objects)
            self.assertEqual(result["parameters"][0]["represented_value_hex"], expected.hex())

    def test_missing_excluded_and_duplicate_bindings_rejected(self):
        for mutation in ("missing", "excluded", "duplicate", "ambiguous_instance"):
            objects, network = copy.deepcopy(self.objects), copy.deepcopy(self.network)
            if mutation == "missing":
                network["inputs"][0]["object"] = "absent"
            elif mutation == "excluded":
                objects[0]["evaluated_instance_count"] = 0
            elif mutation == "ambiguous_instance":
                objects[0]["evaluated_instance_count"] = 2
            else:
                network["inputs"].append(dict(network["inputs"][0]))
            with self.assertRaises(capture.CaptureError):
                capture.resolve_network(network, objects)

    def test_parameter_bounds_units_and_namespace_rejected(self):
        for key, value in [("bounds", [0.5, 1.0]), ("bounds", [float("nan"), 1.0]),
                           ("unit", ""), ("path", ["render", "color"]), ("path", ["optics", "absent"])]:
            network = copy.deepcopy(self.network)
            network["parameters"][0][key] = value
            with self.assertRaises(capture.CaptureError):
                capture.resolve_network(network, self.objects)

    def test_canonical_hash_order_independent(self):
        self.assertEqual(capture.digest({"b": 1, "a": 2}), capture.digest({"a": 2, "b": 1}))

    def test_integrity_tampering_and_fresh_output(self):
        state = {"meshes": {}, "instances": [], "tag": 1}
        snapshot = {"schema": capture.SCHEMA, "state": state, "state_sha256": capture.digest(state)}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "capture.json"
            capture.write_capture(path, snapshot)
            with self.assertRaises(FileExistsError):
                capture.write_capture(path, snapshot)
        snapshot["state"]["tag"] = 2
        with self.assertRaises(capture.CaptureError):
            capture.validate_capture(snapshot)

    def test_bos_diagnostic_explicit_external_not_certificate(self):
        class API:
            def get_state(self):
                return {"coordinate_units": {"mm_per_world_unit": 1.0},
                        "elements": [], "sources": [], "detectors": [], "report": []}
        result = collect_bos_diagnostic(api=API())
        self.assertFalse(result["geometry_certificate"])
        self.assertFalse(result["optical_result_independently_validated"])

    def test_bos_error_or_schema_change_rejected(self):
        for value in ({"error": "bad"}, {"report": []}):
            class API:
                def get_state(self):
                    return value
            with self.assertRaises(capture.CaptureError):
                collect_bos_diagnostic(api=API())


if __name__ == "__main__":
    unittest.main()
