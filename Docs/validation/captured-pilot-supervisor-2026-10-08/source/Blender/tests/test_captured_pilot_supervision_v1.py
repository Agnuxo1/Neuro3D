"""Synthetic ledger/software gate controls; never run the captured pilot."""
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from Tools.audit_captured_pilot_result_v1 import audit_result
from Tools.run_captured_scalar_pilot_v1 import check_protocol, check_registration, main as supervisor

WORK = Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008')


def plane(x, kind, axis=1):
    obj = {"kind": kind, "vertices_world_BU": [[x, -1, -1], [x, 1, -1], [x, 0, 1]], "faces": [[0, 1, 2]]}
    if kind == "bs":
        obj["power_transmittance"] = F(1, 2)
    else:
        obj.update(mode_origin_BU=[x, 0, 0], mode_direction=[axis, 0, 0])
    return obj


def fixture(split=False):
    scene = {"lambda_BU": F(1, 8), "objects": {},
             "sources": [{"id": "a", "field_reim": [1, 0], "position_BU": [0, 0, 0], "direction": [1, 0, 0]}]}
    if split:
        scene["objects"] = {"bs": plane(1, "bs"), "det": plane(2, "det"), "escape": plane(-1, "escape", -1)}
    else:
        scene["objects"] = {"det": plane(2, "det")}
    paths = []
    choices = [("det", "t", 0, 2, 1)] if not split else [("det", "t", 0, 2, 1), ("escape", "r", 1, 3, -1)]
    for name, event, turns, length, axis in choices:
        hits = []
        if split:
            hits.append({"object_id": "bs", "primitive_id": 0, "parameter": 1, "point": [1, 0, 0],
                         "direction": [1, 0, 0], "event": event, "coefficient_power": F(1, 2)})
        hits.append({"object_id": name, "primitive_id": (1 if name == "det" else 2) if split else 0,
                     "parameter": length - 1 if split else length, "point": [2 if name == "det" else -1, 0, 0],
                     "direction": [axis, 0, 0], "event": scene["objects"][name]["kind"]})
        paths.append({"source_id": "a", "source_reim": [1, 0], "terminal": name, "hits": hits,
                      "direction_norm_squared": 1, "parameter_length": length, "phase_length_numerator": length,
                      "power_factor": F(1, 2) if split else 1, "mirror_phase": 0, "quarter_turns": turns})
    ports = ["det", "escape"] if split else ["det"]
    result = {"schema": "neuro3d-exact-multipath-v1", "backend": "CPU_FRACTION", "status": "COMPLETE",
              "paths": paths, "unresolved": [], "ports": ports, "rays": 3 if split else 1, "wavelength": F(1, 8),
              "fields": {p: {"real": 1, "imag": 0} for p in ports}, "powers": {p: 1 for p in ports},
              "output_power": len(ports), "field_certified": False}
    # Fields here are synthetic finite values for structural checks, not a physics oracle.
    return scene, result


