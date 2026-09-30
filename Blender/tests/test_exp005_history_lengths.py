import copy
from fractions import Fraction as F
import unittest
from exp005_history_lengths_audit import audit,fixture,rebinding,reconstruct_lengths,sqrt_interval


class HistoryLengths(unittest.TestCase):
    def test_analytic_lengths_and_references(self):
        out=audit(); self.assertEqual(len(out['valid']),4)
        for case,expected in zip(out['valid'],([3],[2,3],[2.25,3],[2,3,2,3])):
            self.assertEqual([r['effective_length']['outward_float_BU'] for r in case['result']['terminals']],
                             [[x,x] for x in expected])
        self.assertIn('collinear',out['rejected_terminal']['reason'])

    def test_irrational_enclosures_not_rounded_exact(self):
        for q in (F(2),F(5),F(2**60+1),F(1,2**60)):
            lo,hi=sqrt_interval(q);self.assertLessEqual(lo*lo,q);self.assertGreaterEqual(hi*hi,q)
        lo,hi=sqrt_interval(2); self.assertLess(lo,hi)
        with self.assertRaises(ValueError):sqrt_interval(-1)

    def test_no_history_truncation_or_input_mutation(self):
        s,r=fixture(True);before=copy.deepcopy((s,r));out=reconstruct_lengths(s,r)
        self.assertEqual((s,r),before)
        with self.assertRaises(ValueError):reconstruct_lengths(s,r[:-1])
        self.assertFalse(out['phase_error_certified']);self.assertFalse(out['native_exemption_allowed'])

    def test_terminal_antiparallel_rejected_and_scaled_axis_accepted(self):
        s,r=fixture(True);s['objects']['T']['mode_direction']=[7.,0.,0.];rebinding(s,r)
        self.assertEqual(reconstruct_lengths(s,r)['terminals'][0]['effective_length']['outward_float_BU'],[2.,2.])
        s['objects']['T']['mode_direction']=[-1.,0.,0.];rebinding(s,r)
        with self.assertRaisesRegex(ValueError,'collinear'):reconstruct_lengths(s,r)


if __name__=='__main__':unittest.main()
