"""Exercise Iris rebuild compatibility and rejection contracts in real Blender.

Run in an isolated background Blender process:
  blender -b -t 1 --python-exit-code 1 --python test_rebuild_contract_blender.py -- --report contract.json

This suite creates and discards in-memory scenes. It does not train, render,
save .blend files, run GPU kernels, or replace the recorded Iris metrics.
Only the explicitly requested JSON report is written. RNA is never patched.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone

import bpy
import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "neuro3d_iris_demo.py"
DETECTOR_ID = "neuro3d_detector_id"
MATERIAL_MAP = "neuro3d_materials"
EXPECTED_CASES = (
    "legacy_detector_and_material_metadata",
    "duplicate_detector_ids_rejected",
    "invalid_explicit_detector_id_rejected",
    "broken_optics_mapping_rejected",
    "foreign_scene_material_sharing_rejected",
)


def utc_now():
    """Return a timezone-qualified timestamp for the execution record."""
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    """Raise a clear contract failure without relying on Python assert flags."""
    if not condition:
        raise AssertionError(message)


def atomic_report(path, report):
    """Replace a JSON report atomically, retaining no temporary file on failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            prefix="." + path.name + ".", suffix=".tmp",
            dir=path.parent, delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def expect_rejection(operation, description):
    """Require an explicit validation error, rather than a successful zero result."""
    try:
        operation()
    except (RuntimeError, ValueError) as error:
        require(str(error).strip(), description + " raised an empty error")
        return {"exception_type": type(error).__name__, "message": str(error)}
    raise AssertionError(description + " accepted an invalid configuration")


def load_demo():
    """Import the sibling source as a module without activating its GUI entry point."""
    specification = importlib.util.spec_from_file_location(
        "neuro3d_iris_rebuild_contract_target", SOURCE_PATH
    )
    require(specification is not None and specification.loader is not None,
            "The Iris source could not be imported")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.HERE = str(HERE)
    return module


