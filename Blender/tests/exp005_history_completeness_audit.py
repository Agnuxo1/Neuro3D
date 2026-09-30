"""Own tiny synthetic completeness fixtures, no peer imports or writers."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from history_completeness_cpu_v1 import validate_complete_tree
from history_lineage_cpu_v2 import scene_binding,validate_history
from exp005_history_lineage_audit import fixture


def cases():
    s,full=fixture(True)
    for label,ids in (('only_source',{0}),('missing_reflected_branch_and_escape',{0,1,3}),
                      ('both_departures_no_terminals',{0,1,2}),('missing_escape_terminal',{0,1,2,3})):
        yield label,copy.deepcopy(s),[copy.deepcopy(r) for r in full if r['id'] in ids]


def duplicate_sources():
    s,r=fixture(True);s['sources'].append({**s['sources'][0],'id':'s2'});sha,_=scene_binding(s)
    for row in r:row['snapshot_sha256']=sha
    second=copy.deepcopy(r)
    for row in second:
        row['id']+=5;row['source_id']='s2'
        if row['parent_id'] is not None:row['parent_id']+=5
    return s,r+second


def audit():
    positives=[]
    for split in (False,True):
        s,r=fixture(split);positives.append({'fixture':'splitter' if split else 'mirror','snapshot':s,
                                           'records':r,'result':validate_complete_tree(s,r)})
    s,r=duplicate_sources();positives.append({'fixture':'two_sources','snapshot':s,'records':r,
                                             'result':validate_complete_tree(s,r)})
    rejected=[]
    for label,s,r in cases():
        prefix=validate_history(s,r)
        if prefix['all_branches_proved_complete']:raise ValueError('prefix contract changed')
        try:validate_complete_tree(s,r)
        except ValueError as e:rejected.append({'case':label,'snapshot':s,'records':r,'prefix_valid':True,'reason':str(e)})
        else:raise ValueError('omitted branch accepted: '+label)
    return {'scope':'synthetic exact CPU complete geometric tree; NO GPU/Blender/optical-field completeness',
            'positives':positives,'rejected_valid_prefixes':rejected,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();r=audit()
    b=Path(__file__).parents[1];files=[Path(__file__),Path(__file__).with_name('test_exp005_history_completeness.py'),
                                     b/'tests/exp005_history_lineage_audit.py']
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_completeness_cpu_v1.py','history_lineage_cpu_v2.py',
                                                      'history_lineage_cpu_v1.py','frontier_inputs.py','gpu_geometry_probe.py')]
    files += [b/'shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    r['code_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(r,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'complete_trees':len(r['positives']),'incomplete_prefixes_rejected':len(r['rejected_valid_prefixes']),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
