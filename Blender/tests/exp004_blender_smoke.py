"""Headless K=2 candidate geometry smoke; no field propagation or render.

Usage inside Blender: --python exp004_blender_smoke.py -- fixture.json RAW_SHA256
The fixture remains external/unfrozen; this smoke is not EXP-004 acceptance.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from exp004_scene_bridge import build_lattice_disks, load_lattice_fixture
from exp003_scene_cast import observe_scene_disks


def main(path, digest):
    fixture, actual_digest = load_lattice_fixture(path, digest)
    if fixture["K"] != 2:
        raise ValueError("Bounded smoke is only for K=2")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    built = build_lattice_disks(scene, fixture)
    bpy.context.view_layer.update()
    observed = observe_scene_disks(scene)
    if set(observed) != set(built):
        raise AssertionError("Readback role mismatch")
    for spec in fixture["disks"]:
        role = spec["id"]
        got = observed[role]
        if Vector(got["position"]).distance(Vector(spec["p"])) > 1e-6:
            raise AssertionError(f"Position differs: {role}")
        if abs(Vector(got["normal"]).dot(Vector(spec["n"]))) < 1 - 1e-6:
            raise AssertionError(f"Normal differs: {role}")
        if got["faces"] != 1 or got["vertices"] < 32 or got["modifiers"]:
            raise AssertionError(f"Mesh topology differs: {role}")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    first_hits = {}
    for source in fixture["sources"]:
        hit, _point, _normal, _face, obj, _matrix = scene.ray_cast(
            depsgraph, Vector(source["p"]), Vector(source["d"]))
        expected = (f"c0{source['id'][1:]}.bs1" if source["id"].startswith("r")
                    else f"c{source['id'][1:]}0.bs1")
        role = obj.get("neuro3d_role") if hit else None
        if role != expected:
            raise AssertionError(f"First hit for {source['id']}: {role} != {expected}")
        first_hits[source["id"]] = role
    print("EXP004_BUILDER_SMOKE " + json.dumps({"K": 2, "disks": len(observed),
        "fixture_raw_sha256": actual_digest, "first_hits": first_hits}, sort_keys=True))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) != 2:
        raise SystemExit("Expected fixture path and raw SHA-256")
    main(*args)
