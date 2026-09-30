import copy
from fractions import Fraction as F
import unittest
from exp005_history_trace_cpu_audit import audit,fixture,trace_scene,ideal_fields
from history_trace_cpu_v1 import represented


class HistoryTraceCPU(unittest.TestCase):
    def test_three_controls_from_geometry_not_input_paths(self):
        out=audit();self.assertEqual(len(out['cases']),3);self.assertEqual(len(out['cap_negatives']),5)
        for row in out['cases']:
            self.assertLess(row['field_error'],1e-13)
            self.assertEqual(len(row['trace']['records']),13)
            self.assertEqual(row['trace']['nearest_queries'],9)
            self.assertFalse(row['trace']['fields_computed'])

    def test_zero_field_and_extreme_T_never_prune_geometric_branches(self):
        for tau in (0.,1.):
            s,_=fixture();s['sources'][0]['field_reim']=[0.,0.]
            for obj in s['objects'].values():
                if obj['kind']=='bs':obj['power_transmittance']=tau
            out=trace_scene(s);self.assertEqual(len(out['records']),13)
            f=ideal_fields(s,out['records'],coherence_groups={'s':'g'})
            self.assertEqual(len(f['ledger']),4)
            self.assertTrue(all(p['intensity']==0. for p in f['ports'].values()))

    def test_two_sources_separate_ancestry_and_coherence_groups(self):
        s,_=fixture();second=copy.deepcopy(s['sources'][0]);second['id']='other';second['field_reim']=[.5,0.]
        s['sources'].append(second);before=copy.deepcopy(s);out=trace_scene(s)
        self.assertEqual(s,before);self.assertEqual(len(out['records']),26)
        self.assertEqual(out['nearest_queries'],18)
        parents={r['id']:r for r in out['records']}
        for r in out['records']:
            if r['parent_id'] is not None:self.assertEqual(r['source_id'],parents[r['parent_id']]['source_id'])
        same=ideal_fields(s,out['records'],coherence_groups={'s':'g','other':'g'})
        independent=ideal_fields(s,out['records'],coherence_groups={'s':'g','other':'h'})
        self.assertAlmostEqual(same['ports']['Dx']['intensity'],2.25,places=13)
        self.assertAlmostEqual(independent['ports']['Dx']['intensity'],1.25,places=13)

    def test_nonrepresentable_rational_departure_rejected_not_snapped(self):
        with self.assertRaisesRegex(ValueError,'no snapping'):represented((F(1,3),F(0),F(0)))
        self.assertEqual(represented((F(1,8),F(0),F(0))),[.125,0.,0.])
        s,_=fixture();s['objects']={'Dx':s['objects']['Dx']}
        s['objects']['Dx']['vertices_world_BU']=[[2.,-1.,-.125],[2.,1.,-.125],
                                                [2.,1.,.125],[2.,-1.,.125]]
        s['sources'][0]['position_BU']=[0.,0.,0.];s['sources'][0]['direction']=[3.,1.,0.]
        # Exact hit (2,2/3,0), not representable as binary64. No partial result.
        with self.assertRaisesRegex(ValueError,'no snapping'):trace_scene(s)


if __name__=='__main__':unittest.main()
