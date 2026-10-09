import unittest
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit.rational_interval_v1 import Interval as I
from Blender.blender_lab.operator_gram_enclosure_v1 import gram_enclosure,positive_ldl,normalization,rayleigh

def z(a,b=0):return I(a),I(b)

class GramControls(unittest.TestCase):
    def test_orthonormal_columns(self):
        gram=gram_enclosure([[z(1),z(0)],[z(0),z(1)]])
        self.assertEqual(positive_ldl(gram)['rank'],2)
        self.assertEqual(normalization(gram,[[1,0],[0,0]],F(1,10**11))['contractivity_metric'],1)

    def test_identical_columns_unknown_rank_and_coherent_gain(self):
        gram=gram_enclosure([[z(1),z(1)]])
        self.assertEqual(positive_ldl(gram)['status'],'UNKNOWN_POSITIVE_RANK_NOT_PROVED')
        self.assertEqual(normalization(gram,[[1,0],[1,0]],F(1,10**11))['contractivity_metric'],0)
        self.assertTrue(rayleigh(gram,[[1,0],[1,0]]).contains(2))

    def test_imaginary_coherence_and_zero_rejection(self):
        gram=gram_enclosure([[z(1),z(0,1)]])
        self.assertTrue(rayleigh(gram,[[1,0],[0,-1]]).contains(2))
        self.assertTrue(rayleigh(gram,[[1,0],[0,1]]).contains(0))
        with self.assertRaises(ValueError):rayleigh(gram,[[0,0],[0,0]])

    def test_interval_rank_is_unknown_without_positive_pivots(self):
        gram=gram_enclosure([[(I(-1,1),I(0))]])
        self.assertEqual(positive_ldl(gram)['status'],'UNKNOWN_POSITIVE_RANK_NOT_PROVED')

if __name__=='__main__':unittest.main()
