import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from Tools.run_external_cpu_reproduction_v1 import ROOT, validate_profile
from Tools.run_frozen_state_graph_profile_v1 import check_registration
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


class ExternalCPUProfileControls(unittest.TestCase):
    def test_actual_prepared_profile_and_human_receipt(self):
        profile, pin = validate_profile(ROOT / 'Docs/research/external_cpu_reproduction_profile_2026-10-09.json')
        receipt = json.loads((ROOT / 'Docs/research/external_cpu_reproduction_registration_2026-10-09.json').read_bytes())
        check_registration(receipt, profile, pin)
        self.assertIsNone(receipt['ipfsCid'])
        self.assertEqual(len(profile['control_modules']), 5)
        self.assertFalse(profile['limits']['gpu'])

    def test_changed_sources_budget_runtime_rejected(self):
        original = json.loads((ROOT / 'Docs/research/external_cpu_reproduction_profile_2026-10-09.json').read_bytes())
        directory = str(NEURO3D_COGNITION / 'neuro3d-sequential-20261008') if os.name == 'nt' else None
        if directory: Path(directory).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as folder:
            path = Path(folder) / 'profile.json'
            for kind in ('source', 'budget', 'runtime'):
                profile = copy.deepcopy(original)
                if kind == 'source':
                    profile['pins'][profile['worker']] = '0' * 64
                elif kind == 'budget':
                    profile['limits']['training_seconds'] = 99999
                else:
                    profile['packages']['numpy'] = '2.0.0'
                path.write_text(json.dumps(profile))
                with self.assertRaises(ValueError):
                    validate_profile(path)


if __name__ == '__main__':
    unittest.main()
