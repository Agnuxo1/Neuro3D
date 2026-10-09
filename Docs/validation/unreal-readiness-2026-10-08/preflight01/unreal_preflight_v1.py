"""Read-only UE5.6 availability/source-scope receipt. Does not launch GPU/builds.

Registered installation metadata is a candidate path, never proof of engine
availability. Optional --engine-root permits an owner-supplied recovered path.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
METADATA=Path('C:/ProgramData/Epic/UnrealEngineLauncher/LauncherInstalled.dat')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inspect_engine(root):
    root=Path(root).resolve();files={name:root/relative for name,relative in {
        'version':'Engine/Build/Build.version','editor':'Engine/Binaries/Win64/UnrealEditor.exe',
        'editor_command':'Engine/Binaries/Win64/UnrealEditor-Cmd.exe',
        'build_tool':'Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll',
        'build_script':'Engine/Build/BatchFiles/Build.bat','automation_script':'Engine/Build/BatchFiles/RunUAT.bat',
        'shader_compiler':'Engine/Binaries/Win64/ShaderCompileWorker.exe'}.items()}
    observed={key:{'path':str(path),'exists':path.is_file()} for key,path in files.items()}
    version=None
    if files['version'].is_file():
        version=json.loads(files['version'].read_bytes());observed['version']['sha256']=sha(files['version'])
    return root,observed,version


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--engine-root',type=Path);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();candidates=[];registrations=[]
    if METADATA.is_file():
        for entry in json.loads(METADATA.read_bytes()).get('InstallationList',[]):
            registrations.append({key:entry.get(key) for key in ('InstallLocation','AppName','ArtifactId','AppVersion')})
            if entry.get('InstallLocation'):candidates.append(Path(entry['InstallLocation']))
    if args.engine_root:candidates.insert(0,args.engine_root)
    candidates.extend([Path('C:/Program Files/Epic Games/UE_5.6'),Path('D:/TOOLS/Unreal/UE_5.6'),Path('E:/NEBULA_SYSTEM/Engine/UE_5.6')])
    engines=[]
    for candidate in dict.fromkeys(candidates):
        root,files,version=inspect_engine(candidate)
        engines.append({'root':str(root),'files':files,'version':version,
                        'usable_UE_5_6_candidate':all(row['exists'] for row in files.values()) and
                        version is not None and version.get('MajorVersion')==5 and version.get('MinorVersion')==6})
    vswhere=Path('C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe');toolchain={'inventory_available':False}
    if vswhere.is_file():
        completed=subprocess.run([str(vswhere),'-latest','-products','*','-requires','Microsoft.VisualStudio.Component.VC.Tools.x86.x64','-format','json'],capture_output=True,check=True,timeout=15)
        rows=json.loads(completed.stdout);toolchain={'inventory_available':True,'installations':[
            {key:row.get(key) for key in ('installationPath','installationVersion','isComplete','isLaunchable')} for row in rows]}
    plugin=ROOT/'Plugins/SantoGrialPhotonic/SantoGrialPhotonic.uplugin';descriptor=json.loads(plugin.read_bytes())
    reference=ROOT/'Plugins/SantoGrialPhotonic/Tests/photonic_reference.py';legacy=ROOT/'Source/OptiXRayTracing.cu'
    source=legacy.read_text(encoding='utf-8');usable=any(row['usable_UE_5_6_candidate'] for row in engines)
    result={'schema':'neuro3d.unreal.readonly_preflight.v1','checked_utc':datetime.now(timezone.utc).isoformat(),
            'status':'ENGINE_CANDIDATE_AVAILABLE_NOT_COMPILED' if usable else 'BLOCKED_NO_USABLE_ENGINE',
            'registered_candidates':registrations,'engines':engines,'visual_studio_inventory':toolchain,
            'plugin_module_loading_phase':descriptor['Modules'][0]['LoadingPhase'],
            'legacy_OptiX_source_observed':{'has_luminosity_rgb_payload':'Current luminosity' in source and 'current_r' in source,
                                        'uses_fixed_tmin_and_origin_bias':'0.01f' in source,
                                        'canonical_Iris_weights_or_complex_phase_not_implemented_here':True},
            'source_scope':'Unreal plugin is a separate abstract digital graph; legacy OptiX is luminosity/RGB, not canonical coherent Iris',
            'compiled':False,'native_GPU_execution_verified':False,'RT_coherent_propagation_certified':False,'readback_parity_verified':False,
            'next_required_evidence':['usable UE5.6 path','real compilation logs','frozen complete inputs/readbacks','all-field independent parity audit','guarded native RT coherent implementation if retained'],
            'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in (Path(__file__),plugin,reference,legacy)}}
    with args.out.open('xb') as stream:stream.write((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'status':result['status'],'engine_candidates':len(engines),'GPU_executed':False}))
    return 0 if usable else 2


if __name__=='__main__':raise SystemExit(main())
