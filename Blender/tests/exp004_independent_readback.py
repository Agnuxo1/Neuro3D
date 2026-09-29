"""Read-only geometry audit of four EXP-004 candidate Blender files.

Run inside Blender headless with -- fixture.json run_dir. It never saves.
This is independent of Claude's lattice builder/trace code but not an
independent ray-tree oracle or a scientific acceptance of EXP-004.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_close(actual, expected, tolerance, label):
    if not all(math.isfinite(float(x)) for x in actual):
        raise AssertionError(f"Non-finite {label}")
    error = (Vector(actual) - Vector(expected)).length
    if error > tolerance:
        raise AssertionError(f"{label}: error {error} > {tolerance}")
    return error


def main(fixture_path, run_dir):
    fixture_path, run_dir = Path(fixture_path), Path(run_dir)
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture_sha = sha256(fixture_path)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    if summary["fixture_sha256"] != fixture_sha:
        raise AssertionError("Raw fixture digest mismatch")
    iv = fixture["interventions"]
    affected = "c%d%d" % tuple(iv["cell"])
    audited = {}
    for treatment in ("base", "delta", "sham", "ablation"):
        path = run_dir / f"{treatment}.blend"
        digest = sha256(path)
        if digest != summary["treatments"][treatment]["blend_sha256"]:
            raise AssertionError(f"Blend digest mismatch: {treatment}")
        bpy.ops.wm.open_mainfile(filepath=str(path))
        scene = bpy.context.scene
        bpy.context.view_layer.update()
        actual_sources = json.loads(scene["sources"])
        if actual_sources != fixture["sources"]:
            raise AssertionError(f"Sources differ: {treatment}")
        expected = {spec["id"]: spec for spec in fixture["disks"]}
        if treatment == "ablation":
            del expected[f"{affected}.{iv['ablate']}"]
        meshes = {obj.name: obj for obj in scene.objects if obj.type == "MESH"}
        if set(meshes) != set(expected):
            raise AssertionError(f"Roles differ: {treatment}")
        max_position = max_normal = max_radius = 0.0
        for role, spec in expected.items():
            obj = meshes[role]
            if (obj.get("kind") != spec["kind"] or obj.modifiers or obj.parent
                    or require_close(obj.scale, (1., 1., 1.), 1e-6,
                                     f"{role} scale") > 1e-6):
                raise AssertionError(f"Kind/modifier/parent differs: {role}")
            if len(obj.data.vertices) != 64 or len(obj.data.polygons) != 1:
                raise AssertionError(f"Topology differs: {role}")
            wanted = list(spec["p"])
            if role in (f"{affected}.r1", f"{affected}.r2"):
                if treatment == "delta":
                    wanted[0] += iv["delta_x"]
                elif treatment == "sham":
                    wanted[2] += iv["sham_z"]
            max_position = max(max_position, require_close(
                obj.matrix_world.translation, wanted, 1e-5, f"{role} position"))
            matrix = obj.matrix_world.to_3x3()
            normal = (matrix.inverted().transposed() @ obj.data.polygons[0].normal).normalized()
            actual_normal = tuple(normal)
            expected_normal = tuple(spec["n"])
            max_normal = max(max_normal,
                             (Vector(actual_normal) - Vector(expected_normal)).length)
            if max_normal > 1e-6:
                raise AssertionError(f"Normal differs: {role}")
            max_radius = max(max_radius, max(
                abs(math.hypot(v.co.x, v.co.y) - spec["r"])
                for v in obj.data.vertices))
            if max_radius > 1e-6:
                raise AssertionError(f"Radius differs: {role}")
            if any(abs(v.co.z) > 1e-6 for v in obj.data.vertices):
                raise AssertionError(f"Disk is not planar: {role}")
        audited[treatment] = {"sha256": digest, "meshes": len(meshes),
                              "max_position_error": max_position,
                              "max_normal_error": max_normal,
                              "max_radius_error": max_radius}
    print("EXP004_INDEPENDENT_READBACK " + json.dumps({
        "fixture_raw_sha256": fixture_sha, "treatments": audited}, sort_keys=True))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) != 2:
        raise SystemExit("Expected fixture path and run directory")
    main(*args)
