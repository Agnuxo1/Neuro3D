import copy,json,tempfile,unittest
import os
from pathlib import Path
from Tools.run_frozen_wine_comparison_v1 import ROOT,validate_profile
from Tools.run_frozen_state_graph_profile_v1 import check_registration
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


class ProtocolControls(unittest.TestCase):
    def test_actual_pinned_profile_and_human_receipt(self):
        p,pin=validate_profile(ROOT/'Docs/research/wine_comparison_profile_2026-10-09.json')
        receipt=json.loads((ROOT/'Docs/research/wine_comparison_registration_2026-10-09.json').read_bytes())
        check_registration(receipt,p,pin)
        self.assertIsNone(receipt['ipfsCid']);self.assertIsNone(receipt['preregId'])
        bad=copy.deepcopy(receipt);bad['profile_sha256']='0'*64
        with self.assertRaises(ValueError):check_registration(bad,p,pin)

    def test_source_seed_and_budget_mutations_rejected(self):
        original=json.loads((ROOT/'Docs/research/wine_comparison_profile_2026-10-09.json').read_bytes())
        (NEURO3D_COGNITION / 'neuro3d-sequential-20261008').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=NEURO3D_COGNITION / 'neuro3d-sequential-20261008') as directory:
            target=Path(directory)/'profile.json'
            for mutation in ('source','seed','budget','features'):
                p=copy.deepcopy(original)
                if mutation=='source':p['pins'][p['dataset']]='0'*64
                if mutation=='seed':p['initializations'][0]['seed']=42
                if mutation=='budget':p['limits']['worker_seconds']=1801
                if mutation=='features':p['feature_columns_zero_based_in_original_file']=[5,6,7,8]
                target.write_text(json.dumps(p))
                with self.assertRaises(ValueError):validate_profile(target)


if __name__=='__main__':unittest.main()
