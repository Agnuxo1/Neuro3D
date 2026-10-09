"""Registration and integrity controls only: no captured-scene worker launched."""
import copy
import tempfile
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from Tools.run_frozen_indexed_profile_v1 import check_profile,check_registration,main
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

ROOT=Path(__file__).resolve().parents[2]
PROFILE=ROOT/'Docs/research/indexed_capture_profile_prepared_2026-10-09.json'
WORK=NEURO3D_COGNITION / 'neuro3d-sequential-20261008'


class IndexedProfileTests(unittest.TestCase):
    def test_prepared_pins_valid(self):
        p,h=check_profile(PROFILE)
        self.assertEqual(p['max_rays'],4096)
        self.assertEqual(len(h),64)

    def test_missing_registration_never_starts_worker(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder,patch('Tools.run_frozen_indexed_profile_v1.subprocess.Popen') as popen:
            self.assertEqual(main(['--profile',str(PROFILE),'--out',str(Path(folder)/'fresh')]),3)
            popen.assert_not_called()

    def test_preflight_never_starts_worker(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder,patch('Tools.run_frozen_indexed_profile_v1.subprocess.Popen') as popen:
            self.assertEqual(main(['--profile',str(PROFILE),'--out',str(Path(folder)/'fresh'),'--preflight-only']),0)
            popen.assert_not_called()

    def test_registration_requires_matching_profile_and_real_origin(self):
        p,h=check_profile(PROFILE)
        base={'schema':'optic_neuro_blender.profile_registration.v1','approved':True,
              'profile_id':p['profile_id'],'profile_sha256':h,'kind':'HUMAN_GITHUB_EXCEPTION',
              'evidence_reference':'Hypothetical shape for parser tests only, never an execution receipt',
              'evidence_origin':'DIRECT_HUMAN_USER_MESSAGE_VERIFIED_BY_OPERATOR','preregId':None,'ipfsCid':None}
        check_registration(base,p,h)
        for key,value in [('profile_sha256','wrong'),('approved',False),('evidence_origin','LOCAL_FILE_ONLY'),
                          ('ipfsCid','invented'),('evidence_reference','TEST_ONLY synthetic record')]:
            item=copy.deepcopy(base)
            item[key]=value
            with self.assertRaises(ValueError):
                check_registration(item,p,h)


if __name__=='__main__':
    unittest.main()
