"""Opt-in offline closure of the fixed-original-reference chain, not admission.

Only retained JSON/byte fingerprints and identity/coverage/gate relationships.
No numerical producer imports, subprocesses, telemetry, reservations or writers.
A content SHA is not runtime authenticity; CPU grouping remains a hypothesis.
"""
import base64
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'axial-fixed-original-reference-offline-closure-CPU-v1'
STAGES = ('GEOMETRY-WORDS', 'TERMINAL-REFERENCE', 'TREE-COMPLETENESS',
          'REFERENCE-QUOTIENT', 'REFERENCE-ARGUMENT', 'REFERENCE-UNIT',
          'REFERENCE-SOURCE', 'REFERENCE-REDUCTION')
HASHES = (
    'dfdb03a27f7aaa58dd05d750ea1980de789281ed798b75fd2c5209d12712a5fa',
    '806867ae71c97bf352ea2e7552d183e549cfb8f6eb6a14df2aa3e12cb868016b',
    'd895ef448dee2a4bb8657da1b6bd3f36635b91f4b8137ae29d194664c6db7d9e',
    '392cc61542deb189d54762f40e1ffc8da5bfdf08d5a9b34e4b2115e95449c273',
    '7a7e71ac61ffde8a3253a9b5b6880243020d886046a3fd56262992de4174c201',
    '555348ada0093f288e075f8428246ed1a406a7666fd3a8102d3ccb14c1cd1591',
    '58507912b97b88589ce292d22ab88d801578c2d1c69e4abd398ad959afd28d7d',
    '1113b4393372ad9394a14f13adb4e7cebcf387ec2bfc807cff0a21700d82fd4b')
NAMES = ('positive', 'negative', 'thin_resolved', 'thin_collapsed_FAIL',
         'source_contact_FAIL', 'otherowner_contact_FAIL', 'boundary_FAIL',
         'nonexact_geometry_phase_PASS', 'nonexact_geometry_phase_FAIL',
         'declared_radius_PASS', 'declared_contact_FAIL', 'lambda_transport_FAIL',
         'two_sources')
CAPS = {'field_L1': [1, 10**12], 'power': [1, 10**12],
        'relative_field': [1, 10**6], 'relative_power': [1, 10**6]}
DECLARATION = 'explicit CPU grouping hypothesis; not scene/native/physical coherence authentication'
FALSE_FLAGS = ('GPU_executed', 'ALU_executed', 'Bpy_executed', 'RT_executed',
               'execution_authenticated', 'accepted_full_field_pipeline',
               'native_promotion_allowed', 'coherence_authenticated',
               'physical_coherence_verified')
ARTIFACTS = {
    'native0337': ('D:/PROJECTS/.cognition/neuro3d/exp005_shared_native_20260930_0337.json',
                   'ca23f606478b3c5897c141ab80f877af5ba47aacd572bc527825ac7047c7d5b3'),
    'guard0337': ('D:/PROJECTS/.cognition/neuro3d/exp005_shared_guard_20260930_0337.json',
                  '1c41d8042ba07cde611b259b9f490d117a8fbb096c2c1aca5fd8abc40652c6bb')}
