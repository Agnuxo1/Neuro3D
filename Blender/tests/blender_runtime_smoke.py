"""Tiny real-Blender optical circuit smoke check; no rendering or GPU calls.

Called by run_blender_smoke.py with ``-- create|reopen <blend-path>``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import bpy

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "Blender" / "addon"))
from neuro3d.optical_scene import create_circuit, trace_circuit  # noqa: E402


def _assert_close(a: float, b: float, tolerance: float = 1e-8) -> None:
    if not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"Optical state changed unexpectedly: {a} != {b}")


def create(blend_path: Path) -> None:
    if not bpy.app.background:
        raise AssertionError("Smoke check requires background Blender")
    collection = create_circuit(bpy, bpy.context.scene)
    if len(collection.objects) != 3:
        raise AssertionError("The circuit must contain exactly three scene objects")
    initial = trace_circuit(bpy, bpy.context.scene)
    if not initial.hit or initial.intensity <= 0.0 or initial.activation <= 0.0:
        raise AssertionError(f"The aligned optical circuit did not activate: {initial.reason}")

    receiver = next(obj for obj in collection.objects if obj.get("neuro3d_role") == "receiver")
    receiver.location.z += 1.0
    broken = trace_circuit(bpy, bpy.context.scene)
    if broken.hit or broken.intensity != 0.0 or broken.activation != 0.0:
        raise AssertionError("Moving the receiver did not break the optical path")
    receiver.location.z -= 1.0
    restored = trace_circuit(bpy, bpy.context.scene)
    _assert_close(initial.intensity, restored.intensity)
    _assert_close(initial.phase, restored.phase)

    mirror = next(obj for obj in collection.objects if obj.get("neuro3d_role") == "reflector")
    original_reflectance = list(mirror["reflectance_rgb"])
    mirror["reflectance_rgb"] = [0.0, 0.0, 1.0]
    filtered = trace_circuit(bpy, bpy.context.scene)
    if not filtered.hit or filtered.color_power[0] != 0.0 or filtered.color_power[1] != 0.0 or filtered.color_power[2] <= 0.0:
        raise AssertionError("The Blender reflector did not filter RGB power")
    mirror["reflectance_rgb"] = original_reflectance
    restored = trace_circuit(bpy, bpy.context.scene)
    _assert_close(initial.intensity, restored.intensity)

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False, compress=False)
    print("NEURO3D_SMOKE " + json.dumps({
        "phase": "create", "objects": len(collection.objects),
        "intensity": restored.intensity, "activation": restored.activation,
        "moved_receiver_miss": not broken.hit, "blue_filter_passed": True,
    }), flush=True)


def reopen(blend_path: Path) -> None:
    if not blend_path.is_file():
        raise AssertionError("The saved .blend is missing")
    scene = bpy.context.scene
    name = scene.get("neuro3d_active_circuit")
    collection = bpy.data.collections.get(name) if name else None
    if collection is None or len(collection.objects) != 3:
        raise AssertionError("The circuit did not survive reopening")
    receiver = next(obj for obj in collection.objects if obj.get("neuro3d_role") == "receiver")
    saved_intensity = float(receiver["received_intensity"])
    saved_phase = float(receiver["received_phase"])
    saved_rgb = tuple(float(v) for v in receiver["received_rgb_power"])
    saved_activation = float(receiver["activation"])
    saved_frequency = float(receiver["received_frequency"])
    repeated = trace_circuit(bpy, scene)
    _assert_close(repeated.intensity, saved_intensity)
    _assert_close(repeated.phase, saved_phase)
    _assert_close(repeated.activation, saved_activation)
    _assert_close(repeated.frequency, saved_frequency)
    for actual, expected in zip(repeated.color_power, saved_rgb):
        _assert_close(actual, expected)

    emitter = next(obj for obj in collection.objects if obj.get("neuro3d_role") == "emitter")
    original_frequency = float(emitter["frequency"])
    emitter["frequency"] = original_frequency + 0.25
    retuned = trace_circuit(bpy, scene)
    if math.isclose(retuned.phase, repeated.phase, abs_tol=1e-6):
        raise AssertionError("Changing the Blender emitter frequency did not change received phase")
    emitter["frequency"] = original_frequency

    mirror = next(obj for obj in collection.objects if obj.get("neuro3d_role") == "reflector")
    from mathutils import Vector

    mirror.rotation_euler = Vector((1.0, 0.0, 0.0)).to_track_quat("Z", "Y").to_euler()
    broken = trace_circuit(bpy, scene)
    if broken.hit or broken.intensity != 0.0:
        raise AssertionError("Turning the reflector did not break the optical path")
    print("NEURO3D_SMOKE " + json.dumps({
        "phase": "reopen", "objects": len(collection.objects),
        "intensity": repeated.intensity, "saved_state_matches": True,
        "turned_mirror_miss": not broken.hit, "frequency_changes_phase": True,
    }), flush=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) != 2 or args[0] not in {"create", "reopen"}:
        raise SystemExit("Expected -- create|reopen <blend-path>")
    mode, target = args[0], Path(args[1])
    if mode == "create":
        create(target)
    else:
        reopen(target)
