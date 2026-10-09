import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from Tools.run_frozen_own_addon_audit_v2 import ROOT, validate
from Tools.run_frozen_state_graph_profile_v1 import check_registration


class CorrectedInstalledProfileControls(unittest.TestCase):
    def test_real_profile_receipt_same_package_and_budgets(self):
        profile, pin = validate(ROOT / 'Docs/research/own_blender_addon_profile_v2_2026-10-09.json')
        receipt = json.loads((ROOT / 'Docs/research/own_blender_addon_registration_v2_2026-10-09.json').read_bytes())
        check_registration(receipt, profile, pin)
        old = json.loads((ROOT / 'Docs/research/own_blender_addon_profile_2026-10-09.json').read_bytes())
        self.assertEqual(profile['archive_sha256'], old['archive_sha256'])
        self.assertEqual(profile['limits'], old['limits'])
        self.assertEqual(profile['power_tolerance'], old['power_tolerance'])
        self.assertIsNone(receipt['ipfsCid'])

    def test_changed_numeric_version_source_limits_rejected(self):
        original = json.loads((ROOT / 'Docs/research/own_blender_addon_profile_v2_2026-10-09.json').read_bytes())
        directory = 'D:/PROJECTS/.cognition/neuro3d-sequential-20261008' if os.name == 'nt' else None
        with tempfile.TemporaryDirectory(dir=directory) as folder:
            path = Path(folder) / 'profile.json'
            for kind in ('version', 'source', 'limits'):
                profile = copy.deepcopy(original)
                if kind == 'version':
                    profile['blender_version_numeric'] = [4, 5, 13]
                elif kind == 'source':
                    profile['pins'][profile['worker']] = '0' * 64
                else:
                    profile['limits']['worker_seconds'] = 99999
                path.write_text(json.dumps(profile))
                with self.assertRaises(ValueError):
                    validate(path)


if __name__ == '__main__':
    unittest.main()
