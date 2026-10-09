"""Capture represented Blender geometry and neural bindings, without running optics.

Original implementation. The optional Optics Simulator adapter reads public RNA
properties; no upstream GPL source is copied or bundled. Hex floats preserve the
values exposed by bpy, not unrepresented physical or pre-quantization geometry.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

SCHEMA = "neuro3d.blender_lab.scene_capture.v1"
NETWORK_SCHEMA = "neuro3d.blender_lab.network_bindings.v1"


class CaptureError(ValueError):
    """Capture cannot represent the requested state safely and completely."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise CaptureError(message)


def float_hex(value: Any) -> str:
    need(isinstance(value, (int, float)) and not isinstance(value, bool), "numeric scalar required")
    try:
        number = float(value)
    except OverflowError as exc:
        raise CaptureError("scalar exceeds finite float64 range") from exc
    need(math.isfinite(number), "nonfinite represented value")
    return number.hex()


def json_value(value: Any, depth: int = 0) -> Any:
    """Lossless JSON for supported ID/RNA values; unsupported data is rejected."""
    need(depth <= 12, "property nesting exceeds capture bound")
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        return {"float64_hex": float_hex(value)}
    if hasattr(value, "items"):
        return {str(key): json_value(item, depth + 1) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)) or hasattr(value, "to_list"):
        return [json_value(item, depth + 1) for item in value]
    raise CaptureError("unsupported property type: " + type(value).__name__)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def rna_values(group: Any, depth: int = 0) -> dict:
    """Read RNA scalars, vectors, nested property groups and ID references."""
    need(depth <= 8, "RNA nesting exceeds capture bound")
    result = {}
    for prop in sorted(group.bl_rna.properties, key=lambda item: item.identifier):
        key = prop.identifier
        if key == "rna_type":
            continue
        value = getattr(group, key)
        if prop.type == "POINTER":
            if value is None:
                result[key] = None
            elif hasattr(value, "name_full"):
                result[key] = {"id_reference": value.name_full,
                               "rna_type": value.bl_rna.identifier}
            else:
                result[key] = rna_values(value, depth + 1)
        elif prop.type == "COLLECTION":
            need(len(value) <= 4096, "RNA collection exceeds capture bound")
            result[key] = [rna_values(item, depth + 1) for item in value]
        elif getattr(prop, "is_array", False):
            result[key] = [json_value(item) for item in value]
        elif prop.type == "ENUM" and isinstance(value, set):
            result[key] = sorted(value)
        else:
            result[key] = json_value(value)
    return result


def matrix_values(matrix: Any) -> list:
    return [[float_hex(matrix[row][column]) for column in range(4)] for row in range(4)]


def _scalar_at(obj: dict, path: list) -> float:
    need(isinstance(path, list) and 1 <= len(path) <= 12, "invalid parameter path")
    need(path[0] in ("matrix_world", "custom_properties", "optics"), "unsupported parameter namespace")
    current: Any = obj
    try:
        for item in path:
            need(isinstance(item, (str, int)) and not isinstance(item, bool), "invalid path component")
            current = current[item]
    except (KeyError, IndexError, TypeError) as exc:
        raise CaptureError("unresolved parameter path") from exc
    if isinstance(current, dict) and set(current) == {"float64_hex"}:
        current = current["float64_hex"]
    if isinstance(current, str):
        try:
            number = float.fromhex(current)
        except ValueError as exc:
            raise CaptureError("parameter is not a hex float") from exc
        need(math.isfinite(number) and number.hex() == current, "noncanonical parameter float")
        return number
    need(isinstance(current, (float, int)) and not isinstance(current, bool), "parameter is not numeric")
    return float.fromhex(float_hex(current))


