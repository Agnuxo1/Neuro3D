import ast,datetime,hashlib,json,uuid
from pathlib import Path
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');base=Path(__file__).resolve().parent
worker=(repo/'Tools/run_gaussian_wave_reference_v1.py').read_text()
for before,after in [("r['size']==2048 and r['window_BU']==16","r['size']==4096 and r['window_BU']==32"),("r['size']==2048 and r['window_BU']==32","r['size']==4096 and r['window_BU']==64"),("r['size']==1024","r['size']==2048"),('optic_neuro_blender.gaussian_wave_reference.v1','optic_neuro_blender.gaussian_wave_reference.v2')]:
    assert worker.count(before)==1,(before,worker.count(before));worker=worker.replace(before,after)
worker='# Remedial larger-window v2; v1 negative outcome and source remain immutable.\n'+worker
supervisor=(repo/'Tools/run_frozen_wave_reference_v1.py').read_text()
for before,after in [('gaussian_wave_profile.v1','gaussian_wave_profile.v2'),('run_gaussian_wave_reference_v1.py','run_gaussian_wave_reference_v2.py'),('run_frozen_wave_reference_v1.py','run_frozen_wave_reference_v2.py'),("'free_ram_before_mib':4000","'free_ram_before_mib':6144"),("'free_ram_floor_mib':2500","'free_ram_floor_mib':3500"),("'owned_rss_mib':1500","'owned_rss_mib':3000"),('[[512,16],[1024,16],[2048,16],[2048,32]]','[[1024,32],[2048,32],[4096,32],[4096,64]]'),('wave_supervision.v1','wave_supervision.v2')]:
    assert before in supervisor,before;supervisor=supervisor.replace(before,after)
supervisor=supervisor.replace("need(result['profile_sha256']==pin and len(result['rows'])==36 and len(result['gates'])==9,'wave frozen outcome mismatch')","need(result['schema']=='optic_neuro_blender.gaussian_wave_reference.v2' and result['status'] in ('PASS','FAIL_ONE_OR_MORE_FROZEN_GATES') and result['profile_sha256']==pin and len(result['rows'])==36 and len(result['gates'])==9,'wave frozen outcome mismatch')")
supervisor='# Remedial larger-window v2 with explicit increased memory envelope.\n'+supervisor
for filename,text in [('Tools/run_gaussian_wave_reference_v2.py',worker),('Tools/run_frozen_wave_reference_v2.py',supervisor)]:
    ast.parse(text);target=repo/filename;assert not target.exists();target.write_bytes(text.encode())
old=json.loads((repo/'Docs/research/gaussian_wave_profile_2026-10-09.json').read_bytes());p=json.loads(json.dumps(old))
p.update(schema='optic_neuro_blender.gaussian_wave_profile.v2',profile_id=str(uuid.uuid4()),worker='Tools/run_gaussian_wave_reference_v2.py',grids=[[1024,32],[2048,32],[4096,32],[4096,64]],prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
p['limits'].update(free_ram_before_mib=6144,free_ram_floor_mib=3500,owned_rss_mib=3000)
p['previous_valid_negative_profile_sha256']=hashlib.sha256((repo/'Docs/research/gaussian_wave_profile_2026-10-09.json').read_bytes()).hexdigest()
p['amendment']='Remedial adaptation after publishednegative30a835bb: doubledspatialwindows32/64 andgrids1024/2048/4096, samephysicalfamily/readout/allnumericalbudgets; independentwindowcomparisonatidenticaldx2048/32versus4096/64. Explicitlyincreasedmemoryguard6144prefree/3500floor/3000RSS,notoldprofilealteration. Validation ofknownfailure repair,notnewblindscientificdiscovery.'
names=set(old['pins'])-{'Tools/run_gaussian_wave_reference_v1.py','Tools/run_frozen_wave_reference_v1.py'}
names.update({'Tools/run_gaussian_wave_reference_v2.py','Tools/run_frozen_wave_reference_v2.py'})
p['pins']={name:hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in sorted(names)}
target=repo/'Docs/research/gaussian_wave_remedial_profile_2026-10-09.json';assert not target.exists();target.write_bytes((json.dumps(p,indent=2)+'\n').encode())
r=json.loads((repo/'Docs/research/gaussian_wave_registration_2026-10-09.json').read_bytes());r.update(profile_id=p['profile_id'],profile_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
(repo/'Docs/research/gaussian_wave_remedial_registration_2026-10-09.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
with (repo/'.gitattributes').open('a',encoding='utf-8') as s:s.write('\nDocs/research/gaussian_wave_remedial_profile_2026-10-09.json -text !eol whitespace=cr-at-eol\nDocs/research/gaussian_wave_remedial_registration_2026-10-09.json -text !eol whitespace=cr-at-eol\nDocs/validation/gaussian-wave-remedial-2026-10-09/** -text !eol whitespace=cr-at-eol\n')
state={'project':'OpticNeuroBlender','published_negative':'30a835bb,36Gaussianwavecases32.915s/RSS510.734MiB; λ.1/z4L16radialfield2.231e-6>unchanged2e-6; N512/1024/2048sameerror; L32reduces4.087e-7; norm/apertureallpass','proposal':'Separatefrozen/publishedv2,same9physicalcases/tolerances,repairedwindows32/64 and1024/2048/4096 grids;6174MiBprefree? actualprofile6144,hostlast7958MiB,3500floor/3000RSS/240s/1CPU. Retainallnegativeoutcomes, noNobel/physicalclaim; validationofknownnegative notblinddata. ThenownUI/cleanCI/article. NoAMDhardware/externalIPFSIDs.'}
questions={'repair':{'type':'choice','instructions':'Select concrete scientifically valid remedial route; advisoryonly.','criteria':{'separate_larger_window_profile_same_tolerances_and_full_negative_retention':'Publishv2beforetrial, allthresholdsunchanged, boundedRAMandtime; noafterthefactsuccessofv1. UseoriginalcomplexFFT/Hankel/paraxial.','raise_tolerance_in_original_profile_and_hide_negative':'Changebudgetafterdataandoverwritefirstmetric.'}}}
state['proposal']=state['proposal'].replace('6174MiBprefree? actualprofile6144','6144MiBprefree')
for name,obj in [('jev-wave-repair-state-20261009.json',state),('jev-wave-repair-questions-20261009.json',questions)]:
    (base/name).write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps({'profile_id':p['profile_id'],'profile_sha256':r['profile_sha256'],'pins':len(names),'executed':False,'numerical_budgets_identical':p['gates']==old['gates']}))
