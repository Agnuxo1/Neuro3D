import hashlib,json,shutil
from pathlib import Path
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');base=Path(__file__).resolve().parent;backup=base/'wave-prepared-prepublication01';backup.mkdir(exist_ok=False)
profile=repo/'Docs/research/gaussian_wave_profile_2026-10-09.json';receipt=repo/'Docs/research/gaussian_wave_registration_2026-10-09.json'
shutil.copyfile(profile,backup/'profile.json');shutil.copyfile(receipt,backup/'registration.json')
p=json.loads(profile.read_bytes());p['pins']={name:hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in p['pins']}
p['negative_outcomes']='All finite numericalbudget failures retained with36rows andvalidmetric0; onlyinvalidinputs/nonfinite/environmentinterruptionsproduceinconclusive.'
profile.write_bytes((json.dumps(p,indent=2)+'\n').encode());r=json.loads(receipt.read_bytes());r['profile_sha256']=hashlib.sha256(profile.read_bytes()).hexdigest();receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode())
(backup/'amendment.json').write_text(json.dumps({'prepared_not_published_not_executed':True,'before_sha256':hashlib.sha256((backup/'profile.json').read_bytes()).hexdigest(),'after_sha256':r['profile_sha256'],'change':'Storeallfinitemeasuredbudgetfailures asvalidmetric0; allthresholdsunchanged'},indent=2)+'\n')
print(json.dumps({'profile_id':p['profile_id'],'profile_sha256':r['profile_sha256'],'trial_executed':False}))
