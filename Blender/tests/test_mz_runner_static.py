"""Pure CPU orchestration checks for EXP-001; never starts Blender."""

import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

TESTS = Path(__file__).resolve().parent
sys.path[:0] = [str(TESTS), str(TESTS.parent / "oracle")]

import run_mz_exp001
from readback_reconstruct import compare as compare_readback
from test_readback_reconstruct import synthetic_record


class MZRunnerStaticTests(unittest.TestCase):
    def _patch_environment(self):
        return (
            patch.object(sys, "argv", ["run_mz_exp001.py", "--blender", "D:/fake/blender.exe",
                                       "--artifacts", "D:/fake/exp001-new", "--authorized-by-user"]),
            patch.object(Path, "is_file", return_value=True),
            patch.object(Path, "exists", return_value=False),
            patch.object(Path, "mkdir"),
            patch.object(Path, "write_text"),
            patch.object(run_mz_exp001.psutil, "virtual_memory",
                         return_value=SimpleNamespace(available=8 * 2**30)),
            patch("builtins.print"),
        )

    def test_seven_controls_save_then_reopen_without_blender(self):
        patches = self._patch_environment()
        mocks = []
        for item in patches:
            mocks.append(item.start())
            self.addCleanup(item.stop)
        with patch.object(run_mz_exp001, "_run", side_effect=lambda *a: {
                "phase": a[4], "control": a[5]} ) as fake_run, \
             patch.object(run_mz_exp001, "_verify_readback", return_value={
                 "readback_worst_abs_diff": 0.0}):
            run_mz_exp001.main()
        calls = [(call.args[4], call.args[5]) for call in fake_run.call_args_list]
        self.assertEqual(calls, [("init", "A"), ("verify", "A"),
                                 ("edit", "B-geo"), ("verify", "B-geo"),
                                 ("edit", "B-mat"), ("verify", "B-mat"),
                                 ("edit", "C-A"), ("verify", "C-A"),
                                 ("edit", "C-B-geo"), ("verify", "C-B-geo"),
                                 ("edit", "C-B-mat"), ("verify", "C-B-mat"),
                                 ("edit", "D"), ("verify", "D")])
        report = json.loads(mocks[4].mock_calls[-1].args[0])
        self.assertTrue(report["runtime_verified"])
        self.assertEqual(len(report["controls"]), 14)

    def test_failure_writes_partial_report_not_success(self):
        patches = self._patch_environment()
        mocks = []
        for item in patches:
            mocks.append(item.start())
            self.addCleanup(item.stop)

        def fake_phase(_blender, _script, _input, _output, mode, case):
            if mode == "edit" and case == "B-geo":
                raise RuntimeError("synthetic failure")
            return {"phase": mode, "control": case}

        with patch.object(run_mz_exp001, "_run", side_effect=fake_phase), \
             patch.object(run_mz_exp001, "_verify_readback", return_value={
                 "readback_worst_abs_diff": 0.0}):
            with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
                run_mz_exp001.main()
        report = json.loads(mocks[4].mock_calls[-1].args[0])
        self.assertFalse(report["runtime_verified"])
        self.assertEqual(len(report["controls"]), 2)
        self.assertEqual(report["failure"]["type"], "RuntimeError")

    def test_readback_guard_detects_tampered_optical_property(self):
        record = synthetic_record()
        with patch.object(Path, "read_text", return_value=json.dumps(record)):
            verified = run_mz_exp001._verify_readback(Path("D:/fake/A.blend"))
            self.assertEqual(verified["readback_worst_abs_diff"], 0.0)
            self.assertIn("direction_diagnostic", verified)
            self.assertTrue(verified["direction_diagnostic"]["within_tolerance"])
        record["optics"]["mz_mirror2"]["phase_shift"] = 3.141592653589793
        with patch.object(Path, "read_text", return_value=json.dumps(record)):
            with self.assertRaisesRegex(AssertionError, "Independent CPU readback failed"):
                run_mz_exp001._verify_readback(Path("D:/fake/A.blend"))

    def test_readback_rejects_incomplete_or_nonfinite_rgb(self):
        record = synthetic_record()
        record["result"]["optical_a"] = record["result"]["optical_a"][:2]
        self.assertFalse(compare_readback(record)["passes"])
        record = synthetic_record()
        record["result"]["optical_a"][0] = float("nan")
        self.assertFalse(compare_readback(record)["passes"])


if __name__ == "__main__":
    unittest.main()
