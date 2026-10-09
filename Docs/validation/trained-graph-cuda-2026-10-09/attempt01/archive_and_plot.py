import datetime,hashlib,json,shutil,subprocess,sys
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');private=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/trained-graph-cuda-20261009-run01')
dest=root/'Docs/validation/trained-graph-cuda-2026-10-09/attempt01';shutil.copytree(private,dest)
s=json.loads((dest/'supervisor.json').read_text());r=json.loads((dest/'worker/result.json').read_text());assert s['primary_metric']==1
for name,pin in s['raw_file_sha256'].items():assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==pin
for number in (1,2):
    cert_path=Path(f'D:/PROJECTS/.cognition/neuro3d-sequential-20261008/trained-graph-cuda-probe-certificate-20261009-analysis0{number}.json')
    certificate=json.loads(cert_path.read_text());folder=dest/f'interval_analysis0{number}';folder.mkdir();(folder/'certificate.json').write_bytes(cert_path.read_bytes())
    for name,pin in certificate['source_sha256'].items():
        target=folder/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        raw=subprocess.check_output(['git','show','f765452:'+name],cwd=root) if number==1 and name=='Tools/certify_cuda_coherent_probes_v1.py' else (root/name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==pin;target.write_bytes(raw)
    for name in (json.loads((dest/'profile.json').read_text())['scene'],json.loads((dest/'profile.json').read_text())['graph']):
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==json.loads((dest/'profile.json').read_text())['pins'][name]
events=[]
for line in Path('D:/PROJECTS/.cognition/gpu_queue/log.jsonl').read_text(encoding='utf-8').splitlines():
    item=json.loads(line)
    if item.get('name')=='Neuro3D:trained-graph-cuda-v1-20261009':events.append(item)
(dest/'shared_fifo_events.json').write_bytes((json.dumps({'events':events,'queue_source_sha256':hashlib.sha256(Path('D:/PROJECTS/.cognition/gpu_queue/gpuq.py').read_bytes()).hexdigest(),'holder_absent_after_completion':not Path('D:/PROJECTS/.cognition/gpu_queue/holder.json').exists()},indent=2)+'\n').encode())
test=subprocess.run([sys.executable,'-X','utf8','-m','unittest','Blender.tests.test_torch_geometry_backend_v1','-v'],cwd=root,capture_output=True)
(dest/'cpu_controls.log').write_bytes(test.stdout+test.stderr);assert test.returncode==0
plt.rcParams.update({'font.size':10});fig,ax=plt.subplots(figsize=(8.8,4.7),layout='constrained')
curves={'torch_cpu_graph_forward_and_jacobian':'Grafo Torch CPU','cuda_graph_forward_and_jacobian':'Grafo CUDA','cpu_dense_fields_powers_and_jacobians':'Baseline matricial CPU','cuda_dense_fields_powers_and_jacobians':'Baseline matricial CUDA'}
for key,label in curves.items():
    x=[b['batch'] for b in r['batch_timings']];y=[b['seconds_median'][key]*1000 for b in r['batch_timings']]
    ax.plot(x,y,marker='o',label=label)
ax.set(xscale='log',yscale='log',xlabel='Entradas por lote, geometría fija',ylabel='Mediana de ejecución caliente (ms)',title='RTX 3090: campos, potencias y ambos Jacobianos; complex128')
ax.grid(alpha=.25);ax.legend()
fig.text(.02,-.04,'5 repeticiones. Preparación/transferencia/lectura se informan aparte. No GPU para triángulos ni afirmación de energía.',fontsize=9)
asset=root/'Docs/assets/trained-graph-cpu-cuda-scaling-2026-10-09.png';fig.savefig(asset,dpi=170,bbox_inches='tight');plt.close(fig)
(dest/'archive_and_plot.py').write_bytes(Path(__file__).read_bytes())
index={p.relative_to(dest).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in dest.rglob('*') if p.is_file()}
(dest/'evidence_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
accept=root/'Docs/research/optic_neuro_blender_acceptance_v1.json';a=json.loads(accept.read_text())
for entry in a['priorities']:
    if entry['id']==8:entry.update(status='PARTIAL_ACTUAL_NVIDIA_COMPLEX128_GRAPH_AND_GRADIENTS_VERIFIED',achieved='ActualRTX3090/CUDA12.4/Torch2.6.0 kernels/readback60inputs; ownfields/powers/manualJacobian parity/autogradcontrol; independentobservedfieldsL1<=2.9356882610688944e-15,power<=1.3807709003001215e-15;59argmaxcertified,zeroUNKNOWN;5repeatsbatches1/150/2048,fullworker6.7155s,source/setup/transfers/readback costs andequivalentdensebaseline measured',remaining='ActualAMDhardware; wholetrainingandgeometryGPUcost/energy/structuralscaling/ablations; noGPUtrianglepredicate claimed')
a['latest_nvidia_result']='Docs/validation/trained-graph-cuda-2026-10-09/attempt01/worker/result.json'
a['latest_nvidia_certificate']='Docs/validation/trained-graph-cuda-2026-10-09/attempt01/interval_analysis02/certificate.json'
accept.write_bytes((json.dumps(a,indent=2)+'\n').encode())
now=datetime.datetime.now(datetime.timezone.utc).isoformat();checkpoint=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/CHECKPOINT.md')
with checkpoint.open('a',encoding='utf-8') as f:f.write(f'\n## {now} — actual NVIDIA trained graph and secondary certificate PASS\nGPUprofile1ce88403-bf12-4680-9ee1-7e8ef26e89f4/SHA6073f16df3daec27c156f7d347be27d3f621152408ed942da67e4ee32218da19 and18sources published0afc6e2 beforeexecution; allGitpinsmatch. FIFOqueue requestedVRAM4GiB+margin/RAM8GiB, actual3090UUID GPU-b163fedb-dda0-d4f4-68b2-298b6975efe3 driver581.29; CUDA12.4 Torch2.6.0+cu124 complex128. Worker6.7155s,RSS996.0977MiB,CUDAallocated104.61MiB/reserved112MiB. GPU/CPUfieldmax3.608e-16,power3.886e-16,fieldJac5.550e-14,powerJac3.553e-14; functionalautograd1.563e-13. Secondaryexactinterval60inputs PASS L1<=2.9356882610688944e-15,power<=1.3807709003001215e-15;59argmaxcertified,zeroinputUNKNOWN. analysis01preserved; guardaugmented02samebounds/frozengeometryhashesvalidated. WarmTorchCPU/CUDAgraphms(1/150/2048):14.45/24.50,17.43/27.06,75.00/25.72; equaldenseCPU/CUDAms:.0712/.4349,.4988/.5586,8.5968/.8973. Noendtoendtraining speed/energy claim. GPUdoesnottracegeometrictriangles; AMDabsent. Rawrecords/index+scalingfigureprepared. Nextscientificwork: frozen matchedclassifier/generalizationprotocol and wave-model regime/stability references; package ownBlenderUI/cleaninstall; independentreproduction/IPFSstillpending. Lastcommitpushed897270c; results needpublishingnext. JEVconnectedprovenance=jevvalidatedroute.\n')
print(json.dumps({'files':len(index),'bytes':sum(v['bytes'] for v in index.values()),'fifo_events':len(events),'cert_status':certificate['status']}))
