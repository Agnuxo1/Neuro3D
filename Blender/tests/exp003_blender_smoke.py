"""Bounded, no-render Blender CPU smoke for the frozen EXP-003 base scene.

Run only in a dedicated background Blender process with ``-t 1``. This
checks scene construction and ray_cast; it does not save or render a scene.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


def main(fixture_path):
    import bpy
    from mathutils import Vector

    sys.path.insert(0, str(Path(__file__).resolve().parent))

    from exp003_blender_build import build_scene_disks
    from exp003_fixture_guard import validate_baseline_paths, validate_observed_disks
    from exp003_ray_paths import trace_paths
    from exp003_scene_cast import make_scene_cast, observe_scene_disks

    # The caller launches a separate background process; no user scene is read.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    fixture, digest, _objects = build_scene_disks(scene, fixture_path)
    bpy.context.view_layer.update()
    observed = observe_scene_disks(scene)
    geometry_gate = validate_observed_disks(fixture, observed)
    cast = make_scene_cast(scene, bpy.context.evaluated_depsgraph_get(), Vector)
    expected = {arm: order[1:] for arm, order in fixture["hit_order"].items()}
    paths = trace_paths(cast, fixture["source"]["position"],
                        fixture["source"]["direction"], expected_routes=expected)
    validate_baseline_paths(paths)
    print("EXP003_SMOKE " + json.dumps({
        "fixture_sha256": digest,
        "blender_version": bpy.app.version_string,
        "normal_signs": geometry_gate["normal_signs"],
        "paths": {arm: {"status": path["status"], "length": path["length"],
                         "hits": [item["object"] for item in path["hits"]]}
                  for arm, path in paths.items()},
    }, sort_keys=True))


if __name__ == "__main__":
    if "--" not in sys.argv or len(sys.argv[sys.argv.index("--") + 1:]) != 1:
        raise SystemExit("Usage: blender -b -t 1 --python exp003_blender_smoke.py -- fixture.json")
    main(Path(sys.argv[sys.argv.index("--") + 1]))
