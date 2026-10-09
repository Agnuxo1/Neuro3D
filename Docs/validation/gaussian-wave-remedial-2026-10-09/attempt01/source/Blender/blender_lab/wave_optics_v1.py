"""Original coherent scalar Helmholtz angular spectrum, in declared common units.

FFT means a sampled periodic computational window. Returned fields retain phase;
this module does not validate the physical model of a captured point-mode graph.
"""
import math
import numpy as np
from Tools.audit_captured_pilot_result_v1 import need


def grid(size,window_BU):
    need(isinstance(size,int) and size>=8 and size%2==0 and math.isfinite(window_BU) and window_BU>0,'even grid and finite positive window required')
    dx=window_BU/size
    return (np.arange(size)-size//2)*dx,dx


def gaussian_input(size,window_BU,waist_BU):
    need(math.isfinite(waist_BU) and waist_BU>0,'positive Gaussian amplitude waist required')
    axis,dx=grid(size,window_BU)
    return np.exp(-(axis[:,None]**2+axis[None,:]**2)/waist_BU**2).astype(np.complex128),dx


def angular_spectrum(field,window_BU,wavelength_BU,distance_BU,*,carrier_removed=False):
    field=np.asarray(field,dtype=np.complex128)
    need(field.ndim==2 and field.shape[0]==field.shape[1] and np.isfinite(field).all(),'finite square complex field required')
    _,dx=grid(field.shape[0],window_BU)
    need(math.isfinite(wavelength_BU) and wavelength_BU>0 and math.isfinite(distance_BU) and distance_BU>=0,'positive wavelength and forward distance required')
    frequencies=np.fft.fftfreq(field.shape[0],d=dx)
    rho2=(wavelength_BU*frequencies[:,None])**2+(wavelength_BU*frequencies[None,:])**2
    propagating=rho2<=1
    longitudinal=np.sqrt(np.maximum(1-rho2,0));decay=np.sqrt(np.maximum(rho2-1,0));k=2*np.pi/wavelength_BU
    # Stable sqrt(1-s)-1 = -s/(sqrt(1-s)+1), common longitudinal carrier only.
    phase=-rho2/(longitudinal+1) if carrier_removed else longitudinal
    transfer=np.exp(1j*k*distance_BU*phase)
    if np.any(~propagating):
        transfer[~propagating]=np.exp(-k*distance_BU*decay[~propagating])*np.exp(-1j*k*distance_BU if carrier_removed else 0j)
    result=np.fft.ifft2(np.fft.fft2(field)*transfer)
    need(np.isfinite(result).all(),'nonfinite propagated field rejected')
    return result


def disk_power(field,window_BU,radius_BU,subpixels=8):
    field=np.asarray(field,dtype=np.complex128)
    need(field.ndim==2 and field.shape[0]==field.shape[1] and np.isfinite(field).all(),'finite square field required')
    need(math.isfinite(radius_BU) and radius_BU>0 and isinstance(subpixels,int) and 1<=subpixels<=32,'positive aperture and bounded quadrature required')
    axis,dx=grid(field.shape[0],window_BU)
    need(radius_BU+dx<window_BU/2,'disk must lie inside declared computational window')
    chosen=np.where(np.abs(axis)<=radius_BU+dx)[0];local=axis[chosen];weights=np.zeros((len(local),len(local)),dtype=float)
    for i in range(subpixels):
        for j in range(subpixels):
            ox=((i+.5)/subpixels-.5)*dx;oy=((j+.5)/subpixels-.5)*dx
            weights+=((local[:,None]+ox)**2+(local[None,:]+oy)**2<=radius_BU**2)
    intensities=np.abs(field[np.ix_(chosen,chosen)])**2
    return float(np.sum(intensities*weights/subpixels**2)*dx*dx)


def paraxial_gaussian(waist_BU,wavelength_BU,distance_BU,radius_BU):
    need(all(math.isfinite(v) and v>0 for v in (waist_BU,wavelength_BU,radius_BU)) and math.isfinite(distance_BU) and distance_BU>=0,'finite declared Gaussian parameters required')
    zr=np.pi*waist_BU**2/wavelength_BU;ratio=distance_BU/zr
    axis_field=1/(1+1j*ratio);width=waist_BU*math.sqrt(1+ratio*ratio)
    return {'rayleigh_length_BU':zr,'intensity_radius_BU':width,'carrier_removed_axis_field':[axis_field.real,axis_field.imag],
            'disk_power_fraction':-math.expm1(-2*radius_BU**2/width**2),'source_transverse_norm':np.pi*waist_BU**2/2,
            'scope':'Paraxial analytic Gaussian scalar field, not exact high-angle Helmholtz or full electromagnetic flux'}
