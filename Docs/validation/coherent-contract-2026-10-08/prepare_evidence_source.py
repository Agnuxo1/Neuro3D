"""Prepare explicit own-network semantics and archive software-only evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
sys.path.insert(0, str(ROOT))
from Blender.blender_lab.coherent_contract_v1 import SCHEMA, PHASE

CAPTURE = ROOT / 'Docs/validation/blender-lab-capture-2026-10-08/resume01/iris/capture.json'
OLD = ROOT / 'Docs/validation/captured-scalar-ingress-2026-10-08'
WORK = Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/coherent-contract-iris02')
WORK.mkdir(exist_ok=False)
capture = json.loads(CAPTURE.read_text(encoding='utf-8'))
semantics = json.loads((OLD / 'semantics.json').read_text(encoding='utf-8'))
network = capture['state']['network']
contract = {'schema': SCHEMA, 'capture_state_sha256': capture['state_sha256'], 'phase': dict(PHASE),
    'units': {'geometry': 'BU', 'wavelength_BU_hex': semantics['wavelength_BU_hex'],
              'metres_per_BU_hex': capture['state']['units']['scale_length_metres_per_BU_hex'],
              'scale_status': 'SCENE_DISPLAY_SCALE_ONLY', 'reference_power_watt_hex': None},
    'encoding': {'kind': 'EXPLICIT_COMPLEX_FIELDS', 'normalization': 'NONE',
                 'ports': {row['id']: {'coherence_group': 'iris_common_carrier', 'phase_reference': 'iris_common_launch'}
                           for row in network['inputs']}},
    'parameters': {row['id']: {'unit': 'BU', 'role': 'GEOMETRY_COORDINATE'} for row in network['parameters']},
    'detectors': {row['id']: {'object': row['object'], 'measurement': 'NORMALIZED_MODAL_POWER',
                            'field_frame': 'COMMON_LAUNCH_PHASE', 'renormalize': False} for row in network['detectors']}}
CONTRACT = ROOT / 'Docs/research/iris_coherent_contract_v1.json'
if CONTRACT.exists():
    assert json.loads(CONTRACT.read_text(encoding='utf-8')) == contract
else:
    with CONTRACT.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(contract, indent=2) + '\n')
command = [sys.executable, '-X', 'utf8', str(ROOT / 'Tools/admit_coherent_capture_v1.py'), '--capture', str(CAPTURE),
           '--semantics', str(OLD / 'semantics.json'), '--fields', str(OLD / 'fields_admission_only.json'),
           '--contract', str(CONTRACT), '--out', str(WORK / 'admitted.json')]
result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=45, creationflags=subprocess.CREATE_NO_WINDOW)
(WORK / 'cli.stdout').write_bytes(result.stdout)
(WORK / 'cli.stderr').write_bytes(result.stderr)
if result.returncode:
    raise SystemExit(result.returncode)
new = json.loads((WORK / 'admitted.json').read_text(encoding='utf-8'))
old = json.loads((OLD / 'scene.json').read_text(encoding='utf-8'))
added = new.pop('blender_lab_optical_contract')
assert new == old, 'semantic admission must preserve every v1 geometry/source/mode value'
report = {'schema': 'optic_neuro_blender.iris_semantic_admission_check.v1', 'status': 'PASS',
    'command': command, 'exit_code': result.returncode,
    'capture_sha256': hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
    'contract_sha256': hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
    'capture_state_sha256': capture['state_sha256'], 'counts': old['blender_lab_ingress']['counts'],
    'parameter_binding_count': added['parameter_binding_count'], 'detector_count': added['detector_count'],
    'all_original_packet_values_equal': True, 'optical_forward_executed': False,
    'field_certified': False, 'training_executed': False, 'gpu_requested': False,
    'wavelength_metres_is_display_conversion_only': True,
    'pilot_protocol_sha256': hashlib.sha256((OLD / 'pilot_protocol_prepared.json').read_bytes()).hexdigest(),
    'frozen_pilot_executed': False}
(WORK / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
OUT = ROOT / 'Docs/validation/coherent-contract-2026-10-08'
OUT.mkdir(exist_ok=False)
for label, origin in [('bpy01', Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/coherent-contract-bpy01')),
                      ('bpy02', Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/coherent-contract-bpy02')),
                      ('iris-admission01', Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/coherent-contract-iris01')),
                      ('iris-admission02', WORK)]:
    shutil.copytree(origin, OUT / label, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    if label == 'bpy02':
        source = OUT / label / 'source'
        runner = json.loads((origin / 'runner.json').read_text(encoding='utf-8'))
        for name, pin in runner['source_sha256'].items():
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
            assert hashlib.sha256(target.read_bytes()).hexdigest() == pin
        shutil.copyfile(Path(__file__), OUT / 'prepare_evidence_source.py')
for name in ['Blender/blender_lab/coherent_contract_v1.py', 'Tools/admit_coherent_capture_v1.py',
             'Blender/tests/test_coherent_contract_v1.py', 'Blender/benchmarks/capacity_audit/robust_multipath_v1.py']:
    target = OUT / 'source' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, target)
print(json.dumps({k: v for k, v in report.items() if k not in ['command']}))