GATES = ('accepted_geometry_words_CPU_only', 'accepted_terminal_reference_CPU_only',
         'geometric_tree_complete_restricted_CPU_only', 'accepted_reference_quotient_CPU_only',
         'accepted_argument_CPU_only', 'accepted_unit_CPU_only',
         'accepted_source_absolute_CPU_only', 'accepted_reduction_detector_CPU_only')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def parse(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def flag(record, key):
    value = record[key]
    require(type(value) is bool, 'strict bool required: ' + key)
    return value


def negative_claims(record):
    require(flag(record, 'accepted_full_field_pipeline') is False, 'not full pipeline')
    for key in set(FALSE_FLAGS) | {k for k in record if k.startswith('native_') and k.endswith('_implemented')}:
        if key in record:
            require(flag(record, key) is False, 'unexpected runtime claim: ' + key)


def rat(value):
    require(type(value) is list and len(value) == 2 and
            all(type(v) is int for v in value) and value[1] > 0, 'exact rational pair')
    return F(*value)


def pinned(path, expected):
    raw = (ROOT / path).read_bytes()
    require(sha(raw) == expected, 'frozen byte fingerprint mismatch: ' + path)
    return raw


def payload(report):
    run = report['test_run']
    require(type(run['rc']) is int and run['rc'] == 0, 'retained test status')
    raw = zlib.decompress(base64.b64decode(run['stdout_zlib_base64'], validate=True))
    require(type(run['stdout_bytes']) is int and len(raw) == run['stdout_bytes'] and
            sha(raw) == run['stdout_sha256'], 'retained raw fingerprint')
    return parse(raw)


def load_retained():
    lastpath = 'coordinacion/respuestas/AXIAL-REFERENCE-REDUCTION-001-CODEX.json'
    last = parse(pinned(lastpath, HASHES[-1]))
    pins = dict(last['code_doc_sha256'])
    pins[lastpath] = HASHES[-1]
    for path, expected in pins.items():
        pinned(path, expected)
    chain, reports = {}, {}
    for stage, expected in zip(STAGES, HASHES):
        path = 'coordinacion/respuestas/AXIAL-' + stage + '-001-CODEX.json'
        require(pins[path] == expected, 'explicit stage pin')
        report = parse(pinned(path, expected))
        require(report['id'] == 'AXIAL-' + stage + '-001', 'stage ID mismatch')
        negative_claims(report)
        for path2, h in report['code_doc_sha256'].items():
            require(pins[path2] == h, 'inherited frozen pin mismatch')
        body = payload(report)
        chain[stage] = body['cases'] if stage in STAGES[:1] + STAGES[2:3] else body['audit']['cases']
        reports[stage] = report
    for i in range(2, 6):
        require(reports[STAGES[i]]['previous_report'] ==
                {'id': 'AXIAL-' + STAGES[i-1] + '-001', 'sha256': HASHES[i-1]},
                'report-level predecessor mismatch')
    artifacts = {}
    for name, (path, h) in ARTIFACTS.items():
        require(pins[path] == h, 'existing native artifact pin')
        artifacts[name] = parse(pinned(path, h))
    return chain, artifacts, pins


def tree_identity(t, g, binding, ids, abih):
    gate = flag(t, GATES[2])
    if not gate:
        require('certificate' not in t and t['record_count'] == t['transition_count'] ==
                t['primitive_checks'] == 0, 'rejected tree has no certificate')
        return
    cert = t['certificate']
    require(digest(cert) == t['certificate_sha256'] and
            cert['geometry_case_sha256'] == digest(g), 'tree certificate/geometry link')
    require(cert['scene_binding_sha256'] == binding == t['scene_binding_sha256'] and
            cert['word_ABI_sha256'] == abih and cert['source_order'] == ids and
            cert['object_order'] == ['M', 'D'] and cert['primitive_count'] == 4,
            'restricted tree coverage identity')
    require(type(cert['primitive_count']) is int and all(type(t[k]) is int for k in
            ('record_count', 'transition_count', 'primitive_checks')), 'strict tree counts')
    require(cert['model'] == t['model'] ==
            'axial-shared-X-finite-event-tree-certificate-CPU-v1', 'restricted tree model')
    require(len(cert['trees']) == len(ids), 'all source trees required')
    for sid, tree, gp in zip(ids, cert['trees'], g['sources']):
        nodeids = [sid + ':root', sid + ':mirror', sid + ':det']
        require(len(tree) == 3 and [n['id'] for n in tree] == nodeids and
                [n['source_id'] for n in tree] == [sid]*3 and
                [n['parent'] for n in tree] == [None, nodeids[0], nodeids[1]] and
                [n['children'] for n in tree] == [[nodeids[1]], [nodeids[2]], []] and
                [n['event'] for n in tree] == ['source', 'reflect', 'detect'] and
                [n['direction_sign'] for n in tree] == [gp['direction_sign'], -gp['direction_sign'], None],
                'finite absorbing tree lineage')
        require([n['arrival_primitive_id'] for n in tree] ==
                [None] + [v['primitive_id'] for v in gp['segments']], 'tree path primitive identity')
        for node, chosen in zip(tree[:2], tree[1:]):
            partition = node['next_primitive_partition']
            require(all(type(p['primitive_id']) is int and type(p['owner']) is int for p in partition),
                    'strict primitive IDs')
            require([p['primitive_id'] for p in partition] == list(range(4)) and
                    [p['owner'] for p in partition] == [0, 0, 1, 1] and
                    [p['primitive_id'] for p in partition if p['relation'] == 'chosen'] ==
                    [chosen['arrival_primitive_id']], 'exhaustive primitive partition coverage')
        require('next_primitive_partition' not in tree[2], 'absorbing terminal')
    require(t['record_count'] == 3*len(ids) and t['transition_count'] == 2*len(ids) and
            t['primitive_checks'] == 8*len(ids), 'restricted certificate counts')


def validate_cases(chain):
    require(set(chain) == set(STAGES) and all(type(chain[k]) is dict and
            set(chain[k]) == set(NAMES) for k in STAGES), 'complete stage/case coverage')
    result = {}
    for name in NAMES:
        g, ref, tree, q, a, u, s, r = [chain[k][name] for k in STAGES]
        for c in (g, ref, tree, q, a, u, s, r):
            negative_claims(c)
        snapshot, abi = g['scene_snapshot'], g['word_ABI']
        ids = [v['id'] for v in snapshot['sources']]
        require(ids and all(type(v) is str and v for v in ids) and len(set(ids)) == len(ids),
                'unique nonempty source IDs')
        require(snapshot['schema'] == 'exp005-readback-v2' and snapshot['undeclared_meshes'] == [] and
                set(snapshot['objects']) == {'M', 'D'} and
                snapshot['objects']['M']['kind'] == 'mirror' and
                snapshot['objects']['M']['phase_rad'] == 0 and
                snapshot['objects']['D']['kind'] == 'det' and abi['object_ids'] == ['M', 'D'],
                'frozen restricted profile')
        binding = digest({'snapshot': snapshot, 'object_order': abi['object_ids'], 'source_order': ids})
        abih = digest(abi)
        require(binding == abi['original_scene_binding_sha256'] and
                abih == g['word_ABI_sha256'] and abi['source_order'] == ids, 'original scene/ABI digest')
        require(ref['source_ids'] == ids == tree['source_order'], 'reference/tree source order')
        for c in (ref, q, a, u, s, r):
            require(c['scene_binding_sha256'] == binding, 'cross-stage scene binding')
        for c in (q, a, u, s, r):
            require(c['source_order'] == ids and c['word_ABI_sha256'] == abih, 'ordered ABI identity')
        for c, key, previous in ((ref, 'geometry_case_sha256', g),
                (q, 'reference_case_sha256', ref), (q, 'tree_case_sha256', tree),
                (a, 'reference_quotient_case_sha256', q), (u, 'argument_case_sha256', a),
                (s, 'unit_case_sha256', u), (r, 'source_case_sha256', s)):
            require(c[key] == digest(previous), 'case predecessor digest: ' + key)
        inherited = ref['retained_closure_gates_UNCHANGED']
        require(type(inherited) is list and len(inherited) == 6 and
                all(type(v) is bool for v in inherited), 'strict retained legacy gates')
        require(all(c['retained_closure_gates_UNCHANGED'] == inherited and
                    all(type(v) is bool for v in c['retained_closure_gates_UNCHANGED'])
                    for c in (tree, q, a, u, s, r)), 'legacy gates immutable')
        gates = [flag(c, key) for c, key in zip((g, ref, tree, q, a, u, s, r), GATES)]
        phase = flag(g, 'accepted_phase_budget_CPU_only')
        rows = [g['sources'], ref['paths'], q['paths'], a['paths'], u['paths'], s['paths']]
        for stage_rows in rows:
            require([v['source_id'] for v in stage_rows] == ids, 'ordered path coverage')
        for c, paths, key in ((g, rows[0], GATES[0]), (ref, rows[1], GATES[1]),
                (q, rows[2], GATES[3]), (a, rows[3], GATES[4]),
                (u, rows[4], GATES[5]), (s, rows[5], GATES[6])):
            require(flag(c, key) == all(flag(p, key) for p in paths), 'path aggregate: ' + key)
        require(phase == all(flag(p, 'accepted_phase_budget_CPU_only') for p in rows[0]),
                'phase aggregate')
        require(not phase or gates[0], 'phase requires geometry')
        require(not gates[2] or gates[0], 'tree cannot revive geometry')
        require(not gates[1] or gates[0] and phase, 'reference cannot revive phase')
        require(not gates[3] or gates[1] and gates[2], 'quotient requires tree/reference')
        require(all(not gates[i] or gates[i-1] for i in range(4, 8)), 'retained downstream stop')
        tree_identity(tree, g, binding, ids, abih)
        require(ref['reference_model'] == 'axial-fixed-original-terminal-plane-reference-CPU-v1' and
                ref['reference_frame'] == 'fixed original world point; ideal unit-X plane-wave mode' and
                [rat(v) for v in ref['terminal_mode_origin_BU']] ==
                [F(v) for v in snapshot['objects']['D']['mode_origin_BU']] and
                [rat(v) for v in ref['terminal_mode_direction']] ==
                [F(v) for v in snapshot['objects']['D']['mode_direction']], 'fixed ORIGINAL terminal mode')
        terminal = 'fixed-original-plane-mode:' + binding + ':D'
        for gp, rp, qp, ap, up, sp in zip(*rows):
            pg, pp = flag(gp, GATES[0]), flag(gp, 'accepted_phase_budget_CPU_only')
            require(flag(rp, 'previous_geometry_accepted') == pg and
                    flag(rp, 'previous_phase_accepted') == pp and
                    flag(qp, 'previous_geometry_accepted') == pg and
                    flag(qp, 'previous_phase_accepted') == pp and
                    flag(qp, 'previous_reference_accepted') == flag(rp, GATES[1]) and
                    flag(ap, 'previous_reference_quotient_accepted') == flag(qp, GATES[3]) and
                    flag(up, 'previous_argument_accepted') == flag(ap, GATES[4]) and
                    flag(sp, 'previous_unit_accepted') == flag(up, GATES[5]), 'path predecessor gates')
            for p, key in ((rp, GATES[1]), (qp, GATES[3]), (ap, GATES[4]), (up, GATES[5]), (sp, GATES[6])):
                require(not flag(p, key) or 'source_phase_reference_id' in p and
                        'terminal_reference_id' in p, 'accepted path requires gauges')
                if 'source_phase_reference_id' in p:
                    require(p['source_phase_reference_id'] ==
                            'original-source-zero:' + binding + ':' + gp['source_id'] and
                            p['terminal_reference_id'] == terminal, 'source/terminal gauge')
            for p in (rp, qp, ap, up):
                if 'phase_budget_rad' in p:
                    require(rat(p['phase_budget_rad']) == rat(gp['phase_budget_rad']),
                            'original phase budget unchanged')
            require(rat(sp['field_L1_budget']) == rat(CAPS['field_L1']), 'frozen source cap')
            if flag(ap, 'argument_available'):
                require(ap['original_reference_cycles'] == qp['original_reference_cycles'] ==
                        rp['original_effective_cycles'] and ap['upstream_reference_phase_bound_rad'] ==
                        qp['composed_phase_bound_rad'] and ap['integer_turn'] == qp['selector']['integer_turn'] and
                        ap['quarter_index'] == qp['selector']['quarter_index'], 'reference selector/argument identity')
            if flag(up, 'unit_available'):
                require(up['original_reference_cycles'] == ap['original_reference_cycles'] and
                        up['quarter_index'] == ap['quarter_index'] and
                        up['argument_phase_bound_rad'] == ap['composed_argument_phase_bound_rad'],
                        'argument/unit reference identity')
            for p, prev, avail, measurement in (
                    (ap, flag(qp, GATES[3]), 'argument_available', 'measurement'),
                    (up, flag(ap, GATES[4]), 'unit_available', 'unit_measurement'),
                    (sp, flag(up, GATES[5]), 'product_available', 'measurement')):
                require(flag(p, avail) == prev and (prev or measurement not in p), 'stop/evidence availability')
            if flag(sp, 'product_available'):
                original = next(v for v in snapshot['sources'] if v['id'] == sp['source_id'])
                require([rat(v) for v in sp['source_original_rational']] ==
                        [F(v) for v in original['field_reim']], 'ORIGINAL source identity')
                require(sp['port'] == 'D' and sp['mirror_coefficient_exact_reim'] == [[-1, 1], [0, 1]] and
                        sp['measurement']['unit_uint64'] == [v ^ (1 << 63) for v in up['unit_uint64']] and
                        sp['measurement']['source_limb_uint32'] == sp['source_limb_uint32'] and
                        sp['referenced_unit_error_L1'] == up['composed_unit_error_L1_upper'],
                        'reflected unit/source word identity')
        ct = r['contract']
        require(set(ct['limits']) == set(CAPS) and
                all(rat(ct['limits'][k]) == rat(CAPS[k]) for k in CAPS), 'strict frozen group caps')
        require(ct['scene_binding_sha256'] == binding and ct['grouping_provenance'] == DECLARATION and
                ct['limits'] == CAPS and [v['source_id'] for v in ct['assignments']] == ids,
                'explicit grouping/coverage/caps')
        for assignment in ct['assignments']:
            require(assignment['source_phase_reference_id'] ==
                    'original-source-zero:' + binding + ':' + assignment['source_id'] and
                    assignment['terminal_reference_id'] == assignment['common_terminal_reference_id'] == terminal and
                    assignment['port'] == 'D' and rat(assignment['rebase_cycles']) == 0 and
                    type(assignment['coherence_group']) is str and 0 < len(assignment['coherence_group']) <= 64,
                    'explicit fixed terminal grouping gauge')
        previous = flag(s, GATES[6])
        require(flag(r, 'previous_source_accepted') == previous and
                flag(r, 'scene_field_reduced') == flag(r, 'detector_evaluated') == previous,
                'reduction availability')
        if previous:
            require(set(r['ports']) == {'D'}, 'exact terminal coverage')
            groups = r['ports']['D']['groups']
            require(set(groups) == {v['coherence_group'] for v in ct['assignments']}, 'exact group coverage')
            sourcepaths = {p['source_id']: p for p in s['paths']}
            budget_gates = []
            for key, group in groups.items():
                gid = [v['source_id'] for v in ct['assignments'] if v['coherence_group'] == key]
                require(group['source_ids'] == gid == [v['source_id'] for v in group['steps']] and
                        group['common_terminal_reference_id'] == terminal, 'group reduction coverage')
                for step in group['steps']:
                    require(step['cache']['key']['ordered_input_uint64'][2:] ==
                            sourcepaths[step['source_id']]['measurement']['output_uint64'],
                            'actual referenced terminal reduction input')
                budget_gates.extend([flag(group, 'field_absolute_pass'),
                                     flag(group['relative_field'], 'relative_budget_satisfied')])
                for relative in (group['relative_field'],):
                    require(rat(relative['ideal_reference_lower_rational']) != 0 or
                            flag(relative, 'relative_budget_satisfied') is False, 'zero lower rejects relative')
            require(flag(r, GATES[7]) == all(budget_gates +
                    [flag(r['ports']['D'], 'power_absolute_pass'),
                     flag(r['ports']['D']['relative_power'], 'relative_budget_satisfied')]),
                    'reduction budget aggregate gate')
            relative = r['ports']['D']['relative_power']
            require(rat(relative['ideal_reference_lower_rational']) != 0 or
                    flag(relative, 'relative_budget_satisfied') is False, 'zero power lower rejects relative')
        else:
            require(r['ports'] == {}, 'stopped reduction has no outputs')
        result[name] = {'scene_binding_sha256': binding, 'word_ABI_sha256': abih, 'source_ids': ids,
            'case_digests': {stage: digest(chain[stage][name]) for stage in STAGES},
            'retained_stage_gates': dict(zip(STAGES, gates)), 'retained_phase_gate': phase,
            'restricted_tree_identity_checked': gates[2],
            'partial_reference_chain_CPU_only': phase and all(gates),
            'legacy_gates_UNCHANGED': inherited, 'accepted_full_field_pipeline': False,
            'execution_authenticated': False, 'coherence_authenticated': False,
            'native_promotion_allowed': False}
    return result


def inventory(artifacts):
    require(set(artifacts) == set(ARTIFACTS), 'explicit historical inventory')
    native, guard = artifacts['native0337'], artifacts['guard0337']
    require(flag(native, 'passed') and native['backend'] == 'OPENGL' and
            native['scope'] == 'one shared scalar GPU ALU traversal for all ports inside Blender; not RT/BVH',
            'retained legacy ALU scope')
    require(type(guard['exit_code']) is int and guard['exit_code'] == 0 and
            guard['status'] == 'completed' and guard['reasons'] == [] and
            guard['deadline_utc'] == '2026-09-30T06:00:00+00:00', 'immutable closed historical guard')
    return {'native0337_probes': len(native['cases']),
            'native0337_blend_files': sorted(native['input_scene_sha256']),
            'native0337_scope': native['scope'], 'guard0337_samples': len(guard['samples']),
            'guard0337_deadline_utc': guard['deadline_utc'],
            'current_reference_chain_bound': False, 'GPU_job_admission': False,
            'equal_work_equal_output_full_costs_certified': False,
            'reason': 'legacy K3/K4 ALU probes and closed guard; not these fixed-reference RN64 scene bindings'}


def audit():
    chain, artifacts, pins = load_retained()
    cases = validate_cases(chain)
    return {'model': MODEL, 'pins': pins, 'cases': cases, 'existing_artifacts': inventory(artifacts),
            'counts': {'cases': len(cases), 'sources': sum(len(c['source_ids']) for c in cases.values()),
                       'restricted_tree_cases': sum(c['restricted_tree_identity_checked'] for c in cases.values()),
                       'partial_reference_chains_CPU_only': sum(c['partial_reference_chain_CPU_only'] for c in cases.values()),
                       'upstream_source_stops': sum(not c['retained_stage_gates'][STAGES[6]] for c in cases.values())},
            'new_geometry_phase_field_arithmetic_nodes': 0, 'production_modules_imported': False,
            'retained_writers_executed': False, 'GPU_executed': False, 'execution_authenticated': False,
            'coherence_authenticated': False, 'accepted_full_field_pipeline': False,
            'native_promotion_allowed': False, 'GPU_job_admission': False,
            'pending': ['native effective scene/limb/source-ID/ABI/fixed-reference/model binding evidence',
                        'authenticated execution lineage; SHA identity alone is not authenticity',
                        'scene/physical coherence provenance; grouping is explicit CPU hypothesis',
                        'fresh exclusive job, live telemetry, reservation and fail-closed guard',
                        'equal work/output contract and full hardware/export/transfer/build/readback costs']}
