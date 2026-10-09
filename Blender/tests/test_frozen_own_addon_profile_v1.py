import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile

from Tools.run_frozen_own_addon_audit_v1 import ROOT, validate
from Tools.run_frozen_state_graph_profile_v1 import check_registration


class InstalledAddonProfileControls(unittest.TestCase):
    def test_frozen_package_receipt_and_internal_manifest(self):
        profile, pin = validate(ROOT / 'Docs/research/own_blender_addon_profile_2026-10-09.json')
        receipt = json.loads((ROOT / 'Docs/research/own_blender_addon_registration_2026-10-09.json').read_bytes())
        check_registration(receipt, profile, pin)
        self.assertIsNone(receipt['ipfsCid'])
        import hashlib
        with zipfile.ZipFile(ROOT / profile['archive_relative']) as archive:
            names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(all(name.startswith('optic_neuro_blender/') and '..' not in Path(name).parts for name in names))
            manifest_raw = archive.read('optic_neuro_blender/package_manifest.json')
            self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(), profile['manifest_sha256'])
            manifest = json.loads(manifest_raw)
            for name, expected in manifest['files'].items():
                self.assertEqual(hashlib.sha256(archive.read('optic_neuro_blender/' + name)).hexdigest(), expected['sha256'])
            self.assertFalse(manifest['third_party_optical_code_bundled'])

    def test_modified_source_tolerance_and_limits_rejected(self):
        original = json.loads((ROOT / 'Docs/research/own_blender_addon_profile_2026-10-09.json').read_bytes())
        directory = 'D:/PROJECTS/.cognition/neuro3d-sequential-20261008' if os.name == 'nt' else None
        with tempfile.TemporaryDirectory(dir=directory) as folder:
            path = Path(folder) / 'profile.json'
            for kind in ('source', 'tolerance', 'limits'):
                profile = copy.deepcopy(original)
                if kind == 'source':
                    profile['pins'][profile['worker']] = '0' * 64
                elif kind == 'tolerance':
                    profile['power_tolerance'] = 1e-3
                else:
                    profile['limits']['worker_seconds'] = 99999
                path.write_text(json.dumps(profile))
                with self.assertRaises(ValueError):
                    validate(path)


if __name__ == '__main__':
    unittest.main()
