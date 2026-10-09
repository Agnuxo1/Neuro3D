import unittest
import numpy as np
from Blender.blender_lab.wave_optics_v1 import angular_spectrum,gaussian_input,disk_power,paraxial_gaussian
from Tools.independent_gaussian_hankel_v1 import gaussian_radial_field


class CoherentWaveControls(unittest.TestCase):
    def test_plane_wave_outgoing_and_evanescent_branches(self):
        n=32;window=4.;wavelength=.5;distance=.7;coordinate=np.arange(n)*window/n
        for frequency in (.5,3.):
            field=np.broadcast_to(np.exp(2j*np.pi*frequency*coordinate)[None,:],(n,n)).copy()
            root=np.sqrt(complex(1-(wavelength*frequency)**2))
            expected=field*np.exp(2j*np.pi*distance*root/wavelength)
            np.testing.assert_allclose(angular_spectrum(field,window,wavelength,distance),expected,atol=2e-14,rtol=2e-14)

    def test_coherent_linearity_and_no_nonfinite_fill(self):
        a,_=gaussian_input(64,2,.2);b=1j*np.roll(a,3,axis=0)
        direct=angular_spectrum(a+b,2,.1,.5)
        composed=angular_spectrum(a,2,.1,.5)+angular_spectrum(b,2,.1,.5)
        np.testing.assert_allclose(direct,composed,atol=2e-15)
        self.assertLess(np.max(np.abs(angular_spectrum(a-a,2,.1,.5))),1e-15)
        a[0,0]=np.nan
        with self.assertRaises(ValueError):angular_spectrum(a,2,.1,.5)
        with self.assertRaises(ValueError):angular_spectrum(b,2,.1,-.5)

    def test_gaussian_boundary_and_paraxial_limit_independent_reference(self):
        radii=np.array([0,.02,.07,.15]);w=.1
        field=gaussian_radial_field(radii,w,.1,0,512)
        np.testing.assert_allclose(field,np.exp(-radii*radii/w**2),atol=2e-13)
        declared=paraxial_gaussian(w,.001,1,.15)
        native=gaussian_radial_field([0],w,.001,1,512)[0]
        expected=complex(*declared['carrier_removed_axis_field'])
        self.assertLess(abs(native-expected),2e-7)
        source,_=gaussian_input(512,2,w)
        fraction=disk_power(source,2,.15,16)/(np.pi*w*w/2)
        self.assertLess(abs(fraction-(1-np.exp(-4.5))),.0001)


if __name__=='__main__':unittest.main()
