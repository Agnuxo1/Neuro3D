"""Build only the frozen EXP-003 optical disks in an empty Blender scene.

Construction is separate from validation: after ``view_layer.update()`` the
runner must call ``observe_scene_disks`` and ``validate_observed_disks``.
"""

from __future__ import annotations

import math

from exp003_fixture_guard import OPTICAL, load_locked_fixture

SIDES = 64


def disk_vertices(radius, sides=SIDES):
    if not math.isfinite(radius) or radius <= 0 or sides < 32:
        raise ValueError("Invalid optical disk")
    return tuple((radius * math.cos(2 * math.pi * i / sides),
                  radius * math.sin(2 * math.pi * i / sides), 0.0)
                 for i in range(sides))


def build_scene_disks(scene, fixture_path, delay_d=0.0, sham_z=0.0,
                      removed=None):
    """Create a single flat face per role; never add a visual helper mesh."""
    import bpy
    from mathutils import Vector

    fixture, digest = load_locked_fixture(fixture_path)
    if removed is not None and removed not in OPTICAL:
        raise ValueError("Unknown ablation role")
    if any(obj.type == "MESH" for obj in scene.objects):
        raise ValueError("EXP-003 needs a scene without preexisting meshes")
    objects = {}
    for role in OPTICAL:
        if role == removed:
            continue
        spec = fixture[role]
        mesh = bpy.data.meshes.new(f"EXP003_{role}_mesh")
        mesh.from_pydata(disk_vertices(float(spec["radius"])), [],
                         [tuple(range(SIDES))])
        mesh.update()
        obj = bpy.data.objects.new(f"EXP003_{role}", mesh)
        scene.collection.objects.link(obj)
        centre = tuple(spec["position"])
        if role in fixture["delay_pair"]:
            centre = (centre[0] + delay_d, centre[1], centre[2] + sham_z)
        obj.location = centre
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = Vector((0., 0., 1.)).rotation_difference(
            Vector(spec["normal"]))
        obj.scale = (1., 1., 1.)
        obj["neuro3d_role"] = role
        objects[role] = obj
    return fixture, digest, objects
