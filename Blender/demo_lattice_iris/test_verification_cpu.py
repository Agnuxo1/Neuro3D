"""CPU-only fail-closed gate tests, without importing Blender."""
import ast
import math
import json
import os
import tempfile
from pathlib import Path
import unittest

source = Path(__file__).with_name('neuro3d_iris_demo.py').read_text(encoding='utf-8')
nodes = [n for n in ast.parse(source).body if
         isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VERIFY_LIMITS' for t in n.targets)
         or isinstance(n, ast.FunctionDef) and n.name in ('verification_failures', 'main')]
namespace = {'math': math, 'json': json, 'os': os}
exec(compile(ast.Module(body=nodes, type_ignores=[]), '<gate>', 'exec'), namespace)
limits = namespace['VERIFY_LIMITS']
failures = namespace['verification_failures']

class GateTests(unittest.TestCase):
    def test_report_lifecycle(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            namespace['HERE'] = tmp
            path = Path(tmp) / 'scene_verification.json'
            def success(argv):
                self.assertFalse(json.loads(path.read_text())['verification_passed'])
                path.write_text('{"verification_passed":true}')
            namespace['_main'] = success
            namespace['main'](['--verify'])
            self.assertTrue(json.loads(path.read_text())['verification_passed'])
            def failure(argv):
                raise RuntimeError('fixture trace failed')
            namespace['_main'] = failure
            with self.assertRaises(RuntimeError): namespace['main'](['--verify'])
            rep = json.loads(path.read_text())
            self.assertFalse(rep['verification_passed'])
            self.assertIn('fixture trace failed', rep['verification_failures'][0])
            def gate_failure(argv):
                path.write_text(json.dumps({'verification_passed': False,
                    'verification_failures': ['escape_max'], 'escape_max': 0.2,
                    'scene_train_acc': 0.975}))
                raise RuntimeError('Scene verification failed: escape_max')
            namespace['_main'] = gate_failure
            with self.assertRaises(RuntimeError): namespace['main'](['--verify'])
            rep = json.loads(path.read_text())
            self.assertEqual(rep['escape_max'], 0.2)
            self.assertEqual(rep['scene_train_acc'], 0.975)
            self.assertIn('escape_max', rep['verification_failures'])

    def test_good_and_boundary(self):
        self.assertEqual(failures({k: 0.0 for k in limits}), [])
        self.assertEqual(failures(limits.copy()), [])

    def test_every_bad_metric_fails_independently(self):
        for key, limit in limits.items():
            for bad in (float('nan'), float('inf'), -float('inf'), -1.0, limit * 1.01, None, '0'):
                with self.subTest(metric=key, bad=bad):
                    report = {k: 0.0 for k in limits}
                    report[key] = bad
                    self.assertEqual(failures(report), [key])

    def test_missing_metric_fails(self):
        for key in limits:
            report = {k: 0.0 for k in limits if k != key}
            self.assertEqual(failures(report), [key])

if __name__ == '__main__':
    unittest.main()
