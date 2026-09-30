import ast
from pathlib import Path
import unittest
from exp005_history_mzi_export_cpu_audit import audit,doubles,fixture,evaluated_readback


class MZIExportPreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=audit()

    def test_three_fake_export_controls_eight_invalid_readbacks(self):
        self.assertEqual(len(self.report['controls']),3);self.assertEqual(len(self.report['negatives']),8)
        for row in self.report['controls']:
            self.assertLess(row['checks']['analytic_field_error'],1e-13)
            self.assertIn('NOT GPU',row['checks']['scope'])

    def test_scene_owned_groups_no_external_default(self):
        s,_=fixture();bpy,scene=doubles(s);scene['coherence_groups']='{}'
        with self.assertRaises(ValueError):evaluated_readback(bpy,scene)
        scene['coherence_groups']='{"s":""}'
        with self.assertRaises(ValueError):evaluated_readback(bpy,scene)
        del scene['coherence_groups']
        with self.assertRaises(KeyError):evaluated_readback(bpy,scene)

    def test_static_cli_no_render_GPU_delete_or_existing_scene_overwrite(self):
        source=Path(__file__).with_name('exp005_history_mzi_export.py').read_text()
        tree=ast.parse(source)
        self.assertNotIn('import gpu',source);self.assertNotIn('render(',source)
        self.assertNotIn('objects.remove',source);self.assertNotIn('read_factory_settings',source)
        self.assertIn('if bpy.data.filepath',source);self.assertIn("folder.exists()",source)
        module_imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
        self.assertFalse(any(isinstance(n,ast.Import) and any(a.name=='bpy' for a in n.names) for n in module_imports))


if __name__=='__main__':unittest.main()
