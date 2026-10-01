"""Synthetic contract fixtures only. Never native execution or GPU admission."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Blender/benchmarks/capacity_audit'))
import axial_native_evidence_contract_v1 as m

PLAN, PINS = m.load_contract()


def fixture():
    origin = 'synthetic_contract_fixture'
    job = 'contract-fixture-NOT-a-GPU-job'
    backend = {'kind': 'GPU_ALU_digital', 'backend_model': 'scene_mixed_precision_reference_v1',
               'work_origin': 'scene_traversal_not_compiled_U_GEMM_or_expected_lookup',
               'api': 'SYNTHETIC', 'device_id': 'NO-GPU', 'runner_id': 'fixture',
               'code_sha256': {'synthetic_not_backend.py': '0'*64}}
    common = {'job_id': job, 'evidence_kind': origin, 'work_contract_sha256': m.digest(PLAN)}
    artifacts = {'backend': dict(common, effective_backend=backend)}
    artifacts['readback'] = dict(common, effective_cases={n: {k: v for k, v in c.items()
            if not k.startswith('expected_')} for n, c in PLAN['cases'].items()},
            case_outputs={n: {k: v for k, v in c.items() if k.startswith('expected_')}
                          for n, c in PLAN['cases'].items()}, raw_readback_retained=True,
            backend_artifact_sha256=m.digest(artifacts['backend']))
    artifacts['guard'] = dict(common, backend_artifact_sha256=m.digest(artifacts['backend']),
            readback_artifact_sha256=m.digest(artifacts['readback']), status='completed',
            child_exit_code=0, reasons=[], child_start_utc='2026-10-01T18:40:00+00:00',
            child_end_utc='2026-10-01T18:40:01+00:00',
            recorded_deadline_utc='2026-10-01T18:42:00+00:00', timeout_s=120, job_kind='pilot',
            declared_policy=deepcopy(m.GUARD_POLICY), operational_scope='recorded_content_only_not_live_admission')
    artifacts['cost_ledger'] = dict(common, backend_artifact_sha256=m.digest(artifacts['backend']),
            readback_artifact_sha256=m.digest(artifacts['readback']), regime='cold',
            amortization_runs=1, total_wall_ns=len(m.COMPONENTS)+1, clock='single_monotonic_ns',
            components=[{'component': k, 'start_ns': i, 'end_ns': i+1, 'status': 'measured', 'reason': ''}
                        for i, k in enumerate(m.COMPONENTS)], observed_sampler_max_RAM_bytes=0,
            observed_sampler_max_GPU_VRAM_bytes=0, upload_bytes=0, readback_bytes=0,
            memory_scope='sampler_maximum_not_global_peak',
            energy={'status': 'unavailable', 'microjoules': None, 'method': 'synthetic no measurement'})
    manifest = {'schema': m.MODEL, 'work_contract': deepcopy(PLAN), 'evidence_kind': origin,
                'job_id': job, 'backend': deepcopy(backend),
                'artifact_sha256': {k: m.digest(v) for k, v in artifacts.items()},
                **{k: False for k in m.FALSE_CLAIMS}}
    return manifest, deepcopy(artifacts)


def rehash(manifest, artifacts):
    manifest['artifact_sha256'] = {k: m.digest(v) for k, v in artifacts.items()}


def reject(fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError, IndexError):
        return
    raise AssertionError('missing fail-closed rejection')


def inspect(manifest=None, artifacts=None):
    if manifest is None:
        manifest, artifacts = fixture()
    return m.inspect_bundle(PLAN, manifest, artifacts)


def positive_content_only():
    out = inspect()
    assert out['content_contract_matched'] and out['synthetic_fixture_only']
    assert not out['declared_native_content_origin']
    assert all(out[k] is False for k in m.FALSE_CLAIMS)
    assert not out['equivalent_runtime_work_certified'] and not out['efficiency_comparison_certified']


def exact_work_and_inputs():
    for field, value in (('scene_binding_sha256', 'foreign'), ('source_order', ['other'])):
        manifest, arts = fixture()
        arts['readback']['effective_cases']['positive'][field] = value
        rehash(manifest, arts)
        reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    del manifest['work_contract']['cases']['negative']
    reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    arts['readback']['case_outputs']['two_sources']['expected_port_outputs']['D']['port_power_uint64'] = 1
    rehash(manifest, arts)
    reject(lambda: inspect(manifest, arts))


def gates_caps_types():
    for value in (True, 1):
        manifest, arts = fixture()
        arts['readback']['case_outputs']['two_sources']['expected_stage_gates']['REFERENCE-REDUCTION'] = value
        rehash(manifest, arts)
        reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    arts['readback']['effective_cases']['positive']['explicit_group_contract']['limits']['field_L1'] = [1, 1]
    rehash(manifest, arts)
    reject(lambda: inspect(manifest, arts))
    reject(lambda: m.exact([True, 1], [1, 1], 'no bool/int alias'))


def backend_and_origin():
    for key, value in (('kind', 'RT'), ('kind', 'Bpyfloat32'),
                       ('work_origin', 'compiled_U_GEMM'), ('backend_model', 'legacy_probe')):
        manifest, arts = fixture()
        manifest['backend'][key] = value
        reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    arts['backend']['evidence_kind'] = 'retained_native_content'
    rehash(manifest, arts)
    reject(lambda: inspect(manifest, arts))


def fingerprint_and_receipts():
    manifest, arts = fixture()
    manifest['artifact_sha256']['readback'] = '0'*64
    reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    arts['guard']['job_id'] = 'foreign'
    rehash(manifest, arts)
    reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    del arts['guard']
    reject(lambda: inspect(manifest, arts))


def guard_not_admission():
    for key, value in (('recorded_deadline_utc', '2026-09-30T06:00:00+00:00'),
                       ('timeout_s', 121), ('timeout_s', True), ('child_exit_code', False),
                       ('status', 'in_progress'), ('recorded_deadline_utc', 'garbage+00:00')):
        manifest, arts = fixture()
        arts['guard'][key] = value
        rehash(manifest, arts)
        reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    arts['guard']['declared_policy']['fail_closed'] = 1
    rehash(manifest, arts)
    reject(lambda: inspect(manifest, arts))
    for key in m.FALSE_CLAIMS:
        manifest, arts = fixture()
        manifest[key] = True
        reject(lambda: inspect(manifest, arts))


def full_costs():
    for change in (
            lambda x: x['components'].pop(),
            lambda x: x.update(total_wall_ns=0),
            lambda x: x.update(amortization_runs=10),
            lambda x: x.update(upload_bytes=True),
            lambda x: x['energy'].update(microjoules=0),
            lambda x: x['components'][0].update(status='not_applicable', reason=''),
            lambda x: x['components'][0].update(end_ns=999)):
        manifest, arts = fixture()
        change(arts['cost_ledger'])
        rehash(manifest, arts)
        reject(lambda: inspect(manifest, arts))
    manifest, arts = fixture()
    arts['cost_ledger']['components'][0].update(status='not_applicable', end_ns=0,
                                               reason='queue wait excluded from fixture only')
    rehash(manifest, arts)
    assert inspect(manifest, arts)['cost_coverage_content_checked']


def byte_receipts():
    manifest, arts = fixture()
    raw = {str(ROOT / ('fixture-' + k + '.json')): json.dumps(v, sort_keys=True).encode()
           for k, v in arts.items()}
    paths = {k: str(ROOT / ('fixture-' + k + '.json')) for k in arts}
    manifest['artifact_byte_sha256'] = {k: m.sha(raw[p]) for k, p in paths.items()}
    manifest_path = str(ROOT / 'fixture-manifest.json')
    raw[manifest_path] = json.dumps(manifest, sort_keys=True).encode()
    original = Path.read_bytes
    with patch.object(Path, 'read_bytes', lambda p: raw[str(p)] if str(p) in raw else original(p)):
        result, pins = m.inspect_files(manifest_path, paths)
        assert result['synthetic_fixture_only'] and len(pins) == 151
        raw[paths['readback']] += b' '
        reject(lambda: m.inspect_files(manifest_path, paths))
    fake = deepcopy(PLAN)
    fake['work']['source_IDs'] = 1
    manifest, arts = fixture()
    reject(lambda: m.inspect_bundle(fake, manifest, arts))


def historical_and_json():
    native = m.parse((ROOT / 'D:/PROJECTS/.cognition/neuro3d/exp005_shared_native_20260930_0337.json').read_bytes())
    guard = m.parse((ROOT / 'D:/PROJECTS/.cognition/neuro3d/exp005_shared_guard_20260930_0337.json').read_bytes())
    reject(lambda: inspect(native, {'guard': guard}))
    reject(lambda: m.parse('{"x":1,"x":2}'))
    reject(lambda: m.parse('{"x":Infinity}'))


TESTS = (positive_content_only, exact_work_and_inputs, gates_caps_types, backend_and_origin,
         fingerprint_and_receipts, guard_not_admission, full_costs, byte_receipts, historical_and_json)
if __name__ == '__main__':
    for test in TESTS:
        test()
    manifest, arts = fixture()
    print(json.dumps({'PASS': True, 'tests': len(TESTS), 'plan': PLAN, 'pins': PINS,
                      'synthetic_bundle': {'manifest': manifest, 'artifacts': arts},
                      'synthetic_result': inspect(manifest, arts),
                      'historical0337_contract_rejected': True,
                      'new_arithmetic_nodes': 0, 'GPU_executed': False,
                      'production_modules_imported': False}, sort_keys=True, allow_nan=False))
