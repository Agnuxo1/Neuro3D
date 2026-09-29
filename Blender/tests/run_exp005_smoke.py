"""Bounded launcher: use gpuq; 120s maximum per owned child, one CPU thread."""
import argparse
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender',required=True)
    parser.add_argument('--evidence',required=True)
    parser.add_argument('--script',default='exp005_runtime_smoke.py')
    args = parser.parse_args()
    folder = Path(args.evidence).resolve(); folder.mkdir(parents=True,exist_ok=True)
    script = Path(__file__).resolve().parent/args.script
    with (folder/(script.stem+'.log')).open('w',encoding='utf-8') as log:
        child = subprocess.Popen([args.blender,'--background','--factory-startup',
                '--threads','1','--python-exit-code','1','--python',str(script),
                '--','--evidence',str(folder)],stdout=log,stderr=subprocess.STDOUT)
        try: code = child.wait(timeout=120)
        except subprocess.TimeoutExpired:
            child.kill(); child.wait(timeout=15)
            raise RuntimeError('owned Blender child exceeded 120 seconds')
    if code: raise RuntimeError(f'Blender exit {code}; see {folder}')
    print('BOUNDED_BLENDER_DONE',flush=True)


if __name__=='__main__': main()
