"""Semantic/adverse analytic controls; no captured-scene forward is executed."""
import copy
from fractions import Fraction as F
import unittest

from Blender.blender_lab.coherent_contract_v1 import (
    SCHEMA, PHASE, validate_contract, prepare_coherent_scene, modal_power, phase_cycles,
)
from Blender.blender_lab.scene_capture_v1 import digest
from Blender.tests.test_scalar_scene_ingress_v1 import fixture as scalar_fixture


def fixture():
    capture, semantics, fields = scalar_fixture()
    capture["state"]["units"] = {"scale_length_metres_per_BU_hex": (0.001).hex()}
    capture["state"]["network"] = {
        "inputs": [{"id": "x", "object": "source"}],
        "parameters": [{"id": "dx", "object": "detector", "path": ["matrix_world", 0, 3], "unit": "BU"}],
        "detectors": [{"id": "D", "object": "detector"}],
    }
    capture["state_sha256"] = digest(capture["state"])
    semantics["capture_state_sha256"] = capture["state_sha256"]
    contract = {"schema": SCHEMA, "capture_state_sha256": capture["state_sha256"],
        "units": {"geometry": "BU", "wavelength_BU_hex": (0.125).hex(), "metres_per_BU_hex": (0.001).hex(),
                  "scale_status": "SCENE_DISPLAY_SCALE_ONLY", "reference_power_watt_hex": None},
        "phase": dict(PHASE),
        "encoding": {"kind": "EXPLICIT_COMPLEX_FIELDS", "normalization": "NONE",
                     "ports": {"x": {"coherence_group": "carrier", "phase_reference": "launch"}}},
        "parameters": {"dx": {"unit": "BU", "role": "GEOMETRY_COORDINATE"}},
        "detectors": {"D": {"object": "detector", "measurement": "NORMALIZED_MODAL_POWER",
                           "field_frame": "COMMON_LAUNCH_PHASE", "renormalize": False}}}
    return capture, semantics, fields, contract


