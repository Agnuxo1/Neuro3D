"""Narrow new offline closure tests; no upstream producers or arithmetic replay."""
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Blender/benchmarks/capacity_audit'))
import axial_reference_closure_cpu_v1 as m

CHAIN, ARTIFACTS, PINS = m.load_retained()


def reject(fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError, IndexError):
        return
    raise AssertionError('fail-closed rejection missing')


def relink(c, name='positive'):
    g, ref, tree, q, a, u, s, r = [c[k][name] for k in m.STAGES]
    if 'certificate' in tree:
        tree['certificate']['geometry_case_sha256'] = m.digest(g)
        tree['certificate_sha256'] = m.digest(tree['certificate'])
    for current, key, previous in ((ref, 'geometry_case_sha256', g),
            (q, 'reference_case_sha256', ref), (q, 'tree_case_sha256', tree),
            (a, 'reference_quotient_case_sha256', q), (u, 'argument_case_sha256', a),
            (s, 'unit_case_sha256', u), (r, 'source_case_sha256', s)):
        current[key] = m.digest(previous)


def coverage():
    result = m.validate_cases(CHAIN)
    assert len(result) == 13 and sum(len(v['source_ids']) for v in result.values()) == 14
    assert sum(v['partial_reference_chain_CPU_only'] for v in result.values()) == 4
    assert result['lambda_transport_FAIL']['restricted_tree_identity_checked']
    assert not result['lambda_transport_FAIL']['partial_reference_chain_CPU_only']
    assert not result['two_sources']['partial_reference_chain_CPU_only']
    assert all(not v['accepted_full_field_pipeline'] for v in result.values())


def case_and_digest_coverage():
    c = deepcopy(CHAIN)
    del c[m.STAGES[5]]['negative']
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[4]]['positive']['reference_quotient_case_sha256'] = 'foreign'
    reject(lambda: m.validate_cases(c))


def binding_order():
    for stage, field, value in ((m.STAGES[6], 'scene_binding_sha256', 'foreign'),
            (m.STAGES[6], 'source_order', ['other']), (m.STAGES[5], 'word_ABI_sha256', 'foreign')):
        c = deepcopy(CHAIN)
        c[stage]['positive'][field] = value
        relink(c)
        reject(lambda: m.validate_cases(c))


def tree_coverage():
    c = deepcopy(CHAIN)
    c[m.STAGES[2]]['positive']['certificate']['trees'][0][0]['next_primitive_partition'].pop()
    relink(c)
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[2]]['positive']['certificate']['trees'][0][2]['children'] = ['s:root']
    relink(c)
    reject(lambda: m.validate_cases(c))


def source_gauges_and_caps():
    for field, value in (('source_phase_reference_id', 'foreign'),
                         ('terminal_reference_id', 'foreign'), ('field_L1_budget', [1, 1])):
        c = deepcopy(CHAIN)
        c[m.STAGES[6]]['positive']['paths'][0][field] = value
        relink(c)
        reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    del c[m.STAGES[6]]['positive']['paths'][0]['terminal_reference_id']
    relink(c)
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[7]]['positive']['contract']['limits']['field_L1'][0] = True
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[4]]['positive']['paths'][0]['phase_budget_rad'] = [1, 1]
    relink(c)
    reject(lambda: m.validate_cases(c))


def strict_gates_and_stops():
    c = deepcopy(CHAIN)
    c[m.STAGES[4]]['positive']['accepted_argument_CPU_only'] = 1
    relink(c)
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[4]]['boundary_FAIL']['paths'][0]['argument_available'] = True
    relink(c, 'boundary_FAIL')
    reject(lambda: m.validate_cases(c))


def grouping_and_terminal_words():
    for field, value in (('rebase_cycles', [1, 4]), ('common_terminal_reference_id', 'foreign')):
        c = deepcopy(CHAIN)
        c[m.STAGES[7]]['positive']['contract']['assignments'][0][field] = value
        reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[7]]['positive']['ports']['D']['groups']['g']['steps'][0]['cache']['key']['ordered_input_uint64'][2] ^= 1
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[6]]['positive']['paths'][0]['measurement']['unit_uint64'][0] ^= 1
    relink(c)
    reject(lambda: m.validate_cases(c))


def relative_zero_and_claims():
    c = deepcopy(CHAIN)
    c[m.STAGES[7]]['two_sources']['accepted_reduction_detector_CPU_only'] = True
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[7]]['two_sources']['ports']['D']['relative_power']['relative_budget_satisfied'] = True
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[7]]['positive']['accepted_full_field_pipeline'] = True
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[6]]['positive']['retained_closure_gates_UNCHANGED'][0] = 1
    relink(c)
    reject(lambda: m.validate_cases(c))
    c = deepcopy(CHAIN)
    c[m.STAGES[6]]['positive']['retained_closure_gates_UNCHANGED'][0] = False
    relink(c)
    reject(lambda: m.validate_cases(c))


def json_fail_closed():
    reject(lambda: m.parse('{"x":1,"x":2}'))
    reject(lambda: m.parse('{"x":NaN}'))
    reject(lambda: m.rat([True, 1]))
    reject(lambda: m.rat([1, 0]))
    reject(lambda: m.pinned('Blender/benchmarks/capacity_audit/axial_reference_closure_cpu_v1.py', '0'*64))


def historical_inventory():
    inv = m.inventory(ARTIFACTS)
    assert inv['native0337_probes'] == 246 and len(inv['native0337_blend_files']) == 12
    assert inv['guard0337_samples'] == 30 and not inv['GPU_job_admission']
    a = deepcopy(ARTIFACTS)
    a['guard0337']['deadline_utc'] = '2026-10-02T06:00:00+00:00'
    reject(lambda: m.inventory(a))


TESTS = (coverage, case_and_digest_coverage, binding_order, tree_coverage,
         source_gauges_and_caps, strict_gates_and_stops, grouping_and_terminal_words,
         relative_zero_and_claims, json_fail_closed, historical_inventory)
if __name__ == '__main__':
    for test in TESTS:
        test()
    print(json.dumps({'PASS': True, 'tests': len(TESTS), 'audit': m.audit()}, sort_keys=True, allow_nan=False))
