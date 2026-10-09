import datetime,hashlib,json,subprocess
from pathlib import Path
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');base=Path(__file__).resolve().parent
path='Docs/research/wine_comparison_profile_2026-10-09.json';profile=json.loads((repo/path).read_bytes())
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/neuro3d-scientific-closure-20261008'],cwd=repo,text=True).split()[0]
assert head==remote=='0e2e7c1e84f26d621de499ef0669037d655fef99'
for name,pin in {**profile['pins'],path:hashlib.sha256((repo/path).read_bytes()).hexdigest()}.items():
    blob=subprocess.check_output(['git','show','HEAD:'+name],cwd=repo)
    assert hashlib.sha256(blob).hexdigest()==pin and blob==(repo/name).read_bytes(),name
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'published_commit':head,'pins':len(profile['pins']),'profile_sha256':hashlib.sha256((repo/path).read_bytes()).hexdigest(),'git_blob_source_byte_identity':True,'preexecution':True,'scientific_results_observed':False}
(base/'wine-published-preexecution-verification-20261009.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))
with (base/'CHECKPOINT.md').open('a',encoding='utf-8') as stream:
    stream.write('\n## '+report['utc']+' — Wine protocol published before execution\nCommit0e2e7c1e84f26d621de499ef0669037d655fef99 remoteverified; profileaf7bd4fd-2d1f-48c6-91ce-94ab31cd4fa6 SHA623623be2f0be6acccddfa432a94526fafeb484bf2d05d50b8822319c7b0c81c and22sourcepins Gitblobbyteidentical. FivecontrolsPASS includingtrainonlyscaler,convexgradientFD,source/budget/feature/seedmutationrejection andrealhumanreceipt. FreshWinefirst4features fixed141/37split,3fixed60update seeds,183geometryaudits and3freshrebuilds; noheldoutselection. Alllossresults including failures toreport. JEVconnectedprovenancejev recommended fixedroute. Startingonebounded1800sCPUtrial; noAMD or externalIDs.\n')
