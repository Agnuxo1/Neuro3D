"""Offline native-evidence content contract; no execution or admission.

Positive synthetic tests certify schema relationships only, never native work.
A matching content bundle is not runtime authentication or physical coherence.
"""
import base64
import hashlib
import json
from pathlib import Path
from datetime import datetime
import zlib

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'axial-fixed-reference-native-evidence-content-contract-v1'
CLOSURE = 'coordinacion/respuestas/AXIAL-REFERENCE-CLOSURE-001-CODEX.json'
PLAN_SHA = '472ac95b0a30c1bd1674223fc3ab563323cd14590bc4091af494d1d1e412fdb1'
CLOSURE_SHA = '5875def25bf8a3cf3454bef1751dee7573e884fd2f3ccd96cc97de10d325597b'
STAGES = ('GEOMETRY-WORDS', 'TERMINAL-REFERENCE', 'TREE-COMPLETENESS',
          'REFERENCE-QUOTIENT', 'REFERENCE-ARGUMENT', 'REFERENCE-UNIT',
          'REFERENCE-SOURCE', 'REFERENCE-REDUCTION')
COMPONENTS = ('queue_wait', 'export', 'input_validation', 'compile', 'acceleration_build',
              'upload', 'scene_geometry', 'reference_phase', 'source_products',
              'group_detector', 'readback', 'output_validation', 'guard_overhead')
ARTIFACTS = ('backend', 'readback', 'guard', 'cost_ledger')
GUARD_POLICY = {'fail_closed': True, 'RAM_free_after_budget_min_bytes': 4*2**30,
                'VRAM_total_max_bytes': 18*2**30, 'temperature_max_C': 80,
                'bytes_per_cell_min': 1024, 'margins_and_temporaries_included': True,
                'exclusive_job_reservation_required': True}
