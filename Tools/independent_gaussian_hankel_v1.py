"""Independent continuum radial Fourier-Bessel Gaussian propagation reference.

No producer FFT imports. Gauss-Legendre refinement is numerical convergence,
not a rigorous certificate of quadrature/physical error. Spectral tail bound is
analytic, using |J0|<=1 and outgoing scalar Helmholtz |H|<=1 for z>=0.
"""
import math
import numpy as np
from scipy.special import j0,roots_legendre


def quadrature(a,b,order):
    nodes,weights=roots_legendre(order)
    return (nodes+1)*(b-a)/2+a,weights*(b-a)/2


def gaussian_radial_field(radii,waist,wavelength,distance,order=512):
    assert waist>0 and wavelength>0 and distance>=0 and order>=16
    radii=np.asarray(radii,dtype=float);assert np.isfinite(radii).all() and (radii>=0).all()
    fmax=6/(math.pi*waist);cut=1/wavelength;k=2*math.pi/wavelength
    if fmax>=cut:
        theta,weights=quadrature(0,math.pi/2,order);f=np.sin(theta)/wavelength
        measure=2*math.pi*np.sin(theta)*np.cos(theta)/wavelength**2
        root=np.cos(theta);phase=-np.sin(theta)**2/(1+root)
    else:
        f,weights=quadrature(0,fmax,order);measure=2*math.pi*f
        rho=wavelength*f;root=np.sqrt(1-rho*rho);phase=-rho*rho/(1+root)
    spectrum=math.pi*waist**2*np.exp(-(math.pi*waist*f)**2)
    integrand=weights*measure*spectrum*np.exp(1j*k*distance*phase)
    fields=j0(2*math.pi*radii[:,None]*f[None,:])@integrand
    if fmax>cut:
        t,weights=quadrature(0,math.sqrt((wavelength*fmax)**2-1),order)
        f=np.sqrt(1+t*t)/wavelength;measure=2*math.pi*t/wavelength**2
        spectrum=math.pi*waist**2*np.exp(-(math.pi*waist*f)**2)
        integrand=weights*measure*spectrum*np.exp(-k*distance*t)*np.exp(-1j*k*distance)
        fields+=j0(2*math.pi*radii[:,None]*f[None,:])@integrand
    return fields


def reference(waist,wavelength,distance,radius,order=512,radial_order=128):
    radii,weights=quadrature(0,radius,radial_order)
    fields=gaussian_radial_field(np.concatenate([[0],radii]),waist,wavelength,distance,order)
    transverse_norm=math.pi*waist**2/2
    power_fraction=float(np.sum(weights*2*math.pi*radii*np.abs(fields[1:])**2)/transverse_norm)
    return {'carrier_removed_axis_field':[float(fields[0].real),float(fields[0].imag)],'disk_power_fraction':power_fraction,
            'spectral_gaussian_tail_absolute_field_bound':math.exp(-36),'frequency_order':order,'radial_order':radial_order,
            'scope':'Continuum scalar outgoing Helmholtz with Gaussian boundary field and transverse |E|^2 readout; numerical quadrature not a physical measurement or rigorous rounding certificate'}
