"""EXP-003 bounded Blender CPU runner: edit, save, reopen, then ray-cast.

No render/GPU call. Run only in a dedicated background Blender process with
``--python-exit-code 1 -t 1`` and check the ``EXP003_RESULT`` marker.
Outputs .blend cases and a small JSON evidence file under a unique run dir.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from uuid import uuid4


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_in_dir(fixture_path, run_dir):
    import bpy
    from mathutils import Vector

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from exp003_blender_build import build_scene_disks
    from exp003_fixture_guard import validate_observed_disks, validate_baseline_paths
    from exp003_interventions import ablate_existing, place_delay_pair
    from exp003_optics_from_paths import combine_measured_paths
    from exp003_ray_paths import trace_paths
    from exp003_scene_cast import make_scene_cast, observe_scene_disks

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    fixture, fixture_hash, _ = build_scene_disks(scene, fixture_path)
    bpy.context.view_layer.update()
    validate_observed_disks(fixture, observe_scene_disks(scene))
    base_file = run_dir / "base.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(base_file))
    base_hash = digest(base_file)
    expected_routes = {arm: route[1:] for arm, route in fixture["hit_order"].items()}

    def read_scene(delay_d=0.0, sham_z=0.0, removed=None):
        scene = bpy.context.scene
        bpy.context.view_layer.update()
        observed = observe_scene_disks(scene)
        gate = validate_observed_disks(fixture, observed, delay_d, sham_z, removed)
        roles = set(observed)
        matrices = {role: tuple(tuple(row) for row in obj.matrix_world)
                    for obj in scene.objects if obj.type == "MESH"
                    for role in (obj.get("neuro3d_role"),) if role in roles}
        cast = make_scene_cast(scene, bpy.context.evaluated_depsgraph_get(), Vector)
        paths = trace_paths(cast, fixture["source"]["position"],
                            fixture["source"]["direction"], expected_routes)
        optics = combine_measured_paths(paths, fixture["lambda"],
                                        fixture["source"]["power"])
        return {"paths": paths, "optics": optics, "matrices": matrices,
                "normal_signs": gate["normal_signs"]}

    bpy.ops.wm.open_mainfile(filepath=str(base_file), load_ui=False)
    if Path(bpy.data.filepath).resolve() != base_file.resolve() or digest(base_file) != base_hash:
        raise ValueError("Base scene reopen mismatch")
    base = read_scene()
    validate_baseline_paths(base["paths"])
    cases = [(f"d_{i}", float(d), 0.0, None)
             for i, d in enumerate(fixture["interventions"]["delay_d"])]
    cases += [("sham", 0.0, float(fixture["interventions"]["sham_z"]), None),
              ("ablation", 0.0, 0.0, fixture["interventions"]["ablate"])]
    results = {}

    for name, delay_d, sham_z, removed in cases:
        progress_file = run_dir / "progress.json"
        progress_file.write_text(json.dumps({"current_case": name,
                                             "stage": "opening_base",
                                             "completed": results}, indent=2), encoding="utf-8")
        bpy.ops.wm.open_mainfile(filepath=str(base_file), load_ui=False)
        if Path(bpy.data.filepath).resolve() != base_file.resolve():
            raise ValueError("Did not reopen frozen base")
        scene = bpy.context.scene
        objects = {obj.get("neuro3d_role"): obj for obj in scene.objects
                   if obj.type == "MESH" and obj.get("neuro3d_role")}
        place_delay_pair(objects, fixture, delay_d, sham_z)
        if removed:
            ablated = ablate_existing(scene, objects, removed)
            if len(ablated.users_collection) != 0 or ablated.name in scene.objects:
                raise ValueError("Ablated object still in scene/depsgraph")
        before = read_scene(delay_d, sham_z, removed)
        progress_file.write_text(json.dumps({"current_case": name,
                                             "stage": "pre_save_traced",
                                             "before": before,
                                             "completed": results}, indent=2), encoding="utf-8")
        case_file = run_dir / f"{name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(case_file))
        saved_hash = digest(case_file)
        bpy.ops.wm.open_mainfile(filepath=str(case_file), load_ui=False)
        if Path(bpy.data.filepath).resolve() != case_file.resolve() or digest(case_file) != saved_hash:
            raise ValueError(f"Treatment reopen mismatch: {name}")
        after = read_scene(delay_d, sham_z, removed)
        progress_file.write_text(json.dumps({"current_case": name,
                                             "stage": "post_reopen_traced",
                                             "before": before, "after": after,
                                             "completed": results}, indent=2), encoding="utf-8")
        max_matrix_error = max((abs(x-y)
                                for role in before["matrices"]
                                for row_a, row_b in zip(before["matrices"][role],
                                                         after["matrices"][role])
                                for x, y in zip(row_a, row_b)), default=0.0)
        if max_matrix_error > 1e-6:
            raise ValueError(f"World matrix changed on reopen: {name}")
        max_port_reopen_error = max(abs(before["optics"][port] - after["optics"][port])
                                    for port in ("P_A", "P_B"))
        if max_port_reopen_error > 1e-3:
            raise ValueError(f"Port power changed on reopen: {name}")
        paths, optics = after["paths"], after["optics"]
        if optics["balance_error"] > 1e-6 or optics["unresolved"] > 1e-9:
            raise ValueError(f"Energy balance failed: {name}")
        if removed:
            if paths["arm1"]["status"] != "lost" or paths["arm2"]["status"] != "reached_bs2":
                raise ValueError("Ablation did not remove only arm 1")
            if any(abs(optics[port] - .25) > 1e-3 for port in ("P_A", "P_B")):
                raise ValueError("Ablation ports differ from half-arm split")
            if abs(optics["escape"] - .5) > 1e-6:
                raise ValueError("Ablation escape ledger differs")
        else:
            if any(paths[arm]["status"] != "reached_bs2" for arm in ("arm1", "arm2")):
                raise ValueError(f"Expected path lost: {name}")
            if abs(paths["arm1"]["length"] - (5.0 + 2 * delay_d)) > 1e-4:
                raise ValueError(f"Absolute arm 1 length failed: {name}")
            if abs(paths["arm2"]["length"] - 3.0) > 1e-4:
                raise ValueError(f"Absolute arm 2 length failed: {name}")
            delta = (paths["arm1"]["length"] - paths["arm2"]["length"]
                     - base["paths"]["arm1"]["length"] + base["paths"]["arm2"]["length"])
            if abs(delta - 2 * delay_d) > 1e-4:
                raise ValueError(f"Relative delay failed: {name}")
            if abs(2 * math.pi * (delta - 2 * delay_d) / fixture["lambda"]) > 1e-2:
                raise ValueError(f"Phase delay failed: {name}")
            expected_a = math.sin(math.pi * 2 * delay_d / fixture["lambda"]) ** 2
            if abs(optics["P_A"] - expected_a) > 1e-3:
                raise ValueError(f"Port A contrast failed: {name}")
            if sham_z and abs(optics["P_A"] - base["optics"]["P_A"]) > 1e-3:
                raise ValueError("Sham altered port A")
            if sham_z and any(abs(paths[arm]["length"] - base["paths"][arm]["length"]) > 1e-6
                              for arm in ("arm1", "arm2")):
                raise ValueError("Sham altered measured path length")
        results[name] = {"file": str(case_file), "sha256": saved_hash,
                         "max_matrix_reopen_error": max_matrix_error,
                         "max_port_reopen_error": max_port_reopen_error,
                         "paths": paths, "optics": optics}

    report = {"fixture_sha256": fixture_hash, "base_sha256": base_hash,
              "blender_version": bpy.app.version_string, "base": base,
              "cases": results, "status": "PASS"}
    report_file = run_dir / "result.json"
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("EXP003_RESULT " + json.dumps({"status": "PASS", "run_dir": str(run_dir),
                                         "case_count": len(results)}, sort_keys=True))


def main(fixture_path, output_root):
    run_dir = Path(output_root) / ("run-" + uuid4().hex[:12])
    run_dir.mkdir(parents=True, exist_ok=False)
    try:
        return run_in_dir(fixture_path, run_dir)
    except Exception as exc:
        failure = {"status": "FAIL", "error_type": type(exc).__name__,
                   "message": str(exc), "run_dir": str(run_dir),
                   "progress_file": str(run_dir / "progress.json")}
        (run_dir / "failure.json").write_text(json.dumps(failure, indent=2), encoding="utf-8")
        print("EXP003_FAILURE " + json.dumps(failure, sort_keys=True))
        raise


if __name__ == "__main__":
    if "--" not in sys.argv or len(sys.argv[sys.argv.index("--") + 1:]) != 2:
        raise SystemExit("Usage: blender -b -t 1 --python-exit-code 1 --python exp003_blender_run.py -- fixture.json output_root")
    main(*(Path(arg) for arg in sys.argv[sys.argv.index("--") + 1:]))
