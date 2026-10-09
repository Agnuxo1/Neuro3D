"""Same complex128 geometry/input CPU/CUDA graph and equivalent dense baselines."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,hashlib,json,subprocess,sys,time,statistics
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.train_captured_geometry_v1 import parameters_and_bases
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Blender.blender_lab.torch_geometry_backend_v1 import TorchGeometryBackend


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();p=json.loads(args.profile.read_text());args.out.mkdir(exist_ok=False)
    total_start=time.perf_counter();t=time.perf_counter();import torch
    import_seconds=time.perf_counter()-t;torch.set_num_threads(1)
    need(torch.cuda.is_available(),'actual CUDA device required')
    device=torch.device('cuda:0');props=torch.cuda.get_device_properties(device)
    hardware=subprocess.check_output(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],text=True).strip()
    need(p['expected_gpu_uuid'] in hardware and props.name==p['expected_gpu_name'],'declared actual NVIDIA identity required')
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    t=time.perf_counter();scene=decode(json.loads((ROOT/p['scene']).read_text()));graph=decode(json.loads((ROOT/p['graph']).read_text()))
    parameters,_=parameters_and_bases(scene);net=AffineGeometryNetwork(scene,graph,parameters);geometry_seconds=time.perf_counter()-t
    t=time.perf_counter();backend=TorchGeometryBackend(net,device);prepared=backend.prepare(np.zeros(16));packed=backend.upload(prepared);torch.cuda.synchronize();packing_transfer_seconds=time.perf_counter()-t
    x=np.asarray([np.asarray(a[0])+1j*np.asarray(a[1]) for a in p['coherent_probes']],dtype=np.complex128)
    t=time.perf_counter();cpu=net.forward(x,np.zeros(16));cpu_probe_seconds=time.perf_counter()-t
    t=time.perf_counter();gpu_x=torch.tensor(x,dtype=torch.complex128,device=device);torch.cuda.synchronize();input_transfer_seconds=time.perf_counter()-t
    t=time.perf_counter();gpu=backend.forward(gpu_x,packed);torch.cuda.synchronize();gpu_probe_seconds=time.perf_counter()-t
    t=time.perf_counter();readback={k:v.detach().cpu().numpy() for k,v in gpu.items()};torch.cuda.synchronize();readback_seconds=time.perf_counter()-t
    errors={k:float(np.max(np.abs(cpu[k]-readback[k]))) for k in cpu}
    need(errors['fields']<=p['field_tolerance'] and errors['powers']<=p['power_tolerance'] and max(errors['field_jacobian'],errors['power_jacobian'])<=p['gradient_tolerance'],'GPU/CPU samecomplex128 parity gate')
    weights=torch.tensor(p['autograd_weights'],dtype=torch.float64,device=device)
    reference,auto_gradient=backend.autograd_reference(gpu_x,packed,weights)
    own_gradient=(gpu['power_jacobian']*weights[:,:,None]).sum(dim=(0,1))
    auto_error=float((auto_gradient-own_gradient).abs().max().item());need(auto_error<=p['gradient_tolerance'],'independent functional autograd control')
    t=time.perf_counter();basis=net.forward(np.eye(5,dtype=complex),np.zeros(16));matrix=basis['fields'].T;matrix_jac=basis['field_jacobian'];dense_compile_seconds=time.perf_counter()-t
    dense=x@matrix.T;dense_error=float(np.max(np.abs(dense-cpu['fields'])))
    need(dense_error<=p['field_tolerance'],'geometry-derived equivalent dense baseline gate')
    t=time.perf_counter();u=torch.tensor(matrix,dtype=torch.complex128,device=device);uj=torch.tensor(matrix_jac,dtype=torch.complex128,device=device);torch.cuda.synchronize();dense_transfer_seconds=time.perf_counter()-t
    dense_gpu=gpu_x@u.T;dense_gpu_error=float(np.max(np.abs(dense_gpu.cpu().numpy()-cpu['fields'])))
    need(dense_gpu_error<=p['field_tolerance'],'equivalent CUDA dense baseline gate')
    def dense_numpy(values):
        field=values@matrix.T;jac=np.einsum('ns,scp->ncp',values,matrix_jac)
        return field,np.abs(field)**2,jac,2*np.real(field.conjugate()[:,:,None]*jac)
    def dense_cuda(values):
        field=values@u.T;jac=torch.einsum('ns,scp->ncp',values,uj)
        return field,field.abs()**2,jac,2*(field.conj()[:,:,None]*jac).real
    dense_jac_error=max(float(np.max(np.abs(dense_numpy(x)[2]-cpu['field_jacobian']))),float(np.max(np.abs(dense_cuda(gpu_x)[2].cpu().numpy()-cpu['field_jacobian']))))
    need(dense_jac_error<=p['gradient_tolerance'],'geometry-derived equivalent dense field Jacobian gate')
    t=time.perf_counter();cpu_backend=TorchGeometryBackend(net,'cpu');cpu_packed=cpu_backend.upload(prepared);cpu_cached_setup_seconds=time.perf_counter()-t
    rng=np.random.default_rng(p['scaling_seed']);timings=[]
    for batch in p['batch_sizes']:
        values=rng.normal(size=(batch,5))+1j*rng.normal(size=(batch,5));values/=np.linalg.norm(values,axis=1,keepdims=True)
        t=time.perf_counter();tensor=torch.tensor(values,dtype=torch.complex128,device=device);torch.cuda.synchronize();transfer=time.perf_counter()-t
        cpu_tensor=torch.tensor(values,dtype=torch.complex128)
        net.forward(values,np.zeros(16));cpu_backend.forward(cpu_tensor,cpu_packed);backend.forward(tensor,packed);torch.cuda.synchronize()
        dense_numpy(values);dense_cuda(tensor);torch.cuda.synchronize()
        measurements={'numpy_graph_including_phase_argument_preparation':[],'torch_cpu_graph_forward_and_jacobian':[],'cuda_graph_forward_and_jacobian':[],'cpu_dense_fields_powers_and_jacobians':[],'cuda_dense_fields_powers_and_jacobians':[]}
        for repeat in range(p['repeats']):
            t=time.perf_counter();net.forward(values,np.zeros(16));measurements['numpy_graph_including_phase_argument_preparation'].append(time.perf_counter()-t)
            t=time.perf_counter();cpu_backend.forward(cpu_tensor,cpu_packed);measurements['torch_cpu_graph_forward_and_jacobian'].append(time.perf_counter()-t)
            t=time.perf_counter();last=backend.forward(tensor,packed);torch.cuda.synchronize();measurements['cuda_graph_forward_and_jacobian'].append(time.perf_counter()-t)
            t=time.perf_counter();dense_numpy(values);measurements['cpu_dense_fields_powers_and_jacobians'].append(time.perf_counter()-t)
            t=time.perf_counter();dense_cuda(tensor);torch.cuda.synchronize();measurements['cuda_dense_fields_powers_and_jacobians'].append(time.perf_counter()-t)
        t=time.perf_counter();last['fields'].cpu().numpy();last['powers'].cpu().numpy();last['field_jacobian'].cpu().numpy();last['power_jacobian'].cpu().numpy();torch.cuda.synchronize();download=time.perf_counter()-t
        timings.append({'batch':batch,'input_transfer_seconds':transfer,'readback_all_outputs_seconds':download,'seconds_samples':measurements,
                        'seconds_median':{k:statistics.median(v) for k,v in measurements.items()},'dense_scope':'fields,powers,bothJacobians; matrix/Jacobian compiled from geometry basis, never source inference payload',
                        'graph_scope':'fields,powers,bothJacobians; TorchCPU andCUDA use identical cached arguments/same code/warmup/complex128; numpyreference includes phaseargumentprep eachcall'})
        print(json.dumps({'batch':batch,'completed':True}),flush=True)
    result={'schema':'optic_neuro_blender.trained_graph_cuda_benchmark.v1','status':'PASS','profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),
            'torch_version':torch.__version__,'torch_cuda_runtime':torch.version.cuda,'device':str(device),'device_name':props.name,'device_compute_capability':[props.major,props.minor],
            'nvidia_smi_identity':hardware,'actual_readback_verified':True,'precision':'complex128/float64','tf32_enabled':False,
            'cuda_peak_allocated_bytes':torch.cuda.max_memory_allocated(device),'cuda_peak_reserved_bytes':torch.cuda.max_memory_reserved(device),
            'cpu_cuda_errors':errors,'functional_autograd_gradient_max_error':auto_error,'dense_cpu_field_max_error':dense_error,'dense_cuda_field_max_error':dense_gpu_error,
            'dense_field_jacobian_max_error':dense_jac_error,
            'coherent_probe_count':len(x),'source_ids':net.source_ids,'ports':net.ports,'actual_cuda_fields_reim':[readback['fields'].real.tolist(),readback['fields'].imag.tolist()],
            'actual_cuda_powers':readback['powers'].tolist(),'actual_cuda_field_jacobian_reim':[readback['field_jacobian'].real.tolist(),readback['field_jacobian'].imag.tolist()],
            'actual_cuda_power_jacobian':readback['power_jacobian'].tolist(),'batch_timings':timings,
            'cost_seconds':{'torch_import':import_seconds,'geometry_and_affine_compilation':geometry_seconds,'phase_packing_and_device_setup_transfer':packing_transfer_seconds,
                            'geometric_basis_and_dense_jacobian_compilation':dense_compile_seconds,'dense_cuda_transfer':dense_transfer_seconds,'torch_cpu_cached_setup':cpu_cached_setup_seconds,
                            'cpu_coherent_probe_execution':cpu_probe_seconds,'probe_input_transfer':input_transfer_seconds,'cuda_coherent_probe_execution':gpu_probe_seconds,'probe_complete_readback':readback_seconds,
                            'total_worker_after_numpy_import':time.perf_counter()-total_start},
            'scope':'Actual NVIDIA coherent DAG/trigonometry/manualgeometrygradients onCUDA with CPU exactgeometry and phaseargument preparation; no GPUtriangle traversal, nativeerrorcertificate, energy-efficiency or AMDclaim'}
    (args.out/'result.json').write_bytes((json.dumps(result,indent=2,allow_nan=False)+'\n').encode());print(json.dumps({'status':result['status'],'errors':errors,'autograd_error':auto_error,'device':hardware}),flush=True)


if __name__=='__main__':main()
