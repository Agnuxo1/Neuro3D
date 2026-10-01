"""Read retained scenes; isolate cast order, NOT a native shader emulator.

No scene traversal or previous producer rerun. Phase is assumed identity.
Python binary64/struct binary32 arithmetic is CPU evidence, not GPU evidence.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'Blender/shaders/exp005_shared_frontier.glsl': '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1',
    'Blender/benchmarks/capacity_audit/shared_frontier_gpu.py': 'f38a93ae116be66284062297a31aa4dac37c40f7d9eefcf77fc4c146aca23c6b',
    'Blender/tests/exp005_blender_gpu.py': '851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497',
    'Blender/benchmarks/capacity_audit/scene_field_producer_cpu_v1.py': '1a697f1cbe6dab515d27dbf5e4c022aae8b6099115b9961d225c0a318de3d380',
    'coordinacion/respuestas/SCENE-CONVERSION-001-CODEX.json': 'ad04c656087db7511171da92146e17eba73343714c6c43222f046650fd53fd20',
}


def rn32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def ratio(x):
    x = F(x)
    return [x.numerator, x.denominator]


def audit():
    for name, digest in PINS.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise ValueError('changed retained dependency: '+name)
    # Import only the already inspected pure split helper, never main/Bpy/GPU.
    sys.path.insert(0, str(Path(__file__).parent))
    from exp005_blender_gpu import split_double
    retained = json.loads((ROOT/'coordinacion/respuestas/SCENE-CONVERSION-001-CODEX.json').read_text())
    rows = []
    for case in retained['observations']['cases']:
        scene = case['snapshot']
        if scene['lambda_BU'] != .125 or list(scene['objects']) != ['D']:
            raise ValueError('identity-phase retained control required')
        for path in case['producer']['path_evidence']:
            if path['effective_length']['rational_lower'] != [3, 1] or path['effective_length']['rational_upper'] != [3, 1]:
                raise ValueError('retained ideal length changed')
        ideal = [sum((F(s['field_reim'][k]) for s in scene['sources']), F(0)) for k in (0, 1)]
        transported, ledger, transport_errors = [], [], []
        for source in scene['sources']:
            pair, error = [], []
            for value in source['field_reim']:
                hi, lo = split_double(value)
                recovered = hi+lo
                pair.append(recovered)
                error.append(abs(F(recovered)-F(value)))
            transported.append(pair)
            ledger.append(list(map(rn32, pair)))
            transport_errors.append(list(map(ratio, error)))
        accumulated = [0., 0.]
        ledger_accumulated = [0., 0.]
        for pair, diagnostic in zip(transported, ledger):
            for k in (0, 1):
                accumulated[k] += pair[k]
                ledger_accumulated[k] = rn32(ledger_accumulated[k]+diagnostic[k])
        final = list(map(rn32, accumulated))
        # Shader source computes dot on dvec2 BEFORE casting the intensity lane.
        power_lane = rn32(accumulated[0]*accumulated[0]+accumulated[1]*accumulated[1])
        field_squared = sum((F(x)*F(x) for x in final), F(0))
        rows.append({'name': case['name'], 'scene_binding_sha256': case['producer']['scene_binding_sha256'],
            'ideal_field_rational': list(map(ratio, ideal)),
            'source_transport_errors_rational': transport_errors,
            'transported_field_rational': [list(map(ratio, x)) for x in transported],
            'ledger_field_rational': [list(map(ratio, x)) for x in ledger],
            'ledger_RN32_reduction_rational': list(map(ratio, ledger_accumulated)),
            'modeled_accumulate64_cast32_field_rational': list(map(ratio, final)),
            'retained_per_path32_CPU_field_rational': case['modeled_field_rational'],
            'modeled_field_error_L1_rational': ratio(sum(abs(F(a)-b) for a, b in zip(final, ideal))),
            'modeled_power_lane_rational': ratio(power_lane),
            'rounded_field_exact_squared_rational': ratio(field_squared),
            'power_lane_minus_squared_rounded_field_rational': ratio(F(power_lane)-field_squared)})
    return {'id': 'CAST-ORDER-001-CODEX', 'pins_verified': PINS, 'cases': rows,
        'scope': 'CPU isolated identity-phase cast order model plus pinned shader source review',
        'GPU_executed': False, 'shader_compiled': False, 'native_emulation_complete': False,
        'old_producer_rerun': False, 'native_promotion_allowed': False, 'no_jev_aval': True,
        'excluded': ['geometry and phase arithmetic', 'native sin/cos', 'GPU RN/FTZ/reassociation/FMA',
                     'runtime completeness/authentication', 'RT and physical optics']}


class CastOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = audit()
        cls.cases = {r['name']: r for r in cls.evidence['cases']}

    def test_pinned_shader_uses_double_accumulation_not_ledger_feedback(self):
        code = (ROOT/'Blender/shaders/exp005_shared_frontier.glsl').read_text()
        for fragment in ('dvec2 sum_fields[5]', 'sum_fields[port]+=field;',
                         'float(field.x),float(field.y),float(dot(field,field))',
                         'imageStore(ledger_out'):
            self.assertIn(fragment, code)
        self.assertIn('float angle=float(phase-', code)
        self.assertNotIn('imageLoad(ledger_out', code)

    def test_dark_residual_survives64_model_but_not_quantized_ledger(self):
        case = self.cases['near_dark_absolute_not_relative']
        # Actual hi-lo transport errors differ between sources: do not assume
        # they cancel. Exact recovered sum is 2^-30 - 2^-53, not 2^-30.
        self.assertEqual(case['modeled_accumulate64_cast32_field_rational'], [[2**23-1, 2**53], [0, 1]])
        self.assertEqual(case['ledger_RN32_reduction_rational'], [[0, 1], [0, 1]])
        self.assertEqual(case['retained_per_path32_CPU_field_rational'], [[0, 1], [0, 1]])
        self.assertEqual(case['modeled_field_error_L1_rational'], [1, 2**53])
        recovered = sum(F(*row[0]) for row in case['transported_field_rational'])
        self.assertEqual(recovered, F(1, 2**30)-F(1, 2**53))

    def test_single_high_field_final_cast_still_loses_bits(self):
        case = self.cases['high_amplitude_CPU_only']
        self.assertEqual(case['modeled_field_error_L1_rational'], [53687091, 2**30])
        self.assertEqual(case['modeled_accumulate64_cast32_field_rational'], case['retained_per_path32_CPU_field_rational'])

    def test_power_lane_is_not_exact_square_of_rounded_field(self):
        ordinary = self.cases['ordinary']
        self.assertNotEqual(ordinary['power_lane_minus_squared_rounded_field_rational'], [0, 1])
        self.assertGreater(F(*ordinary['source_transport_errors_rational'][0][0]), 0)
        self.assertFalse(self.evidence['native_emulation_complete'])
        self.assertFalse(self.evidence['native_promotion_allowed'])


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(CastOrderTests))
    if hasattr(CastOrderTests, 'evidence'):
        print(json.dumps(CastOrderTests.evidence, sort_keys=True, allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