FALSE_CLAIMS = ('execution_authenticated', 'coherence_authenticated',
                'native_promotion_allowed', 'accepted_full_field_pipeline',
                'GPU_job_admission')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def parse(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def invalid(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def payload(report):
    run = report['test_run']
    require(type(run['rc']) is int and run['rc'] == 0, 'retained test status')
    raw = zlib.decompress(base64.b64decode(run['stdout_zlib_base64'], validate=True))
    require(sha(raw) == run['stdout_sha256'] and len(raw) == run['stdout_bytes'], 'raw byte fingerprint')
    return parse(raw)


def exact(actual, expected, reason):
    # Canonical JSON distinguishes bool/int/float, unlike Python ==.
    require(digest(actual) == digest(expected), reason)


def nonnegative_int(value, reason):
    require(type(value) is int and value >= 0, reason)
    return value


def bounded_text(value):
    require(type(value) is str and 0 < len(value) <= 128 and
            all(c.isalnum() or c in '._:-' for c in value), 'bounded identifier')
    return value


def hash_text(value):
    require(type(value) is str and len(value) == 64 and
            all(c in '0123456789abcdef' for c in value), 'lowercase SHA256')
    return value


def load_contract():
    raw = (ROOT / CLOSURE).read_bytes()
    require(sha(raw) == CLOSURE_SHA, 'frozen referenced closure SHA')
    closure = parse(raw)
    pins = dict(closure['code_doc_sha256'])
    pins[CLOSURE] = CLOSURE_SHA
    for name, h in pins.items():
        require(sha((ROOT / name).read_bytes()) == h, 'changed frozen input: ' + name)
    closed = payload(closure)['audit']
    chain = {}
    models = {}
    for stage in STAGES:
        path = 'coordinacion/respuestas/AXIAL-' + stage + '-001-CODEX.json'
        report = parse((ROOT / path).read_bytes())
        require(report['id'] == 'AXIAL-' + stage + '-001', 'stage ID')
        body = payload(report)
        chain[stage] = body['cases'] if stage in (STAGES[0], STAGES[2]) else body['audit']['cases']
        models[stage] = report['model']
    require(all(set(v) == set(closed['cases']) for v in chain.values()), 'exact case coverage')
    cases = {}
    for name, c in closed['cases'].items():
        g, ref, tree, q, a, u, s, r = [chain[k][name] for k in STAGES]
        require(c['case_digests'] == {k: digest(chain[k][name]) for k in STAGES}, 'closure case links')
        unitpaths = {p['source_id']: p for p in u['paths']}
        sourcepaths = {p['source_id']: p for p in s['paths']}
        outputs = []
        for sid in c['source_ids']:
            up, sp = unitpaths[sid], sourcepaths[sid]
            outputs.append({'source_id': sid, 'unit_uint64': up.get('unit_uint64'),
                            'source_limb_uint32': sp.get('source_limb_uint32'),
                            'field_uint64': sp.get('measurement', {}).get('output_uint64')})
        ports = {port: {'group_field_uint64': {key: v['output_uint64'] for key, v in p['groups'].items()},
                        'group_power_uint64': {key: v['detector']['output_uint64'] for key, v in p['groups'].items()},
                        'port_power_uint64': p['observed_power_uint64']} for port, p in r['ports'].items()}
        cases[name] = {
            'scene_binding_sha256': c['scene_binding_sha256'],
            'original_snapshot_sha256': digest(g['scene_snapshot']),
            'case_dependency_sha256': c['case_digests'],
            'source_order': c['source_ids'],
            'effective_geometry_word_ABI': g['word_ABI'],
            'word_ABI_sha256': c['word_ABI_sha256'],
            'effective_reference': {'frame': ref['reference_frame'], 'model': ref['reference_model'],
                'origin_BU': ref['terminal_mode_origin_BU'], 'direction': ref['terminal_mode_direction'],
                'HOST_reference_ABI': ref.get('reference_ABI')},
            'original_path_phase_caps': {p['source_id']: p.get('phase_budget_rad') for p in g['sources']},
            'explicit_group_contract': r['contract'],
            'expected_stage_gates': c['retained_stage_gates'],
            'expected_original_phase_gate': c['retained_phase_gate'],
            'legacy_gates_UNCHANGED': c['legacy_gates_UNCHANGED'],
            'expected_source_outputs': outputs, 'expected_port_outputs': ports,
            'restricted_tree_certificate_sha256': tree.get('certificate_sha256')}
    plan = {'schema': MODEL, 'closure_report_sha256': CLOSURE_SHA,
            'observable': 'all ordered source fields and grouped detector powers at fixed ORIGINAL plane reference',
            'arithmetic_policy': 'same retained mixed HOST-hi-lo32/signed512/signed256/RN64 models; bit-exact contract, no GEMM/lookup substitution',
            'stage_models': models, 'cases': cases,
            'work': {'cases': 13, 'source_IDs': 14, 'restricted_trees': 9,
                     'primitive_partition_rows': 72, 'source_product_cases': 5,
                     'partial_CPU_gate_cases': 4, 'sampling': 'full frozen case set; no center/output resampling'},
            'grouping_provenance': 'explicit CPU grouping hypothesis; not scene/native/physical coherence authentication',
            'cost_components': list(COMPONENTS),
            'scope': 'content matching only; SHA alone not authenticated scene execution'}
    require(digest(plan) == PLAN_SHA, 'frozen whole-work contract identity')
    return plan, pins


def validate_ledger(ledger):
    require(ledger['regime'] in ('cold', 'warm') and type(ledger['regime']) is str, 'explicit cold/warm regime')
    runs = nonnegative_int(ledger['amortization_runs'], 'explicit amortization')
    require(runs > 0 and (ledger['regime'] != 'cold' or runs == 1), 'cold cannot amortize silently')
    wall = nonnegative_int(ledger['total_wall_ns'], 'whole-job wall clock')
    require(wall > 0 and ledger['clock'] == 'single_monotonic_ns', 'single clock domain')
    rows = ledger['components']
    require(type(rows) is list and [v['component'] for v in rows] == list(COMPONENTS), 'complete ordered costs')
    for row in rows:
        start = nonnegative_int(row['start_ns'], 'component start')
        stop = nonnegative_int(row['end_ns'], 'component stop')
        require(start <= stop <= wall, 'cost span inside full wall; overlaps not summed')
        require(type(row['status']) is str and row['status'] in ('measured', 'not_applicable'), 'cost provenance')
        if row['status'] == 'not_applicable':
            require(type(row['reason']) is str and bool(row['reason'].strip()) and start == stop,
                    'explicit justified zero N/A, never missing cost')
        else:
            require(stop > start and row['reason'] == '', 'positive measured span')
    for key in ('observed_sampler_max_RAM_bytes', 'observed_sampler_max_GPU_VRAM_bytes', 'upload_bytes', 'readback_bytes'):
        nonnegative_int(ledger[key], 'explicit full resource/transfer counts')
    require(ledger['memory_scope'] == 'sampler_maximum_not_global_peak', 'memory metrology scope')
    energy = ledger['energy']
    require(energy['status'] in ('measured', 'unavailable'), 'energy provenance')
    if energy['status'] == 'measured':
        nonnegative_int(energy['microjoules'], 'measured energy unit')
        require(type(energy['method']) is str and bool(energy['method'].strip()), 'energy measurement method')
    else:
        require(energy['microjoules'] is None and type(energy['method']) is str and
                bool(energy['method'].strip()), 'unknown energy is not zero')
    return {'cost_coverage_content_checked': True, 'regime': ledger['regime'],
            'energy_measurement_present': energy['status'] == 'measured',
            'hardware_costs_authenticated': False, 'efficiency_comparison_certified': False}


def inspect_bundle(plan, manifest, artifacts):
    """Pure JSON inspection. Do not dispatch, reserve, admit, write or authenticate."""
    require(digest(plan) == PLAN_SHA, 'caller cannot substitute work contract')
    require(manifest['schema'] == MODEL, 'no legacy/native-probe schema substitution')
    exact(manifest['work_contract'], plan, 'scene/work/reference/effective ABI mismatch')
    kind = manifest['evidence_kind']
    require(type(kind) is str and kind in ('synthetic_contract_fixture', 'retained_native_content'),
            'explicit evidence origin')
    job = bounded_text(manifest['job_id'])
    backend = manifest['backend']
    require(backend['kind'] == 'GPU_ALU_digital' and backend['backend_model'] == 'scene_mixed_precision_reference_v1' and
            backend['work_origin'] == 'scene_traversal_not_compiled_U_GEMM_or_expected_lookup',
            'no CPU/Bpy/RT/optical/GEMM substitute for scene ALU model')
    bounded_text(backend['api'])
    bounded_text(backend['device_id'])
    bounded_text(backend['runner_id'])
    require(type(backend['code_sha256']) is dict and backend['code_sha256'], 'explicit compiled source pins')
    for name, h in backend['code_sha256'].items():
        bounded_text(name)
        hash_text(h)
    for key in FALSE_CLAIMS:
        require(manifest[key] is False, 'content cannot assert auth/promotion/admission')
    require(type(artifacts) is dict and set(artifacts) == set(ARTIFACTS) and
            set(manifest['artifact_sha256']) == set(ARTIFACTS), 'all backend/readback/guard/cost receipts')
    worksha = digest(plan)
    for name in ARTIFACTS:
        artifact = artifacts[name]
        require(digest(artifact) == manifest['artifact_sha256'][name], 'artifact content fingerprint: ' + name)
        require(artifact['job_id'] == job and artifact['work_contract_sha256'] == worksha,
                'same job/work content lineage: ' + name)
        require(artifact['evidence_kind'] == kind, 'synthetic/native origin cannot mix')
    exact(artifacts['backend']['effective_backend'], backend, 'recorded backend/compiler model')
    readback = artifacts['readback']
    exact(readback['effective_cases'], {name: {k: v for k, v in c.items()
          if not k.startswith('expected_')} for name, c in plan['cases'].items()}, 'effective dispatch scene inputs')
    exact(readback['case_outputs'], {name: {k: v for k, v in c.items()
          if k.startswith('expected_')} for name, c in plan['cases'].items()}, 'all original outputs/gates; no resampling')
    require(readback['backend_artifact_sha256'] == manifest['artifact_sha256']['backend'] and
            readback['raw_readback_retained'] is True, 'mandatory raw/readback backend lineage')
    guard = artifacts['guard']
    require(guard['backend_artifact_sha256'] == manifest['artifact_sha256']['backend'] and
            guard['readback_artifact_sha256'] == manifest['artifact_sha256']['readback'] and
            guard['status'] == 'completed' and type(guard['child_exit_code']) is int and
            guard['child_exit_code'] == 0 and guard['reasons'] == [], 'completed same-child content record')
    # Recorded job deadline is evidence only. Never freshness/live telemetry/reservation admission.
    stamps = []
    for key in ('child_start_utc', 'child_end_utc', 'recorded_deadline_utc'):
        value = guard[key]
        require(type(value) is str and value.endswith('+00:00'), 'explicit UTC job timestamps')
        stamp = datetime.fromisoformat(value)
        require(stamp.utcoffset().total_seconds() == 0, 'UTC clock domain')
        stamps.append(stamp)
    start, end, deadline = stamps
    timeout = nonnegative_int(guard['timeout_s'], 'bounded recorded child timeout')
    require(type(guard['job_kind']) is str and guard['job_kind'] in ('pilot', 'child') and
            0 < timeout <= (120 if guard['job_kind'] == 'pilot' else 600) and
            start <= end <= deadline and (end-start).total_seconds() <= timeout,
            'recorded job completed within new job deadline/timeout')
    exact(guard['declared_policy'], GUARD_POLICY, 'immutable fail-closed resource policy')
    require(guard['operational_scope'] == 'recorded_content_only_not_live_admission',
            'recorded content not current authorization')
    costs = artifacts['cost_ledger']
    require(costs['backend_artifact_sha256'] == manifest['artifact_sha256']['backend'] and
            costs['readback_artifact_sha256'] == manifest['artifact_sha256']['readback'], 'cost work lineage')
    result = validate_ledger(costs)
    result.update({'content_contract_matched': True, 'evidence_kind': kind,
                   'synthetic_fixture_only': kind == 'synthetic_contract_fixture',
                   'declared_native_content_origin': kind == 'retained_native_content',
                   'status': 'content_match_only_pending_external_execution_and_precision_evidence',
                   'equivalent_runtime_work_certified': False})
    result.update({k: False for k in FALSE_CLAIMS})
    return result


def inspect_files(manifest_path, artifact_paths):
    """Read-only exact byte receipt verification; no arbitrary process/producer execution."""
    require(set(artifact_paths) == set(ARTIFACTS), 'explicit artifact paths')
    manifest = parse(Path(manifest_path).read_bytes())
    artifacts = {}
    require(set(manifest['artifact_byte_sha256']) == set(ARTIFACTS), 'all raw byte fingerprints')
    for name, path in artifact_paths.items():
        raw = Path(path).read_bytes()
        require(sha(raw) == manifest['artifact_byte_sha256'][name], 'raw artifact fingerprint')
        artifacts[name] = parse(raw)
    plan, pins = load_contract()
    return inspect_bundle(plan, manifest, artifacts), pins
