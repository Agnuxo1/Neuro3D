"""Background Blender regressions for non-destructive Iris rebuilds.

Run in a new process, without rendering or registering timers:
  blender -b --factory-startup -t 1 --python-exit-code 1 --python test_rebuild_blender.py \
    -- --report REPORT.json

Cases are isolated by factory resets. Within a case, reset=False must preserve
every earlier scene, its objects, transforms, material state and exclusion flags.
The report records failures independently so a detector KeyError cannot hide
the remaining regressions. This tests background API calls, not GUI clicks.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
import types

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "neuro3d_iris_demo.py"
LIMITS = {
    "field": 1e-3,
    "power": 1e-3,
    "balance": 2e-4,
    "escape": 1e-8,
    "same_geometry": 1e-8,
}
PROBES = (0, 71, 149)
DEMO = None
STATE = None
FEATURES = None
LABELS = None
MODEL = None
OUTPUTS = None
CLASS_INDICES = None


def require(condition, message):
    """Stop an invalid setup; the case runner will retain the failure."""
    if not condition:
        raise AssertionError(message)


def digest(value):
    """Fingerprint structured snapshots without writing Blender data."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def save_report(path, report):
    """Atomically retain RUNNING, FAIL or PASS evidence, including partial cases."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=path.name + ".",
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def check(step, name, condition, details=None):
    """Record each assertion without discarding later, independent observations."""
    entry = {"name": name, "passed": bool(condition)}
    if details is not None:
        entry["details"] = details
    step["checks"].append(entry)


def run_step(case, name, function):
    """Capture an exception as evidence and allow the next step/case to run."""
    step = {"name": name, "status": "RUNNING", "checks": []}
    case["steps"].append(step)
    wall, cpu = time.perf_counter(), time.process_time()
    result = None
    try:
        result = function(step)
        step["status"] = "PASS" if all(item["passed"] for item in step["checks"]) else "FAIL"
    except Exception as exc:
        step.update(status="FAIL", exception_type=type(exc).__name__,
                    exception_message=str(exc), traceback=traceback.format_exc())
    finally:
        step["wall_seconds"] = time.perf_counter() - wall
        step["cpu_seconds"] = time.process_time() - cpu
    return result


def layer_flags(scene):
    """Record every layer collection, including nested exclusion state."""
    result = {}
    def visit(layer, path):
        key = path + "/" + layer.name
        result[key] = {"exclude": bool(layer.exclude),
                       "collection_pointer": int(layer.collection.as_pointer())}
        for child in layer.children:
            visit(child, key)
    for view_layer in scene.view_layers:
        visit(view_layer.layer_collection, view_layer.name)
    return result


def find_layer(collection):
    """Find an existing active layer collection by datablock identity."""
    wanted = collection.as_pointer()
    def visit(layer):
        if layer.collection.as_pointer() == wanted:
            return layer
        for child in layer.children:
            found = visit(child)
            if found is not None:
                return found
        return None
    found = visit(bpy.context.view_layer.layer_collection)
    require(found is not None, "Collection is absent from the active view layer")
    return found


def socket_value(value):
    """Serialize material socket values and stable datablock references."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "as_pointer"):
        return {"name": value.name, "pointer": int(value.as_pointer())}
    return [socket_value(item) for item in value]


def material_snapshot(material):
    """Capture the material properties affected by build/show/live operations."""
    result = {
        "pointer": int(material.as_pointer()), "name": material.name,
        "use_nodes": bool(material.use_nodes), "diffuse_color": list(material.diffuse_color),
        "metallic": float(material.metallic), "roughness": float(material.roughness),
    }
    if material.node_tree:
        result["nodes"] = {}
        for node in material.node_tree.nodes:
            sockets = {}
            for index, socket in enumerate(node.inputs):
                if hasattr(socket, "default_value"):
                    sockets[str(index) + ":" + socket.name] = socket_value(socket.default_value)
            result["nodes"][node.name] = {"type": node.bl_idname, "inputs": sockets}
        result["links"] = sorted(
            (link.from_node.name, link.from_socket.identifier,
             link.to_node.name, link.to_socket.identifier)
            for link in material.node_tree.links)
    return result


