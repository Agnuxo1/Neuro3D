import copy,json,os,tempfile,unittest
from pathlib import Path
from Tools.run_frozen_wave_reference_v1 import ROOT,validate
from Tools.run_frozen_state_graph_profile_v1 import check_registration
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

class WaveProfileControls(unittest.TestCase):
    def test_real_prepared_profile_and_receipt(self):
        profile,pin=validate(ROOT/'Docs/research/gaussian_wave_profile_2026-10-09.json')
        receipt=json.loads((ROOT/'Docs/research/gaussian_wave_registration_2026-10-09.json').read_bytes())
        check_registration(receipt,profile,pin);self.assertIsNone(receipt['ipfsCid'])

    def test_mutated_budget_grid_source_rejected(self):
        original=json.loads((ROOT/'Docs/research/gaussian_wave_profile_2026-10-09.json').read_bytes())
        directory=str(NEURO3D_COGNITION / 'neuro3d-sequential-20261008') if os.name=='nt' else None
        if directory: Path(directory).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as folder:
            path=Path(folder)/'profile.json'
            for kind in ('budget','grid','source'):
                p=copy.deepcopy(original)
                if kind=='budget':p['limits']['worker_seconds']=241
                elif kind=='grid':p['grids'][0][0]=256
                else:p['pins']['Blender/blender_lab/wave_optics_v1.py']='0'*64
                path.write_text(json.dumps(p))
                with self.assertRaises(ValueError):validate(path)

if __name__=='__main__':unittest.main()
