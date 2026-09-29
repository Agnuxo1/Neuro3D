"""Thin Blender ray_cast boundary for EXP-003; no analytic fallback.

The scene builder must label each optical mesh with ``neuro3d_role``.
Importing this module does not import or launch Blender.
"""

from __future__ import annotations


def make_scene_cast(scene, depsgraph, vector_factory):
    """Adapt Blender's *nearest* scene hit to the measured path accumulator.

    ``vector_factory`` is ``mathutils.Vector`` in Blender and injectable in
    light unit tests. Unknown objects are reported rather than skipped.
    """
    def cast(origin, direction):
        hit, point, normal, _face, obj, _matrix = scene.ray_cast(
            depsgraph, vector_factory(origin), vector_factory(direction)
        )
        if not hit:
            return None
        role = obj.get("neuro3d_role")
        if not role:
            role = f"unmapped:{obj.name}"
        return str(role), tuple(point), tuple(normal)

    return cast


def observe_scene_disks(scene):
    """Read face geometry and world transforms from actual Blender meshes.

    No values are read from cached fixture properties on objects. Unexpected
    mesh objects enter the result and are rejected by the fixture guard.
    """
    from mathutils import Vector

    observed = {}
    basis = (Vector((1., 0., 0.)), Vector((0., 1., 0.)), Vector((0., 0., 1.)))
    for obj in scene.objects:
        if obj.type != "MESH":
            continue
        role = obj.get("neuro3d_role") or f"unmapped:{obj.name}"
        if role in observed:
            raise ValueError(f"Duplicate optical role: {role}")
        mesh = obj.data
        matrix = obj.matrix_world.to_3x3()
        vertices = tuple(tuple(v.co) for v in mesh.vertices)
        if len(mesh.polygons) == 1:
            normal = tuple((matrix.inverted().transposed() @ mesh.polygons[0].normal).normalized())
        else:
            normal = (float("nan"),) * 3
        observed[role] = {
            "position": tuple(obj.matrix_world.translation),
            "normal": normal,
            "radius": max((v.co.x**2 + v.co.y**2)**.5 for v in mesh.vertices) if vertices else float("nan"),
            "faces": len(mesh.polygons),
            "vertices": len(mesh.vertices),
            "modifiers": bool(obj.modifiers),
            "scale": tuple(obj.scale),
            "parented": obj.parent is not None,
            "world_axes": tuple(tuple(matrix @ axis) for axis in basis),
            "local_vertices": vertices,
        }
    return observed
