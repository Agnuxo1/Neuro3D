"""Visualize documented features; grey means unknown, never absence of prior art."""
import json
import re
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

repo=Path(__file__).resolve().parents[1]
rows=json.loads((repo/'Docs/research/literature_catalog_v1.json').read_text(encoding='utf-8'))
features=list(rows[0]['features_inspected'])
values=np.array([[1 if r['features_inspected'][f]==1 else 0 for f in features] for r in rows])
fig,ax=plt.subplots(figsize=(14,max(12,len(rows)*.48)))
ax.imshow(values,cmap=ListedColormap(['#e2e8f0','#2563eb']),vmin=0,vmax=1,aspect='auto')
ax.set_xticks(range(len(features)),['Integración\nfotónica 3D','Coherencia /\ncampo complejo','Ray tracing\nGPU nativo','Geometría /\ncotas rigurosas','Certificado conjunto\ngeometría → campo','Experimento\nfísico'])
ax.xaxis.tick_top()
ax.tick_params(axis='both',length=0,labelsize=10)
ax.set_yticks(range(len(rows)),[r['authors'].split(',')[0]+' · '+(re.search(r'\d{4}',r['year_label']).group(0) if re.search(r'\d{4}',r['year_label']) else '4ª ed.') for r in rows])
for i in range(len(rows)):
 for j in range(len(features)):
  ax.text(j,i,'D' if values[i,j] else '?',ha='center',va='center',color='white' if values[i,j] else '#64748b',fontsize=10)
ax.set_xticks(np.arange(-.5,len(features),1),minor=True)
ax.set_yticks(np.arange(-.5,len(rows),1),minor=True)
ax.grid(which='minor',color='white',linewidth=1.8)
ax.tick_params(which='minor',length=0)
for spine in ax.spines.values(): spine.set_visible(False)
fig.suptitle('Antecedentes: qué se documenta en los pasajes revisados',fontsize=18,fontweight='bold',x=.57,y=.98)
fig.text(.30,.025,'D = documentado · ? = no establecido en la evidencia inspeccionada\nUn ? no demuestra ausencia. La columna de certificado conjunto sigue sin comparación concluyente.',fontsize=11,color='#334155')
fig.subplots_adjust(left=.30,right=.99,top=.88,bottom=.075)
out=repo/'Docs/assets/literature-evidence-map-2026-10-08.png'
fig.savefig(out,dpi=150,facecolor='white',metadata={'Software':'Neuro3D evidence catalog visualization'})
plt.close(fig)
print(str(out))
