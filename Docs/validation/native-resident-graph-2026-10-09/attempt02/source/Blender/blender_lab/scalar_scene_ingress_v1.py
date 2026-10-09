"""Exact affine ingress from captured Blender data to the scalar CPU scene.

Prepares/admit inputs only. No ray tracing, field propagation or training runs.
The represented model uses exact affine transforms of exposed bpy numbers;
it does not claim to reproduce a native floating-point transform pipeline.
"""
from fractions import Fraction as F
import math

from .scene_capture_v1 import digest, need, validate_capture

SCHEMA = "neuro3d.blender_lab.scalar_semantics.v1"


def represented_hex(value):
    need(isinstance(value, str) and len(value) <= 64, "canonical hex scalar required")
    try:
        number = float.fromhex(value)
    except (ValueError, OverflowError) as error:
        raise ValueError("invalid represented hex scalar") from error
    need(math.isfinite(number) and number.hex() == value, "canonical finite hex scalar required")
    return F(number)


def hex_vector(values):
    need(isinstance(values, list) and len(values) == 3, "three hex coordinates required")
    return tuple(represented_hex(value) for value in values)


def affine_matrix(value):
    need(isinstance(value, list) and len(value) == 4 and all(isinstance(row, list) and len(row) == 4 for row in value),
         "captured 4x4 matrix required")
    matrix = tuple(tuple(represented_hex(axis) for axis in row) for row in value)
    need(matrix[3] == (0, 0, 0, 1), "affine homogeneous matrix required")
    return matrix


def transform(matrix, local):
    return tuple(sum((matrix[row][column] * local[column] for column in range(3)), matrix[row][3])
                 for row in range(3))


def input_real(value):
    need(isinstance(value, (int, float, F)) and not isinstance(value, bool), "explicit numeric input field required")
    if isinstance(value, float):
        need(math.isfinite(value), "finite input field required")
    return F(value)


