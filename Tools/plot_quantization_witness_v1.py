"""Illustrate an exact endpoint witness; animation is analytic, not measurement."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

parser=argparse.ArgumentParser()
parser.add_argument('--receipt',type=Path,required=True)
args=parser.parse_args()
receipt=json.loads(args.receipt.read_text())
assert receipt['status']=='PASS_EXACT_CPU_MATHEMATICAL_WITNESS'
repo=Path(__file__).resolve().parents[1]
fig,axes=plt.subplots(1,2,figsize=(11,4.8),gridspec_kw={'width_ratios':[1.5,1]})
fig.suptitle('Geometría distinta, mismos bytes float32, distinta interferencia',fontsize=15,fontweight='bold')
x=np.linspace(0,1,121)
y=np.cos(np.pi*x/2)**2
axes[0].plot(x,y,color='#2563eb',lw=2.5,label='Modelo analítico de la geometría original')
axes[0].plot(x,np.ones_like(x),color='#d97706',ls='--',lw=2,label='Posición convertida a float32')
axes[0].set(xlabel='Desplazamiento del espejo / δ',ylabel='Intensidad normalizada',xlim=(0,1),ylim=(-.05,1.08))
axes[0].grid(alpha=.2)
axes[0].legend(loc='lower left',fontsize=8)
dot,=axes[0].plot([0],[1],'o',color='#2563eb',ms=8)
bars=axes[1].bar(['Original','float32'],[1,1],color=['#2563eb','#d97706'])
axes[1].set(ylim=(0,1.08),ylabel='Intensidad normalizada')
axes[1].set_title('Referencia ≠ reconstrucción cuantizada',fontsize=11)
fig.text(.055,.025,'δ = 2⁻²⁵ BU; λ = 4δ; ΔL = 2δ. Extremos probados con fracciones exactas.\nAnimación de fórmula conocida: no es ejecución Blender/GPU ni medición física.',fontsize=9,color='#475569')
fig.subplots_adjust(left=.065,right=.985,top=.80,bottom=.24,wspace=.28)
def frame(i):
 t=i/40
 v=float(np.cos(np.pi*t/2)**2)
 dot.set_data([t],[v])
 bars[0].set_height(v)
 return dot,bars[0]
frame(40)
fig.savefig(repo/'Docs/assets/quantization-phase-witness-2026-10-08.png',dpi=160,facecolor='white',metadata={'Software':'Neuro3D analytic witness illustration'})
animation=FuncAnimation(fig,frame,frames=list(range(41))+[40]*10,interval=100,blit=False)
animation.save(repo/'Docs/assets/quantization-phase-witness-2026-10-08.gif',writer=PillowWriter(fps=10))
plt.close(fig)
print('Saved PNG and analytic GIF')