def resolve_network(network: Any, objects: list[dict]) -> dict | None:
    """Resolve ordered channels and trainable values from the captured scene."""
    if network is None:
        return None
    need(isinstance(network, dict) and set(network) == {
        "schema", "model", "inputs", "parameters", "detectors"}, "closed network binding schema required")
    need(network["schema"] == NETWORK_SCHEMA, "unknown network binding schema")
    need(isinstance(network["model"], str) and network["model"], "network model identifier required")
    by_name = {obj["name"]: obj for obj in objects}
    need(len(by_name) == len(objects), "duplicate scene object names")
    resolved = {"schema": NETWORK_SCHEMA, "model": network["model"],
                "inputs": [], "parameters": [], "detectors": []}
    for kind in ("inputs", "parameters", "detectors"):
        rows = network[kind]
        need(isinstance(rows, list) and 0 < len(rows) <= 4096, "nonempty bounded network bindings required")
        seen = set()
        for row in rows:
            keys = {"id", "object", "path", "unit", "bounds"} if kind == "parameters" else {"id", "object"}
            need(isinstance(row, dict) and set(row) == keys, "closed " + kind + " binding required")
            need(isinstance(row["id"], str) and row["id"] and row["id"] not in seen, "duplicate/invalid binding id")
            seen.add(row["id"])
            need(isinstance(row["object"], str) and row["object"] in by_name, "binding object missing from scene")
            obj = by_name[row["object"]]
            need(obj["evaluated_instance_count"] == 1,
                 "network binding requires exactly one evaluated instance; excluded or ambiguous object")
            item = dict(row)
            if kind == "parameters":
                need(isinstance(row["unit"], str) and row["unit"], "explicit parameter unit required")
                bounds = row["bounds"]
                need(isinstance(bounds, list) and len(bounds) == 2, "two parameter bounds required")
                low, high = (float.fromhex(float_hex(value)) for value in bounds)
                value = _scalar_at(obj, row["path"])
                need(low <= value <= high, "parameter outside declared bounds")
                item["bounds"] = [low.hex(), high.hex()]
                item["represented_value_hex"] = value.hex()
            resolved[kind].append(item)
    resolved["forward_executed"] = False
    resolved["training_executed"] = False
    resolved["optical_semantics_validated"] = False
    return resolved


