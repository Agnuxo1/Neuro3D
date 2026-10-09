"""Input conversion/admission checks. No optical propagation is executed."""
import copy
from fractions import Fraction as F
import unittest

from Blender.blender_lab.scene_capture_v1 import SCHEMA as CAPTURE_SCHEMA, digest
from Blender.blender_lab.scalar_scene_ingress_v1 import SCHEMA, prepare_scalar_scene, rational_wire


def matrix(translation=(0, 0, 0)):
    return [[float((1 if row == column else 0) if column != 3 or row == 3 else translation[row]).hex()
             for column in range(4)] for row in range(4)]


def fixture():
    mesh = {"vertices_local_hex": [[float(v).hex() for v in vertex] for vertex in
                                   [(0, -2, -2), (0, 2, -2), (0, 0, 2)]],
            "triangles": [{"vertices": [0, 1, 2], "material_index": 0, "polygon_index": 0}],
            "material_slots": []}
    mesh_hash = digest(mesh)
    objects = [{"name": "source", "collections": [], "custom_properties": {}, "evaluated_instance_count": 1},
               {"name": "detector", "collections": ["Optics"], "custom_properties": {"kind": "det"},
                "evaluated_instance_count": 1}]
    instances = [{"object": "source", "matrix_world": matrix(), "geometry_type": "EMPTY", "mesh_sha256": None},
                 {"object": "detector", "matrix_world": matrix((2, 0, 0)), "geometry_type": "MESH", "mesh_sha256": mesh_hash}]
    state = {"objects": objects, "instances": instances, "meshes": {mesh_hash: mesh}}
    capture = {"schema": CAPTURE_SCHEMA, "state": state, "state_sha256": digest(state)}
    semantics = {"schema": SCHEMA, "model": "LOSSLESS_SCALAR_PLANAR_V1", "capture_state_sha256": capture["state_sha256"],
                 "optical_collection": "Optics", "wavelength_BU_hex": (0.125).hex(),
                 "objects": {"detector": {"kind": "det", "mode_origin_local_hex": [float(0).hex()] * 3,
                                          "mode_direction_world_hex": [float(v).hex() for v in (1, 0, 0)]}},
                 "sources": [{"id": "x", "object": "source", "direction_world_hex": [float(v).hex() for v in (1, 0, 0)]}]}
    return capture, semantics, {"x": [1, 0]}


def rehash(capture, semantics):
    capture["state_sha256"] = digest(capture["state"])
    semantics["capture_state_sha256"] = capture["state_sha256"]


