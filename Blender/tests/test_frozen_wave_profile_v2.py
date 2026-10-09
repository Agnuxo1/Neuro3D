import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from Tools.run_frozen_wave_reference_v2 import ROOT, validate
from Tools.run_frozen_state_graph_profile_v1 import check_registration


class RemedialWaveControls(unittest.TestCase):
    def test_receipt_and_unchanged_scientific_gates(self):
        profile, pin = validate(ROOT / 'Docs/research/gaussian_wave_remedial_profile_2026-10-09.json')
        receipt = json.loads((ROOT / 'Docs/research/gaussian_wave_remedial_registration_2026-10-09.json').read_bytes())
        check_registration(receipt, profile, pin)
        prior = json.loads((ROOT / 'Docs/research/gaussian_wave_profile_2026-10-09.json').read_bytes())
        self.assertEqual(profile['gates'], prior['gates'])
        self.assertIsNone(receipt['ipfsCid'])
        self.assertEqual(profile['limits']['worker_seconds'], prior['limits']['worker_seconds'])

    def test_mutated_limits_grid_and_sources_rejected(self):
        original = json.loads((ROOT / 'Docs/research/gaussian_wave_remedial_profile_2026-10-09.json').read_bytes())
        directory = 'D:/PROJECTS/.cognition/neuro3d-sequential-20261008' if os.name == 'nt' else None
        with tempfile.TemporaryDirectory(dir=directory) as folder:
            path = Path(folder) / 'profile.json'
            for kind in ('limits', 'grid', 'source'):
                profile = copy.deepcopy(original)
                if kind == 'limits':
                    profile['limits']['free_ram_before_mib'] = 4000
                elif kind == 'grid':
                    profile['grids'][0][1] = 16
                else:
                    profile['pins']['Blender/blender_lab/wave_optics_v1.py'] = '0' * 64
                path.write_text(json.dumps(profile))
                with self.assertRaises(ValueError):
                    validate(path)


if __name__ == '__main__':
    unittest.main()
