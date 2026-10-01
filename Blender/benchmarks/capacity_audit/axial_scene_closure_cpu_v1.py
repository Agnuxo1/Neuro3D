"""Offline retained-chain provenance checks; never a GPU admission gate.

No production geometry/arithmetic imports, process launch, telemetry or writers.
Content hashes identify local evidence, NOT cryptographic runtime authentication.
"""
import base64
import hashlib
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'axial-retained-scene-chain-provenance-offline-v1'
STAGES = ('WORDS', 'QUOTIENT', 'UNIT', 'SOURCE', 'REDUCTION')
HASHES = (
    'dfdb03a27f7aaa58dd05d750ea1980de789281ed798b75fd2c5209d12712a5fa',
    'a16fd247a6aca8dd71796f0ee84bddb5efb7a7c439df7b644066e57c2772ab8b',
    '525e7dc3fe7ffb2971390a0cc4034dafe07fd585d64f040223ac8b4ede5ef1cb',
    '75b6c5dd33596707875e228acd032997c15b7045c9eac5bde8237831207e8d5e',
    '61220e4c1460d1b867064745d1ac7fbde53faf7d9b160d7e5d2c15dd6fba9f10')
NAMES = ('positive', 'negative', 'thin_resolved', 'thin_collapsed_FAIL',
         'source_contact_FAIL', 'otherowner_contact_FAIL', 'boundary_FAIL',
         'nonexact_geometry_phase_PASS', 'nonexact_geometry_phase_FAIL',
         'declared_radius_PASS', 'declared_contact_FAIL', 'lambda_transport_FAIL',
         'two_sources')
DECLARATION = 'explicit CPU coherence hypothesis; not measured scene/native/physical coherence'
CAPS = {'field_L1': [1, 10**12], 'power': [1, 10**12],
        'relative_field': [1, 10**6], 'relative_power': [1, 10**6]}
ARTIFACTS = {
    'native0337': ('D:/PROJECTS/.cognition/neuro3d/exp005_shared_native_20260930_0337.json',
                   'ca23f606478b3c5897c141ab80f877af5ba47aacd572bc527825ac7047c7d5b3'),
    'guard0337': ('D:/PROJECTS/.cognition/neuro3d/exp005_shared_guard_20260930_0337.json',
                  '1c41d8042ba07cde611b259b9f490d117a8fbb096c2c1aca5fd8abc40652c6bb'),
    'audit0340': ('D:/PROJECTS/.cognition/neuro3d/exp005_shared_audit_20260930_0340.json',
                  'c9a31f7308c4905fd8f9857a871cc5301ad2d18438d4a9af54d0a77b91727dd3'),
    'supervisorCPU': ('coordinacion/respuestas/PHASE-SCALAR-SUPERVISOR-001-CODEX.json',
                      'bb280b865f8635493cbcb75ba0b084a6a7007f3a6b21c3a47cd5993565713913'),
    'captureCPU': ('coordinacion/respuestas/PHASE-SIGNED-NATIVE-CAPTURE-002-CODEX.json',
                   'd41d777e20e6d164bd3ff91072f5a5252ea4bdf18850008be71acad56aede487')}
FALSE_FLAGS = ('GPU_executed', 'ALU_executed', 'execution_authenticated',
               'accepted_full_field_pipeline', 'native_promotion_allowed')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'),
                          allow_nan=False).encode())


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def parse(data):
    def invalid_constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=unique_pairs,
                      parse_constant=invalid_constant)


def pinned(path, expected):
    data = (ROOT / path).read_bytes()
    require(sha(data) == expected, 'retained file SHA mismatch: ' + path)
    return data


def flag(record, key):
    value = record[key]
    require(type(value) is bool, 'exact bool required: ' + key)
    return value


def rational_cap(value):
    require(type(value) is list and len(value) == 2 and
            all(type(x) is int for x in value) and value[0] >= 0 and value[1] > 0,
            'finite nonnegative rational cap required')
    return value


