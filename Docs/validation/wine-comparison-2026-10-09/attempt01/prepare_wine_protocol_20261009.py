import hashlib,json,uuid
from pathlib import Path
import numpy as np
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
previous=json.loads((repo/'Docs/research/captured_geometry_training_profile_2026-10-09.json').read_bytes())
labels=np.loadtxt(repo/'Docs/data/uci-wine/wine.data',delimiter=',')[:,0].astype(int)-1
random=np.random.default_rng(20261009);train=[];test=[]
for label in range(3):
    members=np.where(labels==label)[0];random.shuffle(members);cut=[47,56,38][label]
    train.extend(members[:cut].tolist());test.extend(members[cut:].tolist())
center=np.asarray(previous['untrained_center_deltas_BU']);initial=[]
for seed in (1049,1050,1051):initial.append({'seed':seed,'deltas_BU':(center+np.random.default_rng(seed).uniform(-.0125,.0125,16)).tolist()})
pins=set(previous['pins'])-{'Blender/demo_lattice_iris/iris.csv','Tools/run_frozen_geometry_training_v1.py'}
pins.update({'Tools/train_wine_comparison_v1.py','Tools/run_frozen_wine_comparison_v1.py','Blender/blender_lab/classifier_comparison_v1.py','Docs/data/uci-wine/wine.data','Docs/data/uci-wine/wine.names','Docs/data/uci-wine/provenance.json'})
profile={key:previous[key] for key in ['scene','graph_result','steps','learning_rate_BU','loss_temperature','translation_bound_BU','native_quantization_allowance_BU','untrained_center_deltas_BU','initialization_policy','detectors','gradient_difference_step_BU','gradient_absolute_tolerance','field_rebuild_tolerance','minimum_training_loss_drop']}
profile.update(schema='optic_neuro_blender.wine_comparison_profile.v1',profile_id=str(uuid.uuid4()),worker='Tools/train_wine_comparison_v1.py',dataset='Docs/data/uci-wine/wine.data',feature_columns_zero_based_in_original_file=[1,2,3,4],train_indices=train,test_indices=test,split_seed=20261009,initializations=initial,
    baseline_optimizer={'l2':.001,'maxiter':2000,'gtol':1e-8,'ftol':1e-12,'maximum_gradient_abs':1e-5},
    limits={'worker_seconds':1800,'free_ram_before_mib':4000,'free_ram_floor_mib':2500,'owned_rss_mib':1500,'evidence_mib':64,'cpu_cores':1,'gpu':False},
    endpoints={'software_gate':'All3seeds everygeometryaudit/FD/rebuild and traininglossdrop>=.02, noaccuracy gate','comparative':'Reportall3heldoutcorrect/37 withWilson95 andpairedaccuracydifference to15nominalparamlinear and45nominalparamquadratic; exploratoryMcNemarunadjusted; noseedselection orsuperiorityclaim','capacity':'Independently evaluated realquadratic equivalence numerical<=1e-11, perdetectorrealPSD rank<=2, allports; algebraiccomplexHermitianrank<=1'},
    scope='New within-dataset Wine holdout with fresh optical weights, fixed first4of13features and same unitpower5sourceencoding for all classifiers. Public nonblind data, notzero-shot transfer or external replication. Historical Iris capture supplies geometry only; oldtrained mirror delays erased. Three seeds shareoneheldoutsplit; no pooled sample inflation. No physicalfidelity/noveltyclaim.',
    pins={p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in sorted(pins)})
path=repo/'Docs/research/wine_comparison_profile_2026-10-09.json'
assert not path.exists();path.write_bytes((json.dumps(profile,indent=2)+'\n').encode())
pin=hashlib.sha256(path.read_bytes()).hexdigest()
receipt=json.loads((repo/'Docs/research/captured_geometry_training_registration_2026-10-09.json').read_bytes());receipt.update(profile_id=profile['profile_id'],profile_sha256=pin)
(repo/'Docs/research/wine_comparison_registration_2026-10-09.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
with (repo/'.gitattributes').open('a',encoding='utf-8') as stream:
    stream.write('\nDocs/research/wine_comparison_profile_2026-10-09.json -text !eol whitespace=cr-at-eol\nDocs/research/wine_comparison_registration_2026-10-09.json -text !eol whitespace=cr-at-eol\nDocs/data/uci-wine/** -text !eol whitespace=cr-at-eol\nDocs/validation/wine-comparison-2026-10-09/** -text !eol whitespace=cr-at-eol\n')
print(json.dumps({'profile_id':profile['profile_id'],'profile_sha256':pin,'source_pins':len(pins),'train':len(train),'test':len(test)}))
