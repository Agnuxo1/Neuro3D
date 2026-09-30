"""Prepared private Blender pilot: export/save/reopen and CPU scene tracing.

No render/GPU propagation. NOT executed in bpy yet; requires an external
exclusive gpuq job, fail-closed resource guard and the SAME fresh deadline.
CLI flags alone do not supply authorization, exclusivity or telemetry.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from exp005_history_mzi_export import CASES,fixture,build_isolated_scene,evaluated_readback
from exp005_history_generated_export import validate_generated_export


def deadline_check(deadline,now=None):
    if not isinstance(deadline,datetime) or deadline.tzinfo is None or deadline.utcoffset().total_seconds()!=0:
        raise ValueError('explicit UTC job deadline required')
    remaining=(deadline-(now or datetime.now(timezone.utc))).total_seconds()
    if not 0<remaining<=120:raise ValueError('fresh pilot deadline within 120s required; never reset it')


def run_private_child(bpy,folder,check_deadline):
    check_deadline()
    if bpy.data.filepath:raise ValueError('must not run on an existing .blend')
    if folder.exists():raise ValueError('fresh evidence folder required; no overwrite')
    folder.mkdir()
    report={'scope':'candidate bpy evaluated export/save/reopen plus CPU Python tracing/fields; NOT GPU inference',
            'cases':[],'blender_version':bpy.app.version_string}
    for label,phase,shift in CASES:
        check_deadline();expected,_=fixture(phase,shift);name='history_generated_'+label
        scene=build_isolated_scene(bpy,expected,name);before=evaluated_readback(bpy,scene)
        blend=folder/(label+'.blend')
        if blend.exists():raise ValueError('fresh blend path required')
        check_deadline();bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        check_deadline();bpy.ops.wm.open_mainfile(filepath=str(blend))
        if bpy.context.window is None:raise ValueError('reopened private window context required')
        bpy.context.window.scene=bpy.data.scenes[name]
        after=evaluated_readback(bpy,bpy.data.scenes[name]);check_deadline()
        out=validate_generated_export(expected,before,after,phase,shift)
        report['cases'].append({'case':label,'before':before,'after':after,'result':out,
             'blend_path':str(blend),'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest()})
    check_deadline()
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--job-deadline-utc',required=True);p.add_argument('--authorized-private-child',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.authorized_private_child:raise ValueError('guarded exclusive private child required')
    deadline=datetime.fromisoformat(args.job_deadline_utc.replace('Z','+00:00'))
    check=lambda:deadline_check(deadline)
    check()
    import bpy  # Never imported during CPU-double tests. Outer guard mandatory.
    report=run_private_child(bpy,args.evidence.resolve(),check)
    report['job_deadline_utc']=deadline.isoformat();check()
    with (args.evidence.resolve()/'export.json').open('x',encoding='utf-8') as f:
        f.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    check();print('GENERATED_MZI_PRIVATE_PILOT_PASS',len(report['cases']))


if __name__=='__main__':main()
