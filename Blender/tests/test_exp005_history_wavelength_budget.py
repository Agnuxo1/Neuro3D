from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from exp005_history_mzi_audit import fixture
from history_wavelength_field_budget_v1 import scene_wavelength_field_budget


def upper(encoded):
    return F(*encoded['rational_upper'])


def run_case(wavelength=.125, *, sources=1, coherent=True, opposite=False, zero=False,
             field_budget=1e-4,intensity_budget=2e-4,shift=0.):
    scene,_=fixture(reference_shift=shift)
    scene['lambda_BU']=wavelength
    if zero:scene['sources'][0]['field_reim']=[0.,0.]
    if sources==2:
        src=deepcopy(scene['sources'][0]);src['id']='s2'
        if opposite:src['field_reim']=[-1.,0.]
        scene['sources'].append(src)
    groups={src['id']:('g' if coherent else src['id']) for src in scene['sources']}
    out=scene_wavelength_field_budget(scene,coherence_groups=groups,
        field_budget=field_budget,intensity_budget=intensity_budget,relative_budget=1e-12)
    return scene,out


class HistoryWavelengthBudget(unittest.TestCase):
    def test_exact_lambda_zero_error_does_not_certify_native(self):
        _,result=run_case(field_budget=0.,intensity_budget=0.)
        self.assertTrue(result['accepted_wavelength_only'])
        self.assertFalse(result['native_promotion_allowed'])
        self.assertEqual(result['generated_record_count'],13)
        self.assertEqual(len(result['ledger']),4)
        self.assertTrue(all(upper(p['intensity_error_upper'])==0 for p in result['ports'].values()))

    def test_relative_gate_alone_does_not_admit_many_path_phase_error(self):
        _,result=run_case(1.00416693877201e-12)
        self.assertLess(result['wavelength_transport']['relative_error'],1e-12)
        self.assertFalse(result['accepted_wavelength_only'])
        self.assertGreater(upper(result['ports']['Dx']['groups']['g']['field_error_upper']),F(1e-4))

    def test_source_amplification_and_coherence_intensities(self):
        wavelength=1.00416693877201e-12
        _,one=run_case(wavelength)
        _,coherent=run_case(wavelength,sources=2)
        _,independent=run_case(wavelength,sources=2,coherent=False)
        self.assertEqual(coherent['generated_record_count'],26)
        for port in ('Dx','Dy'):
            e=upper(one['ports'][port]['groups']['g']['field_error_upper'])
            self.assertEqual(upper(coherent['ports'][port]['groups']['g']['field_error_upper']),2*e)
            power=upper(one['ports'][port]['intensity_error_upper'])
            self.assertEqual(upper(coherent['ports'][port]['intensity_error_upper']),4*power)
            self.assertEqual(upper(independent['ports'][port]['intensity_error_upper']),2*power)

    def test_destructive_interference_not_used_to_prune_uncertainty(self):
        _,inphase=run_case(1.00416693877201e-12,sources=2)
        _,opposite=run_case(1.00416693877201e-12,sources=2,opposite=True)
        self.assertEqual(inphase['ports'],opposite['ports'])
        self.assertEqual(len(opposite['ledger']),8)

    def test_zero_source_preserves_paths_but_has_zero_wavelength_effect(self):
        _,result=run_case(1.00416693877201e-12,zero=True,field_budget=0.,intensity_budget=0.)
        self.assertTrue(result['accepted_wavelength_only'])
        self.assertEqual(result['generated_record_count'],13)
        self.assertEqual(len(result['ledger']),4)

    def test_reference_displacement_included_in_bound(self):
        _,base=run_case(1.00416693877201e-12)
        _,moved=run_case(1.00416693877201e-12,shift=.03125)
        self.assertGreater(upper(moved['ports']['Dx']['groups']['g']['field_error_upper']),
                           upper(base['ports']['Dx']['groups']['g']['field_error_upper']))
        self.assertEqual(moved['ports']['Dy'],base['ports']['Dy'])

    def test_explicit_groups_and_budgets_required(self):
        scene,_=fixture()
        with self.assertRaisesRegex(ValueError,'every source'):
            scene_wavelength_field_budget(scene,coherence_groups={},field_budget=1e-4,
                intensity_budget=2e-4,relative_budget=1e-12)
        for value in (-1.,True,float('nan'),float('inf')):
            with self.assertRaises(ValueError):run_case(field_budget=value)
            with self.assertRaises(ValueError):run_case(intensity_budget=value)
        with self.assertRaises(ValueError):run_case(1e-46)


if __name__=='__main__':unittest.main()
