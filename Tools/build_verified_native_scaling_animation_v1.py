"""Replay actual equivalent-output batch costs and whole-GPU samples."""
import hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'Docs/validation/native-graphics-scaling-2026-10-09/attempt01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    report=json.loads((BASE/'worker/result.json').read_bytes());supervisor=json.loads((BASE/'supervisor.json').read_bytes())
    assert report['primary_metric']==supervisor['primary_metric']==1
    records=report['results'];assert len(records)==6 and all(v['all_decisions_equal'] for v in records)
    telemetry=supervisor['gpu_telemetry'];t0=telemetry[0]['monotonic_seconds'];end=telemetry[-1]['monotonic_seconds']-t0
    y=[r['seconds'][arm] for r in records for arm in ('CPU_GEOMETRY_DAG','GPU_DEFERRED_GRAPHICS')];assert min(y)>0
    fig,(left,right)=plt.subplots(1,2,figsize=(12,6),dpi=105);fig.subplots_adjust(left=.085,right=.96,bottom=.25,top=.79,wspace=.35);fig.patch.set_facecolor('#f7fafc');frames=[]
    for index,current in enumerate(records):
        for ax in (left,right):ax.clear();ax.set_facecolor('white');ax.grid(alpha=.17,which='both')
        seen=records[:index+1]
        for arm,color,label in [('CPU_GEOMETRY_DAG','#175b89','CPU · DAG geométrico'),('GPU_DEFERRED_GRAPHICS','#d78327','GPU + fusión CPU')]:
            for repetition,marker in [(0,'^'),(1,'o')]:
                rows=[r for r in seen if r['repetition']==repetition]
                if rows:left.plot([r['batch_size'] for r in rows],[r['seconds'][arm] for r in rows],marker=marker,color=color,ls='--' if repetition==0 else '-',lw=1.4,label=label+(' · primera' if repetition==0 else ' · segunda'))
        left.set(xscale='log',yscale='log',xlim=(.75,5500),ylim=(min(y)*.65,max(y)*1.6),xlabel='Entradas coherentes por lote',ylabel='Tiempo observado (s)',title='Dos órdenes alternados · salidas equivalentes');left.set_xticks([1,150,4096],labels=['1','150','4096']);left.legend(fontsize=7,loc='upper left')
        visible=[s for s in telemetry if s['monotonic_seconds']<=current['monotonic_seconds_end']]
        right.plot([s['monotonic_seconds']-t0 for s in visible],[s['power_draw_watts'] for s in visible],color='#287c8e',lw=1.3)
        right.axvline(current['monotonic_seconds_end']-t0,color='#d78327',ls=':',lw=1.4)
        maximum=max(s['power_draw_watts'] for s in telemetry);right.set(xlim=(0,end*1.03),ylim=(0,maximum*1.15),xlabel='Tiempo del supervisor (s)',ylabel='Potencia de la GPU completa (W)',title='Muestreo real ≈1 Hz · incluye pantalla y sistema')
        fig.text(.5,.95,'OpticNeuroBlender · coste gráfico medido, sin ventaja presupuesta',ha='center',fontsize=14,fontweight='bold',color='#19364b')
        fig.text(.5,.86,f'Lote {current["batch_size"]} · par {current["repetition"]+1}/2 · RTX 3090 / Blender 4.5.14',ha='center',fontsize=10,color='#4d6371')
        fig.text(.085,.16,'GPU: geometría y óptica FP64, ecos y empaquetado incluidos; CPU: topología y suma coherente.',fontsize=9,color='#4d6371')
        fig.text(.085,.10,'Entradas Iris repetidas con fase global: escalado de lote, no nueva generalización.',fontsize=9,color='#175b89')
        fig.text(.085,.05,'Potencia muestreada del dispositivo completo, sin atribución a un kernel ni a un procesador fotónico.',fontsize=8,color='#627887')
        fig.canvas.draw();frames.append(Image.frombuffer('RGBA',fig.canvas.get_width_height(),fig.canvas.buffer_rgba(),'raw','RGBA',0,1).convert('RGB').copy())
        for t in list(fig.texts):t.remove()
    assets=ROOT/'Docs/assets';gif=assets/'native-graphics-batch-cost-2026-10-09.gif';preview=assets/'native-graphics-batch-cost-preview-2026-10-09.png'
    frames[0].save(gif,save_all=True,append_images=frames[1:],duration=[1000]*5+[2500],loop=0,optimize=True);frames[-1].save(preview);plt.close(fig)
    sources=[BASE/'supervisor.json',BASE/'worker/result.json'];manifest={'schema':'optic_neuro_blender.verified_native_scaling_animation.v1','sources':{p.relative_to(ROOT).as_posix():sha(p) for p in sources},'outputs':{p.relative_to(ROOT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in (gif,preview)},'frames':6,'size_px':list(frames[0].size),'scope':'Each frame adds one measured equal-output CPU/GPU pair. Actual native captured geometry andFP64shader; CPUmerge/zero-tangent echoes included. WholeGPU sample trace not isolated energy. Deterministic repeatedIris inputs, two orders per size, not blind generalization or statistically established performance advantage.'}
    (assets/'verified-native-scaling-animation-manifest-2026-10-09.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode());print(json.dumps({'gif_bytes':gif.stat().st_size,'frames':6,'sha256':sha(gif)}))
if __name__=='__main__':main()
