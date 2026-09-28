"""Lightweight structural checks of the MZ adapter; never starts Blender."""

import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "core"), str(ROOT / "addon" / "neuro3d")]

import mz_scene_adapter


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


if __name__ == "__main__":
    unittest.main()