def snapshot_scenes(scenes):
    """Capture owned test scenes without assuming globally unique material names."""
    output = {"scenes": {}, "materials": {}}
    for scene in scenes:
        objects = {}
        for obj in scene.objects:
            materials = [slot.material for slot in obj.material_slots if slot.material]
            objects[obj.name] = {
                "pointer": int(obj.as_pointer()),
                "data_pointer": int(obj.data.as_pointer()) if obj.data else None,
                "matrix_world": [float(value) for row in obj.matrix_world for value in row],
                "location": list(obj.location), "scale": list(obj.scale),
                "rotation_mode": obj.rotation_mode,
                "rotation_euler": list(obj.rotation_euler),
                "rotation_quaternion": list(obj.rotation_quaternion),
                "hide_render": bool(obj.hide_render), "hide_viewport": bool(obj.hide_viewport),
                "collections": sorted(collection.name for collection in obj.users_collection),
                "material_slots": [
                    (slot.link, slot.material.name, int(slot.material.as_pointer()))
                    if slot.material else (slot.link, None, None)
                    for slot in obj.material_slots],
            }
            for material in materials:
                output["materials"][material.name] = material_snapshot(material)
        output["scenes"][scene.name] = {
            "pointer": int(scene.as_pointer()), "objects": objects,
            "exclude_flags": layer_flags(scene),
        }
    return output


def verify_preserved(step, before):
    """Check earlier objects, transforms, material sockets and flags after an operation."""
    names = list(before["scenes"])
    missing = [name for name in names if bpy.data.scenes.get(name) is None]
    check(step, "previous_scenes_exist", not missing, {"missing": missing})
    if missing:
        return
    after = snapshot_scenes([bpy.data.scenes[name] for name in names])
    changed = []
    for name in names:
        old, new = before["scenes"][name], after["scenes"][name]
        if old["pointer"] != new["pointer"]:
            changed.append("scene_identity:" + name)
        if old["exclude_flags"] != new["exclude_flags"]:
            changed.append("exclude_flags:" + name)
        for obj_name in sorted(set(old["objects"]) | set(new["objects"])):
            if old["objects"].get(obj_name) != new["objects"].get(obj_name):
                changed.append("object:" + name + "/" + obj_name)
    for name in sorted(set(before["materials"]) | set(after["materials"])):
        if before["materials"].get(name) != after["materials"].get(name):
            changed.append("material:" + name)
    check(step, "previous_objects_transforms_materials_and_flags_unchanged", not changed,
          {"changed": changed[:40], "changed_count": len(changed),
           "before_sha256": digest(before), "after_sha256": digest(after),
           "scenes_checked": len(names),
           "objects_checked": sum(len(s["objects"]) for s in before["scenes"].values()),
           "materials_checked": len(before["materials"])})


def mark_materials(scene):
    """Give previous materials non-default values so silent global reuse is observable."""
    seen = set()
    for obj in scene.objects:
        for slot in obj.material_slots:
            material = slot.material
            if material is None or material.as_pointer() in seen:
                continue
            seen.add(material.as_pointer())
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        node.inputs["Roughness"].default_value = 0.731
                        node.inputs["Emission Strength"].default_value = 7.125
                        node.inputs["Base Color"].default_value = (0.117, 0.239, 0.371, 1.0)


