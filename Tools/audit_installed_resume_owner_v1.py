"""Actual installed Blender UI train/pause/restart/resume owner for a controller."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import bpy,numpy as np

def need(c,m):
    if not c:raise ValueError(m)
def put(p,v):p.write_bytes((json.dumps(v,indent=2,allow_nan=False)+'\n').encode())

def main():
    a=sys.argv[sys.argv.index('--')+1:];p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--mode',choices=['BASELINE','PAUSE','RESUME'],required=True);p.add_argument('--original',type=Path);args=p.parse_args(a);args.out.mkdir(exist_ok=False);start=time.perf_counter()
    profile=json.loads(args.profile.read_bytes());need(list(bpy.app.version)==[4,5,14],'Actual frozen Blender required');need(hashlib.sha256(Path(profile['archive']).read_bytes()).hexdigest()==profile['archive_sha256'],'Package identity required')
    bpy.context.preferences.use_preferences_save=False;bpy.context.preferences.filepaths.use_auto_save_temporary_files=False
    package=Path(os.environ['BLENDER_USER_SCRIPTS'])/'addons/optic_neuro_blender'
    if not package.exists():bpy.ops.preferences.addon_install(filepath=profile['archive'],overwrite=False)
    import addon_utils
    addon_utils.enable('optic_neuro_blender',default_set=False,persistent=True)
    import optic_neuro_blender as addon
    from optic_neuro_blender.bootstrap import PACKAGE,verify_bundle
    from optic_neuro_blender.runtime import read_json,process_identity
    from optic_neuro_blender.model import capture_current
    verify_bundle();need(addon.bl_info['version']==(0,1,3) and hashlib.sha256((PACKAGE/'package_manifest.json').read_bytes()).hexdigest()==profile['manifest_sha256'],'Actual installed0.1.3 required')
    addon.register();addon.unregister();addon.unregister();addon.register();need(addon._registered,'Idempotent installed lifecycle required')
    need(bpy.ops.optic_neuro.load_example()=={'FINISHED'},'Actual example operator required');example=Path(bpy.data.filepath);example_sha=hashlib.sha256(example.read_bytes()).hexdigest()
    jobs=args.out.parent/'jobs';jobs.mkdir(exist_ok=True);settings=bpy.context.scene.optic_neuro_settings;settings.work_directory=str(jobs);settings.amplitudes=profile['amplitudes'];settings.phases=profile['phases_rad'];checks=[]
    if args.mode=='RESUME':
        need(args.original is not None,'Original interrupted job required');settings.recover_directory=str(args.original)
        settings.phases[0]+=.01
        try:addon.validate_resume_source(args.original)
        except ValueError:checks.append({'name':'changed_inputs_resume_rejected','pass':True})
        else:raise ValueError('Stale inputs accepted for resume')
        settings.phases=profile['phases_rad'];obj=bpy.data.objects['c00.r1'];old=obj.matrix_world.copy();new=old.copy();new[0][3]+=.0001;obj.matrix_world=new;bpy.context.view_layer.update()
        try:addon.validate_resume_source(args.original)
        except ValueError:checks.append({'name':'changed_geometry_resume_rejected','pass':True})
        else:raise ValueError('Stale scene accepted for resume')
        obj.matrix_world=old;bpy.context.view_layer.update()
        checkpoint=args.original/'training/optimizer_checkpoint.json';original_checkpoint=checkpoint.read_bytes();checkpoint.write_bytes(original_checkpoint[:len(original_checkpoint)//2])
        try:addon.validate_resume_source(args.original)
        except (ValueError,json.JSONDecodeError):checks.append({'name':'truncated_checkpoint_resume_rejected','pass':True})
        else:raise ValueError('Truncated checkpoint accepted')
        finally:checkpoint.write_bytes(original_checkpoint)
        need(bpy.ops.optic_neuro.resume_training()=={'FINISHED'},'Actual installed resume operator required')
    elif args.mode=='PAUSE':addon.start_job('TRAIN',audit_pause_after_checkpoint_step=12)
    else:need(bpy.ops.optic_neuro.train()=={'FINISHED'},'Actual installed training operator required')
    folder=addon._last_folder;put(args.out/'owned_child.json',{'host_identity':process_identity(),'child_identity':process_identity(addon._job.process.pid),'job_folder':str(folder)})
    until=time.monotonic()+900
    while addon._job.state=='RUNNING' and time.monotonic()<until:
        addon.poll_job()
        ready=folder/'training/crash_point_ready.json'
        if args.mode=='PAUSE' and ready.exists():
            value=read_json(ready);need(value['next_step']==12 and not (folder/'result.json').exists(),'Exact checkpoint12 with no completed result required')
            put(args.out/'host_kill_ready.json',{'host_identity':process_identity(),'child_identity':process_identity(addon._job.process.pid),'job_folder':str(folder),'checkpoint_sha256':hashlib.sha256((folder/'training/optimizer_checkpoint.json').read_bytes()).hexdigest(),'next_step':12})
            while True:time.sleep(.1)
        time.sleep(.1)
    need(addon._job.state=='COMPLETED','Installed background training did not complete');request,result=addon.validate_recovery(folder);training=result['training']
    need(training['geometry_membership_states']==61 and training['continuous_family_proved_states']==133 and training['exact_affine_expression_identity']=='CERTIFIED_EXACT_AFFINE_EXPRESSION_IDENTITY','Complete continuous proof/membership required')
    need(result['training_native_power_max_difference']<=profile['power_tolerance'],'Actual recaptured native inference parity required')
    if args.mode=='RESUME':
        need(training['recovery']['resume_step']==12 and training['recovery']['prefix_replay_verified'],'Exact optimizer-prefix replay and Adam recovery required')
        need(len(training['recovery']['adversarial_controls'])==4 and all(x['rejected'] for x in training['recovery']['adversarial_controls']),'All four checkpoint adversaries rejected')
        need(bpy.ops.optic_neuro.apply()=={'FINISHED'},'Installed completed resumed training apply required');need(capture_current()['state_sha256']==result['final_capture_state_sha256'],'Recovered actual native scene identity required')
        saved=args.out/'resumed_applied_geometry.blend';settings.save_path=str(saved);need(bpy.ops.optic_neuro.save_copy()=={'FINISHED'},'New copy operator required');before=capture_current()['state_sha256'];bpy.ops.wm.open_mainfile(filepath=str(saved),use_scripts=False,load_ui=False);need(capture_current()['state_sha256']==before,'Reopened resumed actual geometry identity required')
        checks.extend([{'name':'checkpoint12_replay_adam_and_four_adversaries','pass':True},{'name':'resumed_complete_apply_save_reopen','pass':True}])
    need(hashlib.sha256(example.read_bytes()).hexdigest()==example_sha,'Original installed example must be preserved')
    report={'schema':'optic_neuro_blender.installed_resume_owner.v1','status':'PASS','mode':args.mode,'job_folder':str(folder),'checks':checks,'test_correct':training['test_correct'],'native_power_max_difference':result['training_native_power_max_difference'],'resume_step':training['recovery']['resume_step'],'geometry_membership_states':training['geometry_membership_states'],'seconds':time.perf_counter()-start,'original_example_preserved':True}
    put(args.out/'result.json',report);addon.unregister();print(json.dumps(report),flush=True)

if __name__=='__main__':main()
