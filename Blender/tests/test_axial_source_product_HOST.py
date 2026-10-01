"""New source-product tests only; retained receipts read, old suites never run."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib, json, struct, sys, unittest, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_source_product_HOST_v1 as core
ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = 'coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json'
SHA = '9391669247fa4b6b3576ac640174f1cd853535c78591d67ae27adc72f19beaba'

def payload(report):
    t = report['test_run']
    raw = zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']), validate=True))
    assert t['rc'] == 0 and len(raw) == t['stdout_bytes'] and hashlib.sha256(raw).hexdigest() == t['stdout_sha256']
    return json.loads(raw)

def pins_from(report):
    if 'code_doc_sha256' in report:
        return dict(report['code_doc_sha256'])
    dep = report['inherited_pin_source']
    raw = (ROOT/dep['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == dep['sha256']
    pins = pins_from(json.loads(raw)); pins[dep['path']] = dep['sha256']
    pins.update(report['own_code_doc_sha256'])
    return pins

def word(x):
    return struct.unpack('<Q', struct.pack('<d', x))[0]

class ProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT/PREVIOUS).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == SHA
        report = json.loads(raw); cls.pins = pins_from(report); cls.pins[PREVIOUS] = SHA
        for p, h in cls.pins.items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p
        cls.old = payload(report)['cases']
        packets = payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        controls = payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json').read_bytes()))['synthetic_controls']
        cls.inputs = {}
        for n, p in packets.items():
            h = core.digest(p)
            o = core.unit.quarter.prev.quotient.phase.original_cap_overlay_HOST_only(n, p, h)
            cls.inputs[n] = (n, p, o)
        for n, c in controls.items():
            cls.inputs[n] = (c['case_name'], c['parent'], c['overlay'])
        cls.before = {n: [core.digest(p), core.digest(o)] for n, (_,p,o) in cls.inputs.items()}
        cls.cases = {n: core.audit_scene_product_HOST(name,p,core.digest(p),o,core.digest(o),model=core.MODEL)
                     for n,(name,p,o) in cls.inputs.items()}
        primitive = [
            ([word(1),word(0)], [word(1),word(0)], [0,1]),
            ([word(-2),word(3)], [word(0),word(1)], [0,1]),
            ([0x3ff0000008000001,word(-0.125)], [word(1/3),word(2/7)], [1,10**12]),
            ([word(0),word(-0.0)], [word(1),word(-0.0)], [0,1]),
            ([word(1.125),word(1.125)], [word(0.5),word(0.5)], [0,1]),
            ([word(2**-80),word(-2**-80)], [word(1/3),word(-1/3)], [0,1])]
        cls.controls = [core.product_HOST(a,u,b,model=core.MODEL) for a,u,b in primitive]

    def test_actual_source_words_and_binding_not_compiled_GEMM(self):
        self.assertEqual(len(self.cases),17)
        for n,c in self.cases.items():
            old = self.old[n]
            for k in ('input_packet_sha256','overlay_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
                self.assertEqual(c[k],old[k])
            name,p,o = self.inputs[n]
            snapshot = json.loads(base64.b64decode(p['buffers_base64']['original_scene_json']))
            for r,s,prior in zip(c['sources'],snapshot['sources'],old['sources']):
                self.assertEqual(r['source_id'],s['id'])
                self.assertEqual(r['original_source_uint64'],list(struct.unpack('<QQ',struct.pack('<dd',*s['field_reim']))))
                self.assertEqual(r['upstream_unit_row_sha256'],core.digest(prior))
                self.assertEqual(r['phase_reference_id'],prior['phase_reference_id'])
                self.assertEqual(r['terminal_reference_id'],prior['terminal_reference_id'])
            self.assertEqual([core.digest(p),core.digest(o)],self.before[n])

    def test_preserve_14_previous_STOP_even_with_zero_source(self):
        rows = [r for c in self.cases.values() for r in c['sources']]
        self.assertEqual(len(rows),19)
        self.assertEqual(sum(r['source_product_evaluated'] for r in rows),5)
        for n,c in self.cases.items():
            for r,p in zip(c['sources'],self.old[n]['sources']):
                self.assertEqual(r['source_product_evaluated'],p['accepted_unit_phase_bound_CPU_only'])
                if not r['source_product_evaluated']:
                    self.assertEqual(r['reason'],p['reason'])
                    self.assertNotIn('encoded_corner_products',r)
                else:
                    self.assertEqual(r['unchanged_original_phase_cap_rad'],p['unchanged_original_phase_cap_rad'])
                    self.assertEqual(r['upstream_unit_phase_bound_rad'],p['composed_unit_phase_bound_rad'])
                    self.assertEqual(len(r['encoded_corner_products']),4)

    def test_charges_source_decode_unit_product_separate(self):
        products = self.controls + [p for c in self.cases.values() for r in c['sources'] if r['source_product_evaluated'] for p in r['encoded_corner_products']]
        self.assertEqual(len(products),26)
        for p in products:
            self.assertEqual(len(p['operations']),8)
            self.assertEqual([n['label'] for n in p['operations']],['decode0','decode1','ac','bd','ad','bc','real','imag'])
            self.assertEqual(F(*p['error_L1_to_original_source_times_ideal_unit_bound']),sum((F(*v) for v in p['charges_L1'].values()),F(0)))
            self.assertEqual(p['costs_partial'],{'HOST_encoder_RN32_casts':4,'HOST_exact_residual_subtractions':2,'HOST_decode_RN64_adds':2,'modeled_product_RN64_muls':4,'modeled_product_RN64_adds':2})
        self.assertGreater(F(*self.controls[2]['charges_L1']['source_encoding']),0)
        self.assertGreater(F(*self.controls[2]['charges_L1']['product_RN64']),0)

    def test_exact_complex_sign_cancellation_and_dark_source(self):
        self.assertEqual(self.controls[0]['product_rational'],[[1,1],[0,1]])
        self.assertEqual(self.controls[1]['product_rational'],[[-3,1],[-2,1]])
        self.assertEqual(self.controls[3]['product_rational'],[[0,1],[0,1]])
        self.assertEqual(self.controls[4]['product_rational'],[[0,1],[9,8]])
        self.assertEqual(self.controls[3]['source_encoder']['original_source_uint64'][1],1<<63)
        for i in (0,1,3,4):
            self.assertEqual(self.controls[i]['error_L1_to_original_source_times_ideal_unit_bound'],[0,1])

    def test_invalid_primitive_model_words_bound_overflow_subnormal_fail_closed(self):
        bad = [
            ([],[word(1),0],[0,1],core.MODEL),
            ([True,0],[word(1),0],[0,1],core.MODEL),
            ([0x7ff0000000000000,0],[word(1),0],[0,1],core.MODEL),
            ([word(2**-130),0],[word(1),0],[0,1],core.MODEL),
            ([0x7fefffffffffffff,0],[word(1),0],[0,1],core.MODEL),
            ([word(1),0],[1,0],[0,1],core.MODEL),
            ([word(1),0],[word(1),0],[True,1],core.MODEL),
            ([word(1),0],[word(1),0],[-1,1],core.MODEL),
            ([word(1),0],[word(1),0],[1,0],core.MODEL),
            ([word(1),0],[word(1),0],[0,1],'other')]
        for a,u,b,m in bad:
            with self.assertRaises(ValueError):
                core.product_HOST(a,u,b,model=m)
        with self.assertRaises(TypeError):
            core.product_HOST([word(1),0],[word(1),0],[0,1])

    def test_packet_source_word_swap_rehashed_rejected(self):
        name,p,o = self.inputs['positive']; bad = deepcopy(p)
        raw = bytearray(base64.b64decode(bad['buffers_base64']['sources']))
        raw[112] ^= 1
        bad['buffers_base64']['sources'] = base64.b64encode(raw).decode()
        bad['manifest']['buffers']['sources'] = {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        with self.assertRaises(ValueError):
            core.audit_scene_product_HOST(name,bad,core.digest(bad),o,core.digest(o),model=core.MODEL)

    def test_no_amplitude_threshold_field_sum_detector_native_GPU_auth(self):
        for c in self.cases.values():
            self.assertTrue(c['HOST_only'])
            for k in ('amplitude_budget_accepted','field_values_computed','field_sum_computed','detector_evaluated','native_kernel_implemented','GPU_executed','GPU_job_admission','execution_authenticated','reflection_coefficient_applied','accepted_full_field_pipeline'):
                self.assertIs(c[k],False)
            for r in c['sources']:
                self.assertFalse(r['amplitude_budget_accepted'])
                self.assertFalse(r['accepted_full_field_pipeline'])
calls=[]; rejects=[]
if __name__ == '__main__':
    original = core.product_HOST
    def capture(*args,**kwargs):
        try:
            v = original(*args,**kwargs)
        except (ValueError,TypeError) as e:
            rejects.append({'inputs':deepcopy(list(args)),'kwargs':deepcopy(kwargs),'reason':str(e),'type':type(e).__name__})
            raise
        calls.append(deepcopy(v)); return v
    core.product_HOST = capture
    run = unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProductTests))
    print(json.dumps({'PASS':run.wasSuccessful(),'tests':run.testsRun,'pins':getattr(ProductTests,'pins',{}),'cases':getattr(ProductTests,'cases',{}),'controls':getattr(ProductTests,'controls',[]),'calls':calls,'expected_rejections':rejects,'GPU_executed':False},sort_keys=True,separators=(',',':')))
    raise SystemExit(0 if run.wasSuccessful() else 1)
