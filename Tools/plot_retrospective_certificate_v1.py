"""Plot certified error bounds of archived data, never a new GPU benchmark."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

repo=Path(__file__).resolve().parents[1]
base=repo/'Docs/validation/iris-retrospective-interval-2026-10-08'
names=['attempt01-native02','attempt06-native02','attempt07-native01']
reports=[json.loads((base/name/'certificate.json').read_text())for name in names]
fig,axes=plt.subplots(1,2,figsize=(12,5.3))
fig.suptitle('Certificar decisiones no basta para certificar precisión del campo',fontsize=15,fontweight='bold')
labels=['Mismos datos\nintervalos 128 bits','Mismos datos\nintervalos 256 bits','Ejecución antigua\nintervalos 256 bits']
colors=['#d97706','#2563eb','#dc2626']
axes[0].bar(labels,[r['maximum_upper_display']['field_l1']for r in reports],color=colors)
axes[0].set_yscale('log');axes[0].set_ylim(1e-14,1e-3)
axes[0].axhline(1e-11,color='#0f172a',ls='--',lw=1.5,label='Tolerancia histórica 1e-11')
axes[0].set_ylabel('Cota superior del error absoluto de campo (L1)')
axes[0].legend(fontsize=9);axes[0].grid(axis='y',alpha=.15)
axes[1].bar(labels,[r['certified_decisions']for r in reports],color=colors)
axes[1].set_ylim(0,500);axes[1].set_ylabel('Decisiones nativas certificadas frente al modelo')
for i,r in enumerate(reports):axes[1].text(i,460,str(r['certified_decisions']),ha='center',fontsize=11)
fig.text(.045,.045,'Readbacks históricos: no se ha vuelto a ejecutar la GPU. Modelo algebraico canónico, sin recorrido nativo de triángulos.\n128 bits da una cota demasiado ancha; 256 bits certifica la ejecución corregida. La antigua supera la tolerancia aunque conserve las 450 decisiones.',fontsize=9,color='#334155')
fig.subplots_adjust(left=.08,right=.98,top=.82,bottom=.26,wspace=.30)
fig.savefig(repo/'Docs/assets/iris-retrospective-certificate-2026-10-08.png',dpi=155,facecolor='white',metadata={'Software':'Neuro3D retrospective rational certificates'})
plt.close(fig)
print('Saved retrospective certificate figure')
