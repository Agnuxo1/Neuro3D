import json
import unittest
from Tools.run_external_cpu_reproduction_v1 import ROOT, validate_profile
from Tools.run_frozen_state_graph_profile_v1 import check_registration


class RepairedExternalCPUProfileControl(unittest.TestCase):
    def test_same_science_only_workflow_repaired(self):
        profile, pin = validate_profile(ROOT / 'Docs/research/external_cpu_reproduction_profile_v2_2026-10-09.json')
        receipt = json.loads((ROOT / 'Docs/research/external_cpu_reproduction_registration_v2_2026-10-09.json').read_bytes())
        check_registration(receipt, profile, pin)
        previous = json.loads((ROOT / 'Docs/research/external_cpu_reproduction_profile_2026-10-09.json').read_bytes())
        for key in ['limits', 'packages', 'python_version', 'control_modules', 'training_profile', 'requirements']:
            self.assertEqual(profile[key], previous[key])
        changed = [name for name in profile['pins'] if profile['pins'][name] != previous['pins'][name]]
        self.assertEqual(changed, ['.github/workflows/external-cpu-reproduction-20261009.yml'])
        self.assertIsNone(receipt['ipfsCid'])


if __name__ == '__main__':
    unittest.main()
