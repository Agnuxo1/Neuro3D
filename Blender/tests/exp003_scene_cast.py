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
