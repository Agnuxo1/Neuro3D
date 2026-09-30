import copy
import math
import unittest
from exp005_history_fields_audit import audit,fixture,rebinding,ideal_fields


class HistoryFields(unittest.TestCase):
    def test_analytic_splitters_and_explicit_coherence(self):
        out=audit();self.assertEqual(len(out['analytic_cases']),7)
        for item in out['analytic_cases']:
            result=item['result'];self.assertFalse(result['native_precision_certified'])
            self.assertFalse(result['spatial_overlap_validated'])
            self.assertEqual(result['fields_computed_on'],'CPU Python standard-library complex arithmetic')

    def test_complex_amplitude_and_scene_mirror_phase(self):
        s,r=fixture();s['sources'][0]['field_reim']=[.3,.4];s['objects']['M']['phase_rad']=math.pi/2;rebinding(s,r)
        before=copy.deepcopy((s,r));out=ideal_fields(s,r,coherence_groups={'s':'g'})
        actual=out['ports']['D']['groups']['g']['field_reim']
        self.assertAlmostEqual(actual[0],.4,places=14);self.assertAlmostEqual(actual[1],-.3,places=14)
        self.assertAlmostEqual(out['ports']['D']['intensity'],.25,places=14)
        self.assertEqual((s,r),before)

    def test_reference_quarter_turn_and_large_integer_cycles(self):
        s,r=fixture();s['objects']['D']['mode_origin_BU'][0]-=.03125;rebinding(s,r)
        out=ideal_fields(s,r,coherence_groups={'s':'g'})
        self.assertEqual(out['ledger'][0]['reduced_turns_midpoint'],[1,4])
        actual=out['ports']['D']['groups']['g']['field_reim']
        self.assertAlmostEqual(actual[0],0.,places=14);self.assertAlmostEqual(actual[1],-1.,places=14)
        s,r=fixture();s['lambda_BU']=2.**-50;rebinding(s,r)
        out=ideal_fields(s,r,coherence_groups={'s':'g'})
        self.assertEqual(out['ledger'][0]['reduced_turns_midpoint'],[0,1])
        self.assertEqual(out['ports']['D']['groups']['g']['field_reim'],[-1.,0.])

    def test_no_implicit_groups_or_truncated_tree(self):
        s,r=fixture(True)
        for groups in ({},{'s':''},{'s':'g','undeclared':'g'}):
            with self.assertRaises(ValueError):ideal_fields(s,r,coherence_groups=groups)
        with self.assertRaises(ValueError):ideal_fields(s,r[:-1],coherence_groups={'s':'g'})
        a=ideal_fields(s,r,coherence_groups={'s':'g'});b=ideal_fields(s,r,coherence_groups={'s':'other'})
        self.assertNotEqual(a['configuration_sha256'],b['configuration_sha256'])

    def test_zero_field_keeps_geometric_terminals(self):
        s,r=fixture(True);s['sources'][0]['field_reim']=[0.,0.];rebinding(s,r)
        out=ideal_fields(s,r,coherence_groups={'s':'g'})
        self.assertEqual(len(out['ledger']),2)
        self.assertEqual([out['ports'][p]['intensity'] for p in ('T','E')],[0.,0.])


if __name__=='__main__':unittest.main()
