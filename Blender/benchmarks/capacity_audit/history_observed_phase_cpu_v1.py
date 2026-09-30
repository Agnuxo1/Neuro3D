"""Synthetic observation consistency and conditional budget; NO GPU admission.

CPU regenerates the reference paths independently of the supplied terminal
ledger. Hashes/valid arithmetic do not authenticate its execution or geometry.
"""
from fractions import Fraction as F
import hashlib
import json

from history_wavelength_field_budget_v1 import scene_wavelength_field_budget, encoded_upper
from history_compensated_phase_budget_cpu_v1 import interval_phase_bound

SCHEMA = 'exp005-synthetic-observed-phase-CPU-v1'
REPORT_KEYS = {'schema', 'scene_binding_sha256', 'coherence_groups',
               'decoded_lambda_BU', 'terminals'}
PATH_KEYS = {'id', 'source_id', 'port', 'coherence_group',
             'effective_length_BU', 'phase_trace'}


def validate_observed_phase(snapshot, report, *, coherence_groups,
                            field_budget, intensity_budget, relative_budget):
    """Bound observed length + represented phase against the CPU ideal scene.

    No asserted length tolerance is trusted. A changed length is charged to
    phase even when its arithmetic trace is perfectly self-consistent.
    This does not check actual GPU paths, topology, modes or drivers.
    """
    raw = json.dumps(report, sort_keys=True, allow_nan=False, separators=(',', ':'))
    if type(report) is not dict or set(report) != REPORT_KEYS or report['schema'] != SCHEMA:
        raise ValueError('explicit synthetic observation schema required')
    reference = scene_wavelength_field_budget(snapshot, coherence_groups=coherence_groups,
        field_budget=field_budget, intensity_budget=intensity_budget, relative_budget=relative_budget)
    if report['scene_binding_sha256'] != reference['scene_binding_sha256']:
        raise ValueError('scene binding mismatch')
    if report['coherence_groups'] != reference['coherence_groups']:
        raise ValueError('source coherence binding mismatch')
    decoded = reference['wavelength_transport']['decoded_BU']
    if type(report['decoded_lambda_BU']) is not float or report['decoded_lambda_BU'] != decoded:
        raise ValueError('decoded wavelength mismatch')
    supplied = report['terminals']
    if type(supplied) is not list or len(supplied) != len(reference['ledger']):
        raise ValueError('complete terminal coverage required')
    by_id = {}
    for path in supplied:
        if (type(path) is not dict or set(path) != PATH_KEYS
                or type(path['id']) is not int or path['id'] < 0):
            raise ValueError('terminal schema mismatch')
        if path['id'] in by_id:
            raise ValueError('duplicate terminal ID')
        by_id[path['id']] = path
    if set(by_id) != {p['id'] for p in reference['ledger']}:
        raise ValueError('terminal ID set mismatch')
    sums = {port: {group: [F(0), F(0), 0] for group in output['groups']}
            for port, output in reference['ports'].items()}
    ledger = []
    for expected in reference['ledger']:
        observed = by_id[expected['id']]
        if any(observed[key] != expected[key] for key in ('source_id', 'port', 'coherence_group')):
            raise ValueError('terminal source/port/coherence identity mismatch')
        interval = expected['effective_length']
        bound = interval_phase_bound(observed['effective_length_BU'], decoded,
            observed['phase_trace'], length_interval=(F(*interval['rational_lower']),
            F(*interval['rational_upper'])), lambda_interval=(F(snapshot['lambda_BU']),)*2,
            field_budget=field_budget)
        amplitude = F(*expected['amplitude_upper']['rational_upper'])
        error = amplitude*F(*bound['ideal_unit_phase_error_upper']['rational_upper'])
        total = sums[expected['port']][expected['coherence_group']]
        total[0] += amplitude; total[1] += error; total[2] += 1
        ledger.append({'id': expected['id'], 'observed_effective_length_BU': observed['effective_length_BU'],
                       'field_error_upper': encoded_upper(error)})
    outputs = {}; accepted = True
    for port, groups in sums.items():
        power = F(0); fields = {}
        for group, (amplitude, error, count) in groups.items():
            fields[group] = {'path_count': count, 'field_error_upper': encoded_upper(error)}
            power += 2*amplitude*error+error*error
            accepted = accepted and error <= F(field_budget)
        accepted = accepted and power <= F(intensity_budget)
        outputs[port] = {'groups': fields, 'intensity_error_upper': encoded_upper(power)}
    return {'schema': SCHEMA, 'scene_binding_sha256': reference['scene_binding_sha256'],
        'observation_sha256': hashlib.sha256(raw.encode()).hexdigest(),
        'generated_record_count': reference['generated_record_count'], 'ledger': ledger, 'ports': outputs,
        'accepted_conditional_ideal_budget': accepted,
        'observation_execution_authenticated': False, 'native_promotion_allowed': False,
        'CPU_paths_supplied_to_GPU': False,
        'scope': 'synthetic reported scalars versus regenerated ideal CPU scene; NOT runtime/native precision',
        'no_jev_aval': True}