def load_retained():
    reports = {}
    chain = {}
    pins = {}
    for stage, expected in zip(STAGES, HASHES):
        path = 'coordinacion/respuestas/AXIAL-GEOMETRY-' + stage + '-001-CODEX.json'
        r = parse(pinned(path, expected))
        require(r['id'] == 'AXIAL-GEOMETRY-' + stage + '-001', 'report ID mismatch')
        for key in FALSE_FLAGS:
            require(flag(r, key) is False, 'unexpected runtime/full-pipeline claim')
        run = r['test_run']
        require(type(run['rc']) is int and run['rc'] == 0, 'retained test status')
        raw = zlib.decompress(base64.b64decode(run['stdout_zlib_base64'], validate=True))
        require(len(raw) == run['stdout_bytes'] and sha(raw) == run['stdout_sha256'],
                'retained raw payload fingerprint')
        body = parse(raw)
        chain[stage] = body['cases'] if stage == 'WORDS' else body['audit']['cases']
        reports[stage] = r
        pins[path] = expected
        for name, h in r['code_doc_sha256'].items():
            require(name not in pins or pins[name] == h, 'conflicting frozen fingerprint')
            pins[name] = h
    for name, h in pins.items():
        pinned(name, h)
    for i in range(1, len(STAGES)):
        previous = reports[STAGES[i]]['previous_report']
        require(previous == {'path': 'coordinacion/respuestas/AXIAL-GEOMETRY-' +
                             STAGES[i-1] + '-001-CODEX.json', 'sha256': HASHES[i-1]},
                'report-level predecessor mismatch')
    artifacts = {name: parse(pinned(path, h)) for name, (path, h) in ARTIFACTS.items()}
    pins.update({p: h for p, h in ARTIFACTS.values()})
    return chain, artifacts, pins


