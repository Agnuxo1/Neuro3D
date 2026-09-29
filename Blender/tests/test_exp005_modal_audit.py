"""CPU-only diagnostics and deliberate counterexamples; no Blender or GPU."""
import cmath
import copy
import unittest

from exp005_modal_audit import modal_audit
from exp005_triangle_oracle import trace_scene
from test_exp005_triangle_oracle import mz


def two_inputs():
    scene = mz()
    scene['sources'].append({'id':'s2','position_BU':(0,-1,0),
                            'direction':(0,1,0),'field_reim':[0,0]})
    return scene


class ModalAuditTests(unittest.TestCase):
    def test_basis_and_both_pair_phases_across_treatments(self):
        for wavelength,phase in ((.1,0),(.101,0),(.1,.1)):
            with self.subTest(wavelength=wavelength,phase=phase):
                scene = two_inputs(); scene['lambda_BU']=wavelength
                scene['objects']['r1']['phase_rad']=phase
                audit = modal_audit(scene)
                self.assertEqual(audit['traces'],4)
                self.assertEqual(len(audit['pair_cases']),2)
                self.assertLess(audit['gram_identity_error'],1e-12)
                self.assertLess(audit['worst_pair_complex_error'],1e-12)
                self.assertLess(audit['worst_pair_conditional_power_error'],1e-12)
                self.assertFalse(audit['geometry_gate_passed'])

    def test_power_only_gate_misses_pair_phase_bug(self):
        def faulty(scene,**limits):
            result = trace_scene(scene,**limits)
            if sum(any(v!=0 for v in s['field_reim']) for s in scene['sources'])>1:
                result['fields'] = {n:f*cmath.exp(.02j) for n,f in result['fields'].items()}
            return result
        audit = modal_audit(two_inputs(),tracer=faulty)
        self.assertLess(audit['gram_identity_error'],1e-12)
        self.assertLess(audit['worst_pair_conditional_power_error'],1e-12)
        self.assertGreater(audit['worst_pair_complex_error'],.01)

    def test_coincident_inputs_do_not_count_as_two_orthogonal_modes(self):
        scene = two_inputs(); scene['sources'][1] = dict(scene['sources'][0],id='alias')
        audit = modal_audit(scene)
        self.assertGreater(audit['gram_identity_error'],.99)
        self.assertGreater(audit['worst_pair_conditional_power_error'],1.99)

    def test_escape_channels_cannot_be_removed_from_balance(self):
        scene = two_inputs(); scene['objects']['X']['kind']='escape'
        audit = modal_audit(scene)
        self.assertIn('X',audit['ports'])
        self.assertLess(audit['gram_identity_error'],1e-12)
        def detector_only(scene,**limits):
            result = trace_scene(scene,**limits); del result['fields']['X']; return result
        with self.assertRaises(ValueError): modal_audit(scene,tracer=detector_only)

    def test_snapshot_not_mutated(self):
        scene = two_inputs(); before = copy.deepcopy(scene)
        modal_audit(scene)
        self.assertEqual(scene,before)

    def test_bounds_and_nonfinite_fields(self):
        scene = two_inputs()
        scene['sources'] = [dict(scene['sources'][0],id=str(i)) for i in range(9)]
        with self.assertRaises(ValueError): modal_audit(scene)
        def bad(scene,**limits):
            result = trace_scene(scene,**limits); result['fields']['X']=complex(float('nan'),0); return result
        with self.assertRaises(ValueError): modal_audit(two_inputs(),tracer=bad)


if __name__=='__main__': unittest.main()
