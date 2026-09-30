"""Owned hidden Blender child, intended only below gpuq and guarded_job."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--blender',required=True)
    parser.add_argument('--evidence',required=True); parser.add_argument('--report',required=True)
    args=parser.parse_args()
    if sys.platform!='win32': raise ValueError('Windows hidden-launch wrapper only')
    startup=subprocess.STARTUPINFO(); startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow=subprocess.SW_HIDE
    command=[args.blender,'--factory-startup','--threads','1','--window-geometry','0','0','64','64',
             '--python-exit-code','1','--python',str(Path(__file__).with_name('exp005_blender_gpu.py')),
             '--','--evidence',args.evidence,'--report',args.report,'--authorized-by-user']
    env=os.environ.copy()
    temporary=Path(args.report).resolve().parent/(Path(args.report).stem+'_tmp')
    temporary.mkdir(exist_ok=False)
    env['TEMP']=str(temporary); env['TMP']=str(temporary)
    # Retain task-specific temp/crash evidence on D:, never delete user temp data.
    raise SystemExit(subprocess.run(command,startupinfo=startup,env=env,timeout=110).returncode)


if __name__=='__main__': main()
