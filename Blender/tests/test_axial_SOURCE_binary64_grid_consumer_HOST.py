"""Own sealed GRID consumer tests, no numerical replay or native SOURCE."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_binary64_grid_consumer_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=c.load_retained()
    def audit(self,v,x=None):
        with patch.object(c,'load_retained',return_value=self.loaded if x is None else x):
            return c.audit_consumer_HOST(v,model=c.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected rejection '+label)
    def test_a_missing(self):
        with patch.object(c,'inspect_retained_SOURCE_HOST',side_effect=AssertionError('no cert without GRID')) as spy:
            a=self.audit('real_missing');b=self.audit('explicit_None_missing');p=self.audit('domain_present_grid_missing')
            self.assertEqual(spy.call_count,0)
        self.assertEqual(a['cases'],b['cases']);self.assertEqual(len(a['cases']),17)
        self.assertEqual(sum(len(v['context']['source_order']) for v in a['cases'].values()),19)
        self.assertEqual(len(p['cases']),3)
        for audit in (a,b,p):
            self.assertEqual(audit['retained_SOURCE_certificate_inspections'],0)
            self.assertTrue(all(v['sources'] is None for v in audit['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b;DATA['domain_present_grid_missing']=p
    def test_b_conditional_join(self):
        with patch.object(c.theorem,'component_wordclasses_HOST',side_effect=AssertionError('no old predicate')),patch.object(c.theorem,'audit_wordclasses_HOST',side_effect=AssertionError('no old audit')):
            a=self.audit('synthetic_valid')
        self.assertEqual(a['bound_SOURCE_certificates'],4);self.assertEqual(a['conditional_sufficient_SOURCE_count'],2)
        self.assertEqual(a['retained_negative_guard_SOURCE_count'],2)
        for name,case in a['cases'].items():
            for row in case['sources']:
                self.assertTrue(row[c.BOUND]);self.assertTrue(all(row[k] is False for k in c.FALSE))
                self.assertFalse(row['actual_scene_domain_grid_authenticated'])
                self.assertFalse(row['frozen_guard_admission_for_entire_box_proved']);self.assertIsNone(row['uniform_executed_SOURCE_error_L1'])
                self.assertEqual(row[c.SUFFICIENT],name=='two_sources')
        self.assertEqual(a['new_wordclass_predicates'],0);self.assertEqual(a['group_admissions'],0)
        DATA['synthetic_valid']=a
    def test_c_ALL_INPUT_before_inspect(self):
        rows=[]
        changes=[
            ('late_GRID_context',lambda x:x[3]['synthetic_grid_INPUT_plans']['two_sources'].__setitem__('context_sha256','0'*64)),
            ('late_GRID_signbit',lambda x:x[3]['synthetic_grid_INPUT_plans']['two_sources']['sources'][-1]['ORIGINAL_source_uint64'].__setitem__(1,0)),
            ('late_domain_context',lambda x:x[1]['synthetic_domain_INPUT_plans']['two_sources'].__setitem__('context_sha256','0'*64)),
            ('baseline_bool_alias',lambda x:x[3]['synthetic_valid']['cases']['two_sources']['INPUT'].__setitem__(c.prior.FLAG,1)),
            ('domain_bool_alias',lambda x:x[1]['synthetic_validated_domains']['two_sources'].__setitem__('domain_INPUT_valid',1)),
            ('prior_context_alias',lambda x:x[2]['synthetic_valid']['cases']['two_sources']['context'].__setitem__('execution_authenticated',0))]
        # A sign change is always different even if the original imaginary magnitude is zero.
        changes[1]=('late_GRID_signbit',lambda x:x[3]['synthetic_grid_INPUT_plans']['two_sources']['sources'][-1]['ORIGINAL_source_uint64'].__setitem__(1,x[3]['synthetic_grid_INPUT_plans']['two_sources']['sources'][-1]['ORIGINAL_source_uint64'][1]^(1<<63)))
        for label,mut in changes:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'inspect_retained_SOURCE_HOST',side_effect=AssertionError('ALL INPUT before ANY inspect')) as spy:
                self.reject(label,lambda:self.audit('synthetic_valid',x),rows);self.assertEqual(spy.call_count,0)
        DATA['INPUT_rejections']=rows
    def test_d_ALL_CERT_before_emit(self):
        rows=[]
        def row(x):return x[2]['synthetic_valid']['cases']['two_sources']['sources'][-1]
        changes=[
            ('late_cert_flag_bool_alias',lambda x:row(x).__setitem__(c.theorem.FLAG,1)),
            ('late_cert_domain',lambda x:row(x).__setitem__('domain_source_sha256','0'*64)),
            ('late_cert_component_interval',lambda x:row(x)['components'][0].__setitem__('interval',[[1,1],[1,1]])),
            ('late_cert_component_arithmetic',lambda x:row(x)['components'][0].__setitem__('arithmetic_model','FTZ')),
            ('late_cert_proof_missing',lambda x:row(x)['components'][0].__setitem__('proof',None)),
            ('late_cert_actual_guard',lambda x:row(x).__setitem__('frozen_guard_admission_for_entire_box_proved',True)),
            ('late_cert_negative_alias',lambda x:row(x).__setitem__('retained_whole_box_guard_admission_disproved',1)),
            ('late_cert_FALSE_alias',lambda x:row(x).__setitem__(c.FALSE[0],0)),
            ('late_cert_extra',lambda x:row(x).__setitem__('authority',True)),
            ('late_cert_coverage',lambda x:x[2]['synthetic_valid']['cases']['two_sources']['sources'].pop()),
            ('late_cert_seal',lambda x:x[-1]['two_sources'].__setitem__(row(x)['source_id'],'0'*64))]
        for label,mut in changes:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'emit_conditional_SOURCE_HOST',side_effect=AssertionError('ALL cert before ANY emit')) as spy:
                self.reject(label,lambda:self.audit('synthetic_valid',x),rows);self.assertEqual(spy.call_count,0)
        DATA['certificate_rejections']=rows
    def test_e_model_and_lineage(self):
        rows=[]
        self.reject('foreign_model',lambda:c.audit_consumer_HOST('synthetic_valid',model='foreign'),rows)
        self.reject('unknown_variant',lambda:c.audit_consumer_HOST('foreign',model=c.MODEL),rows)
        with patch.object(c,'PARENT_SHA','0'*64):self.reject('parent_SHA',c.load_retained,rows)
        DATA['model_lineage_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
