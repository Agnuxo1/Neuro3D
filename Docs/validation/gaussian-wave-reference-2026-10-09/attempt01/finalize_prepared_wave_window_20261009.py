import hashlib,json,shutil,datetime
from pathlib import Path
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');base=Path(__file__).resolve().parent;backup=base/'wave-prepared-prepublication02';backup.mkdir(exist_ok=False)
profile=repo/'Docs/research/gaussian_wave_profile_2026-10-09.json';receipt=repo/'Docs/research/gaussian_wave_registration_2026-10-09.json'
shutil.copyfile(profile,backup/'profile.json');shutil.copyfile(receipt,backup/'registration.json')
p=json.loads(profile.read_bytes());p['gates'].update(same_dx_window_field_absolute=2e-6,same_dx_window_disk_fraction_absolute=2e-6)
p['pins']={name:hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in p['pins']}
profile.write_bytes((json.dumps(p,indent=2)+'\n').encode());r=json.loads(receipt.read_bytes());r['profile_sha256']=hashlib.sha256(profile.read_bytes()).hexdigest();receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode())
(backup/'amendment.json').write_text(json.dumps({'prepared_not_published_not_executed':True,'before_sha256':hashlib.sha256((backup/'profile.json').read_bytes()).hexdigest(),'after_sha256':r['profile_sha256'],'change':'Explicitsame-dxwindowfield/powercomparison1024L16vs2048L32 beforefirstexecution'},indent=2)+'\n')
with (base/'CHECKPOINT.md').open('a',encoding='utf-8') as s:s.write('\n## '+datetime.datetime.now(datetime.timezone.utc).isoformat()+' — Wine published; declared wave module next\nWineall3runsresults/raw/plotpublished4b227581c7dcb443ee2d7885eed698f2aeedb6e9 remotematched. Counts33/37,30/37,28/37 vs32/37bothclassicalbaselines; no superiority. Actualfullworker1114.174s/RSS107.781MiB. Waveprofile3cb6c42a preparedwithsame-dxwindow/refinementandindependentHankel/paraxialcontrols, notyetpublished/executed. Prepublication01/02 revisionspreservedprivately, no thresholdchangedafteroutcomes. Noownworkeractive. Nextpublishfixedwaveprofile thenrunonce; ownBlenderUI/cleanreproduction andscientificarticle stillrequired. AMDabsent/externalIDsnull.\n')
print(json.dumps({'profile_id':p['profile_id'],'profile_sha256':r['profile_sha256'],'trial_executed':False}))
