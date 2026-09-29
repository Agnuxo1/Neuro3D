import unittest
import numpy as np
from batch_readback import compare_batch,compare_iris


class BatchReadbackTests(unittest.TestCase):
    def test_signed_batch_and_zero_rows(self):
        x=np.array([[1,-2],[0,0.]])
        w=np.array([[2,3],[-4,5.]])
        m,ref=compare_batch(x,w,[[10,-7],[0,0]])
        self.assertEqual(m['relative_l2'],0)
        self.assertEqual(m['zero_reference_rows'],1)
        self.assertTrue(m['zero_reference_rows_exact'])
        m,_=compare_batch(x,w,[[10,-7],[1,0]])
        self.assertFalse(m['zero_reference_rows_exact'])

    def test_invalid_shapes_and_nonfinite(self):
        for x,w,y in (([[1]],[[1]],[[float('nan')]]),([[1,2]],[[1]],[[1]]),([],[[1]],[[1]])):
            with self.assertRaises(ValueError): compare_batch(x,w,y)

    def test_complex_classification_and_split(self):
        y=np.zeros((4,16)); y[:,0]=1; y[1,9]=2
        result=compare_iris(y,y,np.array([0,1,0,0]),np.array([0,1,0,0]),[0,2],[1,3])
        self.assertEqual(result['test_accuracy'],1)
        self.assertEqual(result['agreement_with_current_matvec_reference'],1)
        with self.assertRaises(ValueError): compare_iris(y,y,np.array([0,1,0,0]),np.array([0,1,0,0]),[0,1],[1,3])

    def test_inputs_unchanged(self):
        x=np.array([[1.,2.]]); old=x.copy()
        compare_batch(x,np.ones((2,1)),[[3.]])
        np.testing.assert_array_equal(x,old)


if __name__=='__main__': unittest.main()
