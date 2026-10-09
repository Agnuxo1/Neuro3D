import argparse,datetime,hashlib,json,subprocess
from pathlib import Path
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');base=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--profile',required=True);parser.add_argument('--registration',required=True);parser.add_argument('--commit',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
profile=json.loads((repo/args.profile).read_bytes())
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/neuro3d-scientific-closure-20261008'],cwd=repo,text=True).split()[0]
assert head==remote==args.commit
pins={**profile['pins'],**{name:hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in (args.profile,args.registration)}}
for name,pin in pins.items():
    blob=subprocess.check_output(['git','show','HEAD:'+name],cwd=repo)
    assert hashlib.sha256(blob).hexdigest()==pin and blob==(repo/name).read_bytes(),name
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'published_commit':head,'pins':len(profile['pins']),'profile_sha256':pins[args.profile],'registration_sha256':pins[args.registration],
        'git_blob_source_byte_identity':True,'preexecution':True,'profile_id':profile['profile_id']}
(base/args.output).write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))
with (base/'CHECKPOINT.md').open('a',encoding='utf-8') as s:s.write('\n## '+report['utc']+' — frozen profile publication verified before execution\nProfile '+profile['profile_id']+' SHA'+report['profile_sha256']+' sources'+str(len(profile['pins']))+' publishedcommit'+head+' remotematched/Gitblobsbyteequal. ReceiptGitHubhumanexception verified, externalIDsnull. StartingboundedtrialafterpreviousWine milestonepublished. No scientificoutcomes yet for thisprofile.\n')
