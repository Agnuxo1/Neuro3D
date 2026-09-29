"""EXP-001 scene probe inside Blender; never renders or calls a GPU API.

Only run through the guarded run_mz_exp001.py after explicit authorization.
Modes: init creates A; edit loads A and saves a variant; verify reopens it.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / "Blender" / "core"),
                str(REPO / "Blender" / "addon" / "neuro3d"), str(Path(__file__).parent)]
from mz_scene_adapter import create_mz_circuit, trace_mz_circuit
from mz_exp001_plan import controls

OPTICAL_KEYS = {
    "mz_source": ("power", "rgb", "frequency", "phase", "propagation_speed",
                  "absorption_per_unit", "beam_waist", "mutual_coherence"),
    "mz_bs1": ("radius", "transmission"),
    "mz_bs2": ("radius", "transmission", "overlap_tolerance", "direction_tolerance"),
    "mz_mirror1": ("radius", "reflectance_rgb", "phase_shift"),
    "mz_mirror2": ("radius", "reflectance_rgb", "phase_shift"),
    "mz_detector_a": ("radius", "responsivity_rgb", "activation_threshold", "response_gain"),
    "mz_detector_b": ("radius", "responsivity_rgb", "activation_threshold", "response_gain"),
}


def _roles():
    scene = bpy.context.scene
    collection = bpy.data.collections.get(scene.get("neuro3d_active_mz", ""))
    if collection is None or len(collection.objects) != 8:
        raise AssertionError("Expected seven MZ optics plus combiner parent")
    roles = {obj.get("neuro3d_role"): obj for obj in collection.objects}
    if len(roles) != 8:
        raise AssertionError("MZ roles are missing or duplicated")
    return roles


def _capture(roles, result):
    bpy.context.view_layer.update()
    objects = {}
    for role, obj in sorted(roles.items()):
        objects[role] = {
            "matrix_world": [float(v) for row in obj.matrix_world for v in row],
            "location": [float(v) for v in obj.location],
            "parent": obj.parent.get("neuro3d_role") if obj.parent else None,
        }
    optics = {}
    for role, keys in OPTICAL_KEYS.items():
        obj = roles[role]
        optics[role] = {}
        for key in keys:
            raw = obj[key]
            optics[role][key] = (float(raw) if isinstance(raw, (int, float))
                                 else [float(value) for value in raw])
    return {
        "objects": objects,
        "optics": optics,
        "result": {
            "status": result.status,
            "optical_a": [float(v) for v in result.optical_a],
            "optical_b": [float(v) for v in result.optical_b],
            "input_rgb": [float(v) for v in result.input_rgb],
            "absorption_rgb": [float(v) for v in result.absorption_rgb],
            "mirror_loss_rgb": [float(v) for v in result.mirror_loss_rgb],
            "escape_rgb": [float(v) for v in result.escape_rgb],
            "unresolved_rgb": [float(v) for v in result.unresolved_rgb],
            "residual_rgb": [float(v) for v in result.residual_rgb],
            "mode_overlap": result.mode_overlap,
            "effective_coherence": result.effective_coherence,
            "transverse_separation": result.transverse_separation,
            "signal_a": result.signal_a,
            "signal_b": result.signal_b,
            "activation_a": result.activation_a,
            "activation_b": result.activation_b,
        },
        "scene_status": bpy.context.scene.get("neuro3d_mz_status"),
    }


def _edit(case, roles):
    group = roles["mz_combiner_group"]
    m1 = roles["mz_mirror1"]
    m2 = roles["mz_mirror2"]
    for index in range(3):
        group.location[index] += case.group_delta[index]
        m1.location[index] += case.mirror1_delta[index]
    m2["phase_shift"] = case.mirror2_phase
    roles["mz_source"]["mutual_coherence"] = case.mutual_coherence
    if case.mirror2_turn_deg:
        bpy.context.view_layer.update()
        old_position = m2.matrix_world.translation.copy()
        old_normal = m2.matrix_world.to_quaternion() @ Vector((0.0, 0.0, 1.0))
        turn = Matrix.Rotation(math.radians(case.mirror2_turn_deg), 3, "Z")
        new_normal = turn @ old_normal
        m2.rotation_euler = new_normal.to_track_quat("Z", "Y").to_euler()
        bpy.context.view_layer.update()
        actual_normal = m2.matrix_world.to_quaternion() @ Vector((0.0, 0.0, 1.0))
        if (m2.matrix_world.translation - old_position).length > 1e-6:
            raise AssertionError("D moved M2 instead of rotating in place")
        if (actual_normal - new_normal).length > 1e-6:
            raise AssertionError("D did not rotate the normal about world Z")
        if old_normal.cross(actual_normal).z <= 0:
            raise AssertionError("D rotation has the wrong sign")


def _close(a, b, tolerance):
    if not math.isfinite(float(a)) or not math.isfinite(float(b)) or abs(a - b) > tolerance:
        raise AssertionError(f"Readback mismatch: {a} != {b} (tol={tolerance})")


def _compare_vector(before, after, length, tolerance, name):
    if len(before) != length or len(after) != length:
        raise AssertionError(f"Readback vector length mismatch: {name}")
    for left, right in zip(before, after):
        _close(left, right, tolerance)


def _compare(saved, current):
    if saved["objects"].keys() != current["objects"].keys():
        raise AssertionError("Scene roles changed on reopening")
    for role in saved["objects"]:
        before, after = saved["objects"][role], current["objects"][role]
        if before["parent"] != after["parent"]:
            raise AssertionError(f"Parent changed for {role}")
        for key in ("matrix_world", "location"):
            _compare_vector(before[key], after[key],
                            16 if key == "matrix_world" else 3, 1e-6, f"{role}.{key}")
    for role, properties in saved["optics"].items():
        for key, before in properties.items():
            after = current["optics"][role][key]
            if isinstance(before, list):
                if not isinstance(after, list) or len(before) != len(after):
                    raise AssertionError(f"Optical property length changed: {role}.{key}")
                for left, right in zip(before, after):
                    _close(left, right, 1e-6)
            else:
                _close(before, after, 1e-6)
    if saved["result"]["status"] != current["result"]["status"]:
        raise AssertionError("Status changed on reopening")
    if saved["scene_status"] != current["scene_status"]:
        raise AssertionError("Stored scene status changed on reopening")
    for key in ("optical_a", "optical_b", "input_rgb", "absorption_rgb",
                "mirror_loss_rgb", "escape_rgb", "unresolved_rgb", "residual_rgb"):
        _compare_vector(saved["result"][key], current["result"][key], 3, 1e-12, key)
    for key in ("signal_a", "signal_b", "activation_a", "activation_b",
                "mode_overlap", "effective_coherence", "transverse_separation"):
        before, after = saved["result"][key], current["result"][key]
        if before is None or after is None:
            if before is not None or after is not None:
                raise AssertionError(f"Readback optional value changed: {key}")
        else:
            _close(before, after, 1e-12)


def _accept(case, record):
    result = record["result"]
    if result["status"] != case.expected_status:
        raise AssertionError(f"{case.name}: status {result['status']} != {case.expected_status}")
    for key, target in (("optical_a", case.expected_a), ("optical_b", case.expected_b),
                        ("escape_rgb", case.expected_escape), ("unresolved_rgb", 0.0)):
        value = sum(result[key])
        tolerance = 1e-9 if key in ("optical_a", "optical_b", "escape_rgb") else 1e-12
        _close(value, target, tolerance)
    if max(abs(v) for v in result["residual_rgb"]) > 1e-12:
        raise AssertionError(f"{case.name}: energy ledger did not close")
    if case.expected_status == "ok":
        if result["mode_overlap"] is None or result["mode_overlap"] < 1 - 1e-9:
            raise AssertionError(f"{case.name}: invalid mode overlap")
        _close(result["effective_coherence"], case.mutual_coherence, 1e-9)


def main():
    if not bpy.app.background:
        raise AssertionError("EXP-001 must run in background Blender")
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) != 3 or args[0] not in {"init", "edit", "verify"}:
        raise SystemExit("Expected -- init|edit|verify CASE output.blend")
    mode, name, output = args[0], args[1], Path(args[2])
    case = next((c for c in controls() if c.name == name), None)
    if case is None or (mode == "init") != (name == "A"):
        if mode != "verify" or case is None:
            raise ValueError("Invalid EXP-001 phase or control")
    if mode == "init":
        create_mz_circuit(bpy, bpy.context.scene, layout="nonrect60")
    roles = _roles()
    if mode == "edit":
        _edit(case, roles)
    if mode in {"init", "edit"}:
        if output.exists() or output.with_suffix(".json").exists():
            raise FileExistsError("EXP-001 refuses to overwrite an existing artifact")
        result = trace_mz_circuit(bpy, bpy.context.scene)
        record = _capture(roles, result)
        bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False, compress=False)
        output.with_suffix(".json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    else:
        saved = json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))
        # Capture stored detector/scene outputs before retracing, then compare.
        stored_a = tuple(float(v) for v in roles["mz_detector_a"]["received_optical_rgb"])
        stored_b = tuple(float(v) for v in roles["mz_detector_b"]["received_optical_rgb"])
        stored_status = bpy.context.scene.get("neuro3d_mz_status")
        result = trace_mz_circuit(bpy, bpy.context.scene)
        record = _capture(roles, result)
        readback_path = output.with_suffix(".readback.json")
        if readback_path.exists():
            raise FileExistsError("EXP-001 refuses to overwrite a readback record")
        readback_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        if stored_status != saved["scene_status"]:
            raise AssertionError("Persisted scene status differs from saved result")
        _compare_vector(stored_a, saved["result"]["optical_a"], 3, 1e-12, "stored_a")
        _compare_vector(stored_b, saved["result"]["optical_b"], 3, 1e-12, "stored_b")
        _compare(saved, record)
        _accept(case, record)
    print("NEURO3D_MZ_EXP001 " + json.dumps({
        "phase": mode, "control": name, "status": result.status,
        "a": sum(result.optical_a), "b": sum(result.optical_b),
        "escape": sum(result.escape_rgb), "artifact": str(output),
    }), flush=True)


if __name__ == "__main__":
    main()
