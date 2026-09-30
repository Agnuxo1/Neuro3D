"""Plan/static checks without importing Blender or starting GPU."""
import ast
from pathlib import Path
import unittest
import exp005_cascade_runtime as runtime


class CascadeRuntimeStaticTests(unittest.TestCase):
    def test_frozen_probes_and_limits(self):
        self.assertEqual(len(runtime.CASES),6)
        self.assertEqual(len(runtime.probes()),9)
        self.assertEqual(len(set(label for label,_ in runtime.probes())),9)
        self.assertEqual(runtime.FIELD_TOL,2e-3)
        self.assertEqual(runtime.POWER_TOL,1e-4)
        self.assertEqual(runtime.PATH_TOL,1e-5)

    def test_reopen_evaluated_snapshot_and_no_render(self):
        source=Path(runtime.__file__).read_text(encoding='utf-8')
        tree=ast.parse(source)
        calls=[ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node,ast.Call)]
        self.assertIn('bpy.ops.wm.open_mainfile',calls)
        self.assertIn('bpy.context.evaluated_depsgraph_get',calls)
        self.assertFalse(any('render' in call or 'torch' in call for call in calls))
        self.assertIn('fresh evidence folder required',source)

    def test_actual_hit_normal_used_without_oracle_or_axis_substitution(self):
        import exp005_cascade_bpy_paths as paths
        source=Path(paths.__file__).read_text(encoding='utf-8')
        calls=[ast.unparse(node.func) for node in ast.walk(ast.parse(source)) if isinstance(node,ast.Call)]
        self.assertIn('scene.ray_cast',calls)
        self.assertIn('reflect_direction',calls)
        self.assertNotIn('trace_scene',calls)
        self.assertNotIn('closed_form_columns',calls)


if __name__=='__main__': unittest.main()
