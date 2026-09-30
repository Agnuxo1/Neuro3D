from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from exp005_history_mzi_audit import fixture
from history_relative_power_budget_v1 import scene_relative_power_budget,upper

LAMBDA=1.00416693877201e-12


def make_scene(*,two=False,offset=0.,reference=0.,wavelength=LAMBDA):
    scene,_=fixture(reference_shift=reference);scene['lambda_BU']=wavelength
    if two:
        source=deepcopy(scene['sources'][0]);source['id']='s2'
        source['position_BU'][0]-=offset;scene['sources'].append(source)
    return scene


def evaluate(scene,*,coherent=True):
    groups={s['id']:('g' if coherent else s['id']) for s in scene['sources']}
    return scene_relative_power_budget(scene,coherence_groups=groups,
        field_budget=1e-4,intensity_budget=2e-4,relative_budget=1e-12)


class RelativePowerBudget(unittest.TestCase):
    def test_common_phase_power_zero_does_not_relax_complex_gate(self):
        out=evaluate(make_scene(two=True))
        for port in ('Dx','Dy'):
            value=out['ports'][port]
            self.assertEqual(upper(value['intensity_error_upper']),0)
            self.assertGreater(upper(value['absolute_phase_intensity_error_upper']),0)
            self.assertGreater(upper(value['groups']['g']['field_error_upper']),F(1e-4))
        self.assertFalse(out['accepted_wavelength_only'])
        self.assertFalse(out['native_promotion_allowed'])
        self.assertFalse(out['complex_fields_rephased'])

    def test_different_source_lengths_have_nonzero_relative_error(self):
        out=evaluate(make_scene(two=True,offset=.03125))
        for port in ('Dx','Dy'):
            value=out['ports'][port]
            self.assertGreater(upper(value['intensity_error_upper']),0)
            self.assertLess(upper(value['intensity_error_upper']),
                            upper(value['absolute_phase_intensity_error_upper']))
        self.assertEqual(out['generated_record_count'],26)
        self.assertEqual(len(out['ledger']),8)

    def test_independent_groups_do_not_interfere(self):
        out=evaluate(make_scene(two=True,offset=.03125),coherent=False)
        for value in out['ports'].values():
            self.assertEqual(set(value['groups']),{'s','s2'})
            self.assertEqual(upper(value['intensity_error_upper']),0)
        self.assertFalse(out['accepted_wavelength_only'])

    def test_mode_reference_shift_is_kept_not_removed_from_complex_phase(self):
        out=evaluate(make_scene(reference=.03125))
        self.assertFalse(out['scene_reference_changed'])
        dx=out['ports']['Dx']['groups']['g']
        dy=out['ports']['Dy']['groups']['g']
        self.assertGreater(upper(dx['field_error_upper']),upper(dy['field_error_upper']))
        self.assertEqual(F(*dx['relative_anchor_BU_rational']),F(4)+F(.03125))
        self.assertEqual(upper(out['ports']['Dx']['intensity_error_upper']),0)

    def test_exact_lambda_has_zero_bounds(self):
        out=evaluate(make_scene(two=True,offset=.03125,wavelength=.125))
        self.assertTrue(out['accepted_wavelength_only'])
        self.assertTrue(all(upper(v['intensity_error_upper'])==0 for v in out['ports'].values()))
        self.assertFalse(out['native_precision_certified'])

    def test_scene_immutable_and_missing_coherence_rejected(self):
        scene=make_scene(two=True);before=deepcopy(scene);evaluate(scene)
        self.assertEqual(scene,before)
        with self.assertRaises(ValueError):
            scene_relative_power_budget(scene,coherence_groups={'s':'g'},
                field_budget=1e-4,intensity_budget=2e-4,relative_budget=1e-12)


if __name__=='__main__':unittest.main()
