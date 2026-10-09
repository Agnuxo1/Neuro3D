"""Prepare point-4 geometry/query fixtures in a bounded background CPU child.

Copies and reopens immutable K3/K4 inputs and creates one explicit numerical
control scene. No GPU import, dispatch, ray tracing, training or rendering.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "Blender" / "benchmarks" / "capacity_audit"))
from exp005_scene_readback import export_snapshot
from scene_hilo_transport_v1 import build_packet, admit_for_upload

FROZEN_MANIFEST_SHA256 = "c101286137e59ceb47918e0913f112c3ca1a0e9733610b662be7d2d63dd961f4"
SCHEMA = "neuro3d.scene_hilo.native_job.v1"
BOUNDS_PROPERTY = "neuro3d_direction_bounds"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def read_scene(bpy):
    scene = bpy.context.scene
    for obj in scene.objects:
        obj.update_tag()
    bpy.context.view_layer.update()
    snapshot = export_snapshot(
        scene, depsgraph=bpy.context.evaluated_depsgraph_get(),
        view_layer=bpy.context.view_layer)
    if not snapshot.get("evaluated_optics_checked"):
        raise ValueError("evaluated geometry required")
    bounds_text = scene.get(BOUNDS_PROPERTY)
    if bounds_text is not None:
        if not isinstance(bounds_text, str):
            raise ValueError("direction bounds must be an explicit JSON string")
        snapshot[BOUNDS_PROPERTY] = json.loads(bounds_text)
    return snapshot, bounds_text


def provenance(bpy, blend, input_class, bounds_text):
    result = {
        "input_class": input_class,
        "blend_sha256": sha(blend),
        "blender_version": bpy.app.version_string,
        "scene_name": bpy.context.scene.name,
        "view_layer_name": bpy.context.view_layer.name,
        "blend_path": str(blend.resolve()),
    }
    if bounds_text is not None:
        result["direction_bounds_property"] = BOUNDS_PROPERTY
        result["direction_bounds_json"] = bounds_text
    return result


def controlled_scene(bpy):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Neuro3D_P4_Controlled_Numerics"
    scene["optical_contract"] = "exp005-readback-v2"
    scene["lambda_BU"] = 0.125
    scene["neuro3d_input_scope"] = (
        "Declared numerical test scene; observed Blender mesh coordinates, "
        "binary64 JSON sources and declared direction boxes. "
        "No optical propagation or recovered mesh precision is claimed.")
    names = ["panel_x1", "panel_x2"]
    scene["optical_object_ids"] = json.dumps(names)
    faces = [(0, 1, 2), (0, 2, 3)]
    for name, x in zip(names, (1.0, 2.0)):
        vertices = [(x, -0.5, -0.5), (x, 0.5, -0.5),
                    (x, 0.5, 0.5), (x, -0.5, 0.5)]
        mesh = bpy.data.meshes.new(name + "_mesh")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        obj["kind"] = "mirror"
        # Intentionally retain a non-hi/lo32-exact material parameter as
        # metadata. The geometry/query profile must never round it to PASS.
        obj["phase_rad"] = 0.2
    direction_x = 1.0 + 2.0 ** -30
    sources = [
        {"id": "tiny", "position_BU": [2.0 ** -60, 0.0, 0.0],
         "direction": [direction_x, 0.0, 0.0], "field_reim": [1.0, 0.0]},
        {"id": "low", "position_BU": [1.0 + 2.0 ** -30,
                                      2.0 ** -40, -(2.0 ** -45)],
         "direction": [0.0, 1.0, 0.0], "field_reim": [0.5, 0.25]},
    ]
    bounds = {
        "tiny": [[direction_x - 2.0 ** -50, direction_x + 2.0 ** -50],
                 [0.0, 0.0], [0.0, 0.0]],
        "low": [[0.0, 0.0], [2.0 ** -60 + 2.0 ** -100, 1.0 + 2.0 ** -30], [0.0, 0.0]],
    }
    scene["optical_sources"] = json.dumps(sources, allow_nan=False)
    scene[BOUNDS_PROPERTY] = json.dumps(bounds, allow_nan=False)
    return scene


def retain_case(bpy, folder, blend, case_id, input_class):
    snapshot, bounds_text = read_scene(bpy)
    start = time.perf_counter()
    packet = build_packet(
        snapshot, provenance=provenance(bpy, blend, input_class, bounds_text))
    wire = admit_for_upload(packet, trusted_manifest=packet["manifest"])
    elapsed = time.perf_counter() - start
    packet_path = folder / (case_id + ".packet.json")
    snapshot_path = folder / (case_id + ".snapshot.json")
    wire_path = folder / (case_id + ".wire.bin")
    write_new(packet_path, packet)
    write_new(snapshot_path, snapshot)
    with wire_path.open("xb") as stream:
        stream.write(wire)
    return {
        "case_id": case_id,
        "input_class": input_class,
        "blend_path": str(blend.resolve()),
        "blend_sha256": sha(blend),
        "packet_path": str(packet_path.resolve()),
        "packet_sha256": sha(packet_path),
    }, {
        "case_id": case_id,
        "snapshot_path": str(snapshot_path.resolve()),
        "snapshot_sha256": sha(snapshot_path),
        "wire_path": str(wire_path.resolve()),
        "wire_sha256": sha(wire_path),
        "wire_bytes": len(wire),
        "build_and_admission_seconds": elapsed,
        "object_count": len(snapshot["objects"]),
        "source_count": len(snapshot["sources"]),
        "face_count": sum(len(obj["faces"]) for obj in snapshot["objects"].values()),
        "evaluated_optics_checked": snapshot["evaluated_optics_checked"],
        "direction_bounds_property": BOUNDS_PROPERTY if bounds_text is not None else None,
        "material_parameters_preserved_without_hi_lo32_conversion": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-evidence", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if args.out.exists():
        raise ValueError("fresh output directory required")
    frozen = args.frozen_evidence.resolve()
    old_manifest = frozen.with_suffix(".json")
    if sha(old_manifest) != FROZEN_MANIFEST_SHA256:
        raise ValueError("frozen original scene manifest changed")
    old = json.loads(old_manifest.read_text(encoding="utf-8"))
    hashes = {row["file"]: row["sha256"] for row in old["scenes"]}
    if len(hashes) != 12:
        raise ValueError("twelve-scene frozen provenance required")
    for cells in (3, 4):
        name = f"K{cells}_base.blend"
        if sha(frozen / name) != hashes[name]:
            raise ValueError("original retained scene changed: " + name)
    import bpy
    folder = args.out.resolve()
    folder.mkdir()
    dependencies = [
        Path(__file__).resolve(),
        ROOT / "Blender" / "tests" / "exp005_scene_readback.py",
        ROOT / "Blender" / "tests" / "exp005_scene_properties.py",
        ROOT / "Blender" / "benchmarks" / "capacity_audit" / "scene_hilo_transport_v1.py",
        ROOT / "Blender" / "benchmarks" / "capacity_audit" / "oblique_exact_scalar_hilo32_CPU_v1.py",
    ]
    code = {str(path.relative_to(ROOT)): sha(path) for path in dependencies}
    report = {
        "schema": "neuro3d.scene_hilo.prepare.v1",
        "status": "FAIL", "verification_passed": False,
        "scope": "CPU saved/reopened scene extraction and packet admission only",
        "native_gpu_executed": False,
        "blender_version": bpy.app.version_string,
        "frozen_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "code_sha256": code, "cases": [],
    }
    start = time.perf_counter()
    cases = []
    try:
        for cells in (3, 4):
            name = f"K{cells}_base.blend"
            blend = folder / name
            shutil.copyfile(frozen / name, blend)
            bpy.ops.wm.open_mainfile(filepath=str(blend))
            actual, bounds = read_scene(bpy)
            retained_path = frozen / f"K{cells}_base_snapshot.json"
            retained = json.loads(retained_path.read_text(encoding="utf-8"))
            if actual != retained or bounds is not None:
                raise ValueError("copied baseline differs from frozen evaluated snapshot")
            case_id = f"k{cells}_baseline"
            case, evidence = retain_case(bpy, folder, blend, case_id,
                                         "real_reopened_baseline")
            evidence["retained_snapshot_sha256"] = sha(retained_path)
            evidence["frozen_snapshot_equal"] = True
            if sha(blend) != hashes[name]:
                raise ValueError("opened baseline file changed")
            cases.append(case)
            report["cases"].append(evidence)

        scene = controlled_scene(bpy)
        before, bounds_before = read_scene(bpy)
        source_text_before = scene["optical_sources"]
        blend = folder / "controlled_numeric.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        digest = sha(blend)
        bpy.ops.wm.open_mainfile(filepath=str(blend))
        after, bounds_after = read_scene(bpy)
        if (before != after or bounds_before != bounds_after or
                source_text_before != bpy.context.scene["optical_sources"]):
            raise ValueError("controlled scene values changed across save/reopen")
        case, evidence = retain_case(bpy, folder, blend, "controlled_numeric",
                                     "controlled_numeric_scene")
        if sha(blend) != digest:
            raise ValueError("controlled scene file changed after reopen")
        evidence["saved_reopened_exact"] = True
        evidence["expected_tiny_difference"] = [2 ** 60 - 1, 2 ** 60]
        evidence["explicit_test_sources"] = after["sources"]
        evidence["explicit_direction_bounds"] = after[BOUNDS_PROPERTY]
        cases.append(case)
        report["cases"].append(evidence)

        if sha(old_manifest) != FROZEN_MANIFEST_SHA256:
            raise ValueError("frozen manifest mutated")
        for cells in (3, 4):
            name = f"K{cells}_base.blend"
            if sha(frozen / name) != hashes[name]:
                raise ValueError("frozen scene mutated")
        if any(sha(ROOT / name) != digest for name, digest in code.items()):
            raise ValueError("preparation source changed during execution")
        native_input = {
            "schema": SCHEMA, "cases": cases,
            "limits": {"max_sources": 5, "max_triangles": 64, "max_dispatches": 6},
            "expected_backend": "OPENGL",
            "expected_renderer_contains": "RTX 3090",
        }
        input_path = folder / "input_manifest.json"
        write_new(input_path, native_input)
        report["input_manifest_path"] = str(input_path)
        report["input_manifest_sha256"] = sha(input_path)
        report["status"] = "PASS"
        report["verification_passed"] = True
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        report["total_seconds"] = time.perf_counter() - start
        write_new(folder / "prepare_report.json", report)
    print("SCENE_HILO_PREPARE_PASS " + report["input_manifest_sha256"], flush=True)


if __name__ == "__main__":
    main()
