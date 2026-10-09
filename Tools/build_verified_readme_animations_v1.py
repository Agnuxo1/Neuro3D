"""Build animations from archived native observations; execute no experiment."""
import hashlib
import json
import math
import struct
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from PIL import Image
from Tools.audit_captured_pilot_result_v1 import decode

ROOT=Path(__file__).resolve().parents[1]
BASE='Docs/validation/native-graphics-field-2026-10-09/attempt11/worker/'
JOB='Docs/validation/own-blender-addon-2026-10-09/attempt03/worker/jobs/optic-neuro-326edc59834b425d92ea2a99f43faa61/'
SOURCES=[BASE+'actual_gpu_geometry_graph.json',BASE+'native_gpu_transport_0.json',JOB+'result.json',JOB+'worker.stdout']


def read(name):return json.loads((ROOT/name).read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def frame(fig):
    fig.canvas.draw()
    return Image.frombuffer('RGBA',fig.canvas.get_width_height(),fig.canvas.buffer_rgba(),'raw','RGBA',0,1).convert('RGB').copy()


def main():
    graph=decode(read(SOURCES[0]));transport=read(SOURCES[1]);native=read(SOURCES[2])
    assert graph['status']=='COMPLETE' and transport['samples']==150 and len(graph['nodes'])==133
    stages=[];partial={p:[] for p in graph['ports']};observations={}
    for batch in transport['batches']:
        for k,i in enumerate(batch['node_ids']):
            node=graph['nodes'][i];row=batch['readback']['rows'][150*k]
            assert row['object']==node['hit_object'] and row['native_input_bit_echo_verified']
            observations[i]=complex(*row['propagated_reim'])
            if 'terminal' in node:partial[node['terminal']].append(complex(*row['first_reim']))
        stage_power={p:abs(complex(math.fsum(z.real for z in v),math.fsum(z.imag for z in v)))**2 for p,v in partial.items()}
        stages.append((dict(observations),stage_power))
    for p,v in partial.items():
        observed=complex(math.fsum(z.real for z in v),math.fsum(z.imag for z in v))
        expected=complex(*transport['fields_reim'][0][p])
        assert struct.pack('<dd',observed.real,observed.imag)==struct.pack('<dd',expected.real,expected.imag)
    frames=[];fig,(ax,bars_ax)=plt.subplots(1,2,figsize=(10,5.6),dpi=100,gridspec_kw={'width_ratios':[1.5,1]})
    fig.subplots_adjust(bottom=.22,top=.79,wspace=.38)
    norm=Normalize(-math.pi,math.pi)
    maximum=max(v for _,power in stages for v in power.values())
    cmap=plt.get_cmap('twilight')
    for index,(known,power) in enumerate(stages):
        ax.clear();bars_ax.clear()
        for node in graph['nodes']:
            a,b=node['origin'],node['point']
            ax.plot([float(a[0]),float(b[0])],[float(a[1]),float(b[1])],color='#d7dce2',lw=.6,zorder=1)
        for i,z in known.items():
            node=graph['nodes'][i];a,b=node['origin'],node['point'];phase=math.atan2(z.imag,z.real)
            ax.plot([float(a[0]),float(b[0])],[float(a[1]),float(b[1])],color=cmap(norm(phase)),lw=.6+3*min(abs(z)**2,1),alpha=.85,zorder=2)
        ax.set(xlim=(-1,19),ylim=(-1,23),xlabel='x (BU)',ylabel='y (BU)',title='Recorrido capturado: proyección XY')
        ax.set_aspect('equal');ax.grid(alpha=.12)
        labels=[p.replace('det.','') for p in graph['ports']]
        bars_ax.bar(labels,[power[p] for p in graph['ports']],color=['#277b89' if p.startswith('det.R') else '#df9738' for p in graph['ports']])
        bars_ax.set(ylim=(0,max(1,maximum)*1.08),ylabel='Potencia modal normalizada',title='Acumulación coherente parcial')
        bars_ax.grid(axis='y',alpha=.15)
        fig.suptitle('OpticNeuroBlender · campo coherente calculado en la GPU',fontweight='bold',fontsize=14)
        text=fig.text(.5,.87,f'Etapa {index+1}/{len(stages)} · {len(known)}/133 estados · entrada Iris n.º 0',ha='center',fontsize=11)
        caption=fig.text(.5,.085,'Etapas computacionales del DAG, no tiempo físico. Topología exacta y fusión en CPU.',ha='center',fontsize=9)
        caption2=fig.text(.5,.04,'17.060 caminos representados · RTX 3090 / Blender 4.5.14 · color = fase del campo en radianes',ha='center',fontsize=9)
        frames.append(frame(fig));text.remove();caption.remove();caption2.remove()
    plt.close(fig)
    network=ROOT/'Docs/assets/captured-gpu-coherent-network-2026-10-09.gif'
    frames[0].save(network,save_all=True,append_images=frames[1:],duration=[150]*(len(frames)-1)+[1800],loop=0,optimize=False)
    trace=[]
    for line in (ROOT/SOURCES[3]).read_text(encoding='utf-8').splitlines():
        try:item=json.loads(line)
        except json.JSONDecodeError:continue
        if isinstance(item,dict) and {'step','train_loss','geometry_audit'}<=set(item):trace.append(item)
    assert [v['step'] for v in trace]==list(range(61)) and all(v['geometry_audit']==1 for v in trace)
    assert trace[0]['train_loss']==native['training']['initial_train_loss'] and trace[-1]['train_loss']==native['training']['final_train_loss']
    fig,ax=plt.subplots(figsize=(9.5,5.2),dpi=100);fig.subplots_adjust(bottom=.25,top=.78);frames=[]
    for step in range(0,61,2):
        ax.clear();ax.plot([v['step'] for v in trace[:step+1]],[v['train_loss'] for v in trace[:step+1]],color='#277b89',lw=2)
        ax.scatter([step],[trace[step]['train_loss']],color='#df9738',s=50)
        ax.set(xlim=(0,60),ylim=(0,6.7),xlabel='Actualización de las 16 parejas de espejos',ylabel='Entropía cruzada en entrenamiento')
        ax.grid(alpha=.2);fig.suptitle('Aprendizaje propio desde geometría dentro de Blender',fontweight='bold',fontsize=14)
        text=fig.text(.5,.84,f'Paso {step}/60 · pérdida {trace[step]["train_loss"]:.6f} · geometría auditada',ha='center',fontsize=11)
        caption=fig.text(.5,.12,'Trayectoria observada del trabajador CPU nativo de Blender; no representa entrenamiento en GPU.',ha='center',fontsize=9)
        caption2=fig.text(.5,.06,'120 ejemplos de entrenamiento · evaluación final fija: 27/30 · sin selección por el test',ha='center',fontsize=9)
        frames.append(frame(fig));text.remove();caption.remove();caption2.remove()
    plt.close(fig)
    training=ROOT/'Docs/assets/native-blender-geometry-training-2026-10-09.gif'
    frames[0].save(training,save_all=True,append_images=frames[1:],duration=[140]*(len(frames)-1)+[1800],loop=0,optimize=False)
    outputs={p.relative_to(ROOT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size,'frames':Image.open(p).n_frames} for p in (network,training)}
    receipt={'schema':'optic_neuro_blender.verified_animation_manifest.v1','sources':{n:sha(ROOT/n) for n in SOURCES},'outputs':outputs,'native_gpu_final_complex_accumulations_bit_identical':True,'native_training_all61_audits_verified':True,'scope':'Animations replay archived observations. Computational stages are not physical time; XY projection does not show all3D surfaces. Phase colors are explanatory. No experiment, speedup, physical photon motion or GPU training is inferred.'}
    (ROOT/'Docs/assets/verified-animation-manifest-2026-10-09.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    print(json.dumps(outputs))


if __name__=='__main__':main()
