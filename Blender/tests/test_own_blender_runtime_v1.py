"""Real owned-process controls, no bpy required."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('onb_runtime_controls', ROOT / 'Blender/addon/optic_neuro_blender/runtime.py')
runtime = importlib.util.module_from_spec(spec); spec.loader.exec_module(runtime)


class OwnedRuntimeControls(unittest.TestCase):
    def test_complete_and_actual_cancel_with_evidence(self):
        directory = str(NEURO3D_COGNITION / 'neuro3d-sequential-20261008') if os.name == 'nt' else None
        if directory: Path(directory).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temporary:
            root = Path(temporary)
            completed = root / 'complete'; completed.mkdir()
            script = completed / 'small.py'
            script.write_text("from pathlib import Path\nPath(__file__).with_name('result.json').write_text('{\"status\":\"PASS\"}')\n")
            job = runtime.OwnedJob([sys.executable, str(script)], completed)
            until = time.monotonic() + 10
            while job.poll() == 'RUNNING' and time.monotonic() < until:
                time.sleep(.02)
            self.assertEqual(job.state, 'COMPLETED')
            receipt = runtime.read_json(completed / 'supervision.json')
            self.assertTrue(receipt['owned_process_terminated'])
            self.assertEqual(receipt['result_sha256'], runtime.hashlib.sha256((completed / 'result.json').read_bytes()).hexdigest())
            cancelled = root / 'cancel'; cancelled.mkdir()
            sleeper = cancelled / 'sleep.py'; sleeper.write_text('import time\ntime.sleep(30)\n')
            job = runtime.OwnedJob([sys.executable, str(sleeper)], cancelled)
            self.assertEqual(job.cancel(), 'CANCELLED')
            self.assertIsNotNone(job.process.poll())
            self.assertFalse(runtime.read_json(cancelled / 'supervision.json')['result_collected'])

    def test_duplicate_nonfinite_and_byte_budget_rejected(self):
        directory = str(NEURO3D_COGNITION / 'neuro3d-sequential-20261008') if os.name == 'nt' else None
        if directory: Path(directory).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temporary:
            path = Path(temporary) / 'value.json'
            for value in ['{"x":1,"x":2}', '{"x":NaN}']:
                path.write_text(value)
                with self.assertRaises(ValueError):
                    runtime.read_json(path)
            path.write_text('{"x":1}')
            with self.assertRaises(ValueError):
                runtime.read_json(path, 2)


if __name__ == '__main__':
    unittest.main()
