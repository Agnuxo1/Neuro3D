"""Archive real graph receipts and plot only data from that frozen result."""
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
src=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/coherent-state-graph-capture-20261009-run01')
out=root/'Docs/validation/coherent-state-graph-capture-2026-10-09'
out.mkdir(exist_ok=False)
receipt=json.loads((src/'supervisor.json').read_text())
assert receipt['primary_metric']==1 and receipt['owned_worker_cleaned_up']
assert all(hashlib.sha256((src/p).read_bytes()).hexdigest()==h for p,h in receipt['raw_file_sha256'].items())
shutil.copytree(src,out/'attempt01')
result=json.loads((src/'result.json').read_text())
graph=result['graph']
def scalar(value):
    return value['numerator']/value['denominator'] if isinstance(value,dict) and set(value)=={'numerator','denominator'} else value
fig,(ax,bars)=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1.8,1]})
for node in graph['nodes']:
    x,y=[scalar(v) for v in node['origin'][:2]]
    xx,yy=[scalar(v) for v in node['point'][:2]]
    ax.plot([x,xx],[y,yy],color='#2267a5',alpha=.45,lw=1)
    ax.scatter([xx],[yy],s=12,color='#e27c26' if 'bs' in node['hit_object'] else '#55606e')
    if 'terminal' in node:
        ax.text(xx+.15,yy+.15,node['terminal'].replace('det.',''),fontsize=8)
ax.set(xlabel='x (BU)',ylabel='y (BU)',title='Segmentos de los 133 estados exactos')
ax.set_aspect('equal')
ax.grid(alpha=.18)
names=list(result['powers'])
bars.barh([n.replace('det.','') for n in names],[result['powers'][n] for n in names],color='#2267a5')
bars.set(xlabel='Potencia modal normalizada',title='Campos coherentes: estimaciones nativas')
bars.invert_yaxis()
bars.grid(axis='x',alpha=.18)
fig.suptitle('Captura Blender: 104 superficies, 5 entradas; 17.060 caminos representados por 186 aristas',fontsize=12)
fig.text(.5,.015,'Recorrido y primeros hits auditados; campo todavía sin certificado. No medición física ni ventaja de velocidad.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.045,1,.94))
asset=root/'Docs/assets/captured-coherent-graph-2026-10-09.png'
fig.savefig(asset,dpi=160)
plt.close(fig)
(out/'plot-receipt.json').write_bytes((json.dumps({'result_sha256':hashlib.sha256((src/'result.json').read_bytes()).hexdigest(),
    'asset_path':asset.relative_to(root).as_posix(),'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
    'matplotlib_version':matplotlib.__version__,'physical_measurement':False,'native_field_certified':False},indent=2)+'\n').encode())
shutil.copyfile(Path(__file__),out/'archive_plot_source.py')
files=sorted(p for p in out.rglob('*') if p.is_file())
(out/'artifact_index.json').write_bytes((json.dumps({'files':[{'path':p.relative_to(out).as_posix(),
    'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]},indent=2)+'\n').encode())
print(json.dumps({'files':len(files),'states':len(graph['nodes']),'terminal_paths':result['represented_terminal_paths']}))
