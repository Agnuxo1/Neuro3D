"""Variable SOURCE/fixed UNIT analytic controls; exact RNE diagnostics, not native execution."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_uniform_complex_product_HOST_v1 as core
import axial_guarded_source_product_RN64_CPU_v1 as producer
DATA={}
def p(x):return [x.numerator,x.denominator]
def pow2(e):return F(1<<e) if e>=0 else F(1,1<<(-e))
def rn(x,width):
    if x==0:return F(0)
    a=abs(x);ex=a.numerator.bit_length()-a.denominator.bit_length()
    if a<pow2(ex):ex-=1
    q=pow2(max(ex-(23 if width==32 else 52),-149 if width==32 else -1074))
    t=a/q;n,r=divmod(t.numerator,t.denominator)
    if 2*r>t.denominator or (2*r==t.denominator and n%2):n+=1
    return (-1 if x<0 else 1)*n*q
class ProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=core.load_retained();cls.name='nonexact_geometry_phase_PASS'
        cls.b=cls.loaded[2]['synthetic_domains']['cases'][cls.name]['sources'][0]['bound']
        cls.words=cls.loaded[4]['cases'][cls.name]['sources'][0]['result']['unit_uint64']
    def audit(self,v,loaded=None):
        with patch.object(core,'load_retained',return_value=self.loaded if loaded is None else loaded):
            return core.audit_uniform_product_HOST(v,model=core.MODEL,arithmetic_model=core.ARITH)
    def prove(self,b,words):return core.product_bound_HOST(b,words,model=core.MODEL,arithmetic_model=core.ARITH)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected reject '+label)
    def test_a_missing(self):
        with patch.object(core,'product_bound_HOST',side_effect=AssertionError('missing domain no numeric product')):
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
        x=copy.deepcopy(a);y=copy.deepcopy(b);x.pop('variant');y.pop('variant');self.assertEqual(x,y)
        self.assertEqual(len(a['cases']),17);self.assertEqual(sum(len(c['context']['source_order']) for c in a['cases'].values()),19)
        self.assertTrue(all(c['sources'] is None for c in a['cases'].values()));DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_anchored_products_no_replay(self):
        with patch.object(producer,'execute',side_effect=AssertionError('no SOURCE producer')),patch.object(producer,'encode_source',side_effect=AssertionError('no encoder')),patch.object(core.encoder,'uniform_encode_decode_HOST',side_effect=AssertionError('no old constructor')):
            a=self.audit('synthetic_domains')
        self.assertEqual((a['analytical_product_bounds'],a['blocked_guard_boxes_preserved']),(2,2))
        for c in a['cases'].values():
            for s in c['sources']:
                self.assertTrue(s['whole_box_guard_admission_disproved']);self.assertTrue(s['proof'][core.FLAG])
                self.assertFalse(s['proof']['UNIT_error_to_ORIGINAL_included']);self.assertEqual(len(s['proof']['nodes']),6)
                self.assertIsNone(s['proof']['uniform_executed_SOURCE_error_L1'])
        DATA['synthetic_domains']=a
    def test_c_UNIT_controls_and_simulations(self):
        one=1023<<52;neg=one|(1<<63)
        controls={'zero':[0,0],'axis_one':[one,0],'opposite':[one,neg],'negative_axis':[neg,0]}
        DATA['UNIT_controls']={n:self.prove(self.b,w) for n,w in controls.items()}
        self.assertEqual(DATA['UNIT_controls']['zero']['uniform_error_to_A_times_fixed_represented_UNIT_L1'],[0,1])
        proof=self.prove(self.b,self.words);u=[core.guard.bits(w,64) for w in self.words]
        anchor=core.guard.bits(self.loaded[4]['cases'][self.name]['sources'][0]['admission']['ORIGINAL_source_uint64'][0],64)
        xs=[(anchor,F(0)),(anchor,pow2(-149)),(anchor,-pow2(-149)),(anchor,pow2(-20)),(anchor,-pow2(-20)),
            (anchor+pow2(-24),F(0)),(anchor-pow2(-24),F(0)),(anchor,pow2(-21))]
        samples=[]
        for xy in xs:
            for x,(lo,hi) in zip(xy,core.domain.box_values(self.b['box_reim'])):self.assertLessEqual(lo,x);self.assertLessEqual(x,hi);self.assertEqual(rn(x,64),x)
            decode=[]
            for x in xy:
                h=rn(x,32);r=rn(x-h,64);low=rn(r,32);decode.append(rn(h+low,64))
            a,b=decode;c,d=u
            values=[rn(a*c,64),rn(b*d,64),rn(a*d,64),rn(b*c,64)]
            re=rn(values[0]-values[1],64);im=rn(values[2]+values[3],64)
            target=[xy[0]*c-xy[1]*d,xy[0]*d+xy[1]*c]
            error=abs(re-target[0])+abs(im-target[1])
            self.assertLessEqual(error,F(*proof['uniform_error_to_A_times_fixed_represented_UNIT_L1']))
            exact_args=[a*c,b*d,a*d,b*c,values[0]-values[1],values[2]+values[3]]
            output=values+[re,im]
            for arg,out,node in zip(exact_args,output,proof['nodes']):
                self.assertLessEqual(abs(arg),F(*node['exact_argument_max']));self.assertLessEqual(abs(out-arg),F(*node['RN64_error_bound']))
            samples.append({'kind':'CPU_synthetic_exact_RNE_simulation','SOURCE_A_reim':list(map(p,xy)),
                'decoded_SOURCE_reim':list(map(p,decode)),'product_nodes':list(map(p,output)),
                'target_A_times_fixed_UNIT_reim':list(map(p,target)),'observed_error_L1':p(error)})
        DATA['sample_product_proof']=proof;DATA['exact_RNE_simulations']=samples
    def test_d_model_word_certificate_ranges(self):
        rows=[];wrong=copy.deepcopy(self.b);wrong[core.encoder.FLAG]=1
        changed=copy.deepcopy(self.b);changed['components'][0]['encoding_error_bound']=[0,1]
        bad=[('model',lambda:core.product_bound_HOST(self.b,self.words,model='foreign',arithmetic_model=core.ARITH)),
             ('arithmetic_FMA',lambda:core.product_bound_HOST(self.b,self.words,model=core.MODEL,arithmetic_model='FMA')),
             ('bool_UNIT_word',lambda:self.prove(self.b,[False,0])),
             ('nonfinite_UNIT',lambda:self.prove(self.b,[2047<<52,0])),
             ('UNIT_count',lambda:self.prove(self.b,[0])),
             ('typed_encoder_flag',lambda:self.prove(wrong,self.words)),
             ('encoder_charge_forgery',lambda:self.prove(changed,self.words)),
             ('node_MAX_margin',lambda:core.node_majorant(core.encoder.MAX[64],'ac','mul'))]
        for label,fn in bad:self.reject(label,fn,rows)
        DATA['model_word_range_rejections']=rows
    def test_e_ALL_INPUT_before_majorants(self):
        rows=[]
        def plan(d):return d['synthetic_domain_INPUT_plans']['thin_resolved']
        mutations=[
            ('late_context',lambda d,e,g,b:plan(d).__setitem__('context_sha256','0'*64)),
            ('late_SOURCE_gauge',lambda d,e,g,b:plan(d)['sources'][0].__setitem__('source_phase_reference_id','foreign')),
            ('UNIT_binding',lambda d,e,g,b:b['cases']['thin_resolved']['sources'][0]['result'].__setitem__('unit_uint64',[1023<<52,0])),
            ('typed_guard_negative',lambda d,e,g,b:g['synthetic_domains']['cases']['thin_resolved']['sources'][0]['proof'].__setitem__(core.prior.FLAG,1))]
        for label,mut in mutations:
            loaded=copy.deepcopy(self.loaded);mut(loaded[1],loaded[2],loaded[3],loaded[4])
            with patch.object(core,'product_bound_HOST',side_effect=AssertionError('majorants before ALL INPUT')) as spy:
                self.reject(label,lambda:self.audit('synthetic_domains',loaded),rows);self.assertEqual(spy.call_count,0)
        with patch.object(core,'PARENT_SHA','0'*64),patch.object(core,'product_bound_HOST',side_effect=AssertionError('before SHA')) as spy:
            self.reject('parent_SHA',core.load_retained,rows);self.assertEqual(spy.call_count,0)
        DATA['INPUT_SHA_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProductTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