def add_user_assets(scene):
    """Create a transformed sentinel and deliberately colliding user material names."""
    collections = {}
    for name in ("Optics", "Decor", "Beams", "Labels", "Stage"):
        collections[name] = bpy.data.collections.new(name)
        scene.collection.children.link(collections[name])
    mesh = bpy.data.meshes.new("user-sentinel-mesh")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    sentinel = bpy.data.objects.new("unsaved-user-object", mesh)
    collections["Optics"].objects.link(sentinel)
    sentinel.location = (3.25, -7.5, 0.75)
    sentinel.rotation_euler = (0.13, -0.27, 0.31)
    sentinel.scale = (1.23, 0.67, 2.11)
    names = ["mirror", "beamsplitter", "plate_mirror", "plate_bs", "post", "stage"]
    names += ["det_" + name for name in OUTPUTS]
    names += ["beam_0", "txt_hud.title", "bar_r0"]
    for name in names:
        material = bpy.data.materials.new(name)
        material.use_nodes = True
        mesh.materials.append(material)
    mark_materials(scene)
    bpy.context.view_layer.update()
    find_layer(collections["Decor"]).exclude = True
    return sentinel


def mixed_exclusions():
    """Exercise an initially excluded Optics and distinct descendant flags under Decor."""
    decor = DEMO.scene_collection("Decor")
    first = bpy.data.collections.new("rebuild-nested-excluded")
    second = bpy.data.collections.new("rebuild-nested-visible")
    decor.children.link(first)
    decor.children.link(second)
    bpy.context.view_layer.update()
    for index, name in enumerate(("Beams", "Labels", "Stage", "Decor")):
        find_layer(DEMO.scene_collection(name)).exclude = bool(index % 2)
    find_layer(decor).exclude = False
    find_layer(first).exclude = True
    find_layer(second).exclude = False
    find_layer(DEMO.scene_collection("Optics")).exclude = True
    return layer_flags(bpy.context.scene)


def build(step, reset):
    """Call only the public builder, recording whether a new scene was created."""
    previous = bpy.context.scene
    previous_pointer = previous.as_pointer()
    step["reset_argument"] = reset
    scene = DEMO.build_scene(np.asarray(STATE["theta"]).reshape(4, 4), STATE["ref"], reset=reset)
    check(step, "builder_returned_active_scene",
          scene.as_pointer() == bpy.context.scene.as_pointer())
    if not reset:
        check(step, "new_scene_created", scene.as_pointer() != previous_pointer)
        check(step, "previous_scene_has_fake_user", previous.use_fake_user)
    step["active_scene"] = scene.name
    return scene


def measure(step, index):
    """Check eight outputs, actual class decision, escape, balance and flag restoration."""
    scene = bpy.context.scene
    before_flags = layer_flags(scene)
    wall, cpu = time.perf_counter(), time.process_time()
    try:
        prediction, class_powers, detectors, segments, casts = DEMO.classify(FEATURES[index])
    finally:
        check(step, "exclude_flags_restored", layer_flags(scene) == before_flags,
              {"before": before_flags, "after": layer_flags(scene)})
    elapsed_wall, elapsed_cpu = time.perf_counter() - wall, time.process_time() - cpu
    fields = np.asarray([detectors.get(name, 0j) for name in OUTPUTS], dtype=complex)
    powers = np.abs(fields) ** 2
    class_powers = np.asarray(class_powers, dtype=float)
    escape = float(DEMO.TRACE_INFO["escape"])
    require(np.isfinite(fields).all() and np.isfinite(powers).all() and
            np.isfinite(class_powers).all() and math.isfinite(escape),
            "Non-finite numeric output")
    require(class_powers.shape == (3,), "Wrong class power shape")
    reference = MODEL[index]
    reference_powers = np.abs(reference) ** 2
    errors = {
        "field": float(np.max(np.abs(fields - reference))),
        "power": float(np.max(np.abs(powers - reference_powers))),
        "balance": abs(float(powers.sum()) + escape - 1.0),
        "escape": abs(escape),
    }
    check(step, "recognized_detector_ids", set(detectors) <= set(OUTPUTS),
          {"observed": sorted(detectors)})
    check(step, "detectors_not_all_zero", bool(np.any(powers > 0)),
          {"total_detected_power": float(powers.sum())})
    check(step, "prediction_matches_model",
          prediction == int(reference_powers[CLASS_INDICES].argmax()))
    check(step, "prediction_matches_returned_class_powers",
          prediction == int(class_powers.argmax()))
    check(step, "returned_class_powers_match_fields",
          float(np.max(np.abs(class_powers - powers[CLASS_INDICES]))) <= LIMITS["power"])
    check(step, "escape_nonnegative", escape >= 0)
    check(step, "positive_ray_cast_count", type(casts) is int and casts > 0)
    for name, value in errors.items():
        check(step, name + "_within_limit", value <= LIMITS[name],
              {"error": value, "limit": LIMITS[name]})
    step["sample"] = {
        "index": index, "truth": int(LABELS[index]), "prediction": int(prediction),
        "fields": {name: [float(value.real), float(value.imag)]
                   for name, value in zip(OUTPUTS, fields)},
        "powers": {name: float(value) for name, value in zip(OUTPUTS, powers)},
        "escape": escape, "ray_casts": int(casts), "errors": errors,
        "classify_wall_seconds": elapsed_wall, "classify_cpu_seconds": elapsed_cpu,
    }
    return {"index": index, "prediction": prediction, "fields": fields, "powers": powers,
            "class_powers": class_powers.tolist(), "segments": segments, "escape": escape}


