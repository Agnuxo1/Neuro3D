"""Prepared profile rejects changed sources/limits before scientific execution."""
import json,tempfile
import os
from pathlib import Path
import unittest
from Tools.run_frozen_geometry_training_v1 import ROOT,validate_profile
from Tools.run_frozen_state_graph_profile_v1 import check_registration
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


class FrozenGeometryProfileTests(unittest.TestCase):
    def setUp(self):self.path=ROOT/'Docs/research/captured_geometry_training_profile_2026-10-09.json'

    def test_real_prepared_profile_and_direct_human_sequence_receipt(self):
        profile,pin=validate_profile(self.path)
        receipt=json.loads((ROOT/'Docs/research/captured_geometry_training_registration_2026-10-09.json').read_text())
        check_registration(receipt,profile,pin)
        self.assertIsNone(receipt['ipfsCid'])

    def test_changed_source_or_limits_do_not_admit_execution(self):
        original=json.loads(self.path.read_text())
        (NEURO3D_COGNITION).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=NEURO3D_COGNITION) as directory:
            path=Path(directory)/'profile.json'
            for mutate in (lambda p:p['pins'].__setitem__(p['worker'],'0'*64),lambda p:p['limits'].__setitem__('worker_seconds',901),lambda p:p.__setitem__('steps',61)):
                profile=json.loads(json.dumps(original));mutate(profile);path.write_text(json.dumps(profile),encoding='utf-8')
                with self.assertRaises(ValueError):validate_profile(path)


if __name__=='__main__':unittest.main()