class RebuildContracts:
    """Build isolated real scenes and check only rebuild-related behavior."""

    def __init__(self, demo):
        self.demo = demo
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.state = demo.load_state()
        self.features, self.labels, _ = demo.load_iris()
        self.sample_index = int(self.state["test_idx"][0])
        self.row = self.features[self.sample_index]
        self.outputs = list(demo.modes()[1])
        self.limits = dict(demo.VERIFY_LIMITS)

    def fresh_network(self):
        """Start each case with a valid network through the reset=False branch."""
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.demo.HERE = str(HERE)
        self.demo.build_scene(
            np.array(self.state["theta"]).reshape(self.demo.K, self.demo.K),
            self.state["ref"], reset=False,
        )
        return self.capture()

    def detectors(self):
        """Find detectors by their existing optical kind within the active network."""
        result = [
            obj for obj in self.demo.scene_collection("Optics").objects
            if obj.get("kind") == "det"
        ]
        require(len(result) == len(self.outputs), "The detector fixture is incomplete")
        return result

    def capture(self):
        """Check real outputs against the unchanged model and existing tolerances."""
        prediction, powers, fields, segments, casts = self.demo.classify(self.row)
        require(set(fields) == set(self.outputs),
                "Detector fields do not expose the complete logical output set")
        vector = np.array([fields[key] for key in self.outputs], dtype=complex)
        power_vector = np.asarray(powers, dtype=float)
        require(np.isfinite(vector).all() and np.isfinite(power_vector).all(),
                "The scene returned a non-finite output")
        require(len(power_vector) == len(self.demo.CLASS_DET),
                "The class detector power vector has an invalid size")
        require(bool(np.any(np.abs(vector) > 0)), "All detector fields are zero")
        require(int(casts) > 0, "The classifier did not perform ray casts")
        reference = float(bpy.context.scene["ref"])
        amplitudes = self.demo.encode(self.row[None], reference)[0]
        theta = np.asarray(self.state["theta"]).reshape(self.demo.K, self.demo.K)
        expected = self.demo.model_U(theta * self.demo.LAM / (4 * math.pi)) @ amplitudes
        complex_error = float(np.max(np.abs(vector - expected)))
        class_indices = [self.outputs.index(key) for key in self.demo.CLASS_DET]
        model_power = np.abs(expected[class_indices]) ** 2
        power_error = float(np.max(np.abs(power_vector - model_power)))
        escaped = float(self.demo.TRACE_INFO["escape"])
        balance_error = float(abs(float(np.sum(np.abs(vector) ** 2)) + escaped - 1.0))
        metrics = {
            "outputs_complex_vs_model_max": complex_error,
            "scene_vs_model_max_power_diff": power_error,
            "escape_max": escaped,
            "power_balance_max_err": balance_error,
        }
        for name, value in metrics.items():
            require(math.isfinite(value) and 0 <= value <= self.limits[name],
                    name + " exceeds the existing Iris verification tolerance")
        return {
            "prediction": int(prediction), "powers": power_vector,
            "fields": vector, "segments": segments, "ray_casts": int(casts),
            "metrics": metrics,
        }

    def summary(self, snapshot):
        """Return JSON-safe evidence without serializing the ray path tree."""
        return {
            "sample_index": self.sample_index,
            "prediction": snapshot["prediction"],
            "ray_casts": snapshot["ray_casts"],
            "outputs_checked": self.outputs,
            "metrics": dict(snapshot["metrics"]),
        }

    def draw(self, snapshot):
        """Exercise the actual scene presentation path without invoking rendering."""
        self.demo.show(
            snapshot["segments"], snapshot["powers"].tolist(),
            snapshot["prediction"], truth=int(self.labels[self.sample_index]),
            x_row=self.row,
        )

    def legacy_detector_and_material_metadata(self):
        """Verify unambiguous old scenes still classify and display without new tags."""
        before = self.fresh_network()
        scene = bpy.context.scene
        require(MATERIAL_MAP in scene, "The new scene has no material map to remove")
        removed = 0
        for detector in self.detectors():
            require(DETECTOR_ID in detector, "The new detector has no explicit ID")
            del detector[DETECTOR_ID]
            removed += 1
        del scene[MATERIAL_MAP]
        legacy = self.capture()
        self.draw(legacy)
        self.demo._dim_detectors()
        displayed = self.capture()
        error = max(
            float(np.max(np.abs(before["fields"] - legacy["fields"]))),
            float(np.max(np.abs(before["fields"] - displayed["fields"]))),
        )
        require(error <= self.limits["decoration_invariance_max"],
                "Legacy metadata fallback changed the detector fields")
        require(before["prediction"] == legacy["prediction"] == displayed["prediction"],
                "Legacy metadata fallback changed the prediction")
        details = self.summary(displayed)
        details.update({
            "detector_ids_removed": removed,
            "material_map_removed": True,
            "show_and_dim_completed": True,
            "legacy_output_difference_max": error,
        })
        return details

    def duplicate_detector_ids_rejected(self):
        """Reject two physical detectors claiming the same logical output."""
        self.fresh_network()
        first, second = self.detectors()[:2]
        first_id, second_id = first.get(DETECTOR_ID), second.get(DETECTOR_ID)
        require(first_id in self.outputs and second_id in self.outputs and first_id != second_id,
                "The starting detector IDs are not distinct valid outputs")
        second[DETECTOR_ID] = first_id
        return {
            "duplicated_id": first_id, "replaced_id": second_id,
            "rejection": expect_rejection(
                lambda: self.demo.classify(self.row), "Duplicate detector IDs"
            ),
        }

    def invalid_explicit_detector_id_rejected(self):
        """Never rescue an invalid explicit ID by falling back to a plausible name."""
        self.fresh_network()
        detector = next(obj for obj in self.detectors() if obj.get(DETECTOR_ID) == "R0")
        detector.name = "det.R0"
        require(detector.name == "det.R0", "The legacy-name fixture is ambiguous")
        detector[DETECTOR_ID] = "INVALID_CONTRACT_OUTPUT"
        return {
            "legacy_name": detector.name, "invalid_explicit_id": detector[DETECTOR_ID],
            "rejection": expect_rejection(
                lambda: self.demo.classify(self.row), "Invalid explicit detector ID"
            ),
        }

    def broken_optics_mapping_rejected(self):
        """Reject a broken saved collection map rather than tracing an empty layer."""
        self.fresh_network()
        scene = bpy.context.scene
        mapping = json.loads(scene["neuro3d_collections"])
        missing_name = "Neuro3D_contract_missing_optics"
        require(bpy.data.collections.get(missing_name) is None,
                "The missing-collection fixture unexpectedly exists")
        mapping["Optics"] = missing_name
        scene["neuro3d_collections"] = json.dumps(mapping)
        return {
            "missing_collection": missing_name,
            "rejection": expect_rejection(
                lambda: self.demo.classify(self.row), "Broken Optics collection mapping"
            ),
        }

    @staticmethod
    def emission_snapshot(material):
        """Read all emission values that another scene would observe."""
        require(material.use_nodes and material.node_tree is not None,
                "The detector material has no node tree")
        shader = material.node_tree.nodes.get("Principled BSDF")
        require(shader is not None, "The detector material has no Principled BSDF")
        return {
            "strength": float(shader.inputs["Emission Strength"].default_value),
            "color": [float(value) for value in shader.inputs["Emission Color"].default_value],
        }

    def foreign_scene_material_sharing_rejected(self):
        """Reject shared detector emission resources without changing the other scene."""
        snapshot = self.fresh_network()
        material = self.demo.detector_material("R0")
        foreign_scene = bpy.data.scenes.new("Neuro3D contract foreign scene")
        mesh = bpy.data.meshes.new("Neuro3D contract foreign mesh")
        foreign_object = bpy.data.objects.new("Neuro3D contract foreign material user", mesh)
        foreign_scene.collection.objects.link(foreign_object)
        mesh.materials.append(material)
        require(foreign_scene != bpy.context.scene, "The foreign scene became active")
        require(foreign_object.data.materials[0] == material,
                "The foreign object does not share the target material")
        before = self.emission_snapshot(material)
        rejections = {}
        operations = (
            ("detector_material", lambda: self.demo.detector_material("R0")),
            ("show", lambda: self.draw(snapshot)),
            ("dim", self.demo._dim_detectors),
        )
        for name, operation in operations:
            try:
                rejections[name] = expect_rejection(operation, "Shared material in " + name)
            finally:
                require(foreign_object.data.materials[0] == material,
                        name + " replaced the foreign object's material")
                require(self.emission_snapshot(material) == before,
                        name + " changed emission visible in the foreign scene")
        return {
            "shared_material": material.name,
            "foreign_scene": foreign_scene.name,
            "emission_before": before,
            "emission_after": self.emission_snapshot(material),
            "rejections": rejections,
        }


