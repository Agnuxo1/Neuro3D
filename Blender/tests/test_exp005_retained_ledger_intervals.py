"""One existing GPU capture; conditional RN32 storage compatibility, CPU only.

Never executes a renderer, shader, scene tracer or peer writer. Closed rounding
cells overapproximate ties; this is not a native error or authentication proof.
"""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
REPORT = Path('D:/PROJECTS/.cognition/neuro3d/exp005_shared_native_20260930_0337.json')
REPORT_SHA = 'ca23f606478b3c5897c141ab80f877af5ba47aacd572bc527825ac7047c7d5b3'
CAPTURE = REPORT.with_suffix('')/'K3_base.json'
CAPTURE_SHA = '6f65faf5b53307103aafdc37f48e9fa96330ff0500fd0e45c18e4363308da418'
SHADER_SHA = '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1'


def ratio(x):
    x = F(x)
    return [x.numerator, x.denominator]


def cell32(value):
    """Closed real preimage of one finite normal/zero binary32, RN assumed."""
    if not math.isfinite(value):
        raise ValueError('finite binary32 required')
    word = struct.unpack('<I', struct.pack('<f', value))[0]
    represented = struct.unpack('<f', struct.pack('<I', word))[0]
    if value != represented:
        raise ValueError('captured value is not exactly binary32')
    magnitude = word & 0x7fffffff
    if magnitude == 0:
        return -F(1, 2**150), F(1, 2**150)
    if magnitude < 0x00800000 or magnitude >= 0x7f7fffff:
        raise ValueError('bounded normal/zero profile required')
    previous = struct.unpack('<f', struct.pack('<I', magnitude-1))[0]
    following = struct.unpack('<f', struct.pack('<I', magnitude+1))[0]
    absolute = F(abs(value))
    lo, hi = (F(previous)+absolute)/2, (absolute+F(following))/2
    return (lo, hi) if value > 0 else (-hi, -lo)


def compatibility(ledger, final):
    n = len(ledger)
    if not 1 <= n <= 128:
        raise ValueError('complete bounded ledger required')
    cells = [cell32(value) for value in ledger]
    lo = sum((x[0] for x in cells), F(0))
    hi = sum((x[1] for x in cells), F(0))
    # Conditional normal IEEE RN64 additions; initial zero addition exact.
    # gamma_n is deliberately conservative. Native RN/FTZ is not certified.
    u = F(1, 2**53)
    gamma = n*u/(1-n*u)
    addition_bound = gamma*sum(max(abs(a), abs(b)) for a, b in cells)
    lo -= addition_bound
    hi += addition_bound
    final_lo, final_hi = cell32(final)
    return {'compatible_conditional_RN': max(lo, final_lo) <= min(hi, final_hi),
            'disjoint_interval_gap_rational': ratio(max(F(0), max(lo, final_lo)-min(hi, final_hi))),
            'possible_sum_interval_rational': [ratio(lo), ratio(hi)],
            'final_rounding_cell_rational': [ratio(final_lo), ratio(final_hi)],
            'RN64_addition_bound_rational': ratio(addition_bound)}


