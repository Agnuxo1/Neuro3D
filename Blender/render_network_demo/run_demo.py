"""Bounded two-process launcher. Run THROUGH gpuq, not alongside other loads."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', required=True)
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    repo = folder.parents[1]
    blend = folder/'Neuro3D_Render_Network.blend'
    evidence = Path(args.evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    preview = repo/'Docs/assets/neuro3d-render-network.png'
    stages = [('build', folder/'build_demo.py', ['--blend', str(blend)]),
              ('verify', folder/'verify_demo.py', ['--blend', str(blend),
               '--evidence', str(evidence), '--preview', str(preview)])]
    for name, script, script_args in stages:
        if args.verify_only and name == 'build':
            continue
        command = [args.blender, '--background', '--threads', '1',
                   '--python-exit-code', '1', '--python', str(script), '--', *script_args]
        with (evidence/f'{name}.log').open('w', encoding='utf-8') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            try:
                code = child.wait(timeout=180)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=15)
                raise RuntimeError(f'{name}: 180-second time limit')
        print(f'{name}: exit={code}', flush=True)
        if code:
            raise RuntimeError(f'{name} failed; inspect {evidence / (name + ".log")}')
    report = json.loads((evidence/'verification.json').read_text(encoding='utf-8'))
    if not report['passed']:
        raise RuntimeError('Verification failed')
    # Publish only compact generated evidence; raw render images/logs stay in D:.
    (folder/'verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('Neuro3D render tests PASS', flush=True)


if __name__ == '__main__':
    main()
