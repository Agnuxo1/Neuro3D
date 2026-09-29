import unittest
import numpy as np
from exr_controls import inspect_pixels


class PixelTests(unittest.TestCase):
    def fixture(self):
        x=np.array([[1.,-2.],[0.,1.]])
        w=np.array([[.5,-.2],[-.1,.8]])
        im=np.zeros((8,2,4))
        wr=np.concatenate((w,-w)); rows=np.concatenate((np.maximum(x,0),np.maximum(-x,0)),1)
        for t in range(2):
            im[t*4:t*4+4,:,0]=rows[t,:,None]*np.maximum(wr,0)
            im[t*4:t*4+4,:,1]=rows[t,:,None]*np.maximum(-wr,0)
        return im,x,w
    def test_signed_products_and_cpu_sum(self):
        im,x,w=self.fixture(); y,m=inspect_pixels(im,x,w,[1,2])
        np.testing.assert_allclose(y,x@w)
        self.assertEqual(m['pixel_product_max_abs_error'],0)
    def test_corruption_is_visible(self):
        im,x,w=self.fixture(); im[0,0,0]+=.1
        _,m=inspect_pixels(im,x,w,[1,2]); self.assertGreater(m['pixel_product_max_abs_error'],.09)
    def test_bad_grid_fails_closed(self):
        im,x,w=self.fixture()
        for tiles in ([2,1],[True,2],[1,1]):
            with self.assertRaises(ValueError): inspect_pixels(im,x,w,tiles)
    def test_nonfinite_fails_closed(self):
        im,x,w=self.fixture(); im[0,0,0]=float('nan')
        with self.assertRaises(ValueError): inspect_pixels(im,x,w,[1,2])


if __name__=='__main__': unittest.main()
