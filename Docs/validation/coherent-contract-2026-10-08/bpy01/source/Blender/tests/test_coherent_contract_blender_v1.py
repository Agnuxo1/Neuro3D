"""bpy software roundtrip of units/inputs/parameters/detectors, without tracing."""
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.blender_lab.scene_capture_v1 import capture_scene
from Blender.blender_lab.coherent_contract_v1 import SCHEMA, PHASE, prepare_coherent_scene, modal_power
from Blender.blender_lab.scalar_scene_ingress_v1 import rational_wire


def main():
    out = Path(sys.argv[sys.argv.index("--") + 1])
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    optics = bpy.data.collections.new("OwnOptics")
    scene.collection.children.link(optics)
    for name in ("source.a", "source.b"):
        obj = bpy.data.objects.new(name, None)
        scene.collection.objects.link(obj)
    mesh = bpy.data.meshes.new("ModePlane")
    mesh.from_pydata([(0, -2, -2), (0, 2, -2), (0, 0, 2)], [], [(0, 1, 2)])
    detector = bpy.data.objects.new("detector", mesh)
    detector.location.x = 2
    detector["kind"] = "det"
    optics.objects.link(detector)
    network = {"schema": "neuro3d.blender_lab.network_bindings.v1", "model": "own.software.contract.fixture.v1",
        "inputs": [{"id": "a", "object": "source.a"}, {"id": "b", "object": "source.b"}],
        "parameters": [{"id": "detector.x", "object": "detector", "path": ["matrix_world", 0, 3],
                        "unit": "BU", "bounds": [(-100.0).hex(), (100.0).hex()]}],
        "detectors": [{"id": "D", "object": "detector"}]}
    bpy.context.view_layer.update()
    capture = capture_scene(network=network)
    semantics = {"schema": "neuro3d.blender_lab.scalar_semantics.v1", "model": "LOSSLESS_SCALAR_PLANAR_V1",
        "capture_state_sha256": capture["state_sha256"], "optical_collection": "OwnOptics",
        "wavelength_BU_hex": (0.125).hex(),
        "objects": {"detector": {"kind": "det", "mode_origin_local_hex": [float(0).hex()] * 3,
                   "mode_direction_world_hex": [float(v).hex() for v in (1, 0, 0)]}},
        "sources": [{"id": key, "object": "source." + key, "direction_world_hex": [float(v).hex() for v in (1, 0, 0)]}
                    for key in ("a", "b")]}
    contract = {"schema": SCHEMA, "capture_state_sha256": capture["state_sha256"], "phase": dict(PHASE),
        "units": {"geometry": "BU", "wavelength_BU_hex": (0.125).hex(),
                  "metres_per_BU_hex": capture["state"]["units"]["scale_length_metres_per_BU_hex"],
                  "scale_status": "SCENE_DISPLAY_SCALE_ONLY", "reference_power_watt_hex": None},
        "encoding": {"kind": "EXPLICIT_COMPLEX_FIELDS", "normalization": "NONE",
                     "ports": {key: {"coherence_group": "common", "phase_reference": "launch"} for key in ("a", "b")}},
        "parameters": {"detector.x": {"unit": "BU", "role": "GEOMETRY_COORDINATE"}},
        "detectors": {"D": {"object": "detector", "measurement": "NORMALIZED_MODAL_POWER",
                           "field_frame": "COMMON_LAUNCH_PHASE", "renormalize": False}}}
    fields = {"a": [1, 0], "b": [-1, 0]}
    packet = prepare_coherent_scene(capture, semantics, fields, contract)
    assert packet["objects"]["detector"]["vertices_world_BU"][0][0] == 2
    assert packet["blender_lab_optical_contract"]["metres_per_BU"] == F(float(scene.unit_settings.scale_length))
    # Analytic readout helper only: these are inputs, not fields propagated through the fixture.
    assert modal_power(fields, expected_source_ids=["a", "b"])["normalized_modal_power"] == 0
    blend = out / "contract-fixture.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    reopened = capture_scene(network=network)
    assert reopened["state_sha256"] == capture["state_sha256"]
    prepare_coherent_scene(reopened, semantics, fields, contract)
    failures = []
    for name, operation in [
        ("split_coherence", lambda c: c["encoding"]["ports"]["b"].update(coherence_group="independent")),
        ("detector_renormalization", lambda c: c["detectors"]["D"].update(renormalize=True)),
        ("wrong_unit_scale", lambda c: c["units"].update(metres_per_BU_hex=(1.0).hex()))]:
        changed = copy.deepcopy(contract)
        operation(changed)
        try:
            prepare_coherent_scene(reopened, semantics, fields, changed)
        except ValueError:
            failures.append(name)
        else:
            raise AssertionError("unsafe contract admitted: " + name)
    bpy.context.scene.unit_settings.scale_length = 0.002
    changed_capture = capture_scene(network=network)
    try:
        prepare_coherent_scene(changed_capture, semantics, fields, contract)
    except ValueError:
        failures.append("edited_scene_units")
    else:
        raise AssertionError("stale unit contract admitted")
    for name, data in [("capture", capture), ("semantics", semantics), ("contract", contract), ("fields", fields), ("admitted", rational_wire(packet))]:
        (out / (name + ".json")).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    result = {"schema": "optic_neuro_blender.bpy_semantic_check.v1", "status": "PASS",
        "blender_version": bpy.app.version_string, "blender_build_hash": bpy.app.build_hash.decode(),
        "capture_state_sha256": capture["state_sha256"], "save_reopen_same_identity": True,
        "negative_controls_rejected": failures, "analytic_input_cancellation_only": True,
        "optical_forward_executed": False, "training_executed": False, "gpu_requested": False,
        "physical_calibration_verified": False,
        "blend_sha256": hashlib.sha256(blend.read_bytes()).hexdigest()}
    (out / "checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