def compare_identical(step, first, second):
    """Use the existing 1e-8 invariance limit for unchanged geometry and input."""
    if first is None or second is None:
        check(step, "same_geometry_available", False)
        return
    differences = {
        "field": float(np.max(np.abs(first["fields"] - second["fields"]))),
        "power": float(np.max(np.abs(first["powers"] - second["powers"]))),
        "escape": abs(first["escape"] - second["escape"]),
    }
    for name, value in differences.items():
        check(step, "same_geometry_" + name, value <= LIMITS["same_geometry"],
              {"error": value, "limit": LIMITS["same_geometry"]})
    check(step, "same_geometry_prediction", first["prediction"] == second["prediction"])


def manual_live_start(index):
    """Start a deterministic first trace tick; no timer is registered."""
    DEMO.LIVE.clear()
    DEMO.LIVE.update(on=True, phase="trace", front=0.0, hold=0, P=None, pred=0)
    bpy.context.scene["flower"] = index - 1
    return DEMO._live_tick()


def exercise_display(case, sample, previous):
    """Exercise show, detector dimming and a real manual propagate branch."""
    if sample is None:
        run_step(case, "display_requires_valid_probe",
                 lambda step: check(step, "probe_available", False))
        return
    def shown(step):
        DEMO.show(sample["segments"], sample["class_powers"], sample["prediction"],
                  truth=int(LABELS[sample["index"]]), x_row=FEATURES[sample["index"]])
        verify_preserved(step, previous)
    run_step(case, "show_preserves_previous_scenes", shown)
    run_step(case, "preservation_after_show_even_on_error",
             lambda step: verify_preserved(step, previous))
    def dimmed(step):
        DEMO._dim_detectors()
        verify_preserved(step, previous)
    run_step(case, "dim_detectors_preserves_previous_scenes", dimmed)
    run_step(case, "preservation_after_dim_even_on_error",
             lambda step: verify_preserved(step, previous))
    def propagated(step):
        saved = copy.deepcopy(DEMO.LIVE)
        try:
            manual_live_start(sample["index"])
            require(DEMO.LIVE["phase"] == "propagate", "Manual trace did not start propagation")
            DEMO.LIVE["front"] = 1e9
            result = DEMO._live_tick()
            check(step, "propagate_branch_completed", DEMO.LIVE["phase"] == "hold")
            check(step, "manual_tick_returned_next_interval", result is not None)
            verify_preserved(step, previous)
        finally:
            DEMO.LIVE.clear()
            DEMO.LIVE.update(saved)
    run_step(case, "manual_live_propagate_preserves_previous_scenes", propagated)
    run_step(case, "preservation_after_live_even_on_error",
             lambda step: verify_preserved(step, previous))