class CoherentContractTests(unittest.TestCase):
    def test_admission_preserves_geometry_and_does_not_trace(self):
        capture, semantics, fields, contract = fixture()
        before = copy.deepcopy((capture, semantics, fields, contract))
        scene = prepare_coherent_scene(capture, semantics, fields, contract)
        self.assertEqual(scene["objects"]["detector"]["vertices_world_BU"][0][0], F(2))
        admission = scene["blender_lab_optical_contract"]
        self.assertEqual(admission["declared_wavelength_metres"], F(0.125) * F(0.001))
        self.assertFalse(admission["field_certified"])
        self.assertFalse(admission["physical_calibration_verified"])
        self.assertFalse(admission["optical_forward_executed"])
        self.assertEqual(before, (capture, semantics, fields, contract))

    def test_unit_relabel_and_wavelength_mismatch_rejected(self):
        for key, value in [("geometry", "m"), ("wavelength_BU_hex", (0.25).hex()),
                           ("metres_per_BU_hex", (1.0).hex()), ("scale_status", "CALIBRATED")]:
            capture, semantics, _, contract = fixture()
            contract["units"][key] = value
            with self.assertRaises(ValueError):
                validate_contract(capture, semantics, contract)

    def test_nonfinite_zero_negative_units_rejected(self):
        for key in ("wavelength_BU_hex", "metres_per_BU_hex"):
            for value in ("nan", "inf", (0.0).hex(), (-1.0).hex(), "0.125"):
                capture, semantics, _, contract = fixture()
                contract["units"][key] = value
                with self.assertRaises(ValueError):
                    validate_contract(capture, semantics, contract)

    def test_unknown_fields_missing_semantics_rejected(self):
        for key in ("units", "phase", "encoding", "parameters", "detectors"):
            capture, semantics, _, contract = fixture()
            del contract[key]
            with self.assertRaises(ValueError):
                validate_contract(capture, semantics, contract)
        capture, semantics, _, contract = fixture()
        contract["coherence_assumed"] = True
        with self.assertRaises(ValueError):
            validate_contract(capture, semantics, contract)

    def test_gauge_sign_and_component_conventions_rejected(self):
        for key in PHASE:
            capture, semantics, _, contract = fixture()
            contract["phase"][key] = "unknown"
            with self.assertRaises(ValueError):
                validate_contract(capture, semantics, contract)

    def test_coherence_split_between_neural_ports_rejected(self):
        capture, semantics, _, contract = fixture()
        capture["state"]["network"]["inputs"].append({"id": "y", "object": "source"})
        semantics["sources"].append({"id": "y", "object": "source", "direction_world_hex": [float(v).hex() for v in (1, 0, 0)]})
        capture["state_sha256"] = digest(capture["state"])
        semantics["capture_state_sha256"] = contract["capture_state_sha256"] = capture["state_sha256"]
        for key in ("coherence_group", "phase_reference"):
            changed = copy.deepcopy(contract)
            changed["encoding"]["ports"]["y"] = dict(changed["encoding"]["ports"]["x"])
            changed["encoding"]["ports"]["y"][key] = "independent"
            with self.assertRaises(ValueError):
                validate_contract(capture, semantics, changed)

    def test_detector_interception_or_renormalization_rejected(self):
        for key, value in [("measurement", "INTERCEPTED_BEAM_POWER"), ("field_frame", "LOCAL_UNSPECIFIED"),
                           ("renormalize", True), ("object", "other")]:
            capture, semantics, _, contract = fixture()
            contract["detectors"]["D"][key] = value
            with self.assertRaises(ValueError):
                validate_contract(capture, semantics, contract)

    def test_parameter_units_and_implicit_degrees_rejected(self):
        capture, semantics, _, contract = fixture()
        contract["parameters"]["dx"]["unit"] = "rad"
        with self.assertRaises(ValueError):
            validate_contract(capture, semantics, contract)
        capture, semantics, _, contract = fixture()
        contract["parameters"]["hidden"] = {"unit": "BU", "role": "GEOMETRY_COORDINATE"}
        with self.assertRaises(ValueError):
            validate_contract(capture, semantics, contract)

    def test_watts_require_explicit_reference_and_stay_uncalibrated(self):
        capture, semantics, _, contract = fixture()
        contract["units"]["reference_power_watt_hex"] = (0.25).hex()
        with self.assertRaises(ValueError):
            validate_contract(capture, semantics, contract)
        contract["units"]["scale_status"] = "DECLARED_SI_SCALE_UNVALIDATED"
        admission = validate_contract(capture, semantics, contract)
        self.assertEqual(admission["reference_power_watt"], F(1, 4))
        self.assertFalse(admission["physical_calibration_verified"])

    def test_capture_edit_invalidates_contract(self):
        capture, semantics, _, contract = fixture()
        capture["state"]["units"]["scale_length_metres_per_BU_hex"] = (1.0).hex()
        with self.assertRaises(ValueError):
            validate_contract(capture, semantics, contract)

    def test_duplicate_bindings_rejected(self):
        for kind in ("inputs", "parameters", "detectors"):
            capture, semantics, _, contract = fixture()
            capture["state"]["network"][kind].append(copy.deepcopy(capture["state"]["network"][kind][0]))
            capture["state_sha256"] = digest(capture["state"])
            semantics["capture_state_sha256"] = contract["capture_state_sha256"] = capture["state_sha256"]
            with self.assertRaises(ValueError):
                validate_contract(capture, semantics, contract)

    def test_rotation_matrix_cannot_be_labeled_translation_coordinate(self):
        capture, semantics, _, contract = fixture()
        capture["state"]["network"]["parameters"][0]["path"] = ["matrix_world", 0, 0]
        capture["state_sha256"] = digest(capture["state"])
        semantics["capture_state_sha256"] = contract["capture_state_sha256"] = capture["state_sha256"]
        with self.assertRaises(ValueError):
            validate_contract(capture, semantics, contract)

    def test_constructive_destructive_quadrature_cross_terms(self):
        expected = ["a", "b"]
        for b, power in [((1, 0), 4), ((-1, 0), 0), ((0, 1), 2)]:
            result = modal_power({"a": (1, 0), "b": b}, expected_source_ids=expected)
            self.assertEqual(result["normalized_modal_power"], power)
            self.assertIsNone(result["declared_power_watt"])
            self.assertFalse(result["field_certified"])
        self.assertEqual(sum([1, 1]), 2)  # independent-power baseline differs in the first two cases

    def test_cancellation_keeps_small_signed_residual(self):
        small = F(1, 2**100)
        result = modal_power({"a": (1, 0), "b": (-1 + small, 0)}, expected_source_ids=["a", "b"])
        self.assertEqual(result["field_reim"], (small, 0))
        self.assertEqual(result["normalized_modal_power"], small**2)

    def test_common_phase_rotation_invariance(self):
        fields = {"a": (F(3, 5), F(4, 5)), "b": (F(2, 7), F(-1, 3))}
        rotated = {key: (-value[1], value[0]) for key, value in fields.items()}
        self.assertEqual(modal_power(fields, expected_source_ids=["a", "b"])["normalized_modal_power"],
                         modal_power(rotated, expected_source_ids=["a", "b"])["normalized_modal_power"])

    def test_missing_zero_contribution_and_nonfinite_rejected(self):
        for fields in [{"a": (1, 0)}, {"a": (1, 0), "b": (float("nan"), 0)},
                       {"a": (1, 0), "b": (True, 0)}, {"a": (1, 0), "b": ("1", 0)}]:
            with self.assertRaises(ValueError):
                modal_power(fields, expected_source_ids=["a", "b"])

    def test_exact_phase_scale_invariance_and_mirror_displacement(self):
        # A mirror piston adds a round-trip 2 delta. Delta=lambda/4 adds half a cycle.
        wavelength = F(1, 10)
        self.assertEqual(phase_cycles(2 * (wavelength / 4), wavelength), F(1, 2))
        length = F(19, 7)
        self.assertEqual(phase_cycles(length, wavelength), phase_cycles(1000 * length, 1000 * wavelength))
        with self.assertRaises(ValueError):
            phase_cycles(length, 0)

    def test_weak_paths_can_sum_to_large_field_no_power_cutoff(self):
        fields = {str(i): (F(1, 1000), 0) for i in range(1000)}
        result = modal_power(fields, expected_source_ids=list(fields), reference_power_watt=F(1, 4))
        self.assertEqual(result["normalized_modal_power"], 1)
        self.assertEqual(result["declared_power_watt"], F(1, 4))


if __name__ == "__main__":
    unittest.main()
