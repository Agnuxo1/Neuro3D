"""AST/static only. Importing the plan does not import bpy or use GPU."""
import ast
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name('exp005_parity_runtime.py')


class ParityPlanTests(unittest.TestCase):
    def test_bounded_frozen_plan_and_no_top_level_blender(self):
        spec=importlib.util.spec_from_file_location('parity_plan',SOURCE)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual(len(module.EXPECTED),10)
        self.assertEqual(sum(v is None for v in module.EXPECTED.values()),2)
    def test_no_render_or_gpu_code(self):
        text=SOURCE.read_text(encoding='utf-8')
        self.assertNotIn('bpy.ops.render',text); self.assertNotIn('import torch',text)
        self.assertNotIn('scene.ray_cast',text)
        compile(ast.parse(text),str(SOURCE),'exec')
    def test_reopen_and_fresh_folder_guard_present(self):
        text=SOURCE.read_text(encoding='utf-8')
        self.assertIn('open_mainfile',text); self.assertIn('fresh evidence folder required',text)
        self.assertIn('depsgraph=bpy.context.evaluated_depsgraph_get()',text)


if __name__=='__main__': unittest.main()