class ScalarIngressTests(unittest.TestCase):
    def test_admitted_geometry_no_forward(self):
        scene = prepare_scalar_scene(*fixture())
        self.assertEqual(scene["objects"]["detector"]["vertices_world_BU"][0], (F(2), F(-2), F(-2)))
        self.assertFalse(scene["blender_lab_ingress"]["scope"]["optical_forward_executed"])
        self.assertFalse(scene["blender_lab_ingress"]["scope"]["field_certified"])

    def test_affine_transform_no_added_float_rounding(self):
        capture, semantics, fields = fixture()
        old_hash = next(iter(capture["state"]["meshes"]))
        mesh = capture["state"]["meshes"].pop(old_hash)
        for vertex in mesh["vertices_local_hex"]:
            vertex[0] = (0.1).hex()
        mesh_hash = digest(mesh)
        capture["state"]["meshes"][mesh_hash] = mesh
        capture["state"]["instances"][1]["mesh_sha256"] = mesh_hash
        transform = capture["state"]["instances"][1]["matrix_world"]
        transform[0][0], transform[0][3] = (0.1).hex(), (0.2).hex()
        semantics["objects"]["detector"]["mode_origin_local_hex"][0] = (0.1).hex()
        rehash(capture, semantics)
        scene = prepare_scalar_scene(capture, semantics, fields)
        x = scene["objects"]["detector"]["vertices_world_BU"][0][0]
        self.assertEqual(x, F(0.1) * F(0.1) + F(0.2))
        self.assertNotEqual(x, F(0.1 * 0.1 + 0.2))

    def test_captured_source_edit_reaches_input(self):
        capture, semantics, fields = fixture()
        capture["state"]["instances"][0]["matrix_world"][0][3] = (0.25).hex()
        rehash(capture, semantics)
        scene = prepare_scalar_scene(capture, semantics, fields)
        self.assertEqual(scene["sources"][0]["position_BU"], (F(1, 4), F(0), F(0)))

    def test_rational_wire_roundtrip(self):
        scene = prepare_scalar_scene(*fixture())
        wire = rational_wire(scene)
        coordinate = wire["objects"]["detector"]["vertices_world_BU"][0][0]
        self.assertEqual(coordinate, {"numerator": 2, "denominator": 1})

    def test_tamper_and_wrong_capture_pin_rejected(self):
        for case in ("tamper", "pin"):
            capture, semantics, fields = fixture()
            if case == "tamper":
                capture["state"]["instances"][0]["matrix_world"][0][3] = (0.5).hex()
            else:
                semantics["capture_state_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                prepare_scalar_scene(capture, semantics, fields)

    def test_missing_implicit_physics_rejected(self):
        for key in ("wavelength_BU_hex", "optical_collection", "objects"):
            capture, semantics, fields = fixture()
            del semantics[key]
            with self.assertRaises(ValueError):
                prepare_scalar_scene(capture, semantics, fields)

    def test_noncanonical_nonfinite_or_zero_wavelength_rejected(self):
        for value in ("0.125", "inf", (0.0).hex(), (-0.125).hex()):
            capture, semantics, fields = fixture()
            semantics["wavelength_BU_hex"] = value
            with self.assertRaises(ValueError):
                prepare_scalar_scene(capture, semantics, fields)

    def test_role_mismatch_and_undeclared_surface_rejected(self):
        capture, semantics, fields = fixture()
        semantics["objects"]["detector"]["kind"] = "mirror"
        with self.assertRaises(ValueError):
            prepare_scalar_scene(capture, semantics, fields)
        capture, semantics, fields = fixture()
        capture["state"]["objects"].append({"name": "rogue", "collections": ["Optics"],
                                            "custom_properties": {"kind": "mirror"}, "evaluated_instance_count": 1})
        rehash(capture, semantics)
        with self.assertRaises(ValueError):
            prepare_scalar_scene(capture, semantics, fields)

    def test_optical_role_outside_collection_rejected(self):
        capture, semantics, fields = fixture()
        capture["state"]["objects"].append({"name": "rogue", "collections": ["Other"],
                                            "custom_properties": {"kind": "mirror"}, "evaluated_instance_count": 1})
        rehash(capture, semantics)
        with self.assertRaises(ValueError):
            prepare_scalar_scene(capture, semantics, fields)

    def test_excluded_or_ambiguous_instance_rejected(self):
        for count in (0, 2):
            capture, semantics, fields = fixture()
            capture["state"]["objects"][1]["evaluated_instance_count"] = count
            rehash(capture, semantics)
            with self.assertRaises(ValueError):
                prepare_scalar_scene(capture, semantics, fields)

    def test_projective_matrix_rejected(self):
        capture, semantics, fields = fixture()
        capture["state"]["instances"][1]["matrix_world"][3][0] = (1.0).hex()
        rehash(capture, semantics)
        with self.assertRaises(ValueError):
            prepare_scalar_scene(capture, semantics, fields)

    def test_source_fields_and_directions_fail_closed(self):
        for case in ("extra", "missing", "nan", "zero_direction"):
            capture, semantics, fields = fixture()
            if case == "extra": fields["unknown"] = [1, 0]
            if case == "missing": del fields["x"]
            if case == "nan": fields["x"] = [float("nan"), 0]
            if case == "zero_direction": semantics["sources"][0]["direction_world_hex"] = [float(0).hex()] * 3
            with self.assertRaises(ValueError):
                prepare_scalar_scene(capture, semantics, fields)

    def test_bounds_and_degenerate_triangles_rejected(self):
        for case in ("bound", "degenerate"):
            capture, semantics, fields = fixture()
            if case == "bound":
                with self.assertRaises(ValueError): prepare_scalar_scene(capture, semantics, fields, max_objects=0)
            else:
                old_hash = next(iter(capture["state"]["meshes"]))
                mesh = capture["state"]["meshes"].pop(old_hash)
                mesh["vertices_local_hex"][1] = mesh["vertices_local_hex"][0]
                mesh_hash = digest(mesh);capture["state"]["meshes"][mesh_hash] = mesh
                capture["state"]["instances"][1]["mesh_sha256"] = mesh_hash
                rehash(capture, semantics)
                with self.assertRaises(ValueError): prepare_scalar_scene(capture, semantics, fields)


if __name__ == "__main__":
    unittest.main()
