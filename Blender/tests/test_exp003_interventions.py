"""Mock checks that treatments edit objects and use scene unlinking."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_interventions import ablate_existing, place_delay_pair
from test_exp003_first_hit_preflight import fixture


class Obj:
    def __init__(self):
        self.location = None


class Collection:
    def __init__(self):
        self.unlinked = []

    def unlink(self, obj):
        self.unlinked.append(obj)


class Scene:
    def __init__(self):
        self.collection = type("C", (), {})()
        self.collection.objects = Collection()


class InterventionTests(unittest.TestCase):
    def test_delay_and_sham_move_same_existing_objects(self):
        data = fixture()
        objects = {"r1": Obj(), "r2": Obj()}
        place_delay_pair(objects, data, delay_d=.025)
        self.assertEqual(objects["r1"].location, (2.025, 0., 0.))
        self.assertEqual(objects["r2"].location, (2.025, .5, 0.))
        place_delay_pair(objects, data, sham_z=.01)
        self.assertEqual(objects["r1"].location, (2., 0., .01))
        self.assertEqual(objects["r2"].location, (2., .5, .01))

    def test_ablation_unlinks_object_instead_of_hiding_it(self):
        scene, obj = Scene(), Obj()
        self.assertIs(ablate_existing(scene, {"r2": obj}, "r2"), obj)
        self.assertEqual(scene.collection.objects.unlinked, [obj])


if __name__ == "__main__":
    unittest.main()
