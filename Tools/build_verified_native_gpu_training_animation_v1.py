"""Animate archived native GPU learning observations; run no experiment."""
import hashlib,json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image
from Tools.audit_captured_pilot_result_v1 import decode
from Tools.train_captured_geometry_v1 import parameters_and_bases
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Docs/validation/native-deferred-training-2026-10-09/attempt01'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    supervisor=read(BASE/'supervisor.json');result=read(BASE/'worker/result.json')
    assert supervisor['primary_metric']==1 and supervisor['worker_exit_code']==0
    assert result['status']=='VALID_NATIVE_GRAPHICS_GEOMETRY_TRAINING'
    assert result['optimizer_updates']==60 and result['all61_actual_native_states_captured']
    states=[read(BASE/f'worker/state_{i}.json') for i in range(61)]
    assert [s['step'] for s in states]==list(range(61))
    assert all(s['exact_native_geometry_matches_materialized'] for s in states)
    profile=read(ROOT/'Docs/research/captured_geometry_training_profile_2026-10-09.json')
    first=profile['train_indices'][0];ports=result['ports'];detectors=result['detectors']
    observed=np.asarray(states[-1]['fields_reim'])[0]
    final=np.asarray(result['all150_fields_reim'])[first]
    discrepancy=float(np.max(np.abs(observed-final)))
    assert discrepancy<=1e-11
    scene=decode(read(BASE/'worker/initial_native_scene.json'))
    graph=decode(read(BASE/'worker/initial_native_graph.json'))
    parameters,_=parameters_and_bases(scene);net=AffineGeometryNetwork(scene,graph,parameters)
    assert len(graph['nodes'])==133 and net.ports==ports
    loss=np.asarray([s['train_loss'] for s in states]);steps=np.arange(61)
    changes=np.asarray([s['deltas_BU'] for s in states]);changes=changes-changes[0]
    span=max(float(np.max(np.abs(changes)))*1.12,1e-12)
    field=np.asarray([s['fields_reim'][0] for s in states]);field=field[:,:,0]+1j*field[:,:,1]
    power=np.abs(field)**2;power_max=max(float(power.max())*1.12,1e-12)
    cmap=plt.get_cmap('twilight');norm=Normalize(-math.pi,math.pi)
    fig,axes=plt.subplots(2,2,figsize=(12,8),dpi=105)
    fig.subplots_adjust(left=.075,right=.97,bottom=.18,top=.84,wspace=.32,hspace=.45)
    fig.patch.set_facecolor('#f7fafc');frames=[]
    for k in range(0,61,2):
        for ax in axes.flat:ax.clear();ax.set_facecolor('white');ax.grid(alpha=.14)
        geometry,paths=net.materialize(states[k]['deltas_BU'])
        for node in paths['nodes']:
            a,b=node['origin'],node['point']
            axes[0,0].plot([float(a[0]),float(b[0])],[float(a[1]),float(b[1])],color='#bbc7d1',lw=.6,alpha=.7)
        for j,port in enumerate(ports):
            nodes=[n for n in paths['nodes'] if n.get('terminal')==port]
            assert nodes
            point=nodes[0]['point'];phase=math.atan2(field[k,j].imag,field[k,j].real)
            axes[0,0].scatter([float(point[0])],[float(point[1])],color=cmap(norm(phase)),s=40,edgecolor='#19364b',lw=.7,zorder=4)
        axes[0,0].set(xlim=(-1,19),ylim=(-1,23),xlabel='x (BU)',ylabel='y (BU)',title='Geometría XY · 133 estados, 17.060 caminos')
        axes[0,0].set_aspect('equal')
        axes[0,1].plot(steps,loss,color='#c5d0d9',lw=1.3)
        axes[0,1].plot(steps[:k+1],loss[:k+1],color='#175b89',lw=2.5)
        axes[0,1].scatter([k],[loss[k]],color='#d78327',s=40,zorder=5)
        axes[0,1].set(xlim=(0,60),ylim=(0,float(loss.max())*1.08),xlabel='Actualización del optimizador',ylabel='Entropía cruzada',title=f'Pérdida observada: {loss[k]:.6f}')
        axes[1,0].bar(np.arange(16),changes[k],color=['#287c8e' if v>=0 else '#926696' for v in changes[k]])
        axes[1,0].set(ylim=(-span,span),xlabel='Par de espejos (16 parámetros)',ylabel='Cambio desde inicio (BU)',title='Posiciones capturadas en Blender');axes[1,0].set_xticks(np.arange(0,16,3))
        colors=['#175b89' if p in detectors else '#d78327' for p in ports]
        axes[1,1].bar([p.replace('det.','') for p in ports],power[k],color=colors)
        axes[1,1].set(ylim=(0,power_max),ylabel='Potencia modal normalizada',title=f'Campo GPU + fusión CPU · entrada de entrenamiento {first}')
        fig.text(.5,.965,'OpticNeuroBlender · aprendizaje desde geometría con la GPU',ha='center',fontsize=15,fontweight='bold',color='#19364b')
        fig.text(.5,.9,f'Estado {k}/60 · RTX 3090 · rasterización 3D y transporte óptico FP64',ha='center',fontsize=10,color='#4d6371')
        fig.text(.075,.11,'GPU: intersección, fase y derivadas. CPU: topología, fusión coherente, pérdida y Adam.',fontsize=9,color='#4d6371')
        fig.text(.075,.07,f'61 capturas reales · test evaluado al final: {result["test_correct"]}/30 · color de los puertos = fase',fontsize=9,color='#175b89')
        fig.text(.075,.03,'Replay de datos archivados. Líneas = geometría; estados computacionales, sin tiempo físico ni ventaja de velocidad inferida.',fontsize=8,color='#627887')
        fig.canvas.draw();frames.append(Image.frombuffer('RGBA',fig.canvas.get_width_height(),fig.canvas.buffer_rgba(),'raw','RGBA',0,1).convert('RGB').copy())
        for label in list(fig.texts):label.remove()
    assets=ROOT/'Docs/assets';gif=assets/'native-gpu-geometry-learning-2026-10-09.gif';preview=assets/'native-gpu-geometry-learning-preview-2026-10-09.png'
    frames[0].save(gif,save_all=True,append_images=frames[1:],duration=[180]*30+[1800],loop=0,optimize=True);frames[-1].save(preview);plt.close(fig)
    source=[BASE/'supervisor.json',BASE/'worker/result.json',BASE/'worker/initial_native_scene.json',BASE/'worker/initial_native_graph.json',ROOT/'Docs/research/captured_geometry_training_profile_2026-10-09.json',*[BASE/f'worker/state_{i}.json' for i in range(61)]]
    manifest={'schema':'optic_neuro_blender.verified_native_gpu_training_animation.v1','sources':{p.relative_to(ROOT).as_posix():sha(p) for p in source},'outputs':{p.relative_to(ROOT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in (gif,preview)},'frames':31,'size_px':list(frames[0].size),'sampled_optimizer_states':list(range(0,61,2)),'all61_actual_native_geometry_matches_verified':True,'displayed_training_row_index':first,'final_displayed_field_vs_fresh_reopened_field_difference':discrepancy,'test_score_displayed_only_as_final_observation':True,'geometry_reconstructed_from_observed_native_states_with_producer_verified_capture_equality':True,'scope':'Replay of archived actual native graphical training. Port phase and powers are recorded GPU fields after CPU coherent merges; intermediate ray amplitudes are not invented. Geometry lines represent a static path graph at each actual captured state. CPU optimizer and topology explicit; no wall-time, physical-photon, GPU-speedup, RT or AMD claim.'}
    (assets/'verified-native-gpu-training-animation-manifest-2026-10-09.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(json.dumps({'frames':31,'gif_bytes':gif.stat().st_size,'sha256':sha(gif),'final_field_difference':discrepancy}))

if __name__=='__main__':main()