def baseline_case(case):
    run_step(case, "build_reset_true_baseline", lambda step: build(step, True))
    baseline = {index: run_step(case, "baseline_" + str(index),
                               lambda step, index=index: measure(step, index)) for index in PROBES}
    mixed_exclusions()
    for index in PROBES:
        changed = run_step(case, "excluded_optics_and_nested_decor_" + str(index),
                           lambda step, index=index: measure(step, index))
        run_step(case, "same_geometry_after_exclusion_" + str(index),
                 lambda step, index=index, changed=changed: compare_identical(step, baseline[index], changed))


def user_collision_case(case):
    prior = bpy.context.scene
    add_user_assets(prior)
    before = snapshot_scenes([prior])
    run_step(case, "build_reset_false_with_user_optics", lambda step: build(step, False))
    run_step(case, "preservation_after_build", lambda step: verify_preserved(step, before))
    sample = run_step(case, "numeric_with_colliding_global_names", lambda step: measure(step, 71))
    exercise_display(case, sample, before)


def repeated_rebuild_case(case):
    run_step(case, "initial_build", lambda step: build(step, True))
    baseline = run_step(case, "initial_numeric", lambda step: measure(step, 71))
    if baseline is not None:
        run_step(case, "initial_show",
                 lambda step: DEMO.show(baseline["segments"], baseline["class_powers"],
                                        baseline["prediction"], x_row=FEATURES[71]))
    for generation in (1, 2):
        for scene in bpy.data.scenes:
            mark_materials(scene)
        bpy.context.view_layer.update()
        previous = snapshot_scenes(list(bpy.data.scenes))
        run_step(case, "rebuild_" + str(generation), lambda step: build(step, False))
        run_step(case, "preserve_after_rebuild_" + str(generation),
                 lambda step, previous=previous: verify_preserved(step, previous))
        sample = run_step(case, "numeric_after_rebuild_" + str(generation),
                          lambda step: measure(step, 71))
        run_step(case, "same_geometry_rebuild_" + str(generation),
                 lambda step, sample=sample: compare_identical(step, baseline, sample))
        exercise_display(case, sample, previous)


def no_optics_escape_case(case):
    scene = bpy.context.scene
    def control(step, second_amplitude, second_direction, expected):
        scene["sources"] = json.dumps([
            {"id": "a", "p": [0, 0, 0], "d": [1, 0, 0]},
            {"id": "b", "p": [0, 0, 0], "d": second_direction}])
        flags = layer_flags(scene)
        try:
            detectors, _, casts = DEMO.trace({"a": 1.0, "b": second_amplitude})
        finally:
            check(step, "exclude_flags_restored", layer_flags(scene) == flags)
        observed = float(DEMO.TRACE_INFO["escape"])
        check(step, "empty_scene_detectors_empty", not detectors)
        check(step, "escape_matches_coherent_reference",
              math.isfinite(observed) and abs(observed - expected) <= LIMITS["escape"],
              {"observed": observed if math.isfinite(observed) else None, "expected": expected})
        step["ray_casts"] = casts
    run_step(case, "coincident_constructive_escape", lambda s: control(s, 1.0, [1, 0, 0], 4.0))
    run_step(case, "coincident_destructive_escape", lambda s: control(s, -1.0, [1, 0, 0], 0.0))
    run_step(case, "orthogonal_escape_modes", lambda s: control(s, 1.0, [0, 1, 0], 2.0))