def prepare_scalar_scene(capture, semantics, amplitudes, *, max_objects=256, max_triangles=8192):
    validate_capture(capture)
    need(type(max_objects) is int and max_objects > 0 and type(max_triangles) is int and max_triangles > 0,
         "positive integer ingress bounds required")
    need(isinstance(semantics, dict) and set(semantics) == {
        "schema", "model", "capture_state_sha256", "optical_collection", "wavelength_BU_hex", "objects", "sources"},
         "closed scalar semantics contract required")
    need(semantics["schema"] == SCHEMA and semantics["model"] == "LOSSLESS_SCALAR_PLANAR_V1",
         "unsupported scalar optical model")
    need(semantics["capture_state_sha256"] == capture["state_sha256"], "semantics/capture fingerprint mismatch")
    wavelength = represented_hex(semantics["wavelength_BU_hex"])
    need(wavelength > 0, "positive declared wavelength required")
    state = capture["state"]
    objects = {obj["name"]: obj for obj in state["objects"]}
    need(len(objects) == len(state["objects"]), "unambiguous object identities required")
    collection = semantics["optical_collection"]
    need(isinstance(collection, str) and collection, "explicit optical collection required")
    selected = {name for name, obj in objects.items() if collection in obj["collections"]}
    declared = semantics["objects"]
    need(isinstance(declared, dict) and 0 < len(declared) <= max_objects, "bounded declared optical objects required")
    need(selected == set(declared), "every object in the optical collection must have explicit semantics")
    recognized = {name for name, obj in objects.items()
                  if obj["custom_properties"].get("kind") in ("mirror", "bs", "det", "escape")
                  and obj["evaluated_instance_count"] > 0}
    need(recognized <= selected, "active optical roles outside the declared flat collection")
    instances = {}
    for instance in state["instances"]:
        instances.setdefault(instance["object"], []).append(instance)
    output_objects = {}
    triangle_count = 0
    for name in sorted(declared):
        definition = declared[name]
        need(isinstance(definition, dict), "optical object semantics required")
        kind = definition.get("kind")
        need(kind in ("mirror", "bs", "det", "escape"), "unsupported optical role")
        keys = {"kind", "phase_rad_hex"} if kind == "mirror" else {"kind", "power_transmittance_hex"} if kind == "bs" else {
            "kind", "mode_origin_local_hex", "mode_direction_world_hex"}
        need(set(definition) == keys, "all optical parameters must be explicitly declared")
        need(objects[name]["custom_properties"].get("kind") == kind, "declared/captured optical role mismatch")
        active = instances.get(name, [])
        need(len(active) == 1 and objects[name]["evaluated_instance_count"] == 1,
             "one active evaluated instance per optical element required")
        instance = active[0]
        need(instance["geometry_type"] == "MESH" and instance["mesh_sha256"] is not None,
             "optical element requires captured evaluated triangles")
        matrix = affine_matrix(instance["matrix_world"])
        mesh = state["meshes"][instance["mesh_sha256"]]
        vertices = [transform(matrix, hex_vector(vertex)) for vertex in mesh["vertices_local_hex"]]
        faces = [triangle["vertices"] for triangle in mesh["triangles"]]
        triangle_count += len(faces)
        need(triangle_count <= max_triangles, "scalar ingress triangle bound exceeded")
        record = {"kind": kind, "vertices_world_BU": vertices, "faces": faces}
        if kind == "mirror":
            record["phase_rad"] = represented_hex(definition["phase_rad_hex"])
        elif kind == "bs":
            transmission = represented_hex(definition["power_transmittance_hex"])
            need(0 <= transmission <= 1, "power transmittance outside [0,1]")
            record["power_transmittance"] = transmission
        else:
            record["mode_origin_BU"] = transform(matrix, hex_vector(definition["mode_origin_local_hex"]))
            record["mode_direction"] = hex_vector(definition["mode_direction_world_hex"])
            need(any(record["mode_direction"]), "nonzero terminal mode direction required")
        output_objects[name] = record
    need(any(record["kind"] in ("det", "escape") for record in output_objects.values()),
         "declared terminal required")
    definitions = semantics["sources"]
    need(isinstance(definitions, list) and 0 < len(definitions) <= 16, "bounded explicit sources required")
    need(isinstance(amplitudes, dict), "explicit source-field mapping required")
    sources = []
    source_ids = set()
    for definition in definitions:
        need(isinstance(definition, dict) and set(definition) == {"id", "object", "direction_world_hex"},
             "closed source binding required")
        sid, name = definition["id"], definition["object"]
        need(isinstance(sid, str) and sid and sid not in source_ids, "unique source IDs required")
        source_ids.add(sid)
        need(isinstance(name, str) and name in objects and name not in selected, "source object must be separate from optical surfaces")
        active = instances.get(name, [])
        need(len(active) == 1 and objects[name]["evaluated_instance_count"] == 1, "unambiguous active source instance required")
        origin = transform(affine_matrix(active[0]["matrix_world"]), (F(0), F(0), F(0)))
        direction = hex_vector(definition["direction_world_hex"])
        need(any(direction), "nonzero source direction required")
        field = amplitudes.get(sid)
        need(isinstance(field, (list, tuple)) and len(field) == 2, "explicit real/imag source field required")
        sources.append({"id": sid, "position_BU": origin, "direction": direction,
                        "field_reim": tuple(input_real(v) for v in field)})
    need(set(amplitudes) == source_ids, "source-field IDs must match declared sources")
    network = state.get("network")
    if network is not None:
        network_sources = {row["id"]: row["object"] for row in network["inputs"]}
        need(network_sources == {row["id"]: row["object"] for row in definitions},
             "captured neural input bindings must match optical sources")
        need(all(row["object"] in output_objects and output_objects[row["object"]]["kind"] == "det"
                 for row in network["detectors"]), "neural detectors must bind admitted optical detectors")
        need(all(row["object"] in output_objects for row in network["parameters"]),
             "neural parameters must bind admitted optical surfaces")
    packet = {"schema": "exp005-readback-v2", "lambda_BU": wavelength,
              "objects": output_objects, "sources": sources, "undeclared_meshes": []}
    # Structural admission to the existing engine; no trace_scene() is called.
    from Blender.benchmarks.capacity_audit.robust_multipath_v1 import geometry
    geometry(packet)
    packet["blender_lab_ingress"] = {
        "schema": "neuro3d.blender_lab.scalar_ingress.v1", "capture_state_sha256": capture["state_sha256"],
        "semantics_sha256": digest(semantics), "selected_collection": collection,
        "excluded_geometry_objects": sorted(set(objects) - selected),
        "counts": {"objects": len(output_objects), "triangles": triangle_count, "sources": len(sources)},
        "network_bindings": network,
        "source_position_policy": "CAPTURED_EVALUATED_INSTANCE_TRANSLATION",
        "mirror_rule": "minus_one_times_exp_i_declared_phase", "splitter_rule": "sqrt_tau_and_i_sqrt_one_minus_tau",
        "scope": {"exact_affine_represented_geometry": True, "native_transform_rounding_reproduced": False,
                  "structural_geometry_admitted": True, "optical_forward_executed": False,
                  "field_certified": False, "decision_certified": False, "training_executed": False,
                  "gpu_executed": False, "physical_optics_certified": False}}
    return packet


def rational_wire(value):
    if isinstance(value, F):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, dict):
        return {key: rational_wire(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [rational_wire(item) for item in value]
    return value
