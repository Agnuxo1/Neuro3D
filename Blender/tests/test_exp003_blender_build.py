"""Pure geometry checks; no bpy import or Blender process."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_blender_build import disk_vertices


class DiskConstructionTests(unittest.TestCase):
    def test_flat_regular_disk_has_no_thickness(self):
        vertices = disk_vertices(.2)
        self.assertEqual(len(vertices), 64)
        self.assertTrue(all(z == 0 for _, _, z in vertices))
        self.assertTrue(all(abs(math.hypot(x, y) - .2) < 1e-12
                            for x, y, _ in vertices))

    def test_invalid_disk_is_rejected(self):
        for radius, sides in ((0, 64), (-.2, 64), (float("nan"), 64), (.2, 16)):
            with self.subTest(radius=radius, sides=sides):
                with self.assertRaises(ValueError):
                    disk_vertices(radius, sides)


if __name__ == "__main__":
    unittest.main()
