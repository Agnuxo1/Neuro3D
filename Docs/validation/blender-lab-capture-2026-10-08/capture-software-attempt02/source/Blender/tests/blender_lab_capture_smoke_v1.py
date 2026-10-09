"""Real bpy software checks: evaluated geometry, bindings, edit, save and reopen.

The RNA fixture resembles the documented upstream interface; it is not an
installation or independent execution of Blender Optics Simulator.
"""
import copy
import json
from pathlib import Path
import sys

import bpy
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, FloatVectorProperty, PointerProperty, StringProperty

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.blender_lab import scene_capture_v1 as capture
from Blender.blender_lab.bos_adapter_v1 import capture_bos_scene


class FixturePort(bpy.types.PropertyGroup):
    local_position: FloatVectorProperty(size=3)
    local_normal: FloatVectorProperty(size=3, default=(0, 0, 1))


class FixtureOptics(bpy.types.PropertyGroup):
    is_optical: BoolProperty(default=False)
    element_type: StringProperty(default="MIRROR")
    wavelength: FloatProperty(default=632.8)
    ports: CollectionProperty(type=FixturePort)


def main():
    out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    capture.need(out.is_dir(), "fresh test output directory required")
    for cls in (FixturePort, FixtureOptics):
        bpy.utils.register_class(cls)
    bpy.types.Object.optics = PointerProperty(type=FixtureOptics)
    bpy.types.Scene.optics = PointerProperty(type=FixtureOptics)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    for name in ("source", "detector"):
        obj = bpy.data.objects.new(name, None)
        scene.collection.objects.link(obj)
        obj.optics.is_optical = True
        obj.optics.element_type = name.upper()
    mesh = bpy.data.meshes.new("mirror.mesh")
    mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
    mirror = bpy.data.objects.new("mirror", mesh)
    scene.collection.objects.link(mirror)
    mirror.location.x = 1.0
    mirror["delay"] = 0.125
    mirror.optics.is_optical = True
    mirror.optics.ports.add().local_position = (0.1234567, 0, 0)
    mirror.modifiers.new("thickness", "SOLIDIFY").thickness = 0.01
    # Linked collection instances must retain source metadata even outside scene.objects.
    linked = bpy.data.collections.new("instanced.collection")
    linked_obj = bpy.data.objects.new("instanced.mirror", mesh.copy())
    linked_obj["kind"] = "mirror"
    linked.objects.link(linked_obj)
    instancer = bpy.data.objects.new("instance", None)
    instancer.instance_type = "COLLECTION"
    instancer.instance_collection = linked
    scene.collection.objects.link(instancer)
    network = {"schema": capture.NETWORK_SCHEMA, "model": "software-fixture-no-forward",
               "inputs": [{"id": "x", "object": "source"}],
               "parameters": [{"id": "delay", "object": "mirror", "path": ["custom_properties", "delay"],
                               "unit": "BU", "bounds": [0, 1]}],
               "detectors": [{"id": "y", "object": "detector"}]}
    first = capture_bos_scene(network=network)
    capture.validate_capture(first)
    mirror_records = [i for i in first["state"]["instances"] if i["object"] == "mirror"]
    triangle_count = len(first["state"]["meshes"][mirror_records[0]["mesh_sha256"]]["triangles"])
    capture.need(triangle_count > 2, "modifier must reach evaluated captured geometry")
    port = next(o for o in first["state"]["objects"] if o["name"] == "mirror")["optics"]["ports"][0]
    capture.need(port["local_position"][0]["float64_hex"] == float(mirror.optics.ports[0].local_position[0]).hex(),
                 "RNA port value must not be rounded for export")
    extra = next(o for o in first["state"]["objects"] if o["name"] == "instanced.mirror")
    capture.need(not extra["direct_scene_member"] and extra["evaluated_instance_count"] == 1,
                 "collection instance metadata must be captured")
    mirror.location.x = 1.0 + 2**-22
    edited = capture_bos_scene(network=network)
    capture.need(round(1.0, 6) == round(float(mirror.location.x), 6), "fixture decimal-rounding collision")
    capture.need(edited["state_sha256"] != first["state_sha256"], "represented edit must change capture identity")
    mirror["delay"] = 0.25
    weighted = capture_bos_scene(network=network)
    capture.need(weighted["state"]["network"]["parameters"][0]["represented_value_hex"] == (0.25).hex(),
                 "trainable binding must read new scene value")
    # Failure cases exercise software admission, not phase/intensity hypotheses.
    rejects = []
    for label, change in (("object_bound", {"max_objects": 1}), ("triangle_bound", {"max_triangles": 1})):
        try:
            capture.capture_scene(network=network, **change)
        except capture.CaptureError:
            rejects.append(label)
        else:
            raise AssertionError("expected bounded capture rejection")
    broken = copy.deepcopy(network)
    broken["detectors"][0]["object"] = "missing"
    try:
        capture.capture_scene(network=broken)
    except capture.CaptureError:
        rejects.append("missing_detector")
    else:
        raise AssertionError("expected missing detector rejection")
    mirror.hide_viewport = True
    try:
        capture.capture_scene(network=network)
    except capture.CaptureError:
        rejects.append("excluded_parameter")
    else:
        raise AssertionError("expected excluded parameter rejection")
    mirror.hide_viewport = False
    bpy.context.view_layer.update()
    before = capture_bos_scene(network=network)
    blend_path = out / "capture-software-fixture.blend"
    capture.need(not blend_path.exists(), "fresh fixture blend required")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    after = capture_bos_scene(network=network)
    capture.need(before["state_sha256"] == after["state_sha256"], "capture identity must survive save/reopen")
    capture.write_capture(out / "capture.json", after)
    result = {"schema": "neuro3d.blender_lab.capture_software_checks.v1", "status": "PASS",
              "blender_version": bpy.app.version_string, "state_sha256": after["state_sha256"],
              "objects": len(after["state"]["objects"]), "instances": len(after["state"]["instances"]),
              "evaluated_mirror_triangles": triangle_count, "rejections": rejects,
              "geometry_edit_detected_without_added_rounding": True, "rna_port_preserved": True,
              "bound_parameter_edit_read": True, "collection_instance_metadata_captured": True,
              "save_reopen_identity": True, "upstream_addon_executed": False,
              "optical_forward_executed": False, "training_executed": False, "gpu_executed": False}
    (out / "software_checks.json").write_bytes(capture.canonical_bytes(result))
    print("BLENDER_LAB_SOFTWARE_CHECKS " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