def trace_exception_case(case):
    run_step(case, "build_for_exception", lambda step: build(step, True))
    mesh = bpy.data.meshes.new("non-optical-blocker-mesh")
    mesh.from_pydata([(-0.5, -0.25, -0.25), (-0.5, 0.25, -0.25),
                     (-0.5, 0.25, 0.25), (-0.5, -0.25, 0.25)], [], [(0, 1, 2, 3)])
    blocker = bpy.data.objects.new("controlled-non-optical-blocker", mesh)
    blocker["kind"] = "controlled-invalid-role"
    DEMO.scene_collection("Optics").objects.link(blocker)
    bpy.context.view_layer.update()
    mixed_exclusions()
    def failing_trace(step):
        flags = layer_flags(bpy.context.scene)
        raised = False
        try:
            DEMO.trace({"r0": 1.0})
        except RuntimeError as exc:
            raised = "non-optical hit" in str(exc)
            step["observed_exception"] = str(exc)
        finally:
            check(step, "all_exclude_flags_restored_after_exception",
                  layer_flags(bpy.context.scene) == flags,
                  {"before": flags, "after": layer_flags(bpy.context.scene)})
        check(step, "controlled_non_optical_hit_raised", raised)
    run_step(case, "trace_error_restores_optics_and_descendants", failing_trace)


def stale_live_rebuild_case(case):
    run_step(case, "initial_live_scene", lambda step: build(step, True))
    run_step(case, "manual_first_live_tick", lambda step: manual_live_start(71))
    DEMO.LIVE.update(on=True, phase="propagate", P=[0.2, 0.3, 0.5], pred=2, front=0.0)
    previous = snapshot_scenes(list(bpy.data.scenes))
    run_step(case, "rebuild_with_stale_live_state", lambda step: build(step, False))
    run_step(case, "previous_scene_preserved", lambda step: verify_preserved(step, previous))
    def stopped(step):
        check(step, "live_stopped_by_rebuild", DEMO.LIVE.get("on") is False)
        check(step, "stale_powers_cleared_by_rebuild", DEMO.LIVE.get("P") is None)
        before = snapshot_scenes(list(bpy.data.scenes))
        result = DEMO._live_tick()
        check(step, "stopped_tick_terminates", result is None)
        verify_preserved(step, before)
    run_step(case, "new_scene_cannot_receive_stale_live_output", stopped)


def live_scene_switch_case(case):
    run_step(case, "initial_live_scene", lambda step: build(step, True))
    def start(step):
        manual_live_start(71)
        check(step, "live_session_reached_propagate", DEMO.LIVE.get("phase") == "propagate")
    run_step(case, "bind_live_on_first_manual_trace_tick", start)
    other = bpy.data.scenes.new("Unrelated user scene")
    bpy.context.window.scene = other
    add_user_assets(other)
    before = snapshot_scenes(list(bpy.data.scenes))
    def switched(step):
        result = DEMO._live_tick()
        check(step, "foreign_scene_tick_terminates", result is None)
        check(step, "foreign_scene_stops_live", DEMO.LIVE.get("on") is False)
        verify_preserved(step, before)
    run_step(case, "live_aborts_after_scene_switch", switched)
    run_step(case, "all_scenes_preserved_even_if_tick_raises",
             lambda step: verify_preserved(step, before))


