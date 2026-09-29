"""Build candidate EXP-004 lattice disks from a separately frozen fixture.

This module only constructs scene geometry. It does not infer fields,
validate ray routes, or claim a multicell optical computation. The fixture
must be reviewed and pinned by SHA-256 before any gate measurement.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from exp003_blender_build import SIDES, disk_vertices


def _vector3(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"Invalid {name}")
    result = tuple(float(x) for x in value)
    if not all(math.isfinite(x) for x in result):
        raise ValueError(f"Non-finite {name}")
    return result


def validate_lattice_fixture(fixture):
    """Fail closed on malformed candidate geometry; no optical validation."""
    k = fixture.get("K")
    if not isinstance(k, int) or isinstance(k, bool) or k < 2:
        raise ValueError("Invalid lattice size")
    disks, sources = fixture.get("disks"), fixture.get("sources")
    if not isinstance(disks, list) or not isinstance(sources, list):
        raise ValueError("Missing disks or sources")
    if len(disks) != 6 * k * k + 2 * k or len(sources) != 2 * k:
        raise ValueError("Unexpected disk or source count")
    expected = {f"c{i}{j}.{role}" for i in range(k) for j in range(k)
                for role in ("bs1", "r1", "r2", "f1", "m2", "bs2")}
    expected |= {f"det.R{j}" for j in range(k)}
    expected |= {f"det.C{i}" for i in range(k)}
    ids = [item.get("id") for item in disks]
    if len(set(ids)) != len(ids) or set(ids) != expected:
        raise ValueError("Missing, extra or duplicate disk roles")
    for item in disks:
        kind = item.get("kind")
        if kind not in ("bs", "mirror", "det"):
            raise ValueError("Invalid disk kind")
        role = item["id"].split(".", 1)[-1]
        expected_kind = ("det" if item["id"].startswith("det.") else
                         "bs" if role in ("bs1", "bs2") else "mirror")
        if kind != expected_kind:
            raise ValueError("Disk kind differs from role")
        _vector3(item.get("p"), "disk position")
        normal = _vector3(item.get("n"), "disk normal")
        if abs(math.sqrt(sum(x * x for x in normal)) - 1) > 1e-8:
            raise ValueError("Disk normal is not unit")
        radius = float(item.get("r", float("nan")))
        if not math.isfinite(radius) or radius <= 0:
            raise ValueError("Invalid disk radius")
    source_ids = [item.get("id") for item in sources]
    if len(set(source_ids)) != len(source_ids) or set(source_ids) != (
        {f"r{j}" for j in range(k)} | {f"c{i}" for i in range(k)}
    ):
        raise ValueError("Missing, extra or duplicate sources")
    for item in sources:
        _vector3(item.get("p"), "source position")
        direction = _vector3(item.get("d"), "source direction")
        if abs(math.sqrt(sum(x * x for x in direction)) - 1) > 1e-8:
            raise ValueError("Source direction is not unit")
    return fixture


def load_lattice_fixture(path, expected_sha256):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError("Candidate fixture SHA-256 mismatch")
    return validate_lattice_fixture(json.loads(raw)), digest


def build_lattice_disks(scene, fixture):
    """Create flat face meshes only; caller must read back and ray-cast."""
    import bpy
    from mathutils import Vector

    validate_lattice_fixture(fixture)
    if any(obj.type == "MESH" for obj in scene.objects):
        raise ValueError("Scene contains preexisting mesh")
    result = {}
    for spec in fixture["disks"]:
        role = spec["id"]
        mesh = bpy.data.meshes.new(f"EXP004_{role}_mesh")
        mesh.from_pydata(disk_vertices(float(spec["r"])), [],
                         [tuple(range(SIDES))])
        mesh.update()
        obj = bpy.data.objects.new(f"EXP004_{role}", mesh)
        scene.collection.objects.link(obj)
        obj.location = _vector3(spec["p"], "disk position")
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = Vector((0., 0., 1.)).rotation_difference(
            Vector(spec["n"]))
        obj.scale = (1., 1., 1.)
        obj["neuro3d_role"] = role
        result[role] = obj
    return result