def main(argv):
    """Run every case and persist both successful and failed current-run evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True,
                        help="Destination of the atomic JSON contract report.")
    arguments = parser.parse_args(argv)
    report_path = arguments.report.expanduser().resolve()
    protected = {
        SOURCE_PATH.resolve(), Path(__file__).resolve(),
        (HERE / "scene_verification.json").resolve(),
        (HERE / "trained_lattice.json").resolve(), (HERE / "iris.csv").resolve(),
    }
    require(report_path not in protected, "The report path would replace an Iris source or artifact")
    require(bpy.app.background, "Run this suite in an isolated background Blender process")
    started = time.perf_counter()
    report = {
        "schema_version": 1,
        "suite": "iris_rebuild_compatibility_contracts",
        "started_at": utc_now(),
        "status": "incomplete",
        "verification_passed": False,
        "verification_failures": ["verification_incomplete"],
        "verification_limits": {},
        "runtime": {
            "blender_version": bpy.app.version_string,
            "background": bool(bpy.app.background),
            "training_run": False, "render_run": False, "gpu_kernels_run": False,
        },
        "source": str(SOURCE_PATH),
        "cases": {name: {"status": "not_run"} for name in EXPECTED_CASES},
    }
    atomic_report(report_path, report)
    try:
        report["source_sha256"] = hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()
        report["test_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        report["trained_state_sha256"] = hashlib.sha256(
            (HERE / "trained_lattice.json").read_bytes()
        ).hexdigest()
        demo = load_demo()
        report["verification_limits"] = dict(demo.VERIFY_LIMITS)
        suite = RebuildContracts(demo)
        for name in EXPECTED_CASES:
            case_started = time.perf_counter()
            try:
                details = getattr(suite, name)()
                entry = {"status": "passed", "details": details}
            except Exception as error:
                entry = {
                    "status": "failed", "exception_type": type(error).__name__,
                    "message": str(error), "traceback": traceback.format_exc(),
                }
            entry["seconds"] = time.perf_counter() - case_started
            report["cases"][name] = entry
            atomic_report(report_path, report)
            print("IRIS_REBUILD_CONTRACT", name, entry["status"], flush=True)
        failures = [
            name for name, result in report["cases"].items()
            if result["status"] != "passed"
        ]
        report["verification_failures"] = failures
        report["verification_passed"] = not failures
        report["status"] = "passed" if not failures else "failed"
    except Exception as error:
        report.update({
            "status": "failed", "verification_passed": False,
            "verification_failures": ["suite_setup_or_execution_failed"],
            "error": {"exception_type": type(error).__name__, "message": str(error),
                      "traceback": traceback.format_exc()},
        })
    report["finished_at"] = utc_now()
    report["seconds"] = time.perf_counter() - started
    atomic_report(report_path, report)
    print("IRIS_REBUILD_CONTRACT_REPORT", str(report_path), report["status"], flush=True)
    return 0 if report["verification_passed"] else 1


if __name__ == "__main__":
    cli = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if main(cli):
        raise RuntimeError("Iris rebuild compatibility contracts failed; inspect the JSON report.")