def load_demo():
    """Load this checkout's source using its own compilation semantics."""
    global DEMO, STATE, FEATURES, LABELS, MODEL, OUTPUTS, CLASS_INDICES
    source = SOURCE.read_text(encoding="utf-8")
    DEMO = types.ModuleType("_iris_rebuild_regression_demo")
    DEMO.__file__ = str(SOURCE)
    sys.modules[DEMO.__name__] = DEMO
    exec(compile(source, str(SOURCE), "exec", dont_inherit=True), DEMO.__dict__)
    DEMO.HERE = str(HERE)
    require(DEMO.VERIFY_LIMITS["outputs_complex_vs_model_max"] == LIMITS["field"] and
            DEMO.VERIFY_LIMITS["scene_vs_model_max_power_diff"] == LIMITS["power"] and
            DEMO.VERIFY_LIMITS["power_balance_max_err"] == LIMITS["balance"] and
            DEMO.VERIFY_LIMITS["escape_max"] == LIMITS["escape"] and
            DEMO.VERIFY_LIMITS["save_reopen_max"] == LIMITS["same_geometry"],
            "Existing numerical acceptance limits changed")
    STATE = DEMO.load_state()
    FEATURES, LABELS, _ = DEMO.load_iris()
    _, OUTPUTS = DEMO.modes()
    CLASS_INDICES = [OUTPUTS.index(name) for name in DEMO.CLASS_DET]
    matrix = DEMO.model_U(np.asarray(STATE["theta"]).reshape(4, 4) * DEMO.LAM / (4 * math.pi))
    MODEL = DEMO.encode(FEATURES, STATE["ref"]) @ matrix.T
    require(FEATURES.shape == (150, 4) and MODEL.shape == (150, 8) and
            np.isfinite(MODEL).all(), "Invalid regression reference")
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def main():
    """Run independent cases and retain RED/GREEN evidence without early test abort."""
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    report_path = Path(parser.parse_args(args).report).resolve()
    require(report_path.suffix.lower() == ".json" and report_path != SOURCE,
            "Use a separate JSON report path")
    report = {
        "schema": "neuro3d-iris-rebuild-regression-v1", "status": "RUNNING",
        "verification_passed": False, "started_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "background reset=False API regressions, not GUI clicks",
        "blender_version": bpy.app.version_string, "pid": os.getpid(),
        "limits": LIMITS, "probe_indices": list(PROBES), "cases": [],
        "rendered": False, "trained": False, "timers_registered": False,
    }
    wall, cpu = time.perf_counter(), time.process_time()
    save_report(report_path, report)
    cases = [
        ("baseline_numeric_and_nested_exclusions", baseline_case),
        ("existing_user_optics_and_materials", user_collision_case),
        ("two_repeated_non_destructive_rebuilds", repeated_rebuild_case),
        ("legacy_empty_scene_without_optics", no_optics_escape_case),
        ("trace_exception_restores_exclusions", trace_exception_case),
        ("rebuild_clears_stale_live_state", stale_live_rebuild_case),
        ("live_stops_on_scene_switch", live_scene_switch_case),
    ]
    try:
        require(bpy.app.background, "Run these tests in an isolated background Blender process")
        report["source_sha256"] = load_demo()
        report["source_path"] = str(SOURCE)
        for name, function in cases:
            case = {"name": name, "status": "RUNNING", "steps": []}
            report["cases"].append(case)
            save_report(report_path, report)
            try:
                bpy.ops.wm.read_factory_settings(use_empty=True)
                DEMO.LIVE.clear()
                DEMO.LIVE.update(on=False, phase="trace", front=0.0, hold=0, P=None, pred=0)
                function(case)
                case["status"] = "PASS" if all(step["status"] == "PASS" for step in case["steps"]) else "FAIL"
            except Exception as exc:
                case.update(status="FAIL", exception_type=type(exc).__name__,
                            exception_message=str(exc), traceback=traceback.format_exc())
            finally:
                DEMO.LIVE.clear()
                DEMO.LIVE.update(on=False, phase="trace", front=0.0, hold=0, P=None, pred=0)
                save_report(report_path, report)
            print("IRIS_REBUILD_CASE " + json.dumps({"name": name, "status": case["status"]}), flush=True)
        report["verification_passed"] = len(report["cases"]) == len(cases) and all(
            case["status"] == "PASS" for case in report["cases"])
        report["status"] = "PASS" if report["verification_passed"] else "FAIL"
    except BaseException as exc:
        report.update(status="FAIL", verification_passed=False,
                      exception_type=type(exc).__name__, exception_message=str(exc),
                      traceback=traceback.format_exc())
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        report["total_wall_seconds"] = time.perf_counter() - wall
        report["total_cpu_seconds"] = time.process_time() - cpu
        save_report(report_path, report)
    print("IRIS_REBUILD_RESULT " + json.dumps({
        "status": report["status"], "report": str(report_path),
        "cases": [{"name": case["name"], "status": case["status"]} for case in report["cases"]]}), flush=True)
    return 0 if report["verification_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
