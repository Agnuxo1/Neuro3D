import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
from Tools.run_frozen_own_addon_audit_v3 import ROOT, validate
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.trace_indexed_scene_v1 import wire
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


class ComplexInstalledProfileControls(unittest.TestCase):
    def test_real_profile_and_package_complex_wire_contract(self):
        profile, pin = validate(ROOT / 'Docs/research/own_blender_addon_profile_v3_2026-10-09.json')
        receipt = json.loads((ROOT / 'Docs/research/own_blender_addon_registration_v3_2026-10-09.json').read_bytes())
        check_registration(receipt, profile, pin)
        self.assertIsNone(receipt['ipfsCid'])
        self.assertEqual(json.loads(json.dumps(wire({'fields': {'det': 1 + 2j}})))['fields']['det'], {'real': 1, 'imag': 2})
        with zipfile.ZipFile(ROOT / profile['archive_relative']) as archive:
            manifest = json.loads(archive.read('optic_neuro_blender/package_manifest.json'))
            self.assertEqual(manifest['version'], '0.1.1')
            self.assertNotIn('optic_neuro_blender/worker.py', archive.namelist())
            self.assertIn('optic_neuro_blender/worker_v2.py', archive.namelist())
            for name, expected in manifest['files'].items():
                self.assertEqual(hashlib.sha256(archive.read('optic_neuro_blender/' + name)).hexdigest(), expected['sha256'])

    def test_changed_source_limits_rejected(self):
        original = json.loads((ROOT / 'Docs/research/own_blender_addon_profile_v3_2026-10-09.json').read_bytes())
        directory = str(NEURO3D_COGNITION / 'neuro3d-sequential-20261008') if os.name == 'nt' else None
        if directory: Path(directory).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as folder:
            path = Path(folder) / 'profile.json'
            for kind in ('source', 'limits'):
                profile = copy.deepcopy(original)
                if kind == 'source':
                    profile['pins']['Blender/addon/optic_neuro_blender/worker_v2.py'] = '0' * 64
                else:
                    profile['limits']['worker_seconds'] = 99999
                path.write_text(json.dumps(profile))
                with self.assertRaises(ValueError):
                    validate(path)


if __name__ == '__main__':
    unittest.main()
