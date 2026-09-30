import copy
import unittest
from exp005_history_lineage_audit import audit,fixture,negatives
from history_lineage_cpu_v1 import scene_binding,validate_history


class HistoryLineage(unittest.TestCase):
    def test_two_valid_prefixes_and_eight_negatives(self):
        report=audit();self.assertEqual(len(report['valid']),2);self.assertEqual(len(report['rejected']),8)

    def test_full_optics_and_order_binding(self):
        s,r=fixture();old=r[0]['snapshot_sha256']
        for mutate in (lambda s:s['objects']['M'].update(phase_rad=.2),lambda s:s.update(lambda_BU=.14),
                       lambda s:s['sources'][0].update(field_reim=[0.,1.]),lambda s:s.update(objects=dict(reversed(list(s['objects'].items()))))):
            other=copy.deepcopy(s);mutate(other);self.assertNotEqual(scene_binding(other)[0],old)
            with self.assertRaises(ValueError):validate_history(other,r)

    def test_no_implicit_native_exemption_or_completeness(self):
        s,r=fixture(True);out=validate_history(s,r[:3]);self.assertFalse(out['native_exemption_allowed'])
        self.assertFalse(out['all_branches_proved_complete']);self.assertFalse(out['fields_computed'])

    def test_terminal_child_rejected(self):
        s,r=fixture();child=copy.deepcopy(r[1]);child.update(id=3,parent_id=2,depth=3);r.append(child)
        with self.assertRaises(ValueError):validate_history(s,r)

    def test_duplicate_branch_rejected(self):
        s,r=fixture();child=copy.deepcopy(r[1]);child['id']=3;r.append(child)
        with self.assertRaises(ValueError):validate_history(s,r)

    def test_second_source_ancestry_rejected(self):
        s,r=fixture();s['sources'].append({**s['sources'][0],'id':'s2'});sha,_=scene_binding(s)
        for row in r:row['snapshot_sha256']=sha
        root=copy.deepcopy(r[0]);root.update(id=3,source_id='s2');r.insert(1,root)
        r[2]['source_id']='s2'
        with self.assertRaises(ValueError):validate_history(s,r)

    def test_small_positive_gap_not_dropped(self):
        s,r=fixture(True);gap=2**-30
        s['objects']['T']['vertices_world_BU']=[[1.+gap,y,z] for _,y,z in s['objects']['T']['vertices_world_BU']]
        s['objects']['T']['mode_origin_BU']=[1.+gap,0.,0.];sha,_=scene_binding(s)
        for row in r:row['snapshot_sha256']=sha
        r[3]['origin_BU']=[1.+gap,0.,0.];out=validate_history(s,r)
        self.assertEqual(out['records'][3]['t_parameter_exact'],[1,2**30])

    def test_inputs_unchanged_and_bounds_explicit(self):
        s,r=fixture();before=copy.deepcopy((s,r));validate_history(s,r);self.assertEqual((s,r),before)
        for change in ({'depth':33},{'id':True},{'snapshot_sha256':'0'*64}):
            bad=copy.deepcopy(r);bad[1].update(change)
            with self.assertRaises(ValueError):validate_history(s,bad)


if __name__=='__main__':unittest.main()
