import copy
import json
import unittest
from exp005_rt_report_audit import audit, recalculate, PEER


class RTReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report = audit()

    def test_five_retained_pairs_are_arithmetically_consistent(self):
        self.assertEqual(len(self.report['rows']), 5)
        self.assertTrue(all(v <= 1e-9 for r in self.report['rows'] for v in r['arithmetic_checks'].values()))
        self.assertTrue(self.report['triangle_generator_AST_equal'])

    def test_samples_not_same_as_brute_batch_and_coverage_is_partial(self):
        self.assertEqual(self.report['rt_nominal_samples_per_render'], 16*1048576)
        self.assertEqual(self.report['brute_pixel_center_rays_per_batch'], 1048576)
        self.assertEqual(self.report['coverage_cases'], 1)
        self.assertEqual(self.report['coverage_disagreement_fraction'], 961/1048576)

    def test_unsubtracted_median_is_slower_than_subtracted_min(self):
        for row in self.report['rows']:
            self.assertLess(row['rt_nominal_rate_raw_median_Mrays_s'], row['rt_nominal_rate_subtracted_min_Mrays_s'])
            self.assertLess(row['raw_hot_median_ratio'], row['peer_derived_ratio'])

    def test_altered_workload_duplicate_and_negative_measurement_reject(self):
        rt = json.loads((PEER/'rt_final.json').read_bytes())
        brute = json.loads((PEER/'brute_same.json').read_bytes())
        for kind in ('rays', 'duplicate', 'time'):
            changed = copy.deepcopy(rt)
            if kind == 'rays': changed['rays'] += 1
            elif kind == 'duplicate': changed['rows'][0] = copy.deepcopy(changed['rows'][1])
            else: changed['rows'][0]['t2plus_s'][0] = -1.
            with self.assertRaises(ValueError): recalculate(changed, brute, 1024)


if __name__ == '__main__': unittest.main()
