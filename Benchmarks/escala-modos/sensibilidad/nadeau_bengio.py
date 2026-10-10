import json,numpy as np
from scipy import stats
raw=json.load(open('D:/PROJECTS/9_NEBULA_NEW/Benchmarks/escala-modos/resultados/resultados_raw.json'))
sel=[min([r for r in raw['malla'] if r['k']==k],key=lambda r:r['train_loss']) for k in range(10)]
am=np.array([r['test_acc'] for r in sel]); al=np.array([raw['lineas_base'][k]['logistica']['test_acc'] for k in range(10)])
d=am-al; se=d.std(ddof=1)*np.sqrt(1/10+360/1437); t=stats.t.ppf(.975,9)
print('NB corregido: media',d.mean(),'IC95',d.mean()-t*se,d.mean()+t*se,'t',d.mean()/se,'p',2*stats.t.sf(abs(d.mean()/se),9))
dm=am-np.array([raw['lineas_base'][k]['mlp']['test_acc'] for k in range(10)]); se=dm.std(ddof=1)*np.sqrt(.1+.25)
print('MLP NB IC',dm.mean()-t*se,dm.mean()+t*se)
cv=[(r['loss_curve'][-2][1]-r['loss_curve'][-1][1])/r['loss_curve'][-2][1] for r in sel]; print('caida relativa 1900->2000 elegidas: min/max',min(cv),max(cv))
print('inicial',np.mean([r['loss_curve'][0][1] for r in sel]),'final',np.mean([r['train_loss'] for r in sel]))
