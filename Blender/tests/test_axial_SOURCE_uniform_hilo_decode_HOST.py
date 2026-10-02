"""CPU synthetic rational RNE diagnostics; no native producer/device/guard admission."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_uniform_hilo_decode_HOST_v1 as core
DATA={}
def p(x):return [x.numerator,x.denominator]
def dyadic(e):return F(2**e) if e>=0 else F(1,2**(-e))
def rn(x,bits):
    if not x:return F(0)
    a=abs(x);e=a.numerator.bit_length()-a.denominator.bit_length()
    if a<dyadic(e):e-=1
    q=dyadic(max(e-(23 if bits==32 else 52),-149 if bits==32 else -1074))
    t=a/q;n,r=divmod(t.numerator,t.denominator)
    if 2*r>t.denominator or (2*r==t.denominator and n%2):n+=1
    return (-1 if x<0 else 1)*n*q
def box(x,y=F(0)):return [[p(x),p(x)],[p(y),p(y)]]
class EncoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=core.load_retained()
    def bound(self,b):return core.uniform_encode_decode_HOST(b,model=core.MODEL,arithmetic_model=core.ARITHMETIC_MODEL)
    def audit(self,v,loaded=None):
        with patch.object(core,'load_retained',return_value=self.loaded if loaded is None else loaded):
            return core.audit_uniform_encoder_HOST(v,model=core.MODEL,arithmetic_model=core.ARITHMETIC_MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected rejection '+label)
    def test_a_missing(self):
        with patch.object(core,'uniform_encode_decode_HOST',side_effect=AssertionError('missing domain cannot calculate')):
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
        aa=copy.deepcopy(a);bb=copy.deepcopy(b);aa.pop('variant');bb.pop('variant');self.assertEqual(aa,bb)
        self.assertEqual(len(a['cases']),17);self.assertEqual(sum(len(c['context']['source_order']) for c in a['cases'].values()),19)
        self.assertTrue(all(c['sources'] is None for c in a['cases'].values()));DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_anchored_domains(self):
        with patch.object(core.prior.prior,'inspect_certificate',side_effect=AssertionError('no point certificate reuse')),patch.object(core.prior.prior.phase.prior.prior,'execute',side_effect=AssertionError('no native graph')):
            a=self.audit('synthetic_domains')
        self.assertEqual(a['analytical_encoder_decode_bounds'],2)
        for c in a['cases'].values():
            self.assertEqual(c['status'],'STOP');self.assertIsNone(c['uniform_executed_SOURCE_error_L1'])
            for s in c['sources']:self.assertTrue(s['bound'][core.FLAG]);self.assertFalse(s['bound']['uniform_SOURCE_enclosure_proved'])
        DATA['synthetic_domains']=a
    def test_c_boxes_and_exact_simulations(self):
        z=F(0);tiny=dyadic(-149)
        controls={'zero':box(z),'signed_subnormal':[[p(-tiny),p(tiny)],[p(z),p(z)]],
                  'positive_normal':[[p(F(1)),p(F(2))],[p(F(3)),p(F(4))]],
                  'negative_normal':[[p(F(-3)),p(F(-2))],[p(F(-2)),p(F(-1))]]}
        DATA['box_controls']={n:self.bound(b) for n,b in controls.items()}
        self.assertEqual(DATA['box_controls']['zero']['source_encoding_plus_decode_uniform_L1_bound'],[0,1])
        tie=F(1)+dyadic(-24)
        xs=[z,dyadic(-1074),-dyadic(-1074),tiny,-tiny,F.from_float(0.1),F.from_float(-0.1),tie,-tie,tie-dyadic(-52),tie+dyadic(-52),dyadic(100)+dyadic(76)]
        samples=[]
        for x in xs:
            self.assertEqual(rn(x,64),x)
            h=rn(x,32);r=rn(x-h,64);low=rn(r,32);a=rn(h+low,64)
            b=self.bound(box(x));c=b['components'][0]
            self.assertLessEqual(abs(h+low-x),F(*c['encoding_error_bound']))
            self.assertLessEqual(abs(a-h-low),F(*c['decode_RN64_error_bound']))
            self.assertEqual(h+low-x,(r-(x-h))+(low-r))
            self.assertLessEqual(abs(a-x),F(*c['encoding_plus_decode_bound']))
            samples.append({'kind':'CPU_synthetic_exact_RNE_simulation','x':p(x),'h':p(h),'residual':p(r),'low':p(low),'decoded':p(a),
                            'encoding_error':p(abs(h+low-x)),'decode_error':p(abs(a-h-low)),'total_error':p(abs(a-x)),'bound':b})
        DATA['exact_RNE_simulations']=samples
    def test_d_models_ranges_types(self):
        rows=[];normal=box(F(1))
        bad=[('model',lambda:core.uniform_encode_decode_HOST(normal,model='foreign',arithmetic_model=core.ARITHMETIC_MODEL)),
             ('arithmetic_FTZ',lambda:core.uniform_encode_decode_HOST(normal,model=core.MODEL,arithmetic_model='FTZ')),
             ('above_MAX32',lambda:self.bound(box(core.MAX[32]*2))),
             ('MAX32_margin',lambda:self.bound(box(core.MAX[32]))),
             ('reversed',lambda:self.bound([[[2,1],[1,1]],[[0,1],[0,1]]])),
             ('bool',lambda:self.bound([[[True,1],[2,1]],[[0,1],[0,1]]])),
             ('noncanonical',lambda:self.bound([[[2,2],[2,1]],[[0,1],[0,1]]])),
             ('oversize',lambda:self.bound(box(F(1<<4097))))]
        for label,fn in bad:self.reject(label,fn,rows)
        DATA['model_range_rejections']=rows
    def test_e_INPUT_before_calculation(self):
        rows=[]
        def plan(d):return d['synthetic_domain_INPUT_plans']['thin_resolved']
        mutations=[
            ('late_context',lambda d:plan(d).__setitem__('context_sha256','0'*64)),
            ('late_SOURCE_gauge',lambda d:plan(d)['sources'][0].__setitem__('source_phase_reference_id','foreign')),
            ('late_anchor_outside',lambda d:plan(d)['sources'][0].__setitem__('box_reim',[[[7,1],[8,1]],[[7,1],[8,1]]])),
            ('typed_retained_digest',lambda d:d['synthetic_scene_domains']['cases']['thin_resolved']['domain_INPUT'].__setitem__('domain_INPUT_valid',1))]
        for label,mut in mutations:
            loaded=copy.deepcopy(self.loaded);mut(loaded[2])
            with patch.object(core,'uniform_encode_decode_HOST',side_effect=AssertionError('calculation before ALL INPUT validated')) as spy:
                self.reject(label,lambda:self.audit('synthetic_domains',loaded),rows);self.assertEqual(spy.call_count,0)
        with patch.object(core,'PARENT_SHA','0'*64),patch.object(core,'uniform_encode_decode_HOST',side_effect=AssertionError('before SHA')) as spy:
            self.reject('parent_SHA',core.load_retained,rows);self.assertEqual(spy.call_count,0)
        DATA['INPUT_SHA_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EncoderTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