def validate_cases(chain):
    """Validate frozen scope, exact coverage and predecessor links, not arithmetic."""
    require(set(chain) == set(STAGES), 'complete explicit stages required')
    for stage in STAGES:
        require(type(chain[stage]) is dict and set(chain[stage]) == set(NAMES),
                'complete frozen case coverage required: ' + stage)
    result = {}
    for name in NAMES:
        g, q, u, s, r = [chain[stage][name] for stage in STAGES]
        snapshot = g['scene_snapshot']
        abi = g['word_ABI']
        ids = [v['id'] for v in snapshot['sources']]
        require(ids and len(ids) == len(set(ids)) and
                all(type(v) is str and v for v in ids), 'unique source IDs required')
        require(ids == abi['source_order'] == s['source_order'], 'source order mismatch')
        # These snapshots are a restricted axial mirror->detector profile.
        # We do NOT infer a complete general BS/history tree from this profile.
        require(snapshot['schema'] == 'exp005-readback-v2' and
                snapshot['undeclared_meshes'] == [] and
                set(snapshot['objects']) == {'M', 'D'} and
                snapshot['objects']['M']['kind'] == 'mirror' and
                snapshot['objects']['D']['kind'] == 'det' and
                snapshot['objects']['M']['phase_rad'] == 0, 'frozen axial profile mismatch')
        require(abi['object_ids'] == ['M', 'D'], 'global primitive object order mismatch')
        binding = digest({'snapshot': snapshot, 'object_order': abi['object_ids'],
                          'source_order': ids})
        require(binding == abi['original_scene_binding_sha256'], 'original scene binding mismatch')
        require(digest(abi) == g['word_ABI_sha256'] == q['word_ABI_sha256'], 'word ABI link mismatch')
        for c in (q, u, s, r):
            require(c['original_scene_binding_sha256'] == binding, 'cross-stage binding mismatch')
        for c, key, prev in ((q, 'geometry_case_sha256', g),
                             (u, 'geometry_bridge_case_sha256', q),
                             (s, 'retained_unit_case_sha256', u),
                             (r, 'source_product_case_sha256', s)):
            require(c[key] == digest(prev), 'cross-stage case digest mismatch: ' + key)
        rows = [g['sources'], q['paths'], u['paths'], s['paths']]
        for stage_rows in rows:
            require([v['source_id'] for v in stage_rows] == ids, 'ordered path coverage mismatch')
        gates = [flag(g, 'accepted_geometry_words_CPU_only'),
                 flag(g, 'accepted_phase_budget_CPU_only'),
                 flag(q, 'accepted_bridge_phase_CPU_only'),
                 flag(u, 'accepted_unit_CPU_only'),
                 flag(s, 'accepted_source_product_absolute_CPU_only'),
                 flag(r, 'accepted_reduction_detector_CPU_only')]
        for case_gate, stage_rows, key in (
                (gates[0], rows[0], 'accepted_geometry_words_CPU_only'),
                (gates[1], rows[0], 'accepted_phase_budget_CPU_only'),
                (gates[2], rows[1], 'accepted_bridge_phase_CPU_only'),
                (gates[3], rows[2], 'accepted_unit_CPU_only'),
                (gates[4], rows[3], 'accepted_source_product_absolute_CPU_only')):
            require(case_gate == all(flag(p, key) for p in stage_rows),
                    'case/path aggregate gate mismatch: ' + key)
        for c, key, value in ((q, 'previous_geometry_accepted', gates[0]),
                              (q, 'previous_phase_accepted', gates[1]),
                              (u, 'previous_bridge_phase_accepted', gates[2]),
                              (r, 'previous_source_product_accepted', gates[4])):
            require(flag(c, key) == value, 'predecessor gate mismatch: ' + key)
        require(not any(gates[i] and not all(gates[:i]) for i in range(1, 6)),
                'downstream cannot revive retained rejection')
        for gp, qp, up, sp in zip(*rows):
            pg = flag(gp, 'accepted_geometry_words_CPU_only')
            pp = flag(gp, 'accepted_phase_budget_CPU_only')
            pq = flag(qp, 'accepted_bridge_phase_CPU_only')
            pu = flag(up, 'accepted_unit_CPU_only')
            ps = flag(sp, 'accepted_source_product_absolute_CPU_only')
            require(flag(qp, 'previous_geometry_accepted') == pg and
                    flag(qp, 'previous_phase_accepted') == pp and
                    flag(up, 'previous_bridge_phase_accepted') == pq,
                    'path predecessor gate mismatch')
            require(not (pp and not pg or pq and not pp or pu and not pq or ps and not pu),
                    'path cannot revive retained rejection')
            require(flag(sp, 'previous_unit_accepted') == flag(up, 'accepted_unit_CPU_only'),
                    'path unit gate mismatch')
            require(rational_cap(sp['field_absolute_L1_budget']) == CAPS['field_L1'],
                    'frozen path cap mismatch')
            refs = [p['phase_reference_id'] for p in (gp, qp, up, sp) if 'phase_reference_id' in p]
            for p, accepted in ((gp, pg), (qp, pq), (up, pu), (sp, ps)):
                require(not accepted or 'phase_reference_id' in p,
                        'accepted path requires original phase gauge')
            for p, accepted in ((gp, pg), (qp, pq), (up, pu)):
                require(not accepted or 'phase_budget_rad' in p,
                        'accepted path requires original phase budget')
            require(all(ref == 'original-source-zero:' + binding + ':' + gp['source_id']
                        for ref in refs), 'original source phase gauge mismatch')
            budgets = [p['phase_budget_rad'] for p in (gp, qp, up) if 'phase_budget_rad' in p]
            require(not budgets or all(rational_cap(b) == budgets[0] for b in budgets),
                    'original phase budget mismatch')
        contract = r['contract']
        require(contract['scene_binding_sha256'] == binding and
                contract['grouping_provenance'] == DECLARATION, 'explicit CPU group hypothesis required')
        require(set(contract['limits']) == set(CAPS) and
                all(rational_cap(contract['limits'][k]) == CAPS[k] for k in CAPS),
                'frozen predeclared group caps mismatch')
        assignments = contract['assignments']
        require([v['source_id'] for v in assignments] == ids, 'group assignment coverage mismatch')
        for a in assignments:
            group = a['coherence_group']
            require(type(group) is str and 0 < len(group) <= 64 and a['port'] == 'D' and
                    a['source_phase_reference_id'] == 'original-source-zero:' + binding + ':' + a['source_id'] and
                    a['common_phase_reference_id'] == 'declared-common-source-gauge:' + binding + ':' + group,
                    'group source/port/reference mismatch')
        require(flag(r, 'coherence_authenticated') is False and
                flag(r, 'accepted_full_field_pipeline') is False, 'hypothesis is not authentication')
        require(flag(r, 'scene_field_reduced') == gates[4] and
                flag(r, 'detector_evaluated') == gates[4], 'evaluation/previous gate mismatch')
        if gates[4]:
            require(set(r['ports']) == {'D'}, 'exact detector port coverage required')
            groups = r['ports']['D']['groups']
            require(set(groups) == {a['coherence_group'] for a in assignments}, 'group coverage mismatch')
            for key, group in groups.items():
                expected_ids = [a['source_id'] for a in assignments if a['coherence_group'] == key]
                require(group['source_ids'] == expected_ids ==
                        [step['source_id'] for step in group['steps']], 'ordered reduced source coverage mismatch')
                require(group['common_phase_reference_id'] ==
                        'declared-common-source-gauge:' + binding + ':' + key, 'reduced group gauge mismatch')
        else:
            require(r['ports'] == {}, 'rejected upstream has no evaluated detector')
        result[name] = {'scene_binding_sha256': binding, 'source_ids': ids,
                        'stage_gates_retained': gates,
                        'offline_identity_coverage_checked': True,
                        'numerical_chain_partial_CPU_only': all(gates),
                        'complete_history_tree_certified': False,
                        'terminal_modes_certified': False,
                        'coherence_authenticated': False,
                        'accepted_full_field_pipeline': False}
    return result


