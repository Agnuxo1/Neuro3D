"""Check the actual opened Iris scene against the explicit optical contract.

Run through the bounded Blender software runner. No trace_scene() is invoked.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Blender.blender_lab.scene_capture_v1 import capture_scene, canonical_bytes
from Blender.blender_lab.scalar_scene_ingress_v1 import rational_wire
from Blender.blender_lab.coherent_contract_v1 import prepare_coherent_scene


def main():
    out = Path(sys.argv[sys.argv.index("--") + 1])
    paths = {"network": ROOT / "Docs/research/iris_scene_coordinate_bindings_v1.json",
             "contract": ROOT / "Docs/research/iris_coherent_contract_v1.json",
             "semantics": ROOT / "Docs/validation/captured-scalar-ingress-2026-10-08/semantics.json",
             "fields": ROOT / "Docs/validation/captured-scalar-ingress-2026-10-08/fields_admission_only.json"}
    inputs = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in paths.items()}
    pins = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in paths.items()}
    capture = capture_scene(network=inputs["network"])
    (out / "capture.json").write_bytes(canonical_bytes(capture))
    packet = prepare_coherent_scene(capture, inputs["semantics"], inputs["fields"], inputs["contract"])
    (out / "admitted.json").write_bytes(canonical_bytes(rational_wire(packet)))
    assert all(hashlib.sha256(path.read_bytes()).hexdigest() == pins[key] for key, path in paths.items())
    result = {"schema": "optic_neuro_blender.actual_bpy_semantic_admission.v1", "status": "PASS",
        "blender_version": bpy.app.version_string, "blender_build_hash": bpy.app.build_hash.decode(),
        "opened_scene_sha256": hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        "capture_state_sha256": capture["state_sha256"], "input_file_sha256": pins,
        "counts": packet["blender_lab_ingress"]["counts"],
        "parameter_binding_count": packet["blender_lab_optical_contract"]["parameter_binding_count"],
        "detector_count": packet["blender_lab_optical_contract"]["detector_count"],
        "optical_forward_executed": False, "training_executed": False,
        "field_certified": False, "physical_calibration_verified": False, "gpu_requested": False}
    (out / "checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
