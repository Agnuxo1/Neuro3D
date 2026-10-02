"""Negative HOST contract test; selected-subnormal rejection is expected evidence, not a test failure."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_box_guard_counterexample_HOST_v1 as core
import axial_guarded_source_product_RN64_CPU_v1 as producer
DATA={}
def p(x):return [x.numerator,x.denominator]
Z=[[0,1],[0,1]]
class GuardBoxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=core.load_retained()
    def audit(self,v,loaded=None):
        with patch.object(core,'load_retained',return_value=self.loaded if loaded is None else loaded):
            return core.audit_guard_counterexamples_HOST(v,model=core.MODEL)
    def prove(self,box,words):return core.counterexample_HOST(box,words,model=core.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected input rejection '+label)
    def test_a_missing(self):
        with patch.object(core,'counterexample_HOST',side_effect=AssertionError('missing domain no witness checker')):
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
        x=copy.deepcopy(a);y=copy.deepcopy(b);x.pop('variant');y.pop('variant');self.assertEqual(x,y)
        self.assertEqual(len(a['cases']),17);self.assertEqual(sum(len(c['context']['source_order']) for c in a['cases'].values()),19)
        self.assertTrue(all(c['sources'] is None for c in a['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_retained_anchored_domains(self):
        with patch.object(producer,'encode_source',side_effect=AssertionError('no SOURCE execution')),patch.object(producer,'native_cast32',side_effect=AssertionError('no cast')),patch.object(core.prior,'uniform_encode_decode_HOST',side_effect=AssertionError('no old bound replay')):
            a=self.audit('synthetic_domains')
        self.assertEqual(a['exact_guard_counterexamples'],2)
        for c in a['cases'].values():
            self.assertEqual(c['status'],'STOP')
            for s in c['sources']:
                proof=s['proof'];self.assertTrue(proof[core.FLAG]);w=proof['witness']
                self.assertEqual((w['component'],w['derived_RN32_high_uint32']),(1,1))
                self.assertEqual(w['value'],p(core.TINY));self.assertEqual(w['rejection_reason'],'normal-or-zero selected word')
                self.assertFalse(proof['SOURCE_graph_executed']);self.assertFalse(proof['frozen_guard_admission_for_entire_box_proved'])
        DATA['synthetic_domains']=a
    def test_c_positive_negative_absence(self):
        tiny=core.TINY
        controls={'positive':([Z,[[0,1],p(2*tiny)]],[0,0]),
                  'negative':([Z,[p(-2*tiny),[0,1]]],[0,0]),
                  'zero_only':([Z,Z],[0,0]),
                  'normal_only':([[[1,1],[2,1]],Z],[1023<<52,0])}
        out={n:self.prove(b,w) for n,(b,w) in controls.items()}
        self.assertTrue(out['positive'][core.FLAG]);self.assertTrue(out['negative'][core.FLAG])
        self.assertEqual(out['negative']['witness']['derived_RN32_high_uint32'],(1<<31)|1)
        for n in ('zero_only','normal_only'):self.assertFalse(out[n][core.FLAG]);self.assertIsNone(out[n]['witness'])
        DATA['controls']=out
    def test_d_model_types_domains(self):
        rows=[];b=[Z,Z]
        bad=[('model',lambda:core.counterexample_HOST(b,[0,0],model='foreign')),
             ('bool_anchor',lambda:self.prove(b,[False,0])),
             ('float_endpoint',lambda:self.prove([[[0.0,1],[0,1]],Z],[0,0])),
             ('reversed',lambda:self.prove([[[1,1],[0,1]],Z],[0,0])),
             ('anchor_outside',lambda:self.prove(b,[1023<<52,0])),
             ('nonfinite_anchor',lambda:self.prove(b,[2047<<52,0])),
             ('oversize',lambda:self.prove([[[0,1],[1<<4097,1]],Z],[0,0]))]
        for label,fn in bad:self.reject(label,fn,rows)
        DATA['model_type_domain_rejections']=rows
    def test_e_ALL_INPUT_before_checker(self):
        rows=[]
        def plan(d):return d['synthetic_domain_INPUT_plans']['thin_resolved']
        mutations=[
            ('late_context',lambda d,u:plan(d).__setitem__('context_sha256','0'*64)),
            ('late_SOURCE_gauge',lambda d,u:plan(d)['sources'][0].__setitem__('source_phase_reference_id','foreign')),
            ('typed_retained_validity',lambda d,u:u['synthetic_domains']['cases']['thin_resolved'].__setitem__('domain_INPUT_valid',1)),
            ('typed_analytic_flag',lambda d,u:u['synthetic_domains']['cases']['thin_resolved']['sources'][0]['bound'].__setitem__(core.prior.FLAG,1))]
        for label,mut in mutations:
            loaded=copy.deepcopy(self.loaded);mut(loaded[1],loaded[2])
            with patch.object(core,'counterexample_HOST',side_effect=AssertionError('checker before ALL INPUT validated')) as spy:
                self.reject(label,lambda:self.audit('synthetic_domains',loaded),rows);self.assertEqual(spy.call_count,0)
        with patch.object(core,'PARENT_SHA','0'*64),patch.object(core,'counterexample_HOST',side_effect=AssertionError('before SHA')) as spy:
            self.reject('parent_SHA',core.load_retained,rows);self.assertEqual(spy.call_count,0)
        DATA['INPUT_SHA_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GuardBoxTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