class PilotSoftwareTests(unittest.TestCase):
    def test_direct_local_ledger_audited_without_certifying_field(self):
        audit = audit_result(*fixture())
        self.assertEqual(audit["primary_metric"], 1)
        self.assertTrue(audit["exact_local_ledger_verified"])
        self.assertFalse(audit["nearest_hits_independently_verified"])
        self.assertFalse(audit["field_certified"])

    def test_branch_prefix_coverage_requires_both_nonzero_arms(self):
        scene, result = fixture(split=True)
        self.assertEqual(audit_result(scene, result)["paths"], 2)
        result["paths"].pop()
        with self.assertRaisesRegex(ValueError, "nonzero branch missing"):
            audit_result(scene, result)

    def test_duplicate_leaf_rejected(self):
        scene, result = fixture()
        result["paths"].append(copy.deepcopy(result["paths"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate path leaf"):
            audit_result(scene, result)

    def test_exact_zero_splitter_branch_does_not_require_fabricated_path(self):
        scene, result = fixture(split=True)
        scene["objects"]["bs"]["power_transmittance"] = 1
        result["paths"] = [result["paths"][0]]
        result["paths"][0]["power_factor"] = 1
        result["paths"][0]["hits"][0]["coefficient_power"] = 1
        result["fields"]["escape"] = {"real": 0, "imag": 0}
        result["powers"]["escape"] = 0
        result["output_power"] = 1
        self.assertEqual(audit_result(scene, result)["primary_metric"], 1)

    def test_mirror_phase_and_reflection_quarter_turns(self):
        scene, result = fixture(split=True)
        mirror = scene["objects"]["bs"]
        mirror["kind"] = "mirror"
        mirror["phase_rad"] = F(1, 8)
        mirror.pop("power_transmittance")
        path = result["paths"][1]
        path["power_factor"], path["quarter_turns"], path["mirror_phase"] = 1, 2, F(1, 8)
        path["hits"][0].update(event="mirror", coefficient_power=1)
        result["paths"] = [path]
        result["fields"]["det"] = {"real": 0, "imag": 0}
        result["powers"]["det"] = 0
        result["output_power"] = 1
        self.assertEqual(audit_result(scene, result)["primary_metric"], 1)
        path["mirror_phase"] = 0
        with self.assertRaisesRegex(ValueError, "optical ledger mismatch"):
            audit_result(scene, result)

    def test_local_ray_triangle_and_phase_tampering_rejected(self):
        for target in ("point", "primitive", "direction", "power", "length", "turn", "phase"):
            scene, result = fixture()
            path = result["paths"][0]
            if target == "point": path["hits"][0]["point"] = [3, 0, 0]
            elif target == "primitive": path["hits"][0]["primitive_id"] = -1
            elif target == "direction": path["hits"][0]["direction"] = [-1, 0, 0]
            elif target == "power": path["power_factor"] = F(1, 2)
            elif target == "length": path["parameter_length"] = 3
            elif target == "turn": path["quarter_turns"] = True
            elif target == "phase": path["phase_length_numerator"] = 3
            with self.assertRaises(ValueError):
                audit_result(scene, result)

    def test_unresolved_or_missing_source_cannot_be_complete(self):
        scene, result = fixture()
        result["unresolved"].append({"status": "CONTACT"})
        with self.assertRaises(ValueError):
            audit_result(scene, result)
        scene, result = fixture()
        result["paths"] = []
        with self.assertRaises(ValueError):
            audit_result(scene, result)

    def test_nonfinite_or_missing_terminal_rejected(self):
        for mode in ("nan", "missing", "certificate"):
            scene, result = fixture()
            if mode == "nan": result["fields"]["det"]["real"] = float("nan")
            elif mode == "missing": result["powers"] = {}
            else: result["field_certified"] = True
            with self.assertRaises(ValueError):
                audit_result(scene, result)

    def test_algorithmic_incomplete_preserves_null_outputs(self):
        scene, result = fixture()
        result.update(status="INCOMPLETE", unresolved=[{"status": "RESOURCE_LIMIT"}], fields=None, powers=None, output_power=None)
        self.assertEqual(audit_result(scene, result)["primary_metric"], 0)
        result["fields"] = {"det": {"real": 0, "imag": 0}}
        with self.assertRaises(ValueError):
            audit_result(scene, result)

    def test_actual_frozen_input_source_pins_without_execution(self):
        protocol, pins = check_protocol()
        self.assertEqual(protocol["primary_metric"], "complete_traversal_binary")
        self.assertEqual(len(pins), 5)
        self.assertFalse(protocol["result_collected"])

    def test_prepared_protocol_is_not_authorization(self):
        protocol, _ = check_protocol()
        for record in (None, {}, protocol, {"approved": True}):
            with self.assertRaises(ValueError):
                check_registration(record)

    def test_registration_template_remains_inert_and_synthetic_evidence_rejected(self):
        template = Path(__file__).resolve().parents[2] / "Docs/research/captured_pilot_registration_prepared_v1.json"
        record = json.loads(template.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "decision still pending"):
            check_registration(record)
        record.update(kind="HUMAN_GITHUB_EXCEPTION", approved=True,
                      evidence_origin="DIRECT_HUMAN_USER_MESSAGE_VERIFIED_BY_OPERATOR",
                      evidence_reference="SYNTHETIC_TEST_ONLY_NOT_A_HUMAN_MESSAGE")
        with self.assertRaisesRegex(ValueError, "actual verified evidence"):
            check_registration(record)

    def test_changed_protocol_not_covered_by_registration(self):
        template = Path(__file__).resolve().parents[2] / "Docs/research/captured_pilot_registration_prepared_v1.json"
        record = json.loads(template.read_text(encoding="utf-8"))
        record["protocol_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bind this frozen protocol"):
            check_registration(record)

    def test_missing_registration_never_spawns_worker(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder, patch('Tools.run_captured_scalar_pilot_v1.subprocess.Popen') as popen:
            out = Path(folder) / "not-executed"
            self.assertEqual(supervisor(["--out", str(out)]), 3)
            popen.assert_not_called()
            report = json.loads((out / "supervisor.json").read_text(encoding="utf-8"))
            self.assertFalse(report["worker_started"])
            self.assertFalse(report["result_collected"])
            self.assertIsNone(report["primary_metric"])

    def test_preflight_is_not_experiment_and_stays_pending(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder, patch('Tools.run_captured_scalar_pilot_v1.subprocess.Popen') as popen:
            out = Path(folder) / "preflight"
            self.assertEqual(supervisor(["--out", str(out), "--preflight-only"]), 0)
            popen.assert_not_called()
            report = json.loads((out / "supervisor.json").read_text(encoding="utf-8"))
            self.assertEqual(report["registration_requirement"], "PENDING_HUMAN_OR_EXTERNAL_REGISTRATION")
            self.assertFalse(report["worker_started"])

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder, patch('Tools.run_captured_scalar_pilot_v1.subprocess.Popen') as popen:
            marker = Path(folder) / "keep.txt"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                supervisor(["--out", folder, "--preflight-only"])
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
            popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
