# Remedial larger-window v2; v1 negative outcome and source remain immutable.
"""Separately frozen scalar wave regime study, never a full network claim."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Blender.blender_lab.wave_optics_v1 import gaussian_input,angular_spectrum,disk_power,paraxial_gaussian,grid
from Tools.independent_gaussian_hankel_v1 import reference,gaussian_radial_field
from Tools.audit_captured_pilot_result_v1 import need


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();p=json.loads(args.profile.read_bytes());args.out.mkdir(exist_ok=False)
    waist=p['gaussian_waist_BU'];aperture=p['detector_radius_BU'];norm=np.pi*waist**2/2;rows=[];gates=[];start=time.perf_counter()
    with (args.out/'progress.jsonl').open('x',encoding='utf-8') as stream:
        for wavelength in p['wavelengths_BU']:
            for distance in p['distances_BU']:
                low=reference(waist,wavelength,distance,aperture,512,128);high=reference(waist,wavelength,distance,aperture,1024,256)
                refinement=max(abs(complex(*low['carrier_removed_axis_field'])-complex(*high['carrier_removed_axis_field'])),abs(low['disk_power_fraction']-high['disk_power_fraction']))
                paraxial=paraxial_gaussian(waist,wavelength,distance,aperture)
                pair=[]
                for size,window in p['grids']:
                    tick=time.perf_counter();source,dx=gaussian_input(size,window,waist)
                    input_norm=float(np.sum(np.abs(source)**2)*dx*dx)
                    field=angular_spectrum(source,window,wavelength,distance,carrier_removed=True)
                    full=float(np.sum(np.abs(field)**2)*dx*dx)/norm
                    fraction=disk_power(field,window,aperture,p['disk_subpixels'])/norm
                    axis_field=field[size//2,size//2];axis_error=abs(axis_field-complex(*high['carrier_removed_axis_field']))
                    indices=np.unique(np.round(np.linspace(0,min(size//2-1,int(2/dx)),65)).astype(int));radii=indices*dx
                    radial_native=field[size//2,size//2+indices];radial_ref=gaussian_radial_field(radii,waist,wavelength,distance,1024)
                    radial_error=float(np.max(np.abs(radial_native-radial_ref)))
                    row={'wavelength_BU':wavelength,'distance_BU':distance,'size':size,'window_BU':window,'dx_BU':dx,
                         'carrier_removed_axis_field':[float(axis_field.real),float(axis_field.imag)],'disk_power_fraction':fraction,
                         'total_transverse_norm_fraction':full,'input_norm_relative_error':abs(input_norm/norm-1),
                         'independent_axis_absolute_difference':float(axis_error),'independent_radial_field_max_absolute_difference':radial_error,
                         'independent_disk_fraction_absolute_difference':abs(fraction-high['disk_power_fraction']),
                         'paraxial_disk_fraction':paraxial['disk_power_fraction'],'paraxial_disk_absolute_difference':abs(fraction-paraxial['disk_power_fraction']),
                         'hankel_reference':high,'reference_refinement_max_absolute_difference':float(refinement),
                         'radial_radii_BU':radii.tolist(),'radial_field_real':radial_native.real.tolist(),'radial_field_imag':radial_native.imag.tolist(),
                         'independent_radial_field_real':radial_ref.real.tolist(),'independent_radial_field_imag':radial_ref.imag.tolist(),
                         'seconds':time.perf_counter()-tick}
                    tail_power=np.exp(-2*np.pi**2*waist**2/wavelength**2)
                    row['input_norm_gate']=row['input_norm_relative_error']<=p['gates']['input_norm_relative']
                    row['evanescent_norm_gate']=bool(1-tail_power-p['gates']['norm_roundoff']<=full<=1+p['gates']['norm_roundoff'])
                    pair.append(row);rows.append(row);stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
                    print(json.dumps({k:row[k] for k in ('wavelength_BU','distance_BU','size','window_BU','independent_radial_field_max_absolute_difference','disk_power_fraction')}),flush=True)
                    del source,field
                fine=next(r for r in pair if r['size']==4096 and r['window_BU']==32)
                expanded=next(r for r in pair if r['size']==4096 and r['window_BU']==64)
                medium=next(r for r in pair if r['size']==2048)
                gate={'wavelength_BU':wavelength,'distance_BU':distance,
                      'reference_refinement':refinement<=p['gates']['reference_refinement_absolute'],
                      'finest_radial_complex_field':fine['independent_radial_field_max_absolute_difference']<=p['gates']['finest_radial_field_absolute'],
                      'finest_disk_fraction':fine['independent_disk_fraction_absolute_difference']<=p['gates']['finest_disk_fraction_absolute'],
                      'expanded_window_radial_complex_field':expanded['independent_radial_field_max_absolute_difference']<=p['gates']['expanded_radial_field_absolute'],
                      'expanded_window_disk_fraction':expanded['independent_disk_fraction_absolute_difference']<=p['gates']['expanded_disk_fraction_absolute'],
                      'disk_grid_refinement':abs(fine['disk_power_fraction']-medium['disk_power_fraction'])<=p['gates']['disk_grid_refinement_absolute']}
                need(medium['dx_BU']==expanded['dx_BU'] and medium['radial_radii_BU']==expanded['radial_radii_BU'],'fixed spatial sampling for window comparison')
                medium_field=np.asarray(medium['radial_field_real'])+1j*np.asarray(medium['radial_field_imag'])
                expanded_field=np.asarray(expanded['radial_field_real'])+1j*np.asarray(expanded['radial_field_imag'])
                gate['same_dx_window_field']=float(np.max(np.abs(medium_field-expanded_field)))<=p['gates']['same_dx_window_field_absolute']
                gate['same_dx_window_disk']=abs(medium['disk_power_fraction']-expanded['disk_power_fraction'])<=p['gates']['same_dx_window_disk_fraction_absolute']
                gates.append(gate)
    passed=all(all(value for key,value in row.items() if key not in ('wavelength_BU','distance_BU')) for row in gates) and all(r['input_norm_gate'] and r['evanescent_norm_gate'] for r in rows)
    result={'schema':'optic_neuro_blender.gaussian_wave_reference.v2','status':'PASS' if passed else 'FAIL_ONE_OR_MORE_FROZEN_GATES',
            'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'rows':rows,'gates':gates,'worker_seconds':time.perf_counter()-start,
            'gpu_executed':False,'original_scalar_graph_modified':False,'physical_network_fidelity_established':False,
            'scope':'Declared independent scalar Gaussian half-space experiment in BU with outgoing Helmholtz, periodic FFT discretization and independent continuum radial quadrature. Coherent complex fields kept. Transverse integral |E|^2 readout is not a full vector Poynting flux or captured-network modal detector. No Maxwell/measurement/universal error certificate.'}
    (args.out/'result.json').write_bytes((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'status':result['status'],'rows':len(rows),'worker_seconds':result['worker_seconds'],'gates':gates}),flush=True)
    return 0 if passed else 2


if __name__=='__main__':raise SystemExit(main())