def inventory(artifacts):
    require(set(artifacts) == set(ARTIFACTS), 'explicit existing artifact inventory required')
    n, g, a = [artifacts[k] for k in ('native0337', 'guard0337', 'audit0340')]
    require(flag(n, 'passed') and flag(a, 'passed'), 'historical retained probe status')
    require(a['runtime_report_sha256'] == ARTIFACTS['native0337'][1], 'historical audit link')
    require(type(g['exit_code']) is int and g['exit_code'] == 0 and
            g['status'] == 'completed' and g['reasons'] == [], 'historical guard status')
    require(g['deadline_utc'] == '2026-09-30T06:00:00+00:00', 'historical deadline immutable')
    for k in ('supervisorCPU', 'captureCPU'):
        v = artifacts[k]
        require(type(v['returncode']) is int and v['returncode'] == 0, 'historical CPU status')
        for key in ('GPU_executed', 'runtime_execution_authenticated', 'native_promotion_allowed'):
            require(flag(v, key) is False, 'CPU artifact cannot become native authentication')
    return {
        'historical_native0337': {'retained_passed': True, 'probes': len(n['cases']),
            'blend_files': sorted(n['input_scene_sha256']),
            'backend': n['backend'], 'scope': n['scope'],
            'current_RN64_scene_chain_binding_present': False,
            'reason': 'K3/K4 blend inventory and legacy GPU ALU probes; no current 13-case RN64 chain binding'},
        'historical_guard0337': {'retained_completed': True, 'deadline_utc': g['deadline_utc'],
            'samples': len(g['samples']), 'fresh_job_admission': False,
            'reason': 'closed historical deadline/resources; not a new reservation or telemetry'},
        'supervisor_and_capture': {'retained_CPU_tests_only': True,
            'runtime_execution_authenticated': False, 'current_scene_chain_bound': False},
        'native_promotion_allowed': False, 'GPU_job_admission': False,
        'equal_work_full_cost_comparison_certified': False}


def audit():
    chain, artifacts, pins = load_retained()
    cases = validate_cases(chain)
    return {'model': MODEL, 'pins': pins, 'cases': cases, 'existing_artifacts': inventory(artifacts),
            'counts': {'cases': len(cases), 'sources': sum(len(c['source_ids']) for c in cases.values()),
                       'retained_upstream_stops': sum(not c['stage_gates_retained'][4] for c in cases.values()),
                       'retained_partial_numerical_chains': sum(c['numerical_chain_partial_CPU_only'] for c in cases.values())},
            'new_geometry_phase_field_arithmetic_operations': 0,
            'production_modules_imported': False, 'retained_writers_executed': False,
            'GPU_executed': False, 'execution_authenticated': False,
            'accepted_full_field_pipeline': False, 'native_promotion_allowed': False,
            'pending': ['complete scene-bound history/terminal-mode evidence',
                        'native equivalent geometry/phase/source/group/detector model and effective ABI',
                        'authenticated execution lineage (content SHA alone is not authenticity)',
                        'explicit coherence provenance; current grouping is CPU hypothesis',
                        'new guarded exclusive job with live telemetry and reservation',
                        'equal-work/equal-output protocol with all costs']}
