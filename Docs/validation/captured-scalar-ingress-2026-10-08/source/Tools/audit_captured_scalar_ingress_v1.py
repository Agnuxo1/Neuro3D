"""Independent input-preservation audit. Does not import producer or run optics."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def checksum(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path):
    raw = path.read_bytes()
    need(len(raw) <= 128 * 2**20, "audit input size bound")
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    return value, hashlib.sha256(raw).hexdigest()


def decode(value):
    if isinstance(value, dict):
        if set(value) == {"numerator", "denominator"}:
            need(type(value["numerator"]) is int and type(value["denominator"]) is int and value["denominator"] > 0,
                 "typed rational wire")
            return F(value["numerator"], value["denominator"])
        return {key: decode(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decode(item) for item in value]
    return value


def h(value):
    number = float.fromhex(value)
    need(math.isfinite(number) and number.hex() == value, "canonical finite captured hex")
    return F(number)


def point(matrix, local):
    return [sum(matrix[row][column] * local[column] for column in range(3)) + matrix[row][3] for row in range(3)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("capture", "scene", "semantics", "fields", "out"):
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args()
    capture, capture_sha = load(args.capture)
    wire, scene_sha = load(args.scene)
    semantics, semantics_sha = load(args.semantics)
    fields, fields_sha = load(args.fields)
    packet = decode(wire)
    state = capture["state"]
    need(capture["state_sha256"] == checksum(state) == semantics["capture_state_sha256"], "captured state identity")
    metadata = packet["blender_lab_ingress"]
    need(metadata["input_file_sha256"] == {"capture": capture_sha, "semantics": semantics_sha, "fields": fields_sha},
         "input byte fingerprints")
    need(metadata["capture_state_sha256"] == capture["state_sha256"] and metadata["semantics_sha256"] == checksum(semantics),
         "model/capture identities")
    need(packet["lambda_BU"] == h(semantics["wavelength_BU_hex"]), "declared wavelength preserved")
    objects = {obj["name"]: obj for obj in state["objects"]}
    need(len(objects) == len(state["objects"]), "unambiguous source object names")
    selected = {name for name, obj in objects.items() if semantics["optical_collection"] in obj["collections"]}
    need(selected == set(semantics["objects"]) == set(packet["objects"]), "all declared optical surfaces preserved")
    need(set(metadata["excluded_geometry_objects"]) == set(objects) - selected, "explicit exclusion inventory")
    need(metadata["network_bindings"] == state.get("network"), "captured network bindings preserved")
    instances = {}
    for item in state["instances"]:
        instances.setdefault(item["object"], []).append(item)
    vertices_checked = 0
    for name, observed in packet["objects"].items():
        need(len(instances[name]) == 1, "one evaluated optical instance required")
        instance = instances[name][0]
        mesh_hash = instance["mesh_sha256"]
        mesh = state["meshes"][mesh_hash]
        need(checksum(mesh) == mesh_hash, "captured mesh identity")
        matrix = [[h(v) for v in row] for row in instance["matrix_world"]]
        need(matrix[3] == [0, 0, 0, 1], "affine captured matrix")
        need(observed["faces"] == [triangle["vertices"] for triangle in mesh["triangles"]], "triangle indices preserved")
        need(len(observed["vertices_world_BU"]) == len(mesh["vertices_local_hex"]), "all vertices preserved")
        for local, actual in zip(mesh["vertices_local_hex"], observed["vertices_world_BU"], strict=True):
            need(point(matrix, [h(v) for v in local]) == actual, "exact affine coordinate preservation")
            vertices_checked += 1
        declared = semantics["objects"][name]
        need(observed["kind"] == declared["kind"] == objects[name]["custom_properties"]["kind"], "captured role preserved")
        if declared["kind"] == "mirror":
            need(observed["phase_rad"] == h(declared["phase_rad_hex"]), "declared mirror phase preserved")
        elif declared["kind"] == "bs":
            need(observed["power_transmittance"] == h(declared["power_transmittance_hex"]), "declared splitter preserved")
        else:
            need(observed["mode_origin_BU"] == point(matrix, [h(v) for v in declared["mode_origin_local_hex"]]), "terminal reference preserved")
            need(observed["mode_direction"] == [h(v) for v in declared["mode_direction_world_hex"]], "terminal direction preserved")
    source_definitions = {row["id"]: row for row in semantics["sources"]}
    need(len(source_definitions) == len(semantics["sources"]) == len(packet["sources"]), "all source identities preserved")
    need(set(fields) == set(source_definitions), "declared source fields")
    legacy = {row["id"]: row for row in json.loads(state.get("scene_custom_properties", {}).get("sources", "[]"))}
    differences = []
    for source in packet["sources"]:
        definition = source_definitions.pop(source["id"])
        need(len(instances[definition["object"]]) == 1, "one evaluated source instance")
        matrix = [[h(v) for v in row] for row in instances[definition["object"]][0]["matrix_world"]]
        need(source["position_BU"] == point(matrix, [F(0)] * 3), "captured source origin preserved")
        need(source["direction"] == [h(v) for v in definition["direction_world_hex"]], "declared source direction preserved")
        need(source["field_reim"] == [F(v) for v in fields[source["id"]]], "input field preserved")
        if source["id"] in legacy:
            differences.extend(abs(v - F(w)) for v, w in zip(source["position_BU"], legacy[source["id"]]["p"], strict=True))
    need(not source_definitions, "no omitted source")
    scope = metadata["scope"]
    need(not any(scope[key] for key in ("optical_forward_executed", "field_certified", "decision_certified", "training_executed", "gpu_executed")),
         "ingress-only scope must not claim propagated or certified outputs")
    maximum = max(differences, default=F(0))
    report = {"schema": "neuro3d.blender_lab.scalar_ingress_software_audit.v1", "status": "PASS", "producer_imported": False,
              "objects": len(packet["objects"]), "triangles": sum(len(obj["faces"]) for obj in packet["objects"].values()),
              "sources": len(packet["sources"]), "checked_vertices": vertices_checked, "checked_world_coordinates": 3 * vertices_checked,
              "faces_preserved": True, "exact_affine_coordinates_preserved": True, "source_positions_from_captured_instances": True,
              "legacy_source_json_difference_max_BU": {"numerator": maximum.numerator, "denominator": maximum.denominator},
              "legacy_source_json_difference_max_BU_display": float(maximum),
              "scope": "Input-preservation software audit only; difference to legacy source descriptors is not a complete native/phase/field bound.",
              "optical_forward_executed": False, "field_certified": False, "training_executed": False, "gpu_executed": False,
              "input_sha256": {"capture": capture_sha, "scene": scene_sha, "semantics": semantics_sha, "fields": fields_sha}}
    need(args.out.parent.is_dir(), "existing audit output parent required")
    with args.out.open("xb") as stream:
        stream.write((json.dumps(report, indent=2, allow_nan=False) + "\n").encode())
    print(json.dumps({"status": "PASS", "coordinates_checked": 3 * vertices_checked,
                      "source_descriptor_difference_max_BU": float(maximum), "optical_forward_executed": False}))


if __name__ == "__main__":
    main()
