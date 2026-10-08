"""CPU-only regression for the frozen native first-hit admission contract."""
import copy
import os
from pathlib import Path
import tempfile
import unittest

from Blender.tests import robust_first_hit_native_v1 as native


class FrozenInputAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = native.ROOT / "Docs/validation/robust-first-hit-2026-10-07/inputs01/input_manifest.json"
        self.job = native.read_json(self.manifest)

    def test_original_frozen_manifest_admits_all_twenty_queries(self):
        self.assertEqual(native.sha(self.manifest),
                         "1ba451212cc136442ea34a1ec9a7cefd44fdf366211f28813590f21b732ba800")
        self.assertEqual(native.validate_job(self.job), 20)

    def test_admission_does_not_depend_on_process_working_directory(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                self.assertEqual(native.validate_job(self.job), 20)
            finally:
                os.chdir(previous)

    def test_legacy_absolute_paths_keep_the_same_contract(self):
        job = copy.deepcopy(self.job)
        for case in job["cases"]:
            case["packet_path"] = str(native.ROOT / case["packet_path"])
        self.assertEqual(native.validate_job(job), 20)

    def test_changed_packet_hash_is_rejected(self):
        self.job["cases"][0]["packet_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "pinned packet"):
            native.validate_job(self.job)

    def test_missing_packet_is_rejected(self):
        self.job["cases"][0]["packet_path"] = "Docs/missing-packet.json"
        with self.assertRaisesRegex(ValueError, "pinned packet"):
            native.validate_job(self.job)


if __name__ == "__main__":
    unittest.main(verbosity=2)
