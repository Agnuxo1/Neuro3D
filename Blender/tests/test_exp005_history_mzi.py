import copy
import math
import unittest
from exp005_history_mzi_audit import audit,fixture,ideal_fields,scene_binding


class HistoryMZI(unittest.TestCase):
    def test_six_analytic_controls_and_balance(self):
        out=audit();self.assertEqual(len(out['cases']),6)
        self.assertLess(out['max_field_error'],1e-13);self.assertLess(out['max_balance_error'],1e-13)
        dark=out['cases'][0]['result']['ports'];switched=out['cases'][2]['result']['ports']
        self.assertAlmostEqual(dark['Dx']['intensity'],1.,places=13)
        self.assertAlmostEqual(dark['Dy']['intensity'],0.,places=13)
        self.assertAlmostEqual(switched['Dx']['intensity'],0.,places=13)
        self.assertAlmostEqual(switched['Dy']['intensity'],1.,places=13)

    def test_distinct_verified_ancestors_and_length(self):
        s,r=fixture();out=ideal_fields(s,r,coherence_groups={'s':'g'})
        for row in out['ledger']:self.assertEqual(row['effective_length']['outward_float_BU'],[4.,4.])
        parents={row['id']:row['parent_id'] for row in r}
        self.assertEqual(parents[5],3);self.assertEqual(parents[7],4)
        self.assertNotEqual(r[3]['origin_BU'],r[4]['origin_BU'])
        self.assertEqual(len(r),13)

    def test_missing_arm_terminal_rejected_without_pruning(self):
        for removed in (9,10,11,12):
            s,r=fixture()
            with self.assertRaisesRegex(ValueError,'incomplete tree'):
                ideal_fields(s,[row for row in r if row['id']!=removed],coherence_groups={'s':'g'})

    def test_scene_phase_and_reference_binding_inputs_unchanged(self):
        s,r=fixture(math.pi/2);before=copy.deepcopy((s,r))
        out=ideal_fields(s,r,coherence_groups={'s':'g'});self.assertEqual((s,r),before)
        s['objects']['MA']['phase_rad']=math.pi
        with self.assertRaisesRegex(ValueError,'stale scene'):ideal_fields(s,r,coherence_groups={'s':'g'})
        sha,_=scene_binding(s)
        for row in r:row['snapshot_sha256']=sha
        new=ideal_fields(s,r,coherence_groups={'s':'g'})
        self.assertNotEqual(out['configuration_sha256'],new['configuration_sha256'])


if __name__=='__main__':unittest.main()
