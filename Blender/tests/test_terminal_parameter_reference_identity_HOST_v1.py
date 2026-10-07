"""Exact algebra probes; NOT a shader emulator, native bound or scene replay."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SHADER = 'Blender/shaders/exp005_shared_frontier.glsl'
SHADER_SHA = '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1'
RECORDS = []


def dot(a, b):
    return sum((x*y for x, y in zip(a, b, strict=True)), F(0))


def direct(o, d, r, ell, s, ep, el, edot, eadd):
    point = tuple(x+y*s+e for x, y, e in zip(o, d, ep, strict=True))
    length = ell+s+el
    return length+dot(d, tuple(x-y for x, y in zip(r, point, strict=True)))+edot+eadd


def decomposed(o, d, r, ell, s, ep, el, edot, eadd):
    return (ell+dot(d, tuple(x-y for x, y in zip(r, o, strict=True)))
            +s*(1-dot(d, d))+el-dot(d, ep)+edot+eadd)


def rational(x):
    return [str(x.numerator), str(x.denominator)]


class IdentityTests(unittest.TestCase):
    def test_source_pin(self):
        blob = (ROOT/SHADER).read_bytes()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), SHADER_SHA)
        for anchor in ('dvec3 point=ray.o+ray.d*distance;',
                       'double length=ray.length+distance;',
                       'double effective=length+dot(ray.d,reference-point);'):
            self.assertEqual(blob.decode().count(anchor), 1)
        RECORDS.append(dict(kind='SOURCE_PIN',path=SHADER,sha256=SHADER_SHA))

    def test_exact_identity_and_residual_bound(self):
        # Explicit synthetic states, not SOURCE/triangles from a scene fixture.
        o = (F(1,4), F(-3,4), F(5,4))
        r = (F(1000), F(-2), F(1,4))
        for name, d in [('unit_axial', (F(1), F(0), F(0))),
                        ('unit_rational', (F(3,5), F(4,5), F(0))),
                        ('nonunit_small_defect', (1+F(1,2**52), F(0), F(0))),
                        ('nonunit_raw', (F(1), F(1), F(0)))]:
            for s in (F(1,8), F(2**30)):
                ep = (F(1,2**60), -F(1,2**59), F(1,2**58))
                el, edot, eadd = F(1,2**57), -F(1,2**56), F(1,2**55)
                args = (o,d,r,F(7,8),s,ep,el,edot,eadd)
                actual = direct(*args)
                self.assertEqual(actual, decomposed(*args))
                baseline = F(7,8)+dot(d, tuple(x-y for x,y in zip(r,o)))
                allowance = (abs(s)*abs(1-dot(d,d))+abs(el)
                             +sum(abs(x)*abs(e) for x,e in zip(d,ep))
                             +abs(edot)+abs(eadd))
                self.assertLessEqual(abs(actual-baseline), allowance)
                RECORDS.append(dict(kind='SYNTHETIC_EXACT_IDENTITY',name=name,
                    s_BU=rational(s),direction=[rational(x) for x in d],
                    effective_BU=rational(actual),baseline_BU=rational(baseline),
                    deviation_BU=rational(actual-baseline),allowance_BU=rational(allowance)))

    def test_parameter_sensitivity(self):
        z = (F(0),)*3
        for d in ((F(3,5),F(4,5),F(0)),(1+F(1,2**52),F(0),F(0))):
            delta = direct(z,d,z,F(0),F(2),z,F(0),F(0),F(0))-direct(z,d,z,F(0),F(1),z,F(0),F(0),F(0))
            self.assertEqual(delta, 1-dot(d,d))
            self.assertEqual(delta == 0, dot(d,d) == 1)
            RECORDS.append(dict(kind='SYNTHETIC_PARAMETER_SENSITIVITY',delta_BU=rational(delta)))

    def test_unit_direction_does_not_erase_alu_residual(self):
        z = (F(0),)*3
        d = (F(1),F(0),F(0))
        # Deliberately declared residual, NOT a measured floating-point error.
        e = F(1,2**60)
        value = direct(z,d,z,F(0),F(1),z,e,F(0),F(0))
        self.assertEqual(value, e)
        self.assertNotEqual(value, 0)
        RECORDS.append(dict(kind='SYNTHETIC_UNIT_NONZERO_RESIDUAL',value_BU=rational(value)))

    def test_bias_restores_parameter_not_unit_norm(self):
        o, d = (F(1,4),F(0),F(0)), (F(2),F(0),F(0))
        bias, original_s = F(1,10**6), F(3,4)
        shifted = tuple(x+y*bias for x,y in zip(o,d))
        hit_shifted = tuple(x+y*(original_s-bias) for x,y in zip(shifted,d))
        hit_original = tuple(x+y*original_s for x,y in zip(o,d))
        self.assertEqual(hit_shifted, hit_original)
        self.assertEqual((original_s-bias)+bias, original_s)
        self.assertNotEqual(original_s, abs(hit_original[0]-o[0]))
        RECORDS.append(dict(kind='SYNTHETIC_BIAS_PARAMETER_ONLY',parameter_BU=rational(original_s),
                            axial_geometric_length_BU=rational(abs(hit_original[0]-o[0]))))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IdentityTests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(json.dumps(dict(status='PASS' if result.wasSuccessful() else 'FAIL',
        tests=result.testsRun,records=RECORDS,scope='EXACT_HOST_ALGEBRA_SYNTHETIC_ONLY',
        native_direction_norm_defect=None,native_ALU_residual_bound_BU=None,
        native_phase_error_bound_rad=None,native_precision_certified=False,
        promotion='STOP_MISSING_NATIVE_EVIDENCE',scene_replays=0,GPU_used=False)))
    raise SystemExit(0 if result.wasSuccessful() else 1)
