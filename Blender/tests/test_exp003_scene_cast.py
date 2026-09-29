"""Mock the Blender API boundary; no Blender/GPU process starts."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_scene_cast import make_scene_cast


class Object(dict):
    name = "foreign_mesh"


class Scene:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def ray_cast(self, *args):
        self.calls.append(args)
        return self.response


class SceneCastTests(unittest.TestCase):
    def test_first_scene_hit_and_world_point_are_passed_through(self):
        obj = Object(neuro3d_role="r1")
        scene = Scene((True, (2., 0., 0.), (1., -1., 0.), 0, obj, None))
        cast = make_scene_cast(scene, "depsgraph", tuple)
        self.assertEqual(cast((0., 0., 0.), (1., 0., 0.)),
                         ("r1", (2., 0., 0.), (1., -1., 0.)))
        self.assertEqual(len(scene.calls), 1)

    def test_missing_hit_has_no_fixture_fallback(self):
        scene = Scene((False, None, None, -1, None, None))
        self.assertIsNone(make_scene_cast(scene, None, tuple)(
            (0., 0., 0.), (1., 0., 0.)))

    def test_unmapped_occluder_is_visible(self):
        scene = Scene((True, (1., 0., 0.), (0., 1., 0.), 0, Object(), None))
        result = make_scene_cast(scene, None, tuple)(
            (0., 0., 0.), (1., 0., 0.))
        self.assertEqual(result[0], "unmapped:foreign_mesh")


if __name__ == "__main__":
    unittest.main()
