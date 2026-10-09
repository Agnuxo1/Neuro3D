"""Prevent a learning integration from silently changing the admitted shader."""
import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def constant(module,name):
    tree=ast.parse((ROOT/'Blender/blender_lab'/module).read_text(encoding='utf-8'))
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
class Contract(unittest.TestCase):
    def test_learning_uses_identical_admitted_fp64_shader_arithmetic(self):
        self.assertEqual(constant('native_graphics_gradient_v1.py','FRAGMENT'),constant('native_graphics_gradient_v2.py','FRAGMENT'))
    def test_compact_logging_keeps_context_and_immediate_error_gate(self):
        text=(ROOT/'Blender/blender_lab/native_graphics_compact_stage_audit_v1.py').read_text(encoding='utf-8')
        self.assertIn('self.sync.assert_context()',text);self.assertIn('self.sync._get_error()',text);self.assertIn("if value:self.errors.append(event);self.save();raise ValueError",text)
if __name__=='__main__':unittest.main()
