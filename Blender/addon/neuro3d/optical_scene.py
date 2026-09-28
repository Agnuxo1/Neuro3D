"""Blender scene is the authoritative state for the tiny optical circuit.

No renderer, shader, GPU API or hidden neural graph is used here. One explicit
operator samples object transforms and optical custom properties, applies the
CPU ray equations, then writes the received state back onto the scene object.
"""

from __future__ import annotations

from scene_optics import Emitter, Receiver, Reflector, trace_single_reflection


def _set_role(obj, role: str) -> None:
    obj["neuro3d_role"] = role
    obj.empty_display_size = 0.3


def _point_local_z(obj, direction) -> None:
    from mathutils import Vector

    obj.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()


def create_circuit(bpy, scene):
    """Create three light scene objects; no meshes, rendering or GPU work."""

    collection = bpy.data.collections.new("Neuro3D Optical Circuit")
    scene.collection.children.link(collection)
    scene["neuro3d_active_circuit"] = collection.name

    emitter = bpy.data.objects.new("Neuro3D Emitter", None)
    emitter.empty_display_type = "SINGLE_ARROW"
    collection.objects.link(emitter)
    emitter.location = (-2.0, 0.0, 0.0)
    _point_local_z(emitter, (1.0, 0.0, 0.0))
    _set_role(emitter, "emitter")
    emitter["intensity"] = 1.0
    emitter["color_rgb"] = [1.0, 0.5, 0.2]
    emitter["frequency"] = 1.0
    emitter["phase"] = 0.0

    mirror = bpy.data.objects.new("Neuro3D Reflector", None)
    mirror.empty_display_type = "CIRCLE"
    collection.objects.link(mirror)
    mirror.location = (0.0, 0.0, 0.0)
    _point_local_z(mirror, (1.0, -1.0, 0.0))
    _set_role(mirror, "reflector")
    mirror["radius"] = 0.5
    mirror["reflectance_rgb"] = [0.8, 0.9, 1.0]
    mirror["phase_shift"] = 0.25

    receiver = bpy.data.objects.new("Neuro3D Receiver", None)
    receiver.empty_display_type = "SPHERE"
    collection.objects.link(receiver)
    receiver.location = (0.0, 2.0, 0.0)
    _set_role(receiver, "receiver")
    receiver["radius"] = 0.2
    receiver["responsivity_rgb"] = [1.0, 1.0, 1.0]
    receiver["activation_threshold"] = 0.25
    receiver["response_gain"] = 1.0
    receiver["received_intensity"] = 0.0
    receiver["received_rgb_power"] = [0.0, 0.0, 0.0]
    receiver["received_phase"] = 0.0
    receiver["received_frequency"] = 0.0
    receiver["received_energy"] = 0.0
    receiver["activation"] = 0.0
    receiver["optical_hit"] = False
    receiver["optical_reason"] = "not_traced"

    return collection


def _one_role(collection, role: str):
    found = [obj for obj in collection.objects if obj.get("neuro3d_role") == role]
    if len(found) != 1:
        raise ValueError(f"Circuit requires exactly one {role}; found {len(found)}")
    return found[0]


def _world_point(obj):
    return tuple(float(v) for v in obj.matrix_world.translation)


def _world_z(obj):
    from mathutils import Vector

    return tuple(float(v) for v in (obj.matrix_world.to_quaternion() @ Vector((0.0, 0.0, 1.0))))


def trace_circuit(bpy, scene):
    """Read the saved scene, trace one CPU ray and update the receiver object."""

    name = scene.get("neuro3d_active_circuit")
    collection = bpy.data.collections.get(name) if name else None
    if collection is None:
        raise ValueError("No active Neuro3D optical circuit in this scene")
    bpy.context.view_layer.update()
    source_obj = _one_role(collection, "emitter")
    mirror_obj = _one_role(collection, "reflector")
    receiver_obj = _one_role(collection, "receiver")

    source = Emitter(
        _world_point(source_obj), _world_z(source_obj),
        float(source_obj["intensity"]), tuple(float(v) for v in source_obj["color_rgb"]),
        float(source_obj["frequency"]), float(source_obj["phase"]),
    )
    mirror = Reflector(
        _world_point(mirror_obj), _world_z(mirror_obj),
        float(mirror_obj["radius"]), tuple(float(v) for v in mirror_obj["reflectance_rgb"]),
        float(mirror_obj["phase_shift"]),
    )
    receiver = Receiver(
        _world_point(receiver_obj), float(receiver_obj["radius"]),
        tuple(float(v) for v in receiver_obj["responsivity_rgb"]),
        float(receiver_obj["activation_threshold"]), float(receiver_obj["response_gain"]),
    )
    result = trace_single_reflection(source, mirror, receiver)
    receiver_obj["optical_hit"] = result.hit
    receiver_obj["optical_reason"] = result.reason
    receiver_obj["optical_path_length"] = result.path_length
    receiver_obj["received_intensity"] = result.intensity
    receiver_obj["received_rgb_power"] = list(result.color_power)
    receiver_obj["received_phase"] = result.phase
    receiver_obj["received_frequency"] = result.frequency
    receiver_obj["received_energy"] = result.energy
    receiver_obj["activation"] = result.activation
    return result
