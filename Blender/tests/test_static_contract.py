import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class StaticContractTests(unittest.TestCase):
    def test_cpu_core_has_no_blender_dependency(self):
        source = (ROOT / "core" / "photonic_model.py").read_text(encoding="utf-8")
        self.assertNotIn("import bpy", source)
        self.assertNotIn("import gpu", source)

    def test_shader_is_dormant_contract(self):
        source = (ROOT / "shaders" / "nebula_photonic_compute.glsl").read_text(encoding="utf-8")
        for token in ("#version", "local_size_x", "gl_GlobalInvocationID", "NeuronState", "activation_threshold"):
            self.assertIn(token, source)
        addon = (ROOT / "addon" / "nebula_santo_grial" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("GPU_ENABLED_BY_DEFAULT = False", addon)
        self.assertIn("CPU preview", addon)

    def test_required_layout_exists(self):
        for relative in (
            "core/photonic_model.py",
            "addon/neuro3d/__init__.py",
            "shaders/nebula_photonic_compute.glsl",
            "tests/test_photonic_model.py",
            "tests/test_static_contract.py",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main(verbosity=2)
