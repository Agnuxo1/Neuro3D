"""Archive software-only gating receipts and checksum-verified preimages."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
WORK = Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008')
OUT = ROOT / 'Docs/validation/captured-pilot-supervisor-2026-10-08'
OUT.mkdir(exist_ok=False)
source = ROOT / 'Tools/run_captured_scalar_pilot_v1.py'
lines = source.read_bytes().splitlines(keepends=True)
old_lines, skipped = [], False
for line in lines:
    if b'report["host_ram_preflight_sufficient"]' in line:
        continue
    if b'need(type(result.get("rays")) is int' in line:
        skipped = True
    if skipped:
        if b'"worker output exceeds frozen ray/depth bounds")' in line:
            skipped = False
        continue
    old_lines.append(line)
old_source = b''.join(old_lines)
for name in ['captured-pilot-supervisor-preflight01', 'captured-pilot-supervisor-missing-registration01',
             'captured-pilot-supervisor-preflight02']:
    origin = WORK / name
    target = OUT / name
    shutil.copytree(origin, target)
    receipt = json.loads((target / 'supervisor.json').read_text(encoding='utf-8'))
    preimage = source.read_bytes() if name.endswith('preflight02') else old_source
    assert hashlib.sha256(preimage).hexdigest() == receipt['supervisor_source_sha256'], name
    assert hashlib.sha256((ROOT / 'Tools/audit_captured_pilot_result_v1.py').read_bytes()).hexdigest() == receipt['auditor_source_sha256']
    (target / 'supervisor_source.py').write_bytes(preimage)
    assert receipt['worker_started'] is False and receipt['result_collected'] is False
cmd = [sys.executable, '-X', 'utf8', '-m', 'unittest',
       'Blender.tests.test_coherent_contract_v1', 'Blender.tests.test_scalar_scene_ingress_v1',
       'Blender.tests.test_surface_union_interior_v1', 'Blender.tests.test_blender_lab_capture_v1',
       'Blender.tests.test_captured_pilot_supervision_v1', '-v']
result = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=30)
(OUT / 'software-controls.stdout').write_bytes(result.stdout)
(OUT / 'software-controls.stderr').write_bytes(result.stderr)
assert result.returncode == 0 and b'Ran 66 tests' in result.stderr
sources = ['Tools/run_captured_scalar_pilot_v1.py', 'Tools/audit_captured_pilot_result_v1.py',
           'Tools/bind_network_capture_v1.py', 'Blender/tests/test_captured_pilot_supervision_v1.py']
pins = {}
for name in sources:
    target = OUT / 'source' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, target)
    pins[name] = hashlib.sha256(target.read_bytes()).hexdigest()
(OUT / 'software-controls-receipt.json').write_text(json.dumps({
    'schema': 'optic_neuro_blender.pilot_gate_controls.v1', 'exit_code': result.returncode,
    'test_count': 66, 'new_supervisor_audit_controls': 16, 'command': cmd,
    'source_sha256': pins, 'prerequisite_contract_commit': '308cd0260528683ea6ca49dbf5042cd8414e5993',
    'frozen_pilot_executed': False, 'synthetic_local_ledgers_only': True,
    'external_registration_obtained': False, 'human_exception_received': False}, indent=2) + '\n', encoding='utf-8')
shutil.copyfile(Path(__file__), OUT / 'archive_evidence_source.py')
files = sorted([p for p in OUT.rglob('*') if p.is_file()])
index = {'schema': 'optic_neuro_blender.pilot_supervisor_artifact_index.v1', 'file_count': len(files),
    'files': [{'path': p.relative_to(OUT).as_posix(), 'bytes': p.stat().st_size,
               'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
    'frozen_pilot_executed': False}
(OUT / 'artifact_index.json').write_text(json.dumps(index, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'files': len(files), 'controls': 66, 'frozen_pilot_executed': False}))
