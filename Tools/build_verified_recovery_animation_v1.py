"""Render only archived installed Blender baseline/resume observations."""
import hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Docs/validation/installed-blender-host-recovery-2026-10-09/attempt01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def main():
    supervisor=read(BASE/'supervisor.json');assert supervisor['primary_metric']==1 and supervisor['owned_child_self_exit_code']==9
    stages=supervisor['stages'];names=[stages[i]['result']['job_folder'].replace('\\','/').rsplit('/',1)[-1] for i in (0,2)]
    jobs=[BASE/'jobs'/name for name in names]
    traces=[[json.loads(s) for s in (p/'training/progress.jsonl').read_text(encoding='utf-8').splitlines()] for p in jobs]
    results=[read(p/'result.json') for p in jobs]
    assert all(len(t)==61 for t in traces)
    assert all(a['step']==b['step'] and a['deltas_BU']==b['deltas_BU'] and float(a['train_loss']).hex()==float(b['train_loss']).hex() for a,b in zip(*traces))
    power=np.asarray(results[0]['all150_native_powers']);other=np.asarray(results[1]['all150_native_powers']);assert np.array_equal(power,other) and results[0]['all150_predictions']==results[1]['all150_predictions']
    assert results[1]['training']['recovery']['resume_step']==12 and results[1]['training']['recovery']['prefix_replay_verified']
    steps=np.arange(61);loss=np.asarray([r['train_loss'] for r in traces[0]])
    translations=np.asarray([r['deltas_BU'] for r in traces[1]]);translations=translations-translations[0];frames=[]
    fig,(left,right)=plt.subplots(1,2,figsize=(12,6.3),dpi=110,gridspec_kw={'width_ratios':[1.35,1]});fig.subplots_adjust(left=.075,right=.965,bottom=.23,top=.77,wspace=.3);fig.patch.set_facecolor('#f7fafc')
    for k in range(0,61,2):
        for ax in (left,right):ax.clear();ax.set_facecolor('white');ax.grid(alpha=.16)
        left.plot(steps,loss,color='#bdc9d4',lw=1.3,label='Trayectoria completa observada')
        left.plot(steps[:k+1],loss[:k+1],color='#175b89',lw=3,label='Blender sin interrupción')
        left.plot(steps[:k+1],loss[:k+1],color='#d78327',ls='--',lw=1.4,label='Blender nuevo, reanudado')
        left.axvline(12,color='#bc455b',ls=':',lw=1.5);left.scatter([k],[loss[k]],color='#175b89',s=30,zorder=5)
        left.set(xlim=(0,60),ylim=(0,float(loss.max())*1.08),xlabel='Estado del optimizador',ylabel='Pérdida de entrenamiento',title='61 pérdidas y posiciones idénticas');left.legend(fontsize=8,loc='upper right')
        right.bar(np.arange(16),translations[k],color=['#287c8e' if v>=0 else '#926696' for v in translations[k]])
        span=float(np.max(np.abs(translations)))*1.12;right.set(ylim=(-span,span),xlabel='Par de espejos (16 parámetros)',ylabel='Cambio desde el estado inicial (BU)',title=f'Geometría reanudada · estado {k}/60');right.set_xticks(np.arange(0,16,3))
        fig.text(.5,.945,'OpticNeuroBlender 0.1.3 · recuperación nativa comprobada',ha='center',fontsize=16,fontweight='bold',color='#19364b')
        subtitle='Propietario interrumpido → checkpoint 12 → nuevo Blender → resultado exacto'
        fig.text(.5,.875,subtitle,ha='center',fontsize=10,color='#4d6371')
        fig.text(.075,.145,'Checkpoint tras 12 actualizaciones; el estado 12 se evalúa al reanudar.',fontsize=9,color='#4d6371')
        fig.text(.075,.10,'150 × 8 potencias nativas: diferencia máxima 0 · decisiones idénticas · Iris test 27/30',fontsize=10,color='#175b89')
        fig.text(.075,.055,'Datos archivados reales · flujo CPU · no representa tiempo físico ni recuperación eléctrica',fontsize=8,color='#627887')
        fig.canvas.draw();image=Image.frombuffer('RGBA',fig.canvas.get_width_height(),fig.canvas.buffer_rgba(),'raw','RGBA',0,1).convert('RGB').copy();frames.append(image)
        # Remove figure text between frames while preserving the axes.
        for text in list(fig.texts):text.remove()
    assets=ROOT/'Docs/assets';target=assets/'installed-blender-exact-resume-2026-10-09.gif'
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=[180]*30+[1500],loop=0,optimize=True)
    preview=assets/'installed-blender-exact-resume-preview-2026-10-09.png';frames[-1].save(preview);plt.close(fig)
    source=[BASE/'supervisor.json',*[p/'training/progress.jsonl' for p in jobs],*[p/'result.json' for p in jobs]]
    manifest={'schema':'optic_neuro_blender.verified_animation.v1','sources':{p.relative_to(ROOT).as_posix():sha(p) for p in source},'outputs':{p.relative_to(ROOT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in (target,preview)},'frames':31,'size_px':list(frames[0].size),'sampled_optimizer_states':list(range(0,61,2)),'all61_optimizer_coordinate_and_loss_floathex_exact':True,'all150_native_power_difference':0,'checkpoint_next_step':12,'final_test_correct':27,'scope':'Animation of recorded CPU baseline and actual native installed host-interruption/recovery. Prefix is replayed; all61 losses/positions and150 powers match. Cursor is optimizer state, not wall/physical time; no GPU or machine powerloss claim.'}
    (assets/'verified-recovery-animation-manifest-2026-10-09.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode());print(json.dumps({'frames':31,'gif_bytes':target.stat().st_size,'sha256':sha(target)}))
if __name__=='__main__':main()
