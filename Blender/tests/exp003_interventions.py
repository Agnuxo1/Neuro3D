"""Edit existing EXP-003 scene objects; never rebuild a treatment scene."""

from __future__ import annotations


def place_delay_pair(objects, fixture, delay_d=0.0, sham_z=0.0):
    """Move the two existing mirrors from frozen base coordinates."""
    for role in fixture["delay_pair"]:
        base = fixture[role]["position"]
        objects[role].location = (base[0] + delay_d, base[1], base[2] + sham_z)


def ablate_existing(scene, objects, role):
    """Unlink the existing mesh from the scene/depsgraph, not hide_render."""
    obj = objects[role]
    scene.collection.objects.unlink(obj)
    return obj
