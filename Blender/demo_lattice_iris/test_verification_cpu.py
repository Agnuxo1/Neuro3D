"""CPU-only fail-closed gate tests, without importing Blender."""
import ast
import math
from pathlib import Path
import unittest

source = Path(__file__).with_name('neuro3d_iris_demo.py').read_text(encoding='utf-8')
nodes = [n for n in ast.parse(source).body if
         isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VERIFY_LIMITS' for t in n.targets)
         or isinstance(n, ast.FunctionDef) and n.name == 'verification_failures']
namespace = {'math': math}
exec(compile(ast.Module(body=nodes, type_ignores=[]), '<gate>', 'exec'), namespace)
limits = namespace['VERIFY_LIMITS']
failures = namespace['verification_failures']

class GateTests(unittest.TestCase):
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