def audit():
    pins = {str(REPORT): REPORT_SHA, str(CAPTURE): CAPTURE_SHA,
            str(ROOT/'Blender/shaders/exp005_shared_frontier.glsl'): SHADER_SHA}
    for name, expected in pins.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            raise ValueError('retained artifact changed: '+name)
    report = json.loads(REPORT.read_text())
    if not report['passed'] or SHADER_SHA not in report['code_sha256'].values():
        raise ValueError('retained shader/report binding required')
    rows = json.loads(CAPTURE.read_text())
    row = rows[4]  # One named coherent pair only; not the 246-probe re-audit.
    if row['probe'] != 'pair01_0' or not row['gpu']['valid']:
        raise ValueError('selected retained probe changed')
    ids = {source['id'] for source in row['snapshot']['sources']}
    ports = {}
    paths = 0
    for name, port in row['gpu']['ports'].items():
        ledger = port['ledger']
        if len(ledger) != port['paths'] or any(x['source_id'] not in ids for x in ledger):
            raise ValueError('source-owned complete retained ledger required')
        paths += len(ledger)
        checked = [compatibility([x['field_reim'][k] for x in ledger], port['field_reim'][k]) for k in (0, 1)]
        sums = [sum((F(x['field_reim'][k]) for x in ledger), F(0)) for k in (0, 1)]
        folded = [0., 0.]
        for entry in ledger:
            for k in (0, 1):
                folded[k] = struct.unpack('<f', struct.pack('<f', folded[k]+entry['field_reim'][k]))[0]
        gap = sum(abs(a-F(b)) for a, b in zip(sums, port['field_reim']))
        cell32(port['power'])
        squared = sum(F(x)*F(x) for x in port['field_reim'])
        ports[name] = {'paths': len(ledger), 'field_reim': port['field_reim'],
            'exact_ledger_sum_rational': list(map(ratio, sums)),
            'ledger_sum_to_captured_field_gap_L1_rational': ratio(gap),
            'component_storage_compatibility': checked,
            'CPU_RN32_ledger_fold': folded,
            'CPU_RN32_ledger_fold_equals_capture': folded == port['field_reim'],
            'source_path_counts': {sid: sum(x['source_id'] == sid for x in ledger) for sid in sorted(ids)},
            'captured_power_rational': ratio(port['power']),
            'captured_power_minus_exact_square_of_captured_field_rational': ratio(F(port['power'])-squared)}
    if paths != row['gpu']['work']['total_terminal_paths']:
        raise ValueError('retained total terminal count inconsistent')
    compatible = all(x['compatible_conditional_RN'] for p in ports.values() for x in p['component_storage_compatibility'])
    return {'id': 'LEDGER-INTERVAL-001-CODEX', 'probe': row['probe'], 'ports': ports,
        'all_components_conditional_RN_compatible': compatible,
        'retained_paths': paths, 'pins_verified': pins,
        'capture_pin_origin': 'current readback file fingerprint; original runtime report did not hash this file',
        'scope': 'CPU read-only comparison of one historical GPU ALU capture, conditional RN storage cells',
        'new_GPU_execution': False, 'native_error_bound_certified': False,
        'runtime_authenticated': False, 'native_promotion_allowed': False, 'no_jev_aval': True}


class RetainedIntervalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = audit()

    def test_rounding_cells_at_power_of_two_and_signed_zero(self):
        self.assertEqual(cell32(1.), (F(1)-F(1, 2**25), F(1)+F(1, 2**24)))
        self.assertEqual(cell32(-1.), (-F(1)-F(1, 2**24), -F(1)+F(1, 2**25)))
        self.assertEqual(cell32(-0.), cell32(0.))
        with self.assertRaises(ValueError):
            cell32(.1)

    def test_one_retained_probe_nonzero_gap_but_compatible_storage(self):
        evidence = self.evidence
        self.assertEqual(evidence['retained_paths'], 44)
        self.assertEqual(len(evidence['ports']), 4)
        for port in evidence['ports'].values():
            self.assertGreater(F(*port['ledger_sum_to_captured_field_gap_L1_rational']), 0)
            self.assertTrue(all(x['compatible_conditional_RN'] for x in port['component_storage_compatibility']))
            self.assertEqual(sum(port['source_path_counts'].values()), port['paths'])
        self.assertFalse(evidence['native_error_bound_certified'])

    def test_large_final_tamper_is_not_explained_by_quantized_ledger(self):
        # Separate synthetic negative; retained capture and thresholds unchanged.
        self.assertFalse(compatibility([.5, -.5], 1.)['compatible_conditional_RN'])


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(RetainedIntervalsTests))
    if hasattr(RetainedIntervalsTests, 'evidence'):
        print(json.dumps(RetainedIntervalsTests.evidence, sort_keys=True, allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
