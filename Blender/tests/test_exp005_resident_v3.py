"""Isolated Python import regression, no Blender/GPU launch."""
from pathlib import Path
import subprocess
import sys
import unittest


class EntryPointTests(unittest.TestCase):
    def test_isolated_import_without_sibling_path_needs_no_gpu(self):
        path = Path(__file__).with_name('exp005_resident_v3.py').resolve()
        code = ('import runpy,sys; ns=runpy.run_path(sys.argv[1],run_name="isolated_import"); '
                'assert callable(ns["main"]); assert "exp005_resident_runtime" in sys.modules; '
                'assert "bpy" not in sys.modules and "gpu" not in sys.modules; print("IMPORT_PASS")')
        result = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(path)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'IMPORT_PASS')


if __name__ == '__main__': unittest.main()