def capture_scene(*, network: dict | None = None, max_objects: int = 2048,
                  max_vertices: int = 250_000, max_triangles: int = 500_000) -> dict:
    """Capture the active evaluated view layer. Does not change scene flags."""
    import bpy

    for value in (max_objects, max_vertices, max_triangles):
        need(type(value) is int and value > 0, "positive integer capture bounds required")
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    need(len(scene.objects) <= max_objects, "scene object bound exceeded")
    need(scene.unit_settings.scale_length > 0, "positive scene length scale required")
    def object_record(obj: Any, in_scene: bool) -> dict:
        need(obj.library is None, "linked library objects require an explicit library identity adapter")
        record = {"name": obj.name_full, "type": obj.type,
                  "matrix_world": matrix_values(obj.matrix_world),
                  "custom_properties": json_value(dict(obj.items())),
                  "collections": sorted(collection.name_full for collection in obj.users_collection),
                  "hide_render": bool(obj.hide_render), "hide_viewport": bool(obj.hide_viewport),
                  "direct_scene_member": in_scene, "evaluated_instance_count": 0}
        optics = getattr(obj, "optics", None)
        record["optics"] = rna_values(optics) if optics is not None else None
        return record
    objects = [object_record(obj, True) for obj in sorted(scene.objects, key=lambda item: item.name_full)]
    by_name = {obj["name"]: obj for obj in objects}
    need(len(by_name) == len(objects), "ambiguous object identities")
    instances = []
    meshes = {}
    vertex_count = triangle_count = 0
    # Non-mesh types are recorded explicitly, never silently called triangles.
    for instance in graph.object_instances:
        need(len(instances) < max_objects * 8, "dependency graph instance bound exceeded")
        evaluated = instance.object
        need(evaluated.original.library is None,
             "linked library instances require an explicit library identity adapter")
        source = evaluated.original.name_full
        if source not in by_name:
            need(len(objects) < max_objects, "instanced object metadata bound exceeded")
            extra = object_record(evaluated.original, False)
            objects.append(extra)
            by_name[source] = extra
        by_name[source]["evaluated_instance_count"] += 1
        record = {"object": source, "is_instance": bool(instance.is_instance),
                  "persistent_id": list(instance.persistent_id),
                  "matrix_world": matrix_values(instance.matrix_world), "mesh_sha256": None,
                  "geometry_type": evaluated.type}
        if evaluated.type == "MESH":
            mesh = evaluated.to_mesh(preserve_all_data_layers=False, depsgraph=graph)
            try:
                need(mesh is not None, "evaluated mesh unavailable")
                mesh.calc_loop_triangles()
                vertex_count += len(mesh.vertices)
                triangle_count += len(mesh.loop_triangles)
                need(vertex_count <= max_vertices and triangle_count <= max_triangles,
                     "evaluated geometry bound exceeded")
                payload = {
                    "vertices_local_hex": [[float_hex(axis) for axis in vertex.co] for vertex in mesh.vertices],
                    "triangles": [{"vertices": list(tri.vertices), "material_index": tri.material_index,
                                   "polygon_index": tri.polygon_index} for tri in mesh.loop_triangles],
                    "material_slots": [material.name_full if material else None for material in mesh.materials],
                }
                mesh_hash = digest(payload)
                meshes[mesh_hash] = payload
                record["mesh_sha256"] = mesh_hash
            finally:
                evaluated.to_mesh_clear()
        instances.append(record)
    # Evaluation order is not a scientific identity; retain instance identities and sort records.
    instances.sort(key=canonical_bytes)
    objects.sort(key=lambda item: item["name"])
    units = {"system": scene.unit_settings.system,
             "scale_length_metres_per_BU_hex": float_hex(scene.unit_settings.scale_length),
             "length_unit": scene.unit_settings.length_unit,
             "physical_unit_intent_declared": scene.unit_settings.system != "NONE"}
    optics = getattr(scene, "optics", None)
    state = {"scene_name": scene.name_full, "view_layer": bpy.context.view_layer.name,
             "frame": scene.frame_current, "subframe_hex": float_hex(scene.frame_subframe),
             "units": units, "scene_custom_properties": json_value(dict(scene.items())),
             "scene_optics": rna_values(optics) if optics is not None else None,
             "objects": objects, "instances": instances, "meshes": meshes,
             "network": resolve_network(network, objects)}
    return {"schema": SCHEMA, "state_sha256": digest(state), "state": state,
            "provenance": {"blender_version": bpy.app.version_string,
                           "blender_build_hash": bpy.app.build_hash.decode("ascii"),
                           "source_file": bpy.data.filepath},
            "scope": {"represented_bpy_values_preserved": True, "decimal_rounding_added": False,
                      "mesh_geometry_only": True, "render_materials_interpreted_as_optics": False,
                      "non_mesh_geometry_fully_captured": False,
                      "physical_error_certified": False, "optical_forward_executed": False,
                      "training_executed": False, "gpu_executed": False,
                      "path_completeness_certified": False}}


def validate_capture(snapshot: dict) -> None:
    """Check the content fingerprint. This is integrity, not a physics certificate."""
    need(isinstance(snapshot, dict) and snapshot.get("schema") == SCHEMA, "unknown capture schema")
    need(snapshot.get("state_sha256") == digest(snapshot["state"]), "capture fingerprint mismatch")
    for mesh_hash, mesh in snapshot["state"]["meshes"].items():
        need(digest(mesh) == mesh_hash, "mesh fingerprint mismatch")
    for item in snapshot["state"]["instances"]:
        need(item["mesh_sha256"] is None or item["mesh_sha256"] in snapshot["state"]["meshes"],
             "unresolved mesh reference")


def write_capture(path: Path, snapshot: dict) -> None:
    validate_capture(snapshot)
    need(path.parent.is_dir(), "capture output parent must exist")
    raw = canonical_bytes(snapshot)
    need(len(raw) <= 128 * 2**20, "capture output exceeds 128 MiB bound")
    with path.open("xb") as stream:
        stream.write(raw)
