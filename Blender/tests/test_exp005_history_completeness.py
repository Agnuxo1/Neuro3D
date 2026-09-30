import copy
import unittest
from exp005_history_completeness_audit import audit,fixture,duplicate_sources,scene_binding,validate_history,validate_complete_tree


class CompleteHistory(unittest.TestCase):
    def test_three_complete_trees_and_four_truncations(self):
        r=audit();self.assertEqual(len(r['positives']),3);self.assertEqual(len(r['rejected_valid_prefixes']),4)
        self.assertEqual(len(r['positives'][2]['result']['terminal_ids']),4)

    def test_zero_field_splitter_branches_not_silently_pruned(self):
        for tau in (0.,1.):
            s,r=fixture(True);s['objects']['B']['power_transmittance']=tau;sha,_=scene_binding(s)
            for row in r:row['snapshot_sha256']=sha
            self.assertTrue(validate_complete_tree(s,r)['geometric_tree_complete'])
            # This contract requires both events, not an implicit amplitude cutoff.
            incomplete=[row for row in r if row['id'] in (0,1,3)]
            validate_history(s,incomplete)
            with self.assertRaisesRegex(ValueError,'incomplete tree'):validate_complete_tree(s,incomplete)

    def test_each_declared_source_needs_its_complete_tree(self):
        s,r=duplicate_sources();incomplete=[row for row in r if row['id']<=5]
        validate_history(s,incomplete)
        with self.assertRaisesRegex(ValueError,'incomplete tree'):validate_complete_tree(s,incomplete)

    def test_sibling_order_and_input_preservation(self):
        s,r=fixture(True);r=[r[i] for i in (0,2,4,1,3)];before=copy.deepcopy((s,r))
        result=validate_complete_tree(s,r);self.assertEqual((s,r),before)
        self.assertEqual(result['record_count'],5)

    def test_not_native_or_optical_completeness(self):
        s,r=fixture(True);out=validate_complete_tree(s,r)
        self.assertFalse(out['fields_computed']);self.assertFalse(out['terminal_modes_validated'])
        self.assertFalse(out['native_exemption_allowed'])
        self.assertFalse(validate_history(s,r)['all_branches_proved_complete'])


if __name__=='__main__':unittest.main()
