"""Lightweight structural checks of the MZ adapter; never starts Blender."""

import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "core"), str(ROOT / "addon" / "neuro3d")]
sys.path.insert(0, str(ROOT / "oracle"))

import mz_scene_adapter
from geometry_oracle import NonRectMZ


class Links(list):
    def link(self, item):
        self.append(item)


class FakeObject(dict):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.parent = None
        self.location = None


class Factories:
    def new(self, name, _data=None):
        if _data is None:
            return FakeObject(name)
        raise AssertionError("Only empty objects are expected")


class Collections:
    def new(self, name):
        return SimpleNamespace(name=name, objects=Links())


class Scene(dict):
    def __init__(self):
        super().__init__()
        self.collection = SimpleNamespace(children=Links())


class MZAdapterStaticTests(unittest.TestCase):
    def test_combiner_parent_preserves_local_layout_contract(self):
        bpy = SimpleNamespace(data=SimpleNamespace(objects=Factories(), collections=Collections()))
        scene = Scene()
        with patch.object(mz_scene_adapter, "_point_local_z"):
            collection = mz_scene_adapter.create_mz_circuit(bpy, scene)
        roles = {obj["neuro3d_role"]: obj for obj in collection.objects}
        self.assertEqual(len(roles), 8)  # seven optical objects and one helper
        group = roles["mz_combiner_group"]
        self.assertEqual(group.location, (2.0, 2.0, 0.0))
        for role, local in (("mz_bs2", (0.0, 0.0, 0.0)),
                            ("mz_detector_a", (0.0, 1.0, 0.0)),
                            ("mz_detector_b", (1.0, 0.0, 0.0))):
            self.assertIs(roles[role].parent, group)
            self.assertEqual(roles[role].location, local)
        for role in ("mz_source", "mz_bs1", "mz_mirror1", "mz_mirror2"):
            self.assertIsNone(roles[role].parent)
        self.assertEqual(roles["mz_source"]["beam_waist"], 0.0)
        self.assertEqual(roles["mz_source"]["mutual_coherence"], 1.0)
        self.assertIs(scene.collection.children[0], collection)

    def test_nonrect60_layout_matches_independent_geometry_reference(self):
        bpy = SimpleNamespace(data=SimpleNamespace(objects=Factories(), collections=Collections()))
        scene = Scene()
        with patch.object(mz_scene_adapter, "_point_local_z", side_effect=lambda obj, n: setattr(obj, "normal", n)):
            collection = mz_scene_adapter.create_mz_circuit(bpy, scene, layout="nonrect60")
        roles = {obj["neuro3d_role"]: obj for obj in collection.objects}
        reference = NonRectMZ(60.0, 2.0, 2.0).scene()
        group = roles["mz_combiner_group"]
        for got, expected in zip(group.location, reference["bs2"]["position"]):
            self.assertAlmostEqual(got, expected, places=12)
        for role, key in (("mz_mirror1", "mirror1"), ("mz_mirror2", "mirror2")):
            for got, expected in zip(roles[role].location, reference[key]["position"]):
                self.assertAlmostEqual(got, expected, places=12)
            for got, expected in zip(roles[role].normal, reference[key]["normal"]):
                self.assertAlmostEqual(got, expected, places=12)
        for role, key in (("mz_detector_a", "port_a_direction"),
                          ("mz_detector_b", "port_b_direction")):
            self.assertIs(roles[role].parent, group)
            for got, expected in zip(roles[role].location, reference[key]):
                self.assertAlmostEqual(got, expected, places=12)
        self.assertEqual(roles["mz_source"]["frequency"], 100.0)
        self.assertEqual(roles["mz_source"]["beam_waist"], 0.2)

    def test_unknown_layout_rejected_without_creating_collection(self):
        bpy = SimpleNamespace(data=SimpleNamespace(objects=Factories(), collections=Collections()))
        scene = Scene()
        with self.assertRaisesRegex(ValueError, "Unknown MZ layout"):
            mz_scene_adapter.create_mz_circuit(bpy, scene, layout="unexpected")
        self.assertEqual(scene.collection.children, [])


if __name__ == "__main__":
    unittest.main()
