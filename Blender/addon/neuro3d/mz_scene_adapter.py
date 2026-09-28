"""Blender object adapter for the experimental CPU-only two-port MZ circuit.

No Blender renderer, shader or GPU API is called. This adapter is not yet
runtime-validated in Blender; it is intentionally separate from the stable
three-object circuit and its UI operators.
"""

from __future__ import annotations

from mz_scene import Detector, MZScene, Mirror, Source, Splitter, trace_mz


def _point_local_z(obj, direction) -> None:
    from mathutils import Vector

    obj.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()


def _new_empty(bpy, collection, name, role, position, *, normal=None, shape="CIRCLE"):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = shape
    obj.empty_display_size = 0.3
    collection.objects.link(obj)
    obj.location = position
    obj["neuro3d_role"] = role
    if normal is not None:
        _point_local_z(obj, normal)
    return obj


def create_mz_circuit(bpy, scene):
    """Create seven empty objects holding all optical computation parameters."""

    collection = bpy.data.collections.new("Neuro3D MZ Experimental")
    scene.collection.children.link(collection)
    scene["neuro3d_active_mz"] = collection.name
    n = (1.0, -1.0, 0.0)

    source = _new_empty(bpy, collection, "MZ Source", "mz_source", (-1.0, 0.0, 0.0),
                        normal=(1.0, 0.0, 0.0), shape="SINGLE_ARROW")
    source["power"] = 1.0
    source["rgb"] = [1.0, 1.0, 1.0]
    source["frequency"] = 10.0
    source["phase"] = 0.0
    source["propagation_speed"] = 10.0
    source["absorption_per_unit"] = 0.0

    for role, name, position in (
        ("mz_bs1", "MZ Splitter 1", (0.0, 0.0, 0.0)),
        ("mz_bs2", "MZ Splitter 2", (2.0, 2.0, 0.0)),
    ):
        obj = _new_empty(bpy, collection, name, role, position, normal=n)
        obj["radius"] = 0.4
        obj["transmission"] = 0.5
        if role == "mz_bs2":
            obj["overlap_tolerance"] = 0.02
            obj["direction_tolerance"] = 1e-6

    for role, name, position in (
        ("mz_mirror1", "MZ Mirror 1", (2.0, 0.0, 0.0)),
        ("mz_mirror2", "MZ Mirror 2", (0.0, 2.0, 0.0)),
    ):
        obj = _new_empty(bpy, collection, name, role, position, normal=n)
        obj["radius"] = 0.4
        obj["reflectance_rgb"] = [1.0, 1.0, 1.0]
        obj["phase_shift"] = 0.0

    for role, name, position in (
        ("mz_detector_a", "MZ Detector A", (2.0, 3.0, 0.0)),
        ("mz_detector_b", "MZ Detector B", (3.0, 2.0, 0.0)),
    ):
        obj = _new_empty(bpy, collection, name, role, position, shape="SPHERE")
        obj["radius"] = 0.2
        obj["responsivity_rgb"] = [1.0, 1.0, 1.0]
        obj["activation_threshold"] = 0.25
        obj["response_gain"] = 1.0
        obj["received_optical_rgb"] = [0.0, 0.0, 0.0]
        obj["received_signal"] = 0.0
        obj["activation"] = 0.0

    return collection


def _role(collection, role):
    found = [obj for obj in collection.objects if obj.get("neuro3d_role") == role]
    if len(found) != 1:
        raise ValueError(f"MZ circuit requires exactly one {role}; found {len(found)}")
    return found[0]


def _point(obj):
    return tuple(float(v) for v in obj.matrix_world.translation)


def _local_z(obj):
    from mathutils import Vector

    return tuple(float(v) for v in obj.matrix_world.to_quaternion() @ Vector((0.0, 0.0, 1.0)))


def _rgb(obj, key):
    return tuple(float(v) for v in obj[key])


def trace_mz_circuit(bpy, scene):
    """Read saved object transforms/properties, run CPU optics, save outputs."""

    name = scene.get("neuro3d_active_mz")
    collection = bpy.data.collections.get(name) if name else None
    if collection is None:
        raise ValueError("No active Neuro3D MZ circuit in this scene")
    bpy.context.view_layer.update()
    source_obj = _role(collection, "mz_source")
    bs1_obj = _role(collection, "mz_bs1")
    bs2_obj = _role(collection, "mz_bs2")
    mirror1_obj = _role(collection, "mz_mirror1")
    mirror2_obj = _role(collection, "mz_mirror2")
    detector_a_obj = _role(collection, "mz_detector_a")
    detector_b_obj = _role(collection, "mz_detector_b")

    def splitter(obj):
        return Splitter(_point(obj), _local_z(obj), float(obj["radius"]),
                        float(obj["transmission"]))

    def mirror(obj):
        return Mirror(_point(obj), _local_z(obj), float(obj["radius"]),
                      _rgb(obj, "reflectance_rgb"), float(obj["phase_shift"]))

    def detector(obj):
        return Detector(_point(obj), float(obj["radius"]),
                        _rgb(obj, "responsivity_rgb"),
                        float(obj["activation_threshold"]), float(obj["response_gain"]))

    optical_scene = MZScene(
        Source(_point(source_obj), _local_z(source_obj), float(source_obj["power"]),
               _rgb(source_obj, "rgb"), float(source_obj["frequency"]),
               float(source_obj["phase"])),
        splitter(bs1_obj), mirror(mirror1_obj), mirror(mirror2_obj),
        splitter(bs2_obj), detector(detector_a_obj), detector(detector_b_obj),
        float(source_obj["propagation_speed"]),
        float(source_obj["absorption_per_unit"]),
        float(bs2_obj["overlap_tolerance"]),
        float(bs2_obj["direction_tolerance"]),
    )
    result = trace_mz(optical_scene)
    for obj, rgb, signal, activation in (
        (detector_a_obj, result.optical_a, result.signal_a, result.activation_a),
        (detector_b_obj, result.optical_b, result.signal_b, result.activation_b),
    ):
        obj["received_optical_rgb"] = list(rgb)
        obj["received_signal"] = signal
        obj["activation"] = activation
    scene["neuro3d_mz_status"] = result.status
    scene["neuro3d_mz_interference_valid"] = result.interference_valid
    scene["neuro3d_mz_input_rgb"] = list(result.input_rgb)
    scene["neuro3d_mz_absorption_rgb"] = list(result.absorption_rgb)
    scene["neuro3d_mz_mirror_loss_rgb"] = list(result.mirror_loss_rgb)
    scene["neuro3d_mz_escape_rgb"] = list(result.escape_rgb)
    scene["neuro3d_mz_unresolved_rgb"] = list(result.unresolved_rgb)
    scene["neuro3d_mz_residual_rgb"] = list(result.residual_rgb)
    return result
